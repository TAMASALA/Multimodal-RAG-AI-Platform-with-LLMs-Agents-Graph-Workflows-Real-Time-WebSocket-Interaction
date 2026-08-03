import { createContext, useCallback, useState, type ReactNode } from "react";

interface DocumentSelectionContextValue {
  selectedIds: string[];
  toggle: (documentId: string) => void;
  setSelectedIds: (ids: string[]) => void;
  clear: () => void;
}

export const DocumentSelectionContext = createContext<DocumentSelectionContextValue | null>(
  null
);

/**
 * Holds the set of document IDs the user wants to scope chat retrieval to.
 * Lifted to the App level so a selection made on the Documents page (e.g.
 * "select" button on a document card) is immediately reflected in the Chat
 * page's document filter, and vice versa — without prop-drilling through
 * every tab.
 */
export function DocumentSelectionProvider({ children }: { children: ReactNode }) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const toggle = useCallback((documentId: string) => {
    setSelectedIds((prev) =>
      prev.includes(documentId) ? prev.filter((id) => id !== documentId) : [...prev, documentId]
    );
  }, []);

  const clear = useCallback(() => setSelectedIds([]), []);

  return (
    <DocumentSelectionContext.Provider value={{ selectedIds, toggle, setSelectedIds, clear }}>
      {children}
    </DocumentSelectionContext.Provider>
  );
}
