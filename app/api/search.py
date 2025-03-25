from fastapi import APIRouter, HTTPException, Query, Depends
from enum import Enum

from app.utils.search_client import SearchClientFactory
from app.core.config import settings, SearchProvider
from app.core.security import require_api_key


# Define output format enum
class OutputFormat(str, Enum):
    json = "json"
    markdown = "md"


# Create router
router = APIRouter(prefix="/search", tags=["search"])


# Helper function to format results as markdown
def format_results_as_markdown(results: list) -> str:
    """Format search results as markdown."""
    if not results:
        return "No results found."
    
    markdown = "# Search Results\n\n"
    
    for i, result in enumerate(results, 1):
        markdown += f"## {i}. {result.get('title', 'No Title')}\n\n"
        markdown += f"**URL**: {result.get('url', 'No URL')}\n\n"
        markdown += f"{result.get('snippet', 'No description available.')}\n\n"
        markdown += "---\n\n"
    
    return markdown


@router.get("")
async def search(
    q: str = Query(..., description="Search query"),
    format: OutputFormat = Query(OutputFormat.json, description="Output format (json or md)"),
    max_results: int = Query(5, description="Maximum number of results to return", ge=1, le=10),
    language: str = Query("en-US", description="Search language (e.g., en-US, fr-FR)"),
    time_range: str = Query(None, description="Optional time range for search results (day, week, month, year)"),
    api_key: str = require_api_key
):
    """
    Search the web using the configured search provider.
    
    Args:
        q: Search query
        format: Output format (json or markdown)
        max_results: Maximum number of results to return (1-10)
        language: Language code for search results (e.g., en-US, fr-FR)
        time_range: Optional time filter (day, week, month, year)
        api_key: API key for authentication
        
    Returns:
        Search results in requested format
    
    Note:
        This endpoint uses the configured search provider (SearXNG, DuckDuckGo, or Brave Search).
        The current provider is: {settings.search.provider}
    """
    try:
        # Get appropriate search client based on configuration
        search_client = SearchClientFactory.get_client()
        
        # Perform search
        results = await search_client.search(
            q, 
            num_results=max_results,
            language=language,
            time_range=time_range
        )
        
        if not results:
            if format == OutputFormat.markdown:
                return "No search results found."
            else:
                return {"results": [], "query": q}
        
        # Return in requested format
        if format == OutputFormat.markdown:
            return format_results_as_markdown(results)
        else:
            # JSON format (default)
            return {
                "results": results, 
                "query": q,
                "provider": str(settings.search.provider)
            }
            
    except Exception as e:
        # Log the error and provide a meaningful response
        error_detail = f"Search error for query '{q}': {str(e)}"
        print(error_detail)  # In production, use proper logging
        raise HTTPException(status_code=500, detail=error_detail) 