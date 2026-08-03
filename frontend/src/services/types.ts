export type DocumentStatus = "pending" | "processing" | "ready" | "failed";

export interface DocumentOut {
  id: string;
  filename: string;
  status: DocumentStatus;
  num_pages: number;
  error_message?: string | null;
  created_at: string;
}

export interface SourceRef {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_type: string;
  snippet: string;
  score: number;
  image_url?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: SourceRef[];
  created_at?: string;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: SourceRef[];
  agent_used: "rag" | "translation" | "summarization" | "multimodal" | "fallback";
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  status: DocumentStatus;
  message: string;
}

export type WSMessageType =
  | "query"
  | "token"
  | "sources"
  | "done"
  | "error"
  | "status"
  | "history_updated";

export interface WSMessage {
  type: WSMessageType;
  payload: any;
}

// ---------- Chat History ----------

export interface ChatSessionSummary {
  id: string;
  title: string;
  document_id?: string | null;
  document_name?: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail {
  id: string;
  title: string;
  document_id?: string | null;
  document_name?: string | null;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface HistoryUpdatedPayload {
  action: "message" | "rename" | "clear" | "delete" | "create";
  session_id: string;
  title?: string;
}
