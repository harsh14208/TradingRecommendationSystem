"""
Shared Pydantic schemas and API response envelope.

Every router response should eventually migrate to ApiResponse[T]. New endpoints
must use it from day one. The envelope gives the frontend a consistent shape for
success and error handling.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope.

    Examples
    --------
    Success:
        return ApiResponse(data=user_to_dict(user))

    Error:
        return ApiResponse(ok=False, error="Invalid credentials")

    With metadata:
        return ApiResponse(data=items, meta={"total": count, "page": page})
    """

    ok: bool = True
    data: T | None = None
    error: str | None = None
    meta: dict | None = None

    def model_dump(self, *args, **kwargs):
        # Backwards compatibility: omit None fields by default to keep payloads small
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)
