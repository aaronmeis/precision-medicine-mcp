#!/bin/bash
set -e

# Secret Manager Setup for Hospital Deployment
# Creates secrets for API keys, Epic FHIR credentials, and Azure AD configuration

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Secret Manager Setup${NC}"
echo -e "${GREEN}HIPAA-Compliant Credential Storage${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project set. Run setup-project.sh first${NC}"
    exit 1
fi

echo -e "${GREEN}Project: $PROJECT_ID${NC}"
echo ""

# Function to create secret
create_secret() {
    local SECRET_NAME=$1
    local SECRET_DESCRIPTION=$2
    local PROMPT_MESSAGE=$3

    echo -e "${GREEN}Creating secret: $SECRET_NAME${NC}"
    echo "  Description: $SECRET_DESCRIPTION"

    if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
        echo -e "${YELLOW}  Secret $SECRET_NAME already exists${NC}"
        read -p "  Update with new value? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}  Skipping $SECRET_NAME${NC}"
            echo ""
            return
        fi
    else
        # Create the secret
        gcloud secrets create $SECRET_NAME \
            --project=$PROJECT_ID \
            --replication-policy=automatic \
            --labels=project=precision-medicine,compliance=hipaa

        echo -e "${GREEN}  ✅ Secret created${NC}"
    fi

    # Prompt for value
    echo ""
    echo -e "${YELLOW}$PROMPT_MESSAGE${NC}"
    read -s -p "  Enter value (input hidden): " SECRET_VALUE
    echo ""

    if [ -z "$SECRET_VALUE" ]; then
        echo -e "${YELLOW}  No value provided, skipping version creation${NC}"
        echo -e "${YELLOW}  You can add a version later with: echo -n 'value' | gcloud secrets versions add $SECRET_NAME --data-file=-${NC}"
    else
        # Add secret version
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME \
            --project=$PROJECT_ID \
            --data-file=-

        echo -e "${GREEN}  ✅ Secret version added${NC}"
    fi

    echo ""
}

# 1. Anthropic API Key
echo -e "${GREEN}=== 1/7: Anthropic API Key ===${NC}"
create_secret \
    "anthropic-api-key" \
    "Anthropic Claude API key for MCP client" \
    "Enter your Anthropic API key from https://console.anthropic.com/"

# 2. Epic FHIR Endpoint
echo -e "${GREEN}=== 2/7: Epic FHIR Endpoint ===${NC}"
create_secret \
    "epic-fhir-endpoint" \
    "Epic FHIR API endpoint URL (research instance)" \
    "Enter Epic FHIR endpoint URL (e.g., https://hospital.epic.com/api/FHIR/R4/)"

# 3. Epic Client ID
echo -e "${GREEN}=== 3/7: Epic FHIR Client ID ===${NC}"
create_secret \
    "epic-client-id" \
    "Epic FHIR OAuth 2.0 client ID" \
    "Enter Epic FHIR client ID (from hospital IT)"

# 4. Epic Client Secret
echo -e "${GREEN}=== 4/7: Epic FHIR Client Secret ===${NC}"
create_secret \
    "epic-client-secret" \
    "Epic FHIR OAuth 2.0 client secret" \
    "Enter Epic FHIR client secret (from hospital IT)"

# 5. Azure AD Client ID
echo -e "${GREEN}=== 5/7: Azure AD Client ID ===${NC}"
create_secret \
    "azure-ad-client-id" \
    "Azure AD application client ID for SSO" \
    "Enter Azure AD application (client) ID (from Azure Portal App Registration)"

# 6. Azure AD Client Secret
echo -e "${GREEN}=== 6/7: Azure AD Client Secret ===${NC}"
create_secret \
    "azure-ad-client-secret" \
    "Azure AD application client secret for SSO" \
    "Enter Azure AD client secret (from Azure Portal App Registration)"

# 7. Azure AD Tenant ID
echo -e "${GREEN}=== 7/7: Azure AD Tenant ID ===${NC}"
create_secret \
    "azure-ad-tenant-id" \
    "Azure AD tenant ID (directory ID)" \
    "Enter Azure AD tenant ID (from Azure Portal -> Azure Active Directory -> Overview)"

# Grant service accounts access to secrets
echo -e "${GREEN}Configuring service account access...${NC}"
echo ""
echo -e "${YELLOW}Note: Service accounts will be created later during server deployment${NC}"
echo -e "${YELLOW}After creating service accounts, grant them access with:${NC}"
echo ""
echo "  gcloud secrets add-iam-policy-binding SECRET_NAME \\"
echo "    --member=serviceAccount:SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com \\"
echo "    --role=roles/secretmanager.secretAccessor"
echo ""

# List all secrets
echo -e "${GREEN}Listing all secrets:${NC}"
gcloud secrets list --project=$PROJECT_ID --format="table(name,createTime,labels)"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Secret Manager Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Secrets created:"
echo "  1. anthropic-api-key"
echo "  2. epic-fhir-endpoint"
echo "  3. epic-client-id"
echo "  4. epic-client-secret"
echo "  5. azure-ad-client-id"
echo "  6. azure-ad-client-secret"
echo "  7. azure-ad-tenant-id"
echo ""
echo "Security Notes:"
echo "  ✅ All secrets are encrypted at rest by Google Cloud"
echo "  ✅ Access is logged and audited"
echo "  ✅ Only authorized service accounts can access secrets"
echo ""
echo "Next steps:"
echo "  1. Run ./setup-audit-logging.sh to configure HIPAA audit logs"
echo "  2. Deploy OAuth2 Proxy for SSO authentication"
echo "  3. Deploy MCP servers with secret references"
echo ""
