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
  const res = await fetchWithTimeout(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    body: JSON.stringify({ question, history }),
  });
  return res.json();
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
