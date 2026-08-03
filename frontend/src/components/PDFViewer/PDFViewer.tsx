import { API_BASE_URL } from "../../services/api";

interface PDFViewerProps {
  documentId: string;
  initialPage?: number;
}

/**
 * Embeds the original uploaded PDF using the browser's native PDF renderer.
 * `initialPage` uses the standard #page= fragment supported by Chrome/Firefox/Edge.
 */
export default function PDFViewer({ documentId, initialPage }: PDFViewerProps) {
  const src = `${API_BASE_URL}/api/documents/${documentId}/file${
    initialPage ? `#page=${initialPage}` : ""
  }`;

  return (
    <div className="pdf-viewer">
      <iframe title="PDF preview" src={src} className="pdf-viewer-frame" />
    </div>
  );
}
