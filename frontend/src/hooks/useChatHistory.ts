import { useContext } from "react";
import { ChatHistoryContext } from "../context/ChatHistoryContext";

/**
 * Convenience hook for accessing chat history state/actions (sessions list,
 * active session, search, create/rename/delete/clear). Must be used within
 * a <ChatHistoryProvider>.
 */
export function useChatHistory() {
  const ctx = useContext(ChatHistoryContext);
  if (!ctx) {
    throw new Error("useChatHistory must be used within a ChatHistoryProvider");
  }
  return ctx;
}
