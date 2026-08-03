import type { ChatMessage } from "../services/types";
import GraphViewer from "./GraphViewer/GraphViewer";
import ImageViewer from "./ImageViewer/ImageViewer";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
        <p className="message-content">{message.content}</p>

        {!isUser && message.sources && message.sources.length > 0 && (
          <details className="sources-details">
            <summary>{message.sources.length} source(s)</summary>
            <ul className="sources-list">
              {message.sources.map((s) => (
                <li key={s.chunk_id} className="source-item">
                  <strong>
                    {s.document_name} — p.{s.page_number} ({s.chunk_type})
                  </strong>

                  {s.image_url && s.chunk_type === "graph" && (
                    <GraphViewer
                      imageUrl={s.image_url}
                      description={s.snippet}
                      pageNumber={s.page_number}
                    />
                  )}
                  {s.image_url && s.chunk_type === "image" && (
                    <ImageViewer
                      imageUrl={s.image_url}
                      caption={s.snippet}
                      pageNumber={s.page_number}
                    />
                  )}
                  {!s.image_url && <p className="source-snippet">{s.snippet}</p>}

                  <span className="source-score">score: {s.score.toFixed(3)}</span>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
