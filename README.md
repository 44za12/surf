# SURF API

![License](https://img.shields.io/badge/license-MIT-blue.svg)

SURF (Search Utility & Reading Framework) is an elegant, self-deployable API that bridges the gap between Large Language Models and the web. With minimal setup, deploy a robust solution that enables any LLM to search the web and process content in a format optimized for context windows.

## ✨ Key Features

- **Powerful HTML Processing**:
  - Advanced processing with support for tables, images, and complex layouts
  - Clean content extraction from web pages with noise removal
  - Multi-format support (HTML, plain text, JSON, and more)

- **Intelligent Web Search**: Leverage multiple search providers:
  - Choose between DuckDuckGo (default), SearXNG, or Brave Search for web searches
  - Privacy-respecting searches through configurable instances
  - High-quality results using native ranking algorithms
  - Flexible output formats for seamless LLM integration
  - Customizable result count and presentation format

- **Designed for LLMs**:
  - Content optimized for LLM context windows
  - Structured data for easy comprehension by AI models
  - Consistent formatting for reliable parsing
  - Customizable output formats (JSON, Markdown)

- **Developer-Friendly**:
  - Simple REST API with intuitive endpoints
  - Comprehensive documentation and integration guides
  - Authentication-ready with secure API keys
  - Fully self-hostable with minimal dependencies

- **Model Context Protocol (MCP) Integration**:
  - Easy implementation of MCP servers for standardized AI access
  - Simplified interfaces for search and content reading
  - Compatible with all MCP clients like Claude Desktop
  - Rapid development of AI tools with web access capabilities

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Documentation Index](docs/README.md) - Start here for a complete overview
- [Architecture Overview](docs/architecture.md) - Learn about the system design
- [Integration Guide](docs/integration_guide.md) - Detailed instructions for connecting with LLMs
- [Use Cases & Applications](docs/use_cases.md) - Explore real-world applications
- [Self-Hosting Guide](docs/self_hosting.md) - Deploy SURF on your own infrastructure

## 💻 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/44za12/surf.git
cd surf

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

The API server will be available at http://localhost:8000.

### Basic Usage

#### Read a webpage

```bash
curl "http://localhost:8000/read/https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPython_%28programming_language%29"
```

#### Search the web

```bash
curl "http://localhost:8000/search?q=latest+AI+research+papers"
```

## 📋 API Reference

### GET /read/{url}

Fetches, cleans and processes web content.

- **URL Parameters**:
  - `url`: URL-encoded address of the content to read
- **Query Parameters**:
  - `format`: Output format (json or md, default: json)

### GET /search

Searches the web and returns relevant results.

- **Query Parameters**:
  - `q`: Search query
  - `format`: Output format (json or md, default: json)
  - `max_results`: Number of results (1-10, default: 5)
  - `language`: Language code (e.g., en-US, fr-FR)
  - `time_range`: Time filter (day, week, month, year)

## 🧠 LLM Integration Strategies

SURF API is designed to be easily integrated with any LLM system. Here are some recommended integration patterns:

1. **Tool-based integration**: Configure SURF endpoints as tools in your LLM tool library
2. **Retrieval Augmentation**: Use the search and read endpoints for RAG (Retrieval-Augmented Generation)
3. **Direct Context Injection**: Insert search results or web content directly into your prompts
4. **Multi-step workflow**: First search for relevant sources, then read specific pages based on search results
5. **Model Context Protocol (MCP)**: Create MCP servers that leverage SURF for web access, allowing standardized integration with compatible AI systems

For detailed MCP implementation examples, see our [Integration Guide](docs/integration_guide.md#integration-with-model-context-protocol-mcp).

## 🚀 Deployment Options

SURF can be deployed in multiple ways depending on your requirements:

### 🐳 Docker (Recommended)

Deploy with Docker Compose for the simplest setup:

```bash
# Clone the repository
git clone https://github.com/44za12/surf.git
cd surf

# Start the container
docker-compose up -d
```

For more details, see the [Self-Hosting Guide](docs/self_hosting.md).

### 💻 Bare Metal

Install directly on your server:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

### ☁️ Cloud Platforms

SURF works well on:
- Digital Ocean droplets
- AWS EC2 or Lightsail instances
- Azure VMs
- Google Cloud VMs
- PaaS platforms like Heroku, Railway, and Render

Full deployment instructions are available in the [Self-Hosting Guide](docs/self_hosting.md).

## 📐 Configuration Options

All configuration is managed through environment variables or the `.env` file:

### API Settings
- `DEBUG`: Enable/disable debug mode (default: False)
- `PORT`: Port to run the API on (default: 8000)

### Security Settings
- `AUTH_ENABLED`: Enable/disable API key authentication (default: True)
- `API_KEYS`: Comma-separated list of valid API keys
- `DEFAULT_API_KEY`: A default API key to use (auto-generated if not specified)

### Search Provider Settings
- `SEARCH_PROVIDER`: The search provider to use (`searxng`, `duckduckgo`, or `brave`, default: `duckduckgo`)

### SearXNG Settings
- `SEARXNG_INSTANCE_URL`: SearXNG instance URL (default: https://searx.be)
- `SEARXNG_AUTH_USERNAME`: Username for SearXNG authentication (optional)
- `SEARXNG_AUTH_PASSWORD`: Password for SearXNG authentication (optional)
- `SEARXNG_TIMEOUT`: Request timeout in seconds (default: 10)
- `SEARXNG_MAX_RESULTS`: Maximum search results to fetch (default: 10)

### DuckDuckGo Settings
- `DUCKDUCKGO_TIMEOUT`: Request timeout in seconds (default: 10)
- `DUCKDUCKGO_MAX_RESULTS`: Maximum search results to fetch (default: 10)

### Brave Search Settings
- `BRAVE_API_KEY`: API key for Brave Search (required for Brave Search)
- `BRAVE_TIMEOUT`: Request timeout in seconds (default: 10)
- `BRAVE_MAX_RESULTS`: Maximum search results to fetch (default: 10)

## 🚀 Advanced Usage

### Testing the HTML Parser

```
python run.py --test --url https://example.com
```

This command tests the HTML parser with a specific URL and displays the processed content.

### Custom SearXNG Instance

For full privacy control, you can set up your own SearXNG instance and configure SURF to use it:

1. Deploy SearXNG using their [official documentation](https://searxng.github.io/searxng/)
2. Update your `.env` file with your instance URL:
   ```
   SEARXNG_INSTANCE_URL=https://your-searxng-instance.com
   ```

### Using Different Search Providers

SURF supports multiple search providers that you can configure:

#### DuckDuckGo (Default, No API key required)

DuckDuckGo is the default search provider and requires no API key or special setup.

#### SearXNG

To use SearXNG instead of DuckDuckGo:

```
SEARCH_PROVIDER=searxng
SEARXNG_INSTANCE_URL=https://your-searxng-instance.com
```

#### Brave Search (API key required)

1. Get a Brave Search API key from [Brave Search API](https://brave.com/search/api/)
2. Configure SURF to use Brave Search:
   ```
   SEARCH_PROVIDER=brave
   BRAVE_API_KEY=your-api-key-here
   ```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions to SURF are welcome! Please feel free to submit a Pull Request. 