import { useChatHistory } from "../../hooks/useChatHistory";
import ChatHistorySearch from "./ChatHistorySearch";
import ChatHistoryItem from "./ChatHistoryItem";

interface ChatHistorySidebarProps {
  onNewChat?: () => void;
}

export default function ChatHistorySidebar({ onNewChat }: ChatHistorySidebarProps) {
  const { sessions, activeSessionId, loading, startNewChat, searchQuery } = useChatHistory();

  async function handleNewChat() {
    await startNewChat();
    onNewChat?.();
  }

  return (
    <div className="history-sidebar">
      <button className="history-new-chat-btn" onClick={handleNewChat}>
        + New Chat
      </button>

      <ChatHistorySearch />

      <div className="history-list">
        {loading && sessions.length === 0 && <p className="muted">Loading conversations...</p>}

        {!loading && sessions.length === 0 && (
          <p className="muted">
            {searchQuery ? "No matching conversations." : "No conversations yet."}
          </p>
        )}

        {sessions.map((session) => (
          <ChatHistoryItem
            key={session.id}
            session={session}
            isActive={session.id === activeSessionId}
          />
        ))}
      </div>
    </div>
  );
}
