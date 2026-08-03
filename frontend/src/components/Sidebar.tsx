import { useState } from "react";
import UploadPanel from "./UploadPanel";
import DocumentList from "./DocumentList";

interface SidebarProps {
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

export default function Sidebar({ selectedIds, onSelectionChange }: SidebarProps) {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Documents</h2>
      <UploadPanel onUploaded={() => setRefreshKey((k) => k + 1)} />
      <DocumentList
        refreshKey={refreshKey}
        selectedIds={selectedIds}
        onSelectionChange={onSelectionChange}
      />
      <p className="sidebar-hint">
        {selectedIds.length > 0
          ? `Filtering chat to ${selectedIds.length} selected document(s).`
          : "No filter: searching across all documents."}
      </p>
    </aside>
  );
}
