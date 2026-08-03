import { useChatHistory } from "../../hooks/useChatHistory";

export default function ChatHistorySearch() {
  const { searchQuery, setSearchQuery } = useChatHistory();

  return (
    <div className="history-search">
      <input
        type="text"
        placeholder="Search conversations..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="history-search-input"
      />
      {searchQuery && (
        <button
          className="history-search-clear"
          onClick={() => setSearchQuery("")}
          aria-label="Clear search"
        >
          ×
        </button>
      )}
    </div>
  );
}
