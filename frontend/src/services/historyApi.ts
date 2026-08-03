import { API_BASE_URL } from "./api";
import type {
  ChatSessionSummary,
  ChatSessionDetail,
} from "./types";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed (${res.status})`;

    try {
      const body = await res.json();
      message = body.detail ?? message;
    } catch {}

    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

/* ---------------------------------------
   Create Session
---------------------------------------- */

export async function createChatSession(
  title = "New Chat",
  documentName?: string
): Promise<ChatSessionSummary> {
  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
        document_name: documentName,
      }),
    }
  );

  return handleResponse<ChatSessionSummary>(res);
}

/* ---------------------------------------
   List Sessions
---------------------------------------- */

export async function listChatSessions(): Promise<ChatSessionSummary[]> {
  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions`
  );

  return handleResponse<ChatSessionSummary[]>(res);
}

/* ---------------------------------------
   Search
---------------------------------------- */

export async function searchChatSessions(
  query: string
): Promise<ChatSessionSummary[]> {

  const url = new URL(
    `${API_BASE_URL}/api/history/sessions/search`
  );

  url.searchParams.set("q", query);

  const res = await fetch(url.toString());

  return handleResponse<ChatSessionSummary[]>(res);
}

/* ---------------------------------------
   Session Detail
---------------------------------------- */

export async function getChatSessionDetail(
  sessionId: string
): Promise<ChatSessionDetail> {

  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions/${sessionId}`
  );

  return handleResponse<ChatSessionDetail>(res);
}

/* ---------------------------------------
   Rename
---------------------------------------- */

export async function renameChatSession(
  sessionId: string,
  title: string
): Promise<ChatSessionDetail> {

  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions/${sessionId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
      }),
    }
  );

  return handleResponse<ChatSessionDetail>(res);
}

/* ---------------------------------------
   Delete
---------------------------------------- */

export async function deleteChatSession(
  sessionId: string
): Promise<void> {

  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions/${sessionId}`,
    {
      method: "DELETE",
    }
  );

  await handleResponse(res);
}

/* ---------------------------------------
   Clear Messages
---------------------------------------- */

export async function clearChatSession(
  sessionId: string
): Promise<void> {

  const res = await fetch(
    `${API_BASE_URL}/api/history/sessions/${sessionId}/messages`,
    {
      method: "DELETE",
    }
  );

  if (!res.ok && res.status !== 404) {
    throw new Error("Unable to clear chat.");
  }
}