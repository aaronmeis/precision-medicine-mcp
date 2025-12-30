#!/bin/bash
set -e

# Deploy OAuth2 Proxy for Azure AD SSO Authentication
# Acts as authentication layer in front of Streamlit and Jupyter

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OAuth2 Proxy Deployment${NC}"
echo -e "${GREEN}Azure AD SSO Authentication${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project set. Run setup-project.sh first${NC}"
    exit 1
fi

REGION=${REGION:-us-central1}
VPC_CONNECTOR=${VPC_CONNECTOR:-mcp-connector}

echo -e "${GREEN}Configuration:${NC}"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  VPC Connector: $VPC_CONNECTOR"
echo ""

# Check required secrets exist
echo -e "${GREEN}Checking required secrets...${NC}"
REQUIRED_SECRETS=("azure-ad-client-id" "azure-ad-client-secret" "azure-ad-tenant-id")
for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe $SECRET --project=$PROJECT_ID &>/dev/null; then
        echo -e "  ${GREEN}✅ $SECRET${NC}"
    else
        echo -e "  ${RED}❌ $SECRET not found${NC}"
        echo -e "${RED}Error: Run setup-secrets.sh first${NC}"
        exit 1
    fi
done

echo ""

# Get configuration values
echo -e "${GREEN}Getting configuration values...${NC}"

# Azure AD Tenant ID (needed for OIDC issuer URL)
AZURE_TENANT_ID=$(gcloud secrets versions access latest --secret=azure-ad-tenant-id --project=$PROJECT_ID)

if [ -z "$AZURE_TENANT_ID" ]; then
    echo -e "${RED}Error: Azure AD Tenant ID not found in Secret Manager${NC}"
    exit 1
fi

echo -e "  ${GREEN}✅ Azure AD Tenant ID retrieved${NC}"
echo ""

# Prompt for upstream URL (Streamlit or Jupyter)
echo -e "${YELLOW}Select upstream service to protect:${NC}"
echo "  1. Streamlit UI"
echo "  2. Jupyter Notebook"
read -p "Select option (1 or 2): " -n 1 -r UPSTREAM_OPTION
echo ""

if [ "$UPSTREAM_OPTION" = "1" ]; then
    SERVICE_NAME="oauth2-proxy-streamlit"
    UPSTREAM_URL="https://streamlit-mcp-chat-ondu7mwjpa-uc.a.run.app"
    REDIRECT_PATH="/auth/callback"
    echo -e "${GREEN}Deploying OAuth2 Proxy for Streamlit UI${NC}"
elif [ "$UPSTREAM_OPTION" = "2" ]; then
    SERVICE_NAME="oauth2-proxy-jupyter"
    UPSTREAM_URL="https://jupyter-mcp-notebook-305650208648.us-central1.run.app"
    REDIRECT_PATH="/oauth2/callback"
    echo -e "${GREEN}Deploying OAuth2 Proxy for Jupyter Notebook${NC}"
else
    echo -e "${RED}Invalid option${NC}"
    exit 1
fi

echo ""

# Generate cookie secret (32 bytes, base64 encoded)
echo -e "${GREEN}Generating cookie secret...${NC}"
COOKIE_SECRET=$(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')
echo -e "  ${GREEN}✅ Cookie secret generated${NC}"
echo ""

# Build OAuth2 Proxy container
echo -e "${GREEN}Building OAuth2 Proxy container...${NC}"
cd ui/streamlit-app
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    -f Dockerfile.oauth2-proxy .

echo -e "${GREEN}✅ Container built${NC}"
echo ""

# Push to Container Registry
echo -e "${GREEN}Pushing container to GCR...${NC}"
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

echo -e "${GREEN}✅ Container pushed${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${GREEN}Deploying to Cloud Run...${NC}"

# Get the OAuth2 Proxy URL (will be available after deployment)
OAUTH2_PROXY_URL="https://$SERVICE_NAME-$(echo $PROJECT_ID | tr ':' '-' | tr '[:upper:]' '[:lower:]')-$REGION.run.app"

gcloud run deploy $SERVICE_NAME \
    --image=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform=managed \
    --region=$REGION \
    --project=$PROJECT_ID \
    --vpc-connector=$VPC_CONNECTOR \
    --vpc-egress=all-traffic \
    --ingress=all \
    --allow-unauthenticated \
    --memory=256Mi \
    --cpu=1 \
    --timeout=300 \
    --min-instances=1 \
    --max-instances=10 \
    --port=4180 \
    --set-secrets=OAUTH2_PROXY_CLIENT_ID=azure-ad-client-id:latest,OAUTH2_PROXY_CLIENT_SECRET=azure-ad-client-secret:latest \
    --set-env-vars=OAUTH2_PROXY_PROVIDER=azure,OAUTH2_PROXY_AZURE_TENANT=$AZURE_TENANT_ID,OAUTH2_PROXY_OIDC_ISSUER_URL=https://login.microsoftonline.com/$AZURE_TENANT_ID/v2.0,OAUTH2_PROXY_REDIRECT_URL=$OAUTH2_PROXY_URL$REDIRECT_PATH,OAUTH2_PROXY_UPSTREAMS=$UPSTREAM_URL,OAUTH2_PROXY_COOKIE_SECRET=$COOKIE_SECRET,OAUTH2_PROXY_COOKIE_DOMAINS=$OAUTH2_PROXY_URL,OAUTH2_PROXY_SCOPE='openid profile email',OAUTH2_PROXY_EMAIL_DOMAINS='*' \
    --labels=service=oauth2-proxy,version=v1.0,status=production

echo -e "${GREEN}✅ OAuth2 Proxy deployed${NC}"
echo ""

# Get the deployed URL
DEPLOYED_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='value(status.url)')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "OAuth2 Proxy URL: $DEPLOYED_URL"
echo "Protected Service: $UPSTREAM_URL"
echo "Redirect URL: $DEPLOYED_URL$REDIRECT_PATH"
echo ""
echo -e "${YELLOW}IMPORTANT: Update Azure AD App Registration:${NC}"
echo "  1. Go to Azure Portal -> App Registrations"
echo "  2. Select 'Precision Medicine MCP' application"
echo "  3. Go to Authentication -> Redirect URIs"
echo "  4. Add redirect URI: $DEPLOYED_URL$REDIRECT_PATH"
echo "  5. Save changes"
echo ""
echo -e "${YELLOW}Test SSO Login:${NC}"
echo "  1. Open: $DEPLOYED_URL"
echo "  2. You should be redirected to Azure AD login"
echo "  3. After login, you should see the protected service"
echo ""
echo -e "${YELLOW}Troubleshooting:${NC}"
echo "  View logs: gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo "  Test health: curl $DEPLOYED_URL/ping"
echo ""
