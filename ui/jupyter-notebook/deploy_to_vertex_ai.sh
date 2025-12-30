#!/bin/bash
set -e

# Configuration
PROJECT_ID="precision-medicine-poc"
REGION="us-central1"
INSTANCE_NAME="mcp-jupyter-notebook"
MACHINE_TYPE="n1-standard-4"  # 4 vCPUs, 15 GB RAM
BOOT_DISK_SIZE="100GB"

echo "============================================================================"
echo "Deploying Jupyter Notebook to GCP Vertex AI Workbench"
echo "============================================================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Instance: $INSTANCE_NAME"
echo "Machine Type: $MACHINE_TYPE"
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Please run: export ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

echo "✅ API Key found"
echo ""

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable notebooks.googleapis.com \
    --project="$PROJECT_ID" \
    --quiet 2>/dev/null || echo "API already enabled"

echo ""
echo "Creating Vertex AI Workbench instance..."
echo "(This may take 5-10 minutes)"
echo ""

# Create the instance
gcloud notebooks instances create "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --location="$REGION-a" \
    --machine-type="$MACHINE_TYPE" \
    --boot-disk-size="$BOOT_DISK_SIZE" \
    --boot-disk-type="PD_STANDARD" \
    --network="default" \
    --metadata="proxy-mode=service_account,install-nvidia-driver=True" \
    --no-public-ip \
    --quiet || echo "Instance may already exist"

echo ""
echo "============================================================================"
echo "✅ Deployment Complete!"
echo "============================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Open Vertex AI Workbench console:"
echo "   https://console.cloud.google.com/vertex-ai/workbench/list/instances?project=$PROJECT_ID"
echo ""
echo "2. Click 'OPEN JUPYTERLAB' for instance: $INSTANCE_NAME"
echo ""
echo "3. Upload the notebook and install dependencies:"
echo "   - Upload mcp_client.ipynb"
echo "   - Upload requirements.txt"
echo "   - Create .env file with your API key"
echo "   - Run: pip install -r requirements.txt"
echo ""
echo "4. Start using the notebook!"
echo ""
echo "Cost estimate: ~\$150-200/month (running 24/7)"
echo "Tip: Stop instance when not in use to reduce costs"
echo ""
