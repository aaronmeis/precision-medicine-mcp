FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy server code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Set environment variables for HTTP/SSE transport
ENV MCP_TRANSPORT=sse
ENV MCP_PORT=3004
ENV IMAGE_DRY_RUN=false
ENV IMAGE_DATA_DIR=/app/data/images
ENV IMAGE_CACHE_DIR=/app/data/cache/images

# Create data directories
RUN mkdir -p /app/data/images /app/data/cache/images

# Expose port
EXPOSE 3004

# Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#         CMD curl -f http://localhost:3004/health || exit 1

# Run the server
CMD ["python", "-m", "mcp_openimagedata"]
