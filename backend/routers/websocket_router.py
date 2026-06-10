import json
import math

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from services.auth_svc import decode_access_token

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)


def _json_default(obj):
    """Serialize numpy/pandas scalars and other non-standard types."""
    # numpy scalar types (bool_, int64, float64, etc.)
    t = type(obj)
    tn = t.__name__
    if tn in ("bool_",):
        return bool(obj)
    if tn in ("int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"):
        return int(obj)
    if tn in ("float16", "float32", "float64", "float128", "float_"):
        v = float(obj)
        return None if math.isnan(v) or math.isinf(v) else v
    # ndarray → list
    if hasattr(obj, "tolist"):
        return obj.tolist()
    return str(obj)


class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self._connections = [c for c in self._connections if c is not ws]

    async def broadcast(self, data: dict):
        if not self._connections:
            return
        text = json.dumps(data, default=_json_default)
        dead = []
        for ws in self._connections:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    payload = decode_access_token(token) if token else None
    if not payload:
        await websocket.close(code=1008, reason="Invalid or missing token")
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
