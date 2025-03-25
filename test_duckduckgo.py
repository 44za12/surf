#!/usr/bin/env python
"""Test script for DuckDuckGo search client."""

import asyncio
import sys
from app.utils.duckduckgo import DuckDuckGoClient

async def test_duckduckgo_search(query, num_results=5):
    """Test DuckDuckGo search with a given query."""
    print(f"Searching DuckDuckGo for: {query}")
    client = DuckDuckGoClient()
    results = await client.search(query, num_results=num_results)
    
    if not results:
        print("No results found.")
        return
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No Title')}")
        print(f"   URL: {result.get('url', 'No URL')}")
        print(f"   Snippet: {result.get('snippet', 'No snippet')[:100]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_duckduckgo.py <search query> [num_results]")
        sys.exit(1)
    
    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    asyncio.run(test_duckduckgo_search(query, num_results)) 