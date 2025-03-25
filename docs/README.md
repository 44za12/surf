# SURF API Documentation

Welcome to the SURF API documentation. SURF (Search Utility & Reading Framework) is a self-deployable API that empowers LLMs with web search and content processing capabilities.

## Documentation Index

### Getting Started
- [Main README](../README.md) - Overview, installation, and quick start guide

### Core Documentation
- [Architecture Overview](architecture.md) - Detailed explanation of the system architecture
- [Integration Guide](integration_guide.md) - Guide to integrating SURF with various LLM systems
- [Use Cases & Applications](use_cases.md) - Real-world use cases and application ideas
- [Self-Hosting Guide](self_hosting.md) - Complete guide to deploying SURF on your infrastructure

### API Reference
- API Endpoints
  - `/read/{url}` - Fetch, clean, and process web content
  - `/search` - Search the web and retrieve ranked results

### Development
- [Contributing](../CONTRIBUTING.md) - Guide to contributing to SURF

## About SURF

SURF is an elegant solution that bridges the gap between LLMs and the dynamic web, enabling more accurate, up-to-date, and context-aware AI applications. By providing a standardized interface for retrieving and processing web content, SURF eliminates the complexity of web integration while enhancing LLM capabilities with current information.

Key features:
- Advanced HTML processing with support for tables, code blocks, and complex formatting
- Intelligent web search with multiple providers (SearXNG, DuckDuckGo, Brave Search)
- Multiple output formats optimized for LLM consumption
- Privacy-focused, self-hosted architecture

## Getting Help

If you need help with SURF:
1. Check the documentation in this directory
2. Look for similar issues on the GitHub repository
3. Open a new issue for bugs or feature requests
4. Join our community discussions 