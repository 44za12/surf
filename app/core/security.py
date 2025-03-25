from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# API key header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Dependency for validating the API key.
    
    Args:
        api_key_header: The API key from the request header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If authentication is required and the API key is invalid
    """
    # If auth is disabled, bypass validation
    if not settings.security.auth_enabled:
        return None
    
    # Check if API key is provided
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    # Validate the API key
    if api_key_header not in settings.security.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return api_key_header

# Convenient dependency for routes
require_api_key = Depends(get_api_key) 