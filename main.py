from mcp.server.fastmcp import FastMCP
from app.core.config import settings
from enum import Enum
from app.utils.web_fetcher import WebFetcher
from app.utils.html_parser import HTMLCleaner
from app.utils.search_client import SearchClientFactory

mcp = FastMCP("Surf")


class OutputFormat(str, Enum):
    json = "json"
    markdown = "md"


@mcp.tool()
async def read_url(
    url: str,
    format: OutputFormat = OutputFormat.json,
):
    """
    Fetch and process content from a URL.

    Args:
        url: URL to read content from (as path parameter)
        format: Output format (json or markdown)
        api_key: API key for authentication

    Returns:
        Processed content in requested format
    """
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    fetch_result = await WebFetcher.fetch_url(url)

    content, content_type = fetch_result

    processed_content = await HTMLCleaner.process_html(content, content_type, url)

    # Return in requested format
    if format == OutputFormat.markdown:
        return processed_content["content"]
    else:
        # JSON format (default)
        return processed_content


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


@mcp.tool()
async def search(
    q: str,
    format: OutputFormat = OutputFormat.json,
    max_results: int = 5,
    language: str = "en-US",
    time_range: str = None,
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
    search_client = SearchClientFactory.get_client()

    # Perform search
    results = await search_client.search(
        q, num_results=max_results, language=language, time_range=time_range
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
            "provider": str(settings.search.provider),
        }
