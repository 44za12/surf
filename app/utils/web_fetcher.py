import aiohttp
from typing import Optional, Tuple, Union
from urllib.parse import urlparse
import logging


class WebFetcher:
    """Utility for fetching web content."""
    
    # Max content size to download (10MB)
    MAX_CONTENT_SIZE = 10 * 1024 * 1024
    
    # Content types that should be processed as text
    TEXT_CONTENT_TYPES = [
        'text/html', 
        'text/plain', 
        'application/json', 
        'application/xml', 
        'text/xml',
        'application/javascript',
        'text/css',
        'text/markdown',
        'application/x-yaml',
        'text/yaml'
    ]
    
    @staticmethod
    async def fetch_url(url: str, timeout: int = 30) -> Optional[Tuple[str, str]]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (content, content_type) or None if failed
        """
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL provided")
        
        # Set up timeout
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        # Common headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                try:
                    async with session.get(url, headers=headers, allow_redirects=True) as response:
                        if response.status != 200:
                            logging.warning(f"Failed to fetch {url}: Status code {response.status}")
                            return None
                        
                        # Get content type and check if it's binary or text
                        content_type = response.headers.get('Content-Type', '').split(';')[0].lower()
                        
                        # Check content length if available
                        content_length = response.headers.get('Content-Length')
                        if content_length and int(content_length) > WebFetcher.MAX_CONTENT_SIZE:
                            logging.warning(f"Content too large: {url} ({content_length} bytes)")
                            return (
                                f"Content too large to process (size: {content_length} bytes, max: {WebFetcher.MAX_CONTENT_SIZE} bytes)",
                                'text/plain'
                            )
                        
                        # Determine if content is text-based or binary
                        is_text = any(text_type in content_type for text_type in WebFetcher.TEXT_CONTENT_TYPES)
                        
                        if is_text:
                            # Get content as text
                            try:
                                content = await response.text()
                            except UnicodeDecodeError:
                                # Fallback if text decoding fails
                                logging.warning(f"Unicode decode error for {url}")
                                content = f"Failed to decode content as text (content-type: {content_type})"
                                content_type = 'text/plain'
                        else:
                            # For binary content, just return a message
                            content = f"Binary content type detected: {content_type}. This content type is not supported for processing."
                            content_type = 'text/plain'
                            
                        return (content, content_type)
                except aiohttp.ClientResponseError as e:
                    logging.error(f"Response error for {url}: {str(e)}")
                    return None
                except aiohttp.ClientConnectorError as e:
                    logging.error(f"Connection error for {url}: {str(e)}")
                    return None
                except aiohttp.ClientPayloadError as e:
                    logging.error(f"Payload error for {url}: {str(e)}")
                    return None
                except aiohttp.ClientConnectionError as e:
                    logging.error(f"Connection error for {url}: {str(e)}")
                    return None
                except aiohttp.ServerTimeoutError as e:
                    logging.error(f"Timeout error for {url}: {str(e)}")
                    return None
        
        except Exception as e:
            # Handle any other unexpected errors
            logging.error(f"Error fetching URL {url}: {str(e)}")
            return None 