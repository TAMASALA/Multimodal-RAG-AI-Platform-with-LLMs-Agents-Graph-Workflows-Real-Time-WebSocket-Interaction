import { useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import ChatHistorySidebar from "../components/ChatHistory/ChatHistorySidebar";
import LanguageSelector from "../components/LanguageSelector/LanguageSelector";
import { useChatHistory } from "../hooks/useChatHistory";
import { useDocumentSelection } from "../hooks/useDocumentSelection";

export default function ChatPage() {
  const { selectedIds, setSelectedIds } = useDocumentSelection();
  const [targetLanguage, setTargetLanguage] = useState<string | null>(null);
  const { activeSessionDetail } = useChatHistory();

  return (
    <div className="chat-page three-column">
      <ChatHistorySidebar />

      <main className="chat-main">
        <header className="chat-header">
          <h1>
            {activeSessionDetail?.title || "Multimodal RAG Assistant"}
            {activeSessionDetail?.document_name && (
              <span className="chat-header-doc"> · {activeSessionDetail.document_name}</span>
            )}
          </h1>
          <LanguageSelector value={targetLanguage} onChange={setTargetLanguage} />
        </header>
        <ChatWindow selectedDocumentIds={selectedIds} targetLanguage={targetLanguage} />
      </main>

      <Sidebar selectedIds={selectedIds} onSelectionChange={setSelectedIds} />
    </div>
  );
}

