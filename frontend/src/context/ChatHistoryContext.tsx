import {
  createContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  clearChatSession,
  createChatSession,
  deleteChatSession,
  getChatSessionDetail,
  listChatSessions,
  renameChatSession,
  searchChatSessions,
} from "../services/historyApi";
import { HistorySocket } from "../websocket/historySocket";
import type { ChatSessionDetail, ChatSessionSummary } from "../services/types";

interface ChatHistoryContextValue {
  sessions: ChatSessionSummary[];
  activeSessionId: string | null;
  activeSessionDetail: ChatSessionDetail | null;
  loading: boolean;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  refresh: () => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  startNewChat: (documentId?: string) => Promise<ChatSessionSummary>;
  rename: (sessionId: string, title: string) => Promise<void>;
  remove: (sessionId: string) => Promise<void>;
  clear: (sessionId: string) => Promise<void>;
}

export const ChatHistoryContext = createContext<ChatHistoryContextValue | null>(null);

export function ChatHistoryProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSessionDetail, setActiveSessionDetail] = useState<ChatSessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const socketRef = useRef<HistorySocket | null>(null);

  const refresh = useCallback(async (queryOverride?: string) => {
    setLoading(true);
    try {
      const trimmedQuery = (queryOverride ?? searchQuery).trim();
      const results = trimmedQuery
        ? await searchChatSessions(trimmedQuery)
        : await listChatSessions();
      setSessions(results);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  const selectSession = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    const detail = await getChatSessionDetail(sessionId);
    setActiveSessionDetail(detail);
  }, []);

  const startNewChat = useCallback(
    async (documentId?: string) => {
      const session = await createChatSession("New Chat", documentId);
      await refresh(searchQuery);
      setActiveSessionId(session.id);
      setActiveSessionDetail({
        id: session.id,
        title: session.title,
        document_id: session.document_id,
        document_name: session.document_name,
        created_at: session.created_at,
        updated_at: session.updated_at,
        messages: [],
      });
      return session;
    },
    [refresh, searchQuery]
  );

  const rename = useCallback(
    async (sessionId: string, title: string) => {
      await renameChatSession(sessionId, title);
      await refresh();
      if (activeSessionId === sessionId) {
        setActiveSessionDetail((prev) => (prev ? { ...prev, title } : prev));
      }
    },
    [refresh, activeSessionId]
  );

  const remove = useCallback(
    async (sessionId: string) => {
      await deleteChatSession(sessionId);
      await refresh();
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setActiveSessionDetail(null);
      }
    },
    [refresh, activeSessionId]
  );

  const clear = useCallback(
    async (sessionId: string) => {
      await clearChatSession(sessionId);
      await refresh();
      if (activeSessionId === sessionId) {
        setActiveSessionDetail((prev) => (prev ? { ...prev, messages: [] } : prev));
      }
    },
    [refresh, activeSessionId]
  );

  // Initial load and a debounced re-query when search text changes.
  useEffect(() => {
    const trimmed = searchQuery.trim();
    const timer = window.setTimeout(() => {
      void refresh(trimmed);
    }, 250);

    return () => window.clearTimeout(timer);
  }, [refresh, searchQuery]);

  // Live sync: any create/rename/clear/delete/message event anywhere
  // refreshes the sidebar list, and refreshes the open conversation's
  // messages if the event belongs to the currently active session.
  useEffect(() => {
    const socket = new HistorySocket({
      onUpdated: (payload) => {
        refresh();
        if (payload.session_id === activeSessionId) {
          if (payload.action === "message" || payload.action === "clear") {
            getChatSessionDetail(activeSessionId).then(setActiveSessionDetail).catch(() => {});
          }
          if (payload.action === "rename" && payload.title) {
            setActiveSessionDetail((prev) =>
              prev ? { ...prev, title: payload.title as string } : prev
            );
          }
        }
      },
    });
    socket.connect();
    socketRef.current = socket;
    return () => socket.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId]);

  const value: ChatHistoryContextValue = {
    sessions,
    activeSessionId,
    activeSessionDetail,
    loading,
    searchQuery,
    setSearchQuery: (q) => {
      setSearchQuery(q);
    },
    refresh,
    selectSession,
    startNewChat,
    rename,
    remove,
    clear,
  };

  return (
    <ChatHistoryContext.Provider value={value}>{children}</ChatHistoryContext.Provider>
  );
}
