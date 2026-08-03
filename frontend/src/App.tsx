import { useState } from "react";
import ChatPage from "./pages/ChatPage";
import DocumentsPage from "./pages/DocumentsPage";
import HistoryPage from "./pages/HistoryPage";
import { ChatHistoryProvider } from "./context/ChatHistoryContext";
import { DocumentSelectionProvider } from "./context/DocumentSelectionContext";

type Tab = "chat" | "documents" | "history";

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");

  return (
    <ChatHistoryProvider>
      <DocumentSelectionProvider>
        <div className="app-shell">
          <nav className="app-nav">
            <button
              className={tab === "chat" ? "active" : ""}
              onClick={() => setTab("chat")}
            >
              Chat
            </button>
            <button
              className={tab === "documents" ? "active" : ""}
              onClick={() => setTab("documents")}
            >
              Documents
            </button>
            <button
              className={tab === "history" ? "active" : ""}
              onClick={() => setTab("history")}
            >
              History
            </button>
          </nav>

          <div className="app-content">
            {tab === "chat" && <ChatPage />}
            {tab === "documents" && <DocumentsPage />}
            {tab === "history" && <HistoryPage onOpenInChat={() => setTab("chat")} />}
          </div>
        </div>
      </DocumentSelectionProvider>
    </ChatHistoryProvider>
  );
}

