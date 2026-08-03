import { useContext } from "react";
import { DocumentSelectionContext } from "../context/DocumentSelectionContext";

/**
 * Convenience hook for the shared "documents selected for chat filtering"
 * state. Must be used within a <DocumentSelectionProvider>.
 */
export function useDocumentSelection() {
  const ctx = useContext(DocumentSelectionContext);
  if (!ctx) {
    throw new Error("useDocumentSelection must be used within a DocumentSelectionProvider");
  }
  return ctx;
}
