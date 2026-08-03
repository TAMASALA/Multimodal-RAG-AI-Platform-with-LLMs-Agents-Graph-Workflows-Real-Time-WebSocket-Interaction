import type { HistoryUpdatedPayload, WSMessage } from "../services/types";

const WS_BASE_URL: string =
  (import.meta as any).env?.VITE_WS_BASE_URL || "ws://localhost:8000";

export interface HistorySocketHandlers {
  onUpdated?: (payload: HistoryUpdatedPayload) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

/**
 * Subscribes to the server's /ws/history broadcast channel so the Chat
 * History sidebar can refresh in real time whenever any session anywhere
 * (this tab or another) is created, renamed, cleared, deleted, or receives
 * a new message. Auto-reconnects with backoff if the connection drops.
 */
export class HistorySocket {
  private ws: WebSocket | null = null;
  private handlers: HistorySocketHandlers;
  private reconnectAttempts = 0;
  private closedByClient = false;

  constructor(handlers: HistorySocketHandlers) {
    this.handlers = handlers;
  }

  connect(): void {
    this.closedByClient = false;
    this.ws = new WebSocket(`${WS_BASE_URL}/ws/history`);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.handlers.onOpen?.();
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        if (message.type === "history_updated") {
          this.handlers.onUpdated?.(message.payload as HistoryUpdatedPayload);
        }
      } catch (err) {
        console.error("Failed to parse history websocket message", err);
      }
    };

    this.ws.onclose = () => {
      this.handlers.onClose?.();
      if (!this.closedByClient) this.scheduleReconnect();
    };
  }

  private scheduleReconnect(): void {
    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 15000);
    this.reconnectAttempts += 1;
    setTimeout(() => {
      if (!this.closedByClient) this.connect();
    }, delay);
  }

  close(): void {
    this.closedByClient = true;
    this.ws?.close();
    this.ws = null;
  }
}
