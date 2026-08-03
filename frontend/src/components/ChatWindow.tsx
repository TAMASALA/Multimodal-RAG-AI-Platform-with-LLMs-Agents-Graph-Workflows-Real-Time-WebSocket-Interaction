import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";
import { ChatSocket } from "../websocket/chatSocket";
import { sendChatMessage } from "../services/api";
import type { ChatMessage, SourceRef } from "../services/types";
import { new_id } from "../services/utils";
import { useChatHistory } from "../hooks/useChatHistory";

interface ChatWindowProps {
  selectedDocumentIds: string[];
  targetLanguage: string | null;
}

export default function ChatWindow({
  selectedDocumentIds,
  targetLanguage,
}: ChatWindowProps) {
  const {
    activeSessionId,
    activeSessionDetail,
    startNewChat,
  } = useChatHistory();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [streaming, setStreaming] = useState(false);

  const socketRef = useRef<ChatSocket | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const pendingSources = useRef<SourceRef[]>([]);
  const assistantId = useRef<string | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Always sync from provider whenever not actively streaming.
  useEffect(() => {
    if (!streaming) {
      setMessages(activeSessionDetail?.messages ?? []);
    }
  }, [activeSessionDetail, streaming]);

  useEffect(() => {
    if (!activeSessionId) {
      socketRef.current?.close();
      socketRef.current = null;
      setConnected(false);
      return;
    }

    const socket = new ChatSocket(activeSessionId, {
      onOpen: () => setConnected(true),

      onClose: () => setConnected(false),

      onSources: (sources) => {
        pendingSources.current = sources;
      },

      onToken: (text) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId.current
              ? {
                  ...m,
                  content: m.content + text,
                }
              : m
          )
        );
      },

      onDone: () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId.current
              ? {
                  ...m,
                  sources: pendingSources.current,
                }
              : m
          )
        );

        assistantId.current = null;
        pendingSources.current = [];
        setStreaming(false);
      },

      onError: (err) => {
        console.error(err);
        setStreaming(false);
      },
    });

    socket.connect();
    socketRef.current = socket;

    return () => {
      socket.close();
    };
  }, [activeSessionId]);

  useEffect(() => {
    const container = document.querySelector(".chat-messages") as HTMLElement | null;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  async function waitForSocket(): Promise<boolean> {
    for (let i = 0; i < 100; i++) {
      if (socketRef.current?.isConnected()) {
        return true;
      }

      await new Promise((r) => setTimeout(r, 50));
    }

    return false;
  }

  async function handleSend() {
    const query = input.trim();

    if (!query || streaming) return;

    setInput("");

    let sessionId = activeSessionId;

    if (!sessionId) {
      try {
        const session = await startNewChat();
        sessionId = session.id;
      } catch (e) {
        console.error(e);
        return;
      }
    }

    const userMessage: ChatMessage = {
      id: new_id(),
      role: "user",
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);

    // Translation endpoint (REST)
    if (targetLanguage) {
      setStreaming(true);

      try {
        const response = await sendChatMessage(
          query,
          sessionId,
          selectedDocumentIds.length
            ? selectedDocumentIds
            : undefined,
          targetLanguage
        );

        setMessages((prev) => [
          ...prev,
          {
            id: new_id(),
            role: "assistant",
            content: response.answer,
            sources: response.sources,
          },
        ]);
      } catch (err) {
        console.error(err);
      } finally {
        setStreaming(false);
      }

      return;
    }

    const placeholderId = new_id();

    assistantId.current = placeholderId;
    pendingSources.current = [];

    setMessages((prev) => [
      ...prev,
      {
        id: placeholderId,
        role: "assistant",
        content: "",
        sources: [],
      },
    ]);

    setStreaming(true);

    const ready = await waitForSocket();

    if (!ready || !socketRef.current) {
      console.error("WebSocket not connected.");
      setStreaming(false);
      return;
    }

    socketRef.current.sendQuery(
      query,
      selectedDocumentIds.length
        ? selectedDocumentIds
        : undefined
    );
  }

  function handleKeyDown(
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-status">
        {connected ? "🟢 Connected" : "🟡 Connecting..."}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <h2>Welcome 👋</h2>
            <p>Upload a PDF and ask anything about it.</p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
          />
        ))}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          ref={inputRef}
          className="chat-input"
          rows={2}
          value={input}
          placeholder="Ask something about your documents..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        <button
          className="send-button"
          disabled={streaming}
          onClick={handleSend}
        >
          {streaming ? "Generating..." : "Send"}
        </button>
      </div>
    </div>
  );
}