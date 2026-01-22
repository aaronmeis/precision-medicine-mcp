# Deployment Guide

Complete guide for deploying the Streamlit MCP Chat interface across different environments.

---

## Overview

The Streamlit app can be deployed in three ways:

| Environment | Best For | Cost | Setup Time |
|-------------|----------|------|------------|
| **Local Development** | Testing, debugging | Free | 5 minutes |
| **Streamlit Cloud** | Public demos, education | Free | 10 minutes |
| **GCP Cloud Run** | Production, hospital use | ~$5-20/month | 15 minutes |

---

## Local Development

### Prerequisites

- Python 3.11+
- pip or uv package manager
- Git (for cloning repository)

### Quick Start

```bash
# 1. Navigate to directory
cd ui/streamlit-app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API keys
export ANTHROPIC_API_KEY=your_anthropic_key
export GEMINI_API_KEY=your_gemini_key  # Optional

# Or create .env file
cp .env.example .env
# Edit .env with your keys

# 5. Run app
streamlit run app.py
```

The app will open at http://localhost:8501

### Using deploy_now.sh Script

```bash
# Quick deployment with script
cd ui/streamlit-app

# Create .env with keys
echo "ANTHROPIC_API_KEY=your_key" > .env
echo "GEMINI_API_KEY=your_key" >> .env

# Run locally
streamlit run app.py

# Deploy to Cloud Run (if configured)
./deploy_now.sh
```

### Development Tips

- **Hot reload:** Streamlit auto-reloads when you edit code
- **Debug mode:** Add `st.write(variable)` to inspect values
- **Clear cache:** Click "Clear Cache" in hamburger menu (top right)
- **Logs:** Check terminal where `streamlit run` is running

---

## Streamlit Cloud (Free Hosting)

Perfect for public demos and educational use.

### Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

3. **Deploy app**
   - Click "New app"
   - Select repository: `precision-medicine-mcp`
   - Branch: `main`
   - Main file path: `ui/streamlit-app/app.py`

4. **Add secrets**
   - Click "Advanced settings"
   - Add secrets in TOML format:
     ```toml
     ANTHROPIC_API_KEY = "your_anthropic_key_here"
     GEMINI_API_KEY = "your_gemini_key_here"
     ```

5. **Deploy!**
   - Click "Deploy"
   - App will be live at `https://your-app-name.streamlit.app`

### Streamlit Cloud Features

- ✅ Free for public apps
- ✅ Auto-deployment on git push
- ✅ Built-in secrets management
- ✅ HTTPS by default
- ❌ No custom authentication (public only)
- ❌ Limited compute resources

**Cost:** $0 (free tier)

---

## GCP Cloud Run (Production)

Recommended for hospital deployments with SSO, HIPAA compliance, and scaling.

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed ([Install](https://cloud.google.com/sdk/docs/install))
- Docker (optional, for local testing)

### Quick Deploy

```bash
cd ui/streamlit-app

# Set API keys in .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
EOF

# Deploy using script
./deploy_now.sh
```

The script will:
1. Load API keys from .env
2. Build container image
3. Deploy to Cloud Run
4. Output service URL

### Manual Deployment

If you prefer manual control:

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. Build and test locally (optional)

```bash
# Build image
docker build -t streamlit-mcp-chat .

# Test locally
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  streamlit-mcp-chat

# Visit http://localhost:8501
```

#### 3. Deploy to Cloud Run

```bash
# Set project
gcloud config set project precision-medicine-poc

# Deploy
gcloud run deploy streamlit-mcp-chat \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 300 \
  --set-env-vars "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY},GEMINI_API_KEY=${GEMINI_API_KEY},ENVIRONMENT=production" \
  --port 8501
```

#### 4. Get service URL

```bash
SERVICE_URL=$(gcloud run services describe streamlit-mcp-chat \
  --region us-central1 \
  --format 'value(status.url)')

echo "🌐 App URL: $SERVICE_URL"
```

### Cloud Run Configuration Options

**Memory & CPU:**
```bash
--memory 2Gi          # Increase for large file uploads
--cpu 2               # More CPU for faster response
```

**Scaling:**
```bash
--min-instances 1     # Keep 1 instance warm (no cold starts)
--max-instances 10    # Scale up to 10 instances
```

**Timeout:**
```bash
--timeout 600         # Increase for long-running analyses (max 3600s)
```

**Authentication:**
```bash
--no-allow-unauthenticated   # Require IAM auth
--ingress internal           # VPC-only access
```

### Cost Estimates

**Cloud Run Pricing (us-central1):**
- Memory: $0.0000025 per GB-second
- CPU: $0.00002400 per vCPU-second
- Requests: $0.40 per million

**Typical costs:**
- **Idle (0 requests):** $0 (scales to zero)
- **Light use (100 queries/month):** ~$2-5
- **Moderate use (1000 queries/month):** ~$10-15
- **Heavy use (10,000 queries/month):** ~$30-50

**Breakdown per query:**
- Average response: 10-30 seconds
- Memory: 1GB
- Cost: ~$0.0005-0.002 per query

---

## Advanced Configuration

### Environment Variables

**Required:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...  # Required for Claude
GEMINI_API_KEY=AIza...               # Optional, for Gemini
```

**Optional:**
```bash
ENVIRONMENT=production               # Environment name
DEFAULT_MODEL=claude-sonnet-4-5      # Default LLM model
DEFAULT_MAX_TOKENS=4096              # Default token limit
LOG_LEVEL=INFO                       # Logging level
```

### Custom Domain

**Cloud Run custom domain:**
```bash
# Add domain mapping
gcloud run domain-mappings create \
  --service streamlit-mcp-chat \
  --domain chat.yourdomain.com \
  --region us-central1
```

### HTTPS & SSL

- **Streamlit Cloud:** Automatic HTTPS
- **Cloud Run:** Automatic HTTPS with Google-managed certificate
- **Local:** Use ngrok for HTTPS tunnel:
  ```bash
  ngrok http 8501
  ```

### Authentication

**Cloud Run with IAM:**
```bash
# Deploy with authentication required
gcloud run deploy streamlit-mcp-chat \
  --no-allow-unauthenticated

# Grant access to specific users
gcloud run services add-iam-policy-binding streamlit-mcp-chat \
  --member=user:doctor@hospital.org \
  --role=roles/run.invoker \
  --region us-central1
```

**OAuth2 Proxy (SSO):**
For Azure AD / Google SSO, deploy OAuth2 proxy in front:
- See: `docs/for-hospitals/DEPLOYMENT_CHECKLIST.md`

---

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]
    paths:
      - 'ui/streamlit-app/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Deploy to Cloud Run
        run: |
          cd ui/streamlit-app
          gcloud run deploy streamlit-mcp-chat \
            --source . \
            --platform managed \
            --region us-central1 \
            --set-env-vars ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }},GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}
```

---

## Health Checks & Monitoring

### Health Check Endpoint

Streamlit provides health check at:
```
http://your-app/_stcore/health
```

**Test health:**
```bash
curl https://streamlit-mcp-chat-ondu7mwjpa-uc.a.run.app/_stcore/health
```

### Cloud Run Monitoring

**View metrics:**
```bash
# Request count
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'

# Latency
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
```

**Set up alerts:**
- Go to Cloud Console → Monitoring → Alerting
- Create alert for high error rate (>5%)
- Create alert for high latency (>30s)

### Logs

**View recent logs:**
```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-mcp-chat" \
  --limit 50 --format json
```

**Filter for errors:**
```bash
gcloud logging read \
  "resource.labels.service_name=streamlit-mcp-chat AND severity>=ERROR" \
  --limit 20
```

---

## Updating the App

### Local Changes

```bash
# Make changes to code
git add .
git commit -m "Update feature"

# Test locally
streamlit run app.py

# Push to trigger CI/CD (if configured)
git push origin main

# Or deploy manually
./deploy_now.sh
```

### Rolling Updates

Cloud Run deployments are rolling by default:
- New revision created
- Traffic gradually shifted to new revision
- Old revision kept for rollback

### Rollback

```bash
# List revisions
gcloud run revisions list \
  --service streamlit-mcp-chat \
  --region us-central1

# Rollback to previous revision
gcloud run services update-traffic streamlit-mcp-chat \
  --to-revisions streamlit-mcp-chat-00027-xxx=100 \
  --region us-central1
```

---

## Security Best Practices

### API Key Management

- ✅ Use environment variables (never hardcode)
- ✅ Use .env file locally (git ignored)
- ✅ Use Cloud Run secrets for production
- ✅ Rotate keys regularly
- ❌ Never commit .env to git
- ❌ Never share production keys

### Network Security

**VPC Ingress:**
```bash
# Restrict to VPC only
gcloud run services update streamlit-mcp-chat \
  --ingress internal \
  --region us-central1
```

**Firewall rules:**
```bash
# Allow only from specific IP ranges
gcloud compute firewall-rules create allow-streamlit \
  --allow tcp:8501 \
  --source-ranges 10.0.0.0/8
```

---

## Troubleshooting Deployment

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common deployment issues.

**Quick checks:**
```bash
# Verify Cloud Run service is running
gcloud run services describe streamlit-mcp-chat --region us-central1

# Check logs for errors
gcloud logging read "resource.labels.service_name=streamlit-mcp-chat AND severity>=ERROR" --limit 10

# Test endpoint
curl -I https://your-service-url.run.app/_stcore/health
```

---

**Related Documentation:**
- [Main README](README.md)
- [File Handling Guide](FILE_HANDLING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Provider Architecture](providers/README.md)
