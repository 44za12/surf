import os
import sys
import secrets
import pathlib
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class SearchProvider(str, Enum):
    SEARXNG = "searxng"
    DUCKDUCKGO = "duckduckgo"
    BRAVE = "brave"


class SearXNGConfig(BaseModel):
    instance_url: str = os.getenv("SEARXNG_INSTANCE_URL", "https://searx.be")
    auth_username: Optional[str] = os.getenv("SEARXNG_AUTH_USERNAME")
    auth_password: Optional[str] = os.getenv("SEARXNG_AUTH_PASSWORD")
    timeout: int = int(os.getenv("SEARXNG_TIMEOUT", "10"))
    max_results: int = int(os.getenv("SEARXNG_MAX_RESULTS", "10"))


class BraveSearchConfig(BaseModel):
    api_key: Optional[str] = os.getenv("BRAVE_API_KEY")
    timeout: int = int(os.getenv("BRAVE_TIMEOUT", "10"))
    max_results: int = int(os.getenv("BRAVE_MAX_RESULTS", "10"))


class DuckDuckGoConfig(BaseModel):
    timeout: int = int(os.getenv("DUCKDUCKGO_TIMEOUT", "10"))
    max_results: int = int(os.getenv("DUCKDUCKGO_MAX_RESULTS", "10"))


class SearchConfig(BaseModel):
    provider: SearchProvider = os.getenv("SEARCH_PROVIDER", SearchProvider.DUCKDUCKGO)
    searxng: SearXNGConfig = SearXNGConfig()
    brave: BraveSearchConfig = BraveSearchConfig()
    duckduckgo: DuckDuckGoConfig = DuckDuckGoConfig()


def _generate_and_persist_api_key() -> str:
    """Generate a new API key, persist it to .env, and print it."""
    key = secrets.token_urlsafe(32)

    try:
        content = ""
        if ENV_FILE.exists():
            content = ENV_FILE.read_text()

        if "API_KEYS=" not in content:
            with open(ENV_FILE, "a") as f:
                f.write(f"\nAPI_KEYS={key}\n")
            saved = True
        else:
            saved = False
    except OSError:
        saved = False

    print(f"\n{'=' * 60}", file=sys.stderr)
    if saved:
        print(f"  Auto-generated API key (saved to .env):", file=sys.stderr)
    else:
        print(f"  Auto-generated API key (could not save to .env):", file=sys.stderr)
        print(f"  Add this to your .env:  API_KEYS={key}", file=sys.stderr)
    print(f"  {key}", file=sys.stderr)
    print(f"{'=' * 60}\n", file=sys.stderr)

    return key


class SecurityConfig(BaseModel):
    api_keys: List[str] = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
    auth_enabled: bool = os.getenv("AUTH_ENABLED", "True").lower() == "true"

    def __init__(self, **data):
        super().__init__(**data)
        if self.auth_enabled and not self.api_keys:
            key = _generate_and_persist_api_key()
            self.api_keys.append(key)


class Settings(BaseModel):
    app_name: str = "SURF API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))
    search: SearchConfig = SearchConfig()
    searxng: SearXNGConfig = SearXNGConfig()
    security: SecurityConfig = SecurityConfig()


settings = Settings()