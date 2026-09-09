export interface Citation {
  source_file: string;
  standard_number: string;
  clause: string;
  page_number?: number | null;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  grounded?: boolean;
}

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function postChatQuestion(
  question: string,
  history: { role: "user" | "assistant"; content: string }[] = []
): Promise<{
  query: string;
  response: string;
  citations: Citation[];
  grounded: boolean;
}> {
  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, history }),
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

