import aiohttp
import re
import json
from typing import List, Dict, Any
from urllib.parse import unquote, urlencode
from app.core.config import settings


class DuckDuckGoClient:
    """Client for interacting with DuckDuckGo search engine without relying on additional libraries."""
    
    def __init__(self):
        """Initialize DuckDuckGo client with configured settings."""
        self.search_url = "https://html.duckduckgo.com/html/"
        self.timeout = settings.search.duckduckgo.timeout
    
    async def search(self, query: str, num_results: int = None, language: str = None, time_range: str = None) -> list:
        """
        Perform a search query against DuckDuckGo.
        
        Args:
            query: The search query
            num_results: Number of results to return, defaults to configured max_results
            language: Language code for search results (e.g., en-US, fr-FR)
            time_range: Optional time filter (day, week, month, year)
            
        Returns:
            List of search results
        """
        if num_results is None:
            num_results = settings.search.duckduckgo.max_results
        
        # Prepare search parameters
        params = {
            "q": query,
            "kl": self._convert_language(language) if language else "wt-wt",  # Default to international
        }
        
        # Add time range if specified
        if time_range:
            params["df"] = self._convert_time_range(time_range)
        
        # Set up timeout
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    # Make the request
                    async with session.post(
                        self.search_url, 
                        data=params,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml",
                        }
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"DuckDuckGo error: Status {response.status}, Response: {error_text[:200]}")
                            raise ValueError(f"DuckDuckGo search failed with status code: {response.status}")
                        
                        html_content = await response.text()
                        
                        # Parse the HTML response
                        results = self._parse_html_results(html_content)
                        return results[:num_results]
                        
                except aiohttp.ClientError as e:
                    print(f"DuckDuckGo connection error: {str(e)}")
                    return []
                
        except Exception as e:
            print(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _parse_html_results(self, html_content: str) -> List[Dict[str, str]]:
        """
        Parse the HTML response from DuckDuckGo to extract search results.
        
        Args:
            html_content: HTML content from DuckDuckGo
            
        Returns:
            List of search results with title, URL, and snippet
        """
        results = []
        
        try:
            # Extract titles
            title_matches = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>', html_content)
            
            # Extract snippets
            snippet_matches = re.findall(r'<a class="result__snippet" href="[^"]+">([^<]+(?:<[^>]+>[^<]+)*)</a>', html_content)
            
            # Process results
            for i, (url, title) in enumerate(title_matches):
                snippet = ""
                if i < len(snippet_matches):
                    # Remove HTML tags from snippet
                    snippet = re.sub(r'<[^>]+>', ' ', snippet_matches[i])
                
                # Clean up title and snippet
                title = title.strip()
                snippet = snippet.strip()
                
                # Replace HTML entities
                for entity, char in [('&quot;', '"'), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&#x27;', "'")]:
                    title = title.replace(entity, char)
                    snippet = snippet.replace(entity, char)
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
            
            return results
        except Exception as e:
            print(f"Error parsing DuckDuckGo HTML: {str(e)}")
            return []
    
    def _convert_language(self, language: str) -> str:
        """
        Convert ISO language code to DuckDuckGo's language code.
        
        Args:
            language: Language code (e.g., 'en-US')
            
        Returns:
            DuckDuckGo language code
        """
        # Map common language codes to DuckDuckGo region codes
        language_map = {
            "en-US": "us-en",
            "en-GB": "uk-en",
            "en-CA": "ca-en",
            "fr-FR": "fr-fr",
            "de-DE": "de-de",
            "es-ES": "es-es",
            "it-IT": "it-it",
            "ja-JP": "jp-jp",
        }
        
        # Default to world-wide if not found
        return language_map.get(language, "wt-wt")
    
    def _convert_time_range(self, time_range: str) -> str:
        """
        Convert time range to DuckDuckGo's time range parameter.
        
        Args:
            time_range: Time range (day, week, month, year)
            
        Returns:
            DuckDuckGo time range parameter
        """
        time_map = {
            "day": "d",
            "week": "w",
            "month": "m",
            "year": "y"
        }
        return time_map.get(time_range, "") 