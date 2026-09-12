export interface Citation {
  source_file: string;
  standard_number: string;
  clause: string;
  page_number?: number | null;
  snippet: string;
  source_url?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  grounded?: boolean;
  source?: string;
  error?: boolean;
  retryOf?: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  query: string;
  response: string;
  citations: Citation[];
  grounded: boolean;
  source: string;
  gated: boolean;
}

export interface HealthService {
  status: string;
  model?: string;
  url?: string;
  model_ready?: boolean;
  vectors?: number;
  collection?: string;
  error?: string;
}

export interface HealthReport {
  status: string;
  services: {
    chroma: HealthService;
    embedding: HealthService;
    ollama: HealthService;
    groq: HealthService;
  };
}

export interface DocumentReviewCheck {
  label: string;
  status: "pass" | "review";
  detail: string;
}

export interface DocumentReviewResult {
  filename: string;
  file_type: string;
  size_bytes: number;
  review_status: string;
  standards: string[];
  dates_found: string[];
  checks: DocumentReviewCheck[];
  disclaimer: string;
  checked_at: string;
}

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

/**
 * fetch() with an AbortController timeout so the UI can never hang forever
 * when the backend is slow or unreachable.
 */
async function fetchWithTimeout(
  input: string,
  init: RequestInit = {},
  timeoutMs = 60000
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const isFormData = init.body instanceof FormData;
    const res = await fetch(input, {
      ...init,
      signal: controller.signal,
      headers: isFormData
        ? init.headers
        : { "Content-Type": "application/json", ...(init.headers ?? {}) },
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }
    return res;
  } catch (err: unknown) {
    if ((err as Error).name === "AbortError") {
      throw new Error(
        "The backend took too long to respond. Please try again."
      );
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export async function postChatQuestion(
  question: string,
  history: ChatTurn[] = []
): Promise<ChatResponse> {
  // Use a longer timeout (200 seconds) to accommodate slow local Ollama generation.
  const res = await fetchWithTimeout(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    body: JSON.stringify({ question, history }),
  }, 200_000);
  return res.json();
}

/**
 * SSE streaming chat. Consumes /api/chat/stream and invokes callbacks as
 * `message` (token) and `done` (final citations/grounded/source) events
 * arrive, so tokens can be rendered progressively.
 */
export interface StreamDone {
  query: string;
  response: string;
  citations: Citation[];
  grounded: boolean;
  source: string;
  gated: boolean;
}

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onDone: (payload: StreamDone) => void;
  onError: (message: string) => void;
  /** User-initiated stop (abort() on the signal passed to streamChatQuestion). */
  onCancel?: () => void;
}

function handleSSEBlock(block: string, cb: StreamCallbacks) {
  let data = "";
  for (const raw of block.split("\n")) {
    const line = raw.replace(/\r$/, "");
    // The `event:` name duplicates payload.type — dispatch on the JSON.  Also
    // skip comment / keepalive lines (": ping") which have no payload.
    if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return;
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(data);
  } catch {
    return; // incomplete/malformed block — ignore
  }
  switch (payload.type) {
    case "message":
      cb.onToken(typeof payload.content === "string" ? payload.content : "");
      break;
    case "done":
      cb.onDone(payload as unknown as StreamDone);
      break;
    case "error":
      cb.onError(
        typeof payload.message === "string"
          ? payload.message
          : "Unknown streaming error"
      );
      break;
  }
}

/**
 * SSE streaming chat. Consumes /api/chat/stream and invokes callbacks as
 * `message` (token) and `done` (final citations/grounded/source) events
 * arrive, so tokens can be rendered progressively.
 *
 * Pass an optional `signal` (e.g. a Stop button's AbortController) to cancel
 * mid-stream. A caller-initiated abort calls `onCancel`; only the internal
 * 200s timeout is reported as an `onError`.
 */
export async function streamChatQuestion(
  question: string,
  history: ChatTurn[] = [],
  cb: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 200_000);
  // Merge the caller's signal (Stop button) with the internal timeout so an
  // abort is unambiguous: caller-initiated -> onCancel, timeout -> onError.
  const onExternalAbort = () => controller.abort();
  if (signal) {
    if (signal.aborted) controller.abort();
    else signal.addEventListener("abort", onExternalAbort, { once: true });
  }
  let sawDone = false;
  let reportedError = false;
  const wrapped: StreamCallbacks = {
    onToken: cb.onToken,
    onDone: (payload) => {
      sawDone = true;
      cb.onDone(payload);
    },
    onError: (message) => {
      reportedError = true;
      cb.onError(message);
    },
    onCancel: cb.onCancel,
  };
  try {
    const res = await fetch(`${BACKEND_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history }),
      signal: controller.signal,
    });
    if (!res.ok || !res.body) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // sse-starlette frames events with CRLF (`\r\n\r\n`). Splitting on
      // `\n\n` never matches that, so the whole body was previously treated
      // as one block, JSON.parse failed, and the UI rendered nothing.
      buffer = buffer.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
      let sep = buffer.indexOf("\n\n");
      while (sep !== -1) {
        handleSSEBlock(buffer.slice(0, sep), wrapped);
        buffer = buffer.slice(sep + 2);
        sep = buffer.indexOf("\n\n");
      }
    }
    // Flush any final block that was not terminated by a blank line.
    if (buffer.trim()) handleSSEBlock(buffer, wrapped);
    if (!sawDone && !reportedError && !signal?.aborted) {
      wrapped.onError(
        "The assistant returned an empty response. Please try again."
      );
    }
  } catch (err: unknown) {
    if ((err as Error).name === "AbortError") {
      if (signal?.aborted) {
        cb.onCancel?.();
      } else {
        wrapped.onError("The backend took too long to respond. Please try again.");
      }
    } else {
      wrapped.onError(
        err instanceof Error ? err.message : "Unknown connection error"
      );
    }
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", onExternalAbort);
  }
}

export async function fetchHealth(): Promise<HealthReport> {
  const res = await fetchWithTimeout(`${BACKEND_URL}/health`, {}, 8000);
  return res.json();
}
export async function reviewDocument(
  file: File
): Promise<DocumentReviewResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetchWithTimeout(
    BACKEND_URL + "/api/review",
    { method: "POST", body: form },
    60000
  );
  return res.json();
}
