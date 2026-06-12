import json
import math

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from services.auth_svc import decode_access_token

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)


def _extract_ws_token(websocket: WebSocket) -> tuple[str | None, bool]:
    """Accept token from subprotocol header (preferred) or query param (legacy).

    Browser WebSocket API cannot set arbitrary headers, so the client sends the
    access token as a requested subprotocol: Sec-WebSocket-Protocol: token,<jwt>.
    The server validates the first subprotocol token and returns it.

    Returns (token, used_subprotocol).
    """
    # Subprotocol header is exposed as a comma-separated string by FastAPI/Starlette.
    proto = websocket.headers.get("sec-websocket-protocol") or websocket.headers.get("Sec-WebSocket-Protocol")
    if proto:
        parts = [p.strip() for p in proto.split(",")]
        if parts and parts[0].lower() == "token" and len(parts) >= 2:
            return parts[1], True
    return websocket.query_params.get("token"), False


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

    async def connect(self, ws: WebSocket, subprotocol: str | None = None):
        await ws.accept(subprotocol=subprotocol)
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
    token, used_subprotocol = _extract_ws_token(websocket)
    payload = decode_access_token(token) if token else None
    if not payload:
        await websocket.close(code=1008, reason="Invalid or missing token")
        return
    # Return the subprotocol so the browser handshake succeeds.
    await manager.connect(websocket, subprotocol="token" if used_subprotocol else None)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
