import type { ChatResponse, DocumentOut, UploadResponse } from "./types";

const API_BASE_URL: string =
  (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<UploadResponse>(res);
}

export async function listDocuments(): Promise<DocumentOut[]> {
  const res = await fetch(`${API_BASE_URL}/api/documents`);
  const data = await handleResponse<{ documents: DocumentOut[] }>(res);
  return data.documents;
}

export async function getDocumentStatus(documentId: string): Promise<DocumentOut> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
  return handleResponse<DocumentOut>(res);
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: "DELETE",
  });
  await handleResponse(res);
}

export async function sendChatMessage(
  query: string,
  sessionId: string | null,
  documentIds?: string[],
  targetLanguage?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      query,
      document_ids: documentIds,
      target_language: targetLanguage,
    }),
  });
  return handleResponse<ChatResponse>(res);
}

export { API_BASE_URL };
