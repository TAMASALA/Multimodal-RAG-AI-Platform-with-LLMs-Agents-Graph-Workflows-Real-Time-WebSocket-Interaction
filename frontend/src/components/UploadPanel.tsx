import { useRef, useState } from "react";
import { uploadDocument } from "../services/api";

interface UploadPanelProps {
  onUploaded: () => void;
}

export default function UploadPanel({ onUploaded }: UploadPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      onUploaded();
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="upload-panel">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        disabled={uploading}
        id="pdf-upload-input"
        style={{ display: "none" }}
      />
      <label htmlFor="pdf-upload-input" className="upload-button">
        {uploading ? "Uploading..." : "+ Upload PDF"}
      </label>
      {error && <p className="upload-error">{error}</p>}
    </div>
  );
}
