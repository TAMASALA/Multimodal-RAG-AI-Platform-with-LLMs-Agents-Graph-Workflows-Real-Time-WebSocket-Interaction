import { API_BASE_URL } from "../../services/api";

interface GraphViewerProps {
  imageUrl: string;
  description: string;
  pageNumber?: number;
}

/**
 * Renders a chart/graph image next to its vision-LLM-generated factual
 * description (trends, axes, key data points) so users can visually verify
 * what the assistant read off the chart.
 */
export default function GraphViewer({ imageUrl, description, pageNumber }: GraphViewerProps) {
  const fullUrl = imageUrl.startsWith("http") ? imageUrl : `${API_BASE_URL}${imageUrl}`;

  return (
    <div className="graph-viewer">
      <img src={fullUrl} alt="Extracted chart or graph" loading="lazy" />
      <div className="graph-viewer-details">
        {pageNumber && <span className="graph-viewer-page">Page {pageNumber}</span>}
        <p className="graph-viewer-description">{description}</p>
      </div>
    </div>
  );
}
