import type { SourceRef } from "../services/types";

const WS_BASE_URL =
  (import.meta as any).env?.VITE_WS_BASE_URL ??
  "ws://localhost:8000";

export interface ChatSocketHandlers {
  onOpen?: () => void;
  onClose?: () => void;
  onToken?: (text: string) => void;
  onSources?: (sources: SourceRef[]) => void;
  onDone?: () => void;
  onError?: (detail: string) => void;
}

export class ChatSocket {
  private ws: WebSocket | null = null;
  private connected = false;

  constructor(
    private sessionId: string,
    private handlers: ChatSocketHandlers
  ) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(
        `${WS_BASE_URL}/ws/chat/${this.sessionId}`
      );

      this.ws.onopen = () => {
        console.log("WebSocket Connected");
        this.connected = true;
        this.handlers.onOpen?.();
        resolve();
      };

      this.ws.onclose = () => {
        console.log("WebSocket Closed");
        this.connected = false;
        this.handlers.onClose?.();
      };

      this.ws.onerror = () => {
        console.log("WebSocket Error");
        this.connected = false;
        this.handlers.onError?.("WebSocket Error");
        reject();
      };

      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        switch (msg.type) {
          case "sources":
            this.handlers.onSources?.(msg.payload.items);
            break;

          case "token":
            this.handlers.onToken?.(msg.payload.text);
            break;

          case "done":
            this.handlers.onDone?.();
            break;

          case "error":
            this.handlers.onError?.(msg.payload.detail);
            break;
        }
      };
    });
  }

  sendQuery(query: string, documentIds?: string[]) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error("Socket not connected");
      return;
    }

    console.log("Sending Query");

    this.ws.send(
      JSON.stringify({
        type: "query",
        payload: {
          query,
          document_ids: documentIds,
        },
      })
    );
  }

  close() {
    this.ws?.close();
    this.connected = false;
  }

  isConnected() {
    return this.connected;
  }
}