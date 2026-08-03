import { useState } from "react";
import type { ChatSessionSummary } from "../../services/types";
import { useChatHistory } from "../../hooks/useChatHistory";

interface ChatHistoryItemProps {
  session: ChatSessionSummary;
  isActive: boolean;
}

function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

export default function ChatHistoryItem({ session, isActive }: ChatHistoryItemProps) {
  const { selectSession, rename, remove, clear } = useChatHistory();
  const [isEditing, setIsEditing] = useState(false);
  const [draftTitle, setDraftTitle] = useState(session.title);
  const [menuOpen, setMenuOpen] = useState(false);

  async function commitRename() {
    const trimmed = draftTitle.trim();
    setIsEditing(false);
    if (trimmed && trimmed !== session.title) {
      await rename(session.id, trimmed);
    } else {
      setDraftTitle(session.title);
    }
  }

  return (
    <div
      className={`history-item ${isActive ? "active" : ""}`}
      onClick={() => !isEditing && selectSession(session.id)}
    >
      <div className="history-item-main">
        {isEditing ? (
          <input
            autoFocus
            className="history-item-rename-input"
            value={draftTitle}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => setDraftTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitRename();
              if (e.key === "Escape") {
                setDraftTitle(session.title);
                setIsEditing(false);
              }
            }}
            onBlur={commitRename}
          />
        ) : (
          <span className="history-item-title" title={session.title}>
            {session.title}
          </span>
        )}

        <button
          className="history-item-menu-btn"
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpen((v) => !v);
          }}
          aria-label="Conversation options"
        >
          ⋮
        </button>
      </div>

      <div className="history-item-meta">
        {session.document_name && (
          <span className="history-item-doc" title={session.document_name}>
            📄 {session.document_name}
          </span>
        )}
        <span className="history-item-time">{formatRelativeTime(session.updated_at)}</span>
      </div>

      {menuOpen && (
        <div className="history-item-menu" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => {
              setIsEditing(true);
              setMenuOpen(false);
            }}
          >
            Rename
          </button>
          <button
            onClick={() => {
              clear(session.id);
              setMenuOpen(false);
            }}
          >
            Clear messages
          </button>
          <button
            className="danger"
            onClick={() => {
              remove(session.id);
              setMenuOpen(false);
            }}
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}
