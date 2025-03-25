from app.core.config import settings, SearchProvider
from app.utils.searx import SearXNGClient
from app.utils.duckduckgo import DuckDuckGoClient
from app.utils.brave import BraveSearchClient
from typing import Union


class SearchClientFactory:
    """Factory for creating search client instances based on configuration."""
    
    @staticmethod
    def get_client() -> Union[SearXNGClient, DuckDuckGoClient, BraveSearchClient]:
        """
        Get the appropriate search client based on the configured provider.
        
        Returns:
            A search client instance based on configuration
        """
        provider = settings.search.provider
        
        if provider == SearchProvider.SEARXNG:
            return SearXNGClient()
        elif provider == SearchProvider.DUCKDUCKGO:
            return DuckDuckGoClient()
        elif provider == SearchProvider.BRAVE:
            return BraveSearchClient()
        else:
            # Default to SearXNG if provider is not recognized
            print(f"WARNING: Unknown search provider '{provider}', using SearXNG instead")
            return SearXNGClient() 