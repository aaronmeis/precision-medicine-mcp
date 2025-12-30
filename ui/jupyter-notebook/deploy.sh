#!/bin/bash
set -e

# Configuration
PROJECT_ID="precision-medicine-poc"
REGION="us-central1"
SERVICE_NAME="jupyter-mcp-notebook"

echo "============================================================================"
echo "Deploying Jupyter Notebook MCP Client to GCP Cloud Run"
echo "============================================================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Please run: export ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

echo "✅ API Key found"
echo ""

# Deploy to Cloud Run
echo "Building and deploying to Cloud Run..."
echo "(This may take 3-5 minutes)"
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 5 \
    --timeout 3600 \
    --set-env-vars ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    --port 8888 \
    --quiet

# Get the URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --format 'value(status.url)')

echo ""
echo "============================================================================"
echo "✅ Deployment Complete!"
echo "============================================================================"
echo ""
echo "🌐 JupyterLab URL: $SERVICE_URL"
echo ""
echo "📝 How to use:"
echo "1. Click the URL above to open JupyterLab"
echo "2. Open mcp_client.ipynb"
echo "3. Start running cells!"
echo ""
echo "💡 Note: No authentication required (configured for easy access)"
echo "⚠️  Warning: This is a public instance - do not store sensitive data!"
echo ""
echo "💵 Cost estimate: ~\$0.50-2.00 per hour of active use"
echo "   (Automatically scales to zero when not in use)"
echo ""
