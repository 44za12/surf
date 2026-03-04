# SURF

SURF (Search Utility & Reading Framework) is a self-deployable API that lets LLMs search the web and read pages. It cleans HTML into markdown/JSON optimised for context windows, and supports multiple search providers out of the box.

It exposes both a **REST API** and an **MCP server** so you can use it from any HTTP client or any MCP-compatible AI tool (Claude Desktop, etc.).

## Features

- **HTML → Markdown** — tables, lists, links, code blocks all converted cleanly
- **Multiple search providers** — DuckDuckGo (default, no key needed), Brave Search, or SearXNG
- **Auth with auto-generated keys** — on first start, an API key is created and saved to `.env`
- **MCP support** — `main.py` runs as a Model Context Protocol server with `search` and `read_url` tools
- **REST API** — `run.py` serves familiar HTTP endpoints at `/search` and `/read/{url}`

## Quick Start

```bash
git clone https://github.com/44za12/surf.git
cd surf

# Set up virtualenv & install deps
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env if you want to change search provider, port, etc.

# Start the REST API
.venv/bin/python3 run.py
```

On first boot with `AUTH_ENABLED=True` (the default) and no `API_KEYS` set, an API key is **auto-generated and saved to `.env`**. It is printed to stderr so you can find it in your logs.

## Authentication

Both `X-API-Key` header and `Authorization: Bearer` are accepted:

```bash
# Either works:
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8000/search?q=hello"
curl -H "Authorization: Bearer YOUR_KEY" "http://localhost:8000/search?q=hello"
```

Set `AUTH_ENABLED=False` in `.env` to disable auth entirely.

## REST API

### `GET /search`

Search the web.

| Parameter     | Default | Description                              |
|---------------|---------|------------------------------------------|
| `q`           | —       | Search query (required)                  |
| `format`      | `json`  | `json` or `md`                           |
| `max_results` | `5`     | 1–10                                     |
| `language`    | `en-US` | Language/region code                     |
| `time_range`  | —       | `day`, `week`, `month`, or `year`        |

```bash
curl -H "X-API-Key: KEY" "http://localhost:8000/search?q=latest+AI+research&max_results=3"
```

### `GET /read/{url}`

Fetch a page, strip boilerplate, return clean content.

| Parameter | Default | Description    |
|-----------|---------|----------------|
| `format`  | `json`  | `json` or `md` |

```bash
curl -H "X-API-Key: KEY" "http://localhost:8000/read/https://example.com"
```

### `GET /`

Health check / info endpoint.

## MCP Server

`main.py` exposes the same `search` and `read_url` functionality as MCP tools. To use with Claude Desktop or another MCP client:

```json
{
  "mcpServers": {
    "surf": {
      "command": "/path/to/surf/.venv/bin/python3",
      "args": ["/path/to/surf/main.py"]
    }
  }
}
```

## Configuration

All settings live in `.env` (see `.env.example`):

| Variable               | Default      | Description                                      |
|------------------------|--------------|--------------------------------------------------|
| `DEBUG`                | `False`      | Enable debug mode                                |
| `PORT`                 | `8000`       | REST API port                                    |
| `AUTH_ENABLED`         | `True`       | Require API key auth                             |
| `API_KEYS`             | (auto)       | Comma-separated API keys; auto-generated if empty|
| `SEARCH_PROVIDER`      | `duckduckgo` | `duckduckgo`, `brave`, or `searxng`              |
| `BRAVE_API_KEY`        | —            | Required when using Brave Search                 |
| `SEARXNG_INSTANCE_URL` | `https://searx.be` | SearXNG instance URL                      |
| `SEARXNG_AUTH_USERNAME` | —           | SearXNG basic auth username                      |
| `SEARXNG_AUTH_PASSWORD` | —           | SearXNG basic auth password                      |

Timeout and max-result settings are also available per provider (`BRAVE_TIMEOUT`, `DUCKDUCKGO_MAX_RESULTS`, etc.).

## Deploying with PM2

```bash
cd /path/to/surf
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env   # then edit

pm2 start run.py --name surf-api --cwd /path/to/surf --interpreter /path/to/surf/.venv/bin/python3
pm2 save
pm2 logs surf-api      # find your auto-generated API key here
```

## License

MIT
