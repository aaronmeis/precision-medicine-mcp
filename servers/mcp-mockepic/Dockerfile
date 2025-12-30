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
ENV MCP_PORT=3008
ENV EPIC_DRY_RUN=false

# Expose port
EXPOSE 3008

# Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#         CMD curl -f http://localhost:3008/health || exit 1

# Run the server
CMD ["python", "-m", "mcp_mockepic"]
