"""
WebSocket connection manager.

- Multiple websocket connections per chat session.
- Dedicated history channel.
- Automatic cleanup of disconnected sockets.
"""

from collections import defaultdict

from fastapi import WebSocket

from app.utils.logger import logger

HISTORY_CHANNEL = "__history__"


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, key: str, websocket: WebSocket) -> None:
        await websocket.accept()

        self._connections[key].append(websocket)

        logger.info(f"WebSocket connected: {key}")

    def disconnect(self, key: str, websocket: WebSocket) -> None:
        sockets = self._connections.get(key)

        if not sockets:
            return

        try:
            sockets.remove(websocket)
        except ValueError:
            pass

        if not sockets:
            self._connections.pop(key, None)

        logger.info(f"WebSocket disconnected: {key}")

    async def send_json(self, key: str, payload: dict) -> None:
        sockets = list(self._connections.get(key, []))

        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception as exc:
                logger.warning(f"Dead websocket ({key}): {exc}")
                self.disconnect(key, ws)

    async def broadcast(
        self,
        payload: dict,
        exclude_key: str | None = None,
    ) -> None:

        for key, sockets in list(self._connections.items()):

            if key == exclude_key:
                continue

            for ws in list(sockets):
                try:
                    await ws.send_json(payload)
                except Exception as exc:
                    logger.warning(f"Broadcast failed ({key}): {exc}")
                    self.disconnect(key, ws)

    def is_connected(self, key: str) -> bool:
        return bool(self._connections.get(key))


manager = ConnectionManager()