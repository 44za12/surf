import aiohttp
import json
from app.core.config import settings


class SearXNGClient:
    """Client for interacting with SearXNG search engine."""
    
    def __init__(self):
        """Initialize SearXNG client with configured settings."""
        self.instance_url = settings.searxng.instance_url
        self.auth = None
        
        # Configure authentication if provided
        if settings.searxng.auth_username and settings.searxng.auth_password:
            self.auth = aiohttp.BasicAuth(
                login=settings.searxng.auth_username,
                password=settings.searxng.auth_password
            )
    
    async def search(self, query: str, num_results: int = None, language: str = None, time_range: str = None) -> list:
        """
        Perform a search query against the SearXNG instance.
        
        Args:
            query: The search query
            num_results: Number of results to return, defaults to configured max_results
            language: Language code for search results (e.g., en-US, fr-FR)
            time_range: Optional time filter (day, week, month, year)
            
        Returns:
            List of search results
        """
        if num_results is None:
            num_results = settings.searxng.max_results
        
        if language is None:
            language = "en-US"
        
        # Validate time_range parameter if provided
        valid_time_ranges = [None, "day", "week", "month", "year"]
        if time_range not in valid_time_ranges:
            print(f"Warning: Invalid time_range '{time_range}', ignoring parameter")
            time_range = None
        
        # Prepare search parameters
        params = {
            "q": query,
            "format": "json",
            "language": language,
        }
        
        # Add optional parameters
        if time_range:
            params["time_range"] = time_range
        
        # Set up timeout
        timeout = aiohttp.ClientTimeout(total=settings.searxng.timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Create search URL
                search_url = f"{self.instance_url}/search"
                
                try:
                    # Make the request
                    async with session.get(
                        search_url, 
                        params=params, 
                        auth=self.auth,
                        headers={"Accept": "application/json"}
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"SearXNG error: Status {response.status}, Response: {error_text[:200]}")
                            raise ValueError(f"SearXNG search failed with status code: {response.status}")
                        
                        try:
                            response_data = await response.json()
                        except Exception as e:
                            error_text = await response.text()
                            print(f"Failed to parse SearXNG JSON response: {str(e)}")
                            print(f"Response text: {error_text[:200]}")
                            return []
                        
                        # Process and normalize results
                        results = []
                        for result in response_data.get("results", []):
                            # Keep only necessary fields
                            results.append({
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "snippet": result.get("content", "")
                            })
                        
                        return results[:num_results]
                except aiohttp.ClientError as e:
                    print(f"SearXNG connection error: {str(e)}")
                    return []
                
        except Exception as e:
            # In a production environment, you would want to log this error
            print(f"SearXNG search error: {str(e)}")
            return []