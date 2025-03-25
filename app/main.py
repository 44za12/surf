from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import sys

from app.core.config import settings
from app.api import read, search
from app.core.security import API_KEY_NAME


# Configure logging
def setup_logging():
    """Set up logging configuration."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Set levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    return logging.getLogger("app")

# Initialize logger
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="SURF API for web content retrieval and search",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(read.router)
app.include_router(search.router)

# Custom OpenAPI schema to document API key usage
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add API key security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_NAME,
            "description": f"API key to authenticate requests. Example: {API_KEY_NAME}: YOUR_API_KEY"
        }
    }
    
    # Add security requirement to all endpoints
    if settings.security.auth_enabled:
        openapi_schema["security"] = [{"APIKeyHeader": []}]
        
        # Add note about authentication to description
        auth_note = f"""
        ## Authentication
        
        This API requires authentication using an API key. Include your API key in the `{API_KEY_NAME}` header with your requests.
        
        Example: `{API_KEY_NAME}: YOUR_API_KEY`
        """
        
        openapi_schema["info"]["description"] = app.description + auth_note
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Root route
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint returns basic information about the API
    """
    auth_status = "enabled" if settings.security.auth_enabled else "disabled"
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "API for web content retrieval and search",
        "auth_status": auth_status,
        "endpoints": {
            "read": "/read/{url}",
            "search": "/search?q={query}"
        }
    }

# Display API keys in debug mode when server starts
@app.on_event("startup")
async def startup_event():
    if settings.debug and settings.security.auth_enabled:
        keys_info = "\n".join([f"- {key}" for key in settings.security.api_keys])
        print(f"\n\nAuth is ENABLED. Available API key(s):\n{keys_info}\n")
        if settings.security.default_key in settings.security.api_keys:
            print(f"Default key was auto-generated. Use this for testing: {settings.security.default_key}\n\n")
    elif settings.debug:
        print("\n\nAuth is DISABLED. No API key required for requests.\n\n") 