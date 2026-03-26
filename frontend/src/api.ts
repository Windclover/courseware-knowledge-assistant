import type {
  AssessmentSuite,
  ChatRecord,
  DocumentDetail,
  DocumentSummary,
  MarkdownPreview,
  UploadResponse,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(data?.detail ?? "请求失败，请稍后重试。");
  }
  return (await response.json()) as T;
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`);
  return parseResponse<DocumentSummary[]>(response);
}

export async function fetchDocumentDetail(
  documentId: string,
): Promise<DocumentDetail> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
  return parseResponse<DocumentDetail>(response);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });
  return parseResponse<UploadResponse>(response);
}

export async function fetchMarkdownPreview(
  documentId: string,
): Promise<MarkdownPreview> {
  const response = await fetch(
    `${API_BASE_URL}/api/documents/${documentId}/markdown`,
  );
  return parseResponse<MarkdownPreview>(response);
}

export async function sendChatMessage(
  documentId: string,
  question: string,
): Promise<ChatRecord> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, scope: "all" }),
  });
  return parseResponse<ChatRecord>(response);
}

export async function generateAssessment(
  documentId: string,
): Promise<AssessmentSuite> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/assessment`, {
    method: "POST",
  });
  return parseResponse<AssessmentSuite>(response);
}

export function markdownDownloadUrl(documentId: string): string {
  return `${API_BASE_URL}/api/documents/${documentId}/markdown?download=true`;
}
