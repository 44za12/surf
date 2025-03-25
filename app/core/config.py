import os
import secrets
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SearchProvider(str, Enum):
    """Supported search providers."""
    SEARXNG = "searxng"
    DUCKDUCKGO = "duckduckgo"
    BRAVE = "brave"

class SearXNGConfig(BaseModel):
    """Configuration for SearXNG search engine."""
    instance_url: str = os.getenv("SEARXNG_INSTANCE_URL", "https://searx.be")
    auth_username: Optional[str] = os.getenv("SEARXNG_AUTH_USERNAME")
    auth_password: Optional[str] = os.getenv("SEARXNG_AUTH_PASSWORD")
    timeout: int = int(os.getenv("SEARXNG_TIMEOUT", "10"))
    max_results: int = int(os.getenv("SEARXNG_MAX_RESULTS", "10"))

class BraveSearchConfig(BaseModel):
    """Configuration for Brave Search API."""
    api_key: Optional[str] = os.getenv("BRAVE_API_KEY")
    timeout: int = int(os.getenv("BRAVE_TIMEOUT", "10"))
    max_results: int = int(os.getenv("BRAVE_MAX_RESULTS", "10"))

class DuckDuckGoConfig(BaseModel):
    """Configuration for DuckDuckGo search."""
    timeout: int = int(os.getenv("DUCKDUCKGO_TIMEOUT", "10"))
    max_results: int = int(os.getenv("DUCKDUCKGO_MAX_RESULTS", "10"))

class SearchConfig(BaseModel):
    """Search configuration."""
    provider: SearchProvider = os.getenv("SEARCH_PROVIDER", SearchProvider.DUCKDUCKGO)
    searxng: SearXNGConfig = SearXNGConfig()
    brave: BraveSearchConfig = BraveSearchConfig()
    duckduckgo: DuckDuckGoConfig = DuckDuckGoConfig()

class SecurityConfig(BaseModel):
    """Security configuration."""
    # Read API keys from environment variable - comma-separated list
    api_keys: List[str] = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
    # Generate a random default key if none provided
    default_key: str = os.getenv("DEFAULT_API_KEY", secrets.token_urlsafe(32))
    # Whether API key auth is enabled
    auth_enabled: bool = os.getenv("AUTH_ENABLED", "True").lower() == "true"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Add the default key to api_keys if auth is enabled and no keys are provided
        if self.auth_enabled and not self.api_keys:
            self.api_keys.append(self.default_key)

class Settings(BaseModel):
    """Application settings."""
    app_name: str = "SURF API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))
    search: SearchConfig = SearchConfig()
    searxng: SearXNGConfig = SearXNGConfig() # For backward compatibility
    security: SecurityConfig = SecurityConfig()

# Create global settings object
settings = Settings() 