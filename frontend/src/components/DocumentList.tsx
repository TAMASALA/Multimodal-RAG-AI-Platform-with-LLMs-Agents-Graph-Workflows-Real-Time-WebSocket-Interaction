import { useCallback, useEffect, useRef, useState } from "react";
import { deleteDocument, listDocuments } from "../services/api";
import type { DocumentOut } from "../services/types";

interface DocumentListProps {
  refreshKey: number;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  onPreview?: (documentId: string) => void;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "#999",
  processing: "#e0a800",
  ready: "#2e7d32",
  failed: "#c62828",
};

export default function DocumentList({
  refreshKey,
  selectedIds,
  onSelectionChange,
  onPreview,
}: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const lastRefreshKeyRef = useRef<number | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (lastRefreshKeyRef.current === refreshKey) {
      return;
    }

    lastRefreshKeyRef.current = refreshKey;
    void refresh();
  }, [refresh, refreshKey]);

  useEffect(() => {
    const hasActiveProcessing = documents.some(
      (doc) => doc.status === "pending" || doc.status === "processing"
    );

    if (!hasActiveProcessing) {
      return;
    }

    const interval = window.setInterval(() => {
      void refresh();
    }, 4000);

    return () => window.clearInterval(interval);
  }, [documents, refresh]);

  function toggleSelection(id: string) {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((x) => x !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  }

  function handleItemClick(id: string) {
    if (onPreview) {
      onPreview(id);
    } else {
      toggleSelection(id);
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    await deleteDocument(id);
    await refresh();
  }

  if (loading && documents.length === 0) {
    return <p className="muted">Loading documents...</p>;
  }

  if (documents.length === 0) {
    return <p className="muted">No documents uploaded yet.</p>;
  }

  return (
    <ul className="document-list">
      {documents.map((doc) => (
        <li
          key={doc.id}
          className={`document-item ${selectedIds.includes(doc.id) ? "selected" : ""}`}
          onClick={() => handleItemClick(doc.id)}
        >
          <div className="document-item-main">
            <span className="document-name" title={doc.filename}>
              {doc.filename}
            </span>
            <span
              className="document-status"
              style={{ color: STATUS_COLORS[doc.status] || "#666" }}
            >
              {doc.status}
            </span>
          </div>
          <div className="document-item-meta">
            <span>{doc.num_pages} pages</span>
            <div className="document-item-actions">
              {onPreview && (
                <button
                  className="select-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleSelection(doc.id);
                  }}
                  title={
                    selectedIds.includes(doc.id)
                      ? "Remove from chat filter"
                      : "Use in chat filter"
                  }
                >
                  {selectedIds.includes(doc.id) ? "✓ selected" : "select"}
                </button>
              )}
              <button className="delete-btn" onClick={(e) => handleDelete(doc.id, e)}>
                delete
              </button>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
