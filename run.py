import uvicorn
import argparse
import asyncio
from app.core.config import settings
from app.utils.web_fetcher import WebFetcher
from app.utils.html_parser import HTMLCleaner


async def test_html_parser(url="https://en.wikipedia.org/wiki/Markdown"):
    """Test the HTML parser with a sample URL."""
    print(f"\n\nTesting HTML Parser with URL: {url}")
    print("=" * 80)
    
    # Fetch the URL
    result = await WebFetcher.fetch_url(url)
    if not result:
        print(f"Failed to fetch URL: {url}")
        return
    
    content, content_type = result
    
    # Process the HTML
    if 'text/html' in content_type:
        processed = await HTMLCleaner.process_html(content, url)
        
        # Print the title
        print(f"Title: {processed['title']}")
        print(f"URL: {processed['url']}")
        print("\nContent Preview (first 1000 characters):")
        print("-" * 80)
        print(processed['content'][:1000] + "...")
        print("-" * 80)
        
        # Check for tables
        if "| ---" in processed['content']:
            table_start = processed['content'].find("|")
            table_end = processed['content'].find("\n\n", table_start)
            if table_end == -1:
                table_end = table_start + 500
            
            print("\nTable Found:")
            print("-" * 80)
            print(processed['content'][table_start:table_end])
            print("-" * 80)
        else:
            print("\nNo tables found in the content.")
    else:
        print(f"URL did not return HTML content: {content_type}")


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the SURF API server")
    parser.add_argument("--test", action="store_true", help="Test HTML parser with a URL")
    parser.add_argument("--url", type=str, help="URL to test with HTML parser")
    args = parser.parse_args()
    
    if args.test:
        # Run the test in an asyncio event loop
        asyncio.run(test_html_parser(args.url))
        return
    
    # Run the FastAPI application directly without asyncio
    # Uvicorn manages its own event loop
    port = int(settings.port) if hasattr(settings, 'port') else 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main() 