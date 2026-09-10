export type Language = "en" | "hi" | "te" | "unknown";

export type Citation = {
  evidence_id: string;
  document_id: string;
  document_title: string | null;
  standard_number: string | null;
  clause_number: string | null;
  page_number: number | null;
  excerpt: string;
  version: string | null;
  source_url: string | null;
};

export type AssistantResponse = {
  answer: string;
  confidence: "high" | "medium" | "low";
  evidence_sufficient: boolean;
  citations: Citation[];
  related_standards: string[];
  unknowns: string[];
  warnings: string[];
  source_documents: string[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function askBIS(question: string, language: Language): Promise<AssistantResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/assistant/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? "The BIS service is temporarily unavailable.");
  }
  return response.json() as Promise<AssistantResponse>;
}
