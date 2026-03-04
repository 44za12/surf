from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def _extract_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


async def get_api_key(request: Request, header_key: str = Security(api_key_header)):
    if not settings.security.auth_enabled:
        return None

    key = header_key or _extract_bearer_token(request)

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Pass via X-API-Key header or Authorization: Bearer <key>",
        )

    if key not in settings.security.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return key


require_api_key = Depends(get_api_key)