import json
import math

from database import get_db
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from models import User
from services.auth_svc import _get_user_from_token, decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession

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


def _user_can_receive_signals(user: User | None) -> bool:
    """Return True if the user is allowed to receive real-time new_signal pushes.

    Free users and inactive paid users must use the REST endpoints, where the
    daily signal quota is enforced.  Owners and active Basic/Pro users get live
    WebSocket signals.
    """
    if not user or not user.is_active:
        return False
    if user.is_owner:
        return True
    if user.subscription_status != "active":
        return False
    return user.subscription_tier in ("basic", "pro")


class _Connection:
    """Metadata for a single WebSocket connection."""

    def __init__(self, ws: WebSocket, user_id: int | None, eligible_for_signals: bool):
        self.ws = ws
        self.user_id = user_id
        self.eligible_for_signals = eligible_for_signals


class ConnectionManager:
    def __init__(self):
        self._connections: list[_Connection] = []

    async def connect(
        self,
        ws: WebSocket,
        user: User | None,
        subprotocol: str | None = None,
    ):
        await ws.accept(subprotocol=subprotocol)
        eligible = _user_can_receive_signals(user)
        self._connections.append(_Connection(ws, user.id if user else None, eligible))

    def disconnect(self, ws: WebSocket):
        self._connections = [c for c in self._connections if c.ws is not ws]

    async def broadcast(self, data: dict):
        """Broadcast a non-signal message to every connected client."""
        if not self._connections:
            return
        text = json.dumps(data, default=_json_default)
        dead = []
        for conn in self._connections:
            try:
                await conn.ws.send_text(text)
            except Exception:
                dead.append(conn.ws)
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_signal(self, data: dict):
        """Broadcast a new_signal only to clients eligible for live signals."""
        if not self._connections:
            return
        text = json.dumps(data, default=_json_default)
        dead = []
        for conn in self._connections:
            if not conn.eligible_for_signals:
                continue
            try:
                await conn.ws.send_text(text)
            except Exception:
                dead.append(conn.ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    token, used_subprotocol = _extract_ws_token(websocket)
    payload = decode_access_token(token) if token else None
    if not payload:
        await websocket.close(code=1008, reason="Invalid or missing token")
        return

    # Load the live user row so we respect is_active, subscription_status, and tier.
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await _get_user_from_token(creds, db)

    # Return the subprotocol so the browser handshake succeeds.
    await manager.connect(websocket, user, subprotocol="token" if used_subprotocol else None)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
