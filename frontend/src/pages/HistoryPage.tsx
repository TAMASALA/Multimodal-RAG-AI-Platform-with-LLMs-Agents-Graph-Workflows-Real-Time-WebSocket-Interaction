import React from "react";

interface HistoryPageProps {
  onOpenInChat: () => void;
}

const HistoryPage: React.FC<HistoryPageProps> = ({ onOpenInChat }) => {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Chat History</h1>
      <p>Your previous conversations will appear here.</p>
      <button onClick={onOpenInChat}>Open chat</button>
    </div>
  );
};

export default HistoryPage;