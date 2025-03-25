# Self-Hosting Guide for SURF

This guide will help you deploy SURF on your own infrastructure, whether you're running it on a personal server, a cloud VPS, or in a containerized environment.

## Table of Contents

- [Requirements](#requirements)
- [Deployment Options](#deployment-options)
  - [Docker Deployment](#docker-deployment)
  - [Bare Metal Deployment](#bare-metal-deployment)
  - [Cloud Platform Deployment](#cloud-platform-deployment)
- [Security Considerations](#security-considerations)
- [Reverse Proxy Configuration](#reverse-proxy-configuration)
- [Environment Variables](#environment-variables)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Requirements

Before deploying SURF, ensure your system meets these minimum requirements:

- **CPU**: 1+ cores (2+ recommended for production)
- **RAM**: 512MB minimum (1GB+ recommended)
- **Disk**: 1GB for application and dependencies
- **Network**: Public internet access for search functionality
- **Operating System**: Linux (recommended), macOS, or Windows with WSL2

## Deployment Options

### Docker Deployment

Using Docker is the simplest way to deploy SURF.

#### Step 1: Create a Docker Compose File

Create a file named `docker-compose.yml`:

```yaml
version: '3'

services:
  surf:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - AUTH_ENABLED=True
      - API_KEYS=your-secure-api-key-here
      - SEARCH_PROVIDER=duckduckgo
      - DUCKDUCKGO_MAX_RESULTS=10
    volumes:
      - ./data:/app/data
```

#### Step 2: Create a Dockerfile

Create a file named `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn aiohttp python-dotenv beautifulsoup4 markdown

# Copy application files
COPY . /app/

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]
```

#### Step 3: Build and Start the Container

```bash
docker-compose up -d
```

Your SURF API will be available at `http://localhost:8000`.

### Bare Metal Deployment

For direct installation on a server without containers:

#### Step 1: Ensure Python 3.12+ is Installed

```bash
python3 --version
# Should be 3.12 or higher
```

If not, install Python 3.12+:

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-venv python3.12-dev
```

#### Step 2: Clone the Repository

```bash
git clone https://github.com/44za12/surf.git
cd surf
```

#### Step 3: Set Up a Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 4: Install Dependencies

```bash
pip install fastapi uvicorn aiohttp python-dotenv beautifulsoup4 markdown
```

#### Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred settings.

#### Step 6: Run as a Service with Systemd (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/surf.service
```

Add the following content (adjust paths as needed):

```
[Unit]
Description=SURF API
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/surf
ExecStart=/path/to/surf/venv/bin/python run.py
Restart=on-failure
RestartSec=5
Environment=PATH=/path/to/surf/venv/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable surf
sudo systemctl start surf
sudo systemctl status surf
```

### Cloud Platform Deployment

#### Digital Ocean, AWS Lightsail, or similar VPS

1. Create a VPS with at least 1GB RAM running Ubuntu 22.04+
2. Follow the Bare Metal Deployment steps above
3. Configure firewall to allow traffic on port 8000 (or your chosen port)

#### Heroku Deployment

1. Create a `Procfile` in your project root:
   ```
   web: python run.py
   ```

2. Add a `runtime.txt` file:
   ```
   python-3.12.0
   ```

3. Deploy using the Heroku CLI:
   ```bash
   heroku create your-surf-instance
   git push heroku main
   ```

#### Railway, Render, or similar PaaS

1. Connect your GitHub repository
2. Set environment variables in the platform dashboard
3. Set the start command to `python run.py`

## Security Considerations

### API Keys

Always use strong, unique API keys in production:

```
API_KEYS=your-long-random-string-here,another-key-for-different-user
```

You can generate secure keys with:

```bash
openssl rand -base64 32
```

### HTTPS

In production, always use HTTPS. Set up a reverse proxy like Nginx or Caddy with Let's Encrypt.

### Rate Limiting

Consider implementing rate limiting at the reverse proxy level to prevent abuse.

## Reverse Proxy Configuration

### Nginx

Create a configuration file `/etc/nginx/sites-available/surf`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site and set up HTTPS with Certbot:

```bash
sudo ln -s /etc/nginx/sites-available/surf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Caddy (Simpler alternative with automatic HTTPS)

Create a `Caddyfile`:

```
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

## Environment Variables

Here's a summary of important environment variables for production:

```
# Security
AUTH_ENABLED=True
API_KEYS=your-secure-api-key-1,your-secure-api-key-2
DEBUG=False

# Search Provider
SEARCH_PROVIDER=duckduckgo

# Performance
PORT=8000

# If using SearXNG
SEARXNG_INSTANCE_URL=https://your-private-searxng-instance.com
SEARXNG_TIMEOUT=15

# If using Brave Search
BRAVE_API_KEY=your-brave-api-key
```

## Monitoring

### Basic Monitoring with Uptime Checks

Use a service like UptimeRobot, StatusCake, or Pingdom to monitor your API endpoint.

### Advanced Monitoring

For production deployments, consider setting up:

1. Prometheus for metrics collection
2. Grafana for visualization
3. AlertManager for notifications

## Troubleshooting

### Common Issues

1. **API returns 500 errors**:
   - Check the application logs: `sudo journalctl -u surf`
   - Ensure all dependencies are installed

2. **Search fails but the API is running**:
   - Check internet connectivity from your server
   - Verify your search provider configuration

3. **High memory usage**:
   - Adjust the `MAX_CONTENT_SIZE` in `app/utils/web_fetcher.py` to a lower value

4. **Slow response times**:
   - Increase the number of workers in uvicorn by modifying the run.py file
   - Add `--workers 4` to the uvicorn command for multi-core systems

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/44za12/surf/issues) for similar problems
2. Start a new discussion in the repository
3. Join our community chat for real-time assistance 