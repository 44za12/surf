import aiohttp
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings


class BraveSearchClient:
    """Client for interacting with Brave Search API."""
    
    def __init__(self):
        """Initialize Brave Search client with configured settings."""
        self.api_endpoint = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = settings.search.brave.api_key
        self.timeout = settings.search.brave.timeout
        
        if not self.api_key:
            print("WARNING: Brave Search API key is not configured. API calls will fail.")
    
    async def search(self, query: str, num_results: int = None, language: str = None, time_range: str = None) -> list:
        """
        Perform a search query against the Brave Search API.
        
        Args:
            query: The search query
            num_results: Number of results to return, defaults to configured max_results
            language: Language code for search results (e.g., en-US, fr-FR)
            time_range: Optional time filter (day, week, month, year)
            
        Returns:
            List of search results
        """
        if not self.api_key:
            print("ERROR: Brave Search API key is not configured")
            return []
            
        if num_results is None:
            num_results = settings.search.brave.max_results
        
        # Prepare search parameters
        params = {
            "q": query,
            "count": num_results
        }
        
        # Add language if specified
        if language:
            params["country"] = self._extract_country_code(language)
        
        # Add time range if specified
        if time_range:
            params["freshness"] = self._convert_time_range(time_range)
        
        # Set up timeout
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    # Make the request
                    async with session.get(
                        self.api_endpoint, 
                        params=params, 
                        headers={
                            "Accept": "application/json",
                            "X-Subscription-Token": self.api_key
                        }
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"Brave Search API error: Status {response.status}, Response: {error_text[:200]}")
                            raise ValueError(f"Brave Search failed with status code: {response.status}")
                        
                        try:
                            response_data = await response.json()
                        except Exception as e:
                            error_text = await response.text()
                            print(f"Failed to parse Brave Search JSON response: {str(e)}")
                            print(f"Response text: {error_text[:200]}")
                            return []
                        
                        # Process and normalize results
                        return self._process_brave_results(response_data)
                        
                except aiohttp.ClientError as e:
                    print(f"Brave Search connection error: {str(e)}")
                    return []
                
        except Exception as e:
            print(f"Brave Search error: {str(e)}")
            return []
    
    def _process_brave_results(self, response_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Process Brave Search API response to extract and normalize search results.
        
        Args:
            response_data: JSON response from Brave Search API
            
        Returns:
            List of search results with title, URL, and snippet
        """
        results = []
        
        web_results = response_data.get("web", {}).get("results", [])
        for result in web_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("description", "")
            })
            
        return results
    
    def _extract_country_code(self, language: str) -> str:
        """
        Extract country code from language code.
        
        Args:
            language: Language code (e.g., 'en-US')
            
        Returns:
            Country code (e.g., 'US')
        """
        if "-" in language:
            return language.split("-")[1].upper()
        return "US"  # Default
    
    def _convert_time_range(self, time_range: str) -> str:
        """
        Convert time range to Brave Search API time range parameter.
        
        Args:
            time_range: Time range (day, week, month, year)
            
        Returns:
            Brave Search time range parameter
        """
        time_map = {
            "day": "pd",  # past day
            "week": "pw",  # past week
            "month": "pm",  # past month
            "year": "py"   # past year
        }
        return time_map.get(time_range, "") 