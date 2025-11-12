from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, topic: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(topic, set()).add(websocket)

    def disconnect(self, topic: str, websocket: WebSocket) -> None:
        conns = self.active.get(topic)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                self.active.pop(topic, None)

    async def broadcast(self, topic: str, message: dict) -> None:
        for ws in list(self.active.get(topic, set())):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(topic, ws)


manager = ConnectionManager()


@router.websocket("/shops/{shop_id}/ws")
async def shop_ws(websocket: WebSocket, shop_id: int):
    topic = f"shop:{shop_id}"
    await manager.connect(topic, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo and ignore; server-side updates will push notifications
            await websocket.send_text(f"ack:{data}")
    except WebSocketDisconnect:
        manager.disconnect(topic, websocket)


async def notify_shop_update(shop_id: int, payload: dict) -> None:
    await manager.broadcast(f"shop:{shop_id}", {"type": "shop_update", "data": payload})