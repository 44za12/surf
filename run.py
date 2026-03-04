"""REST API entry point for SURF. Run with: python run.py"""

import logging
import sys

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from enum import Enum

from app.core.config import settings
from app.core.security import get_api_key
from app.utils.web_fetcher import WebFetcher
from app.utils.html_parser import HTMLCleaner
from app.utils.search_client import SearchClientFactory


log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logger = logging.getLogger("surf")

require_api_key = Depends(get_api_key)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="SURF - Search & read the web, optimised for LLM tool-use.",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OutputFormat(str, Enum):
    json = "json"
    markdown = "md"


@app.exception_handler(Exception)
async def _global_exc(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "auth": "enabled" if settings.security.auth_enabled else "disabled",
        "search_provider": str(settings.search.provider),
        "endpoints": {
            "read": "/read/{url}",
            "search": "/search?q={query}",
        },
    }


@app.get("/read/{url:path}", tags=["Read"])
async def read_url(
    url: str,
    format: OutputFormat = Query(OutputFormat.json),
    api_key: str = require_api_key,
):
    """Fetch, clean, and return the content of a URL."""
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        result = await WebFetcher.fetch_url(url)
        if not result:
            raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {url}")

        content, content_type = result
        processed = await HTMLCleaner.process_html(content, content_type, url)

        if format == OutputFormat.markdown:
            return processed["content"]
        return processed
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing URL {url}: {e}")


@app.get("/search", tags=["Search"])
async def search(
    q: str = Query(..., description="Search query"),
    format: OutputFormat = Query(OutputFormat.json),
    max_results: int = Query(5, ge=1, le=10),
    language: str = Query("en-US"),
    time_range: str = Query(None, description="day, week, month, or year"),
    api_key: str = require_api_key,
):
    """Search the web using the configured search provider."""
    try:
        client = SearchClientFactory.get_client()
        results = await client.search(
            q, num_results=max_results, language=language, time_range=time_range
        )

        if not results:
            if format == OutputFormat.markdown:
                return "No search results found."
            return {"results": [], "query": q}

        if format == OutputFormat.markdown:
            lines = ["# Search Results\n"]
            for i, r in enumerate(results, 1):
                lines.append(f"## {i}. {r.get('title', 'No Title')}\n")
                lines.append(f"**URL**: {r.get('url', '')}\n")
                lines.append(f"{r.get('snippet', '')}\n")
                lines.append("---\n")
            return "\n".join(lines)

        return {
            "results": results,
            "query": q,
            "provider": str(settings.search.provider),
        }
    except Exception as e:
        logger.error(f"Search error for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {e}")


if __name__ == "__main__":
    port = settings.port
    logger.info(f"Starting SURF API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
