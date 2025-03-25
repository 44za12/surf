FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create a non-root user to run the application
RUN useradd -m surf && \
    chown -R surf:surf /app

USER surf

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"] 