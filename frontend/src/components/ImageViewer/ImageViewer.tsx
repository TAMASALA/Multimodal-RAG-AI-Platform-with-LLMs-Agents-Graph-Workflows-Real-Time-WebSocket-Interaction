import { API_BASE_URL } from "../../services/api";

interface ImageViewerProps {
  imageUrl: string;
  caption?: string;
  pageNumber?: number;
}

/**
 * Renders a single extracted image (embedded photo/figure) alongside its
 * OCR-derived caption/snippet, used inline in source citations or a
 * dedicated document media panel.
 */
export default function ImageViewer({ imageUrl, caption, pageNumber }: ImageViewerProps) {
  const fullUrl = imageUrl.startsWith("http") ? imageUrl : `${API_BASE_URL}${imageUrl}`;

  return (
    <figure className="image-viewer">
      <img src={fullUrl} alt={caption || "Extracted document image"} loading="lazy" />
      {(caption || pageNumber) && (
        <figcaption>
          {pageNumber && <span className="image-viewer-page">p.{pageNumber}</span>}
          {caption && <span className="image-viewer-caption">{caption}</span>}
        </figcaption>
      )}
    </figure>
  );
}
