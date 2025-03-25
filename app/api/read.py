from fastapi import APIRouter, HTTPException, Query, Depends
from enum import Enum
import json
import re

from app.utils.web_fetcher import WebFetcher
from app.utils.html_parser import HTMLCleaner
from app.core.security import require_api_key


# Define output format enum
class OutputFormat(str, Enum):
    json = "json"
    markdown = "md"


# Create router
router = APIRouter(prefix="/read", tags=["read"])


async def extract_text_content(content, content_type, url):
    """Extract text content from non-HTML sources."""
    # Basic processing for plain text
    if 'text/plain' in content_type:
        lines = content.split('\n')
        
        # Try to extract a title from the first non-empty line
        title = "Text Document"
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        # Return the content with minimal formatting
        return {
            "title": title,
            "url": url,
            "content": content
        }
    
    # Basic processing for JSON
    elif 'application/json' in content_type:
        try:
            # Try to parse JSON and pretty-print it
            json_data = json.loads(content)
            formatted_json = json.dumps(json_data, indent=2)
            
            # Try to find a title in common JSON fields
            title = "JSON Document"
            for field in ['title', 'name', 'id', 'key']:
                if isinstance(json_data, dict) and field in json_data:
                    title = f"JSON: {json_data[field]}"
                    break
            
            return {
                "title": title,
                "url": url,
                "content": f"```json\n{formatted_json}\n```"
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return as plain text
            return {
                "title": "Invalid JSON Document",
                "url": url,
                "content": content
            }
    
    # For other formats, return a simple representation
    else:
        return {
            "title": f"Document ({content_type})",
            "url": url,
            "content": f"Content type '{content_type}' not fully supported. Raw content:\n\n```\n{content[:5000]}\n```\n\n(Content may be truncated)"
        }


@router.get("/{url:path}")
async def read_url(
    url: str,
    format: OutputFormat = Query(OutputFormat.json, description="Output format (json or md)"),
    api_key: str = require_api_key
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
    try:
        # Make sure URL is properly formatted
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Fetch content
        fetch_result = await WebFetcher.fetch_url(url)
        
        if not fetch_result:
            raise HTTPException(status_code=404, detail=f"Failed to fetch URL or URL not found: {url}")
        
        content, content_type = fetch_result
        
        # Process content based on content type
        if 'text/html' in content_type:
            processed_content = await HTMLCleaner.process_html(content, url)
        else:
            # For non-HTML content, apply basic processing
            processed_content = await extract_text_content(content, content_type, url)
        
        # Return in requested format
        if format == OutputFormat.markdown:
            return processed_content["content"]
        else:
            # JSON format (default)
            return processed_content
    except Exception as e:
        # Log the error and provide a meaningful response
        error_detail = f"Error processing URL {url}: {str(e)}"
        print(error_detail)  # In production, use proper logging
        raise HTTPException(status_code=500, detail=error_detail) 