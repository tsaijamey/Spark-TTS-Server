from fastapi import Header, HTTPException, status
from functools import lru_cache
from .config import get_settings

@lru_cache()
def get_api_key_header():
    settings = get_settings()
    return Header(
        default=None,
        alias="X-API-Key",
        description="API Key for authentication",
        example=settings.API_KEY
    )

async def get_api_key(api_key: str = get_api_key_header()):
    settings = get_settings()
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key