#!/bin/bash
set -e

# Research Hospital GCP Project Setup Script
# Creates GCP project in hospital's existing organization for HIPAA-compliant deployment

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Research Hospital - GCP Project Setup${NC}"
echo -e "${GREEN}Precision Medicine MCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if required environment variables are set
if [ -z "$HOSPITAL_ORG_ID" ]; then
    echo -e "${RED}Error: HOSPITAL_ORG_ID environment variable not set${NC}"
    echo "Please set it to the hospital's GCP Organization ID"
    echo "Example: export HOSPITAL_ORG_ID=123456789012"
    exit 1
fi

if [ -z "$HOSPITAL_BILLING_ACCOUNT" ]; then
    echo -e "${RED}Error: HOSPITAL_BILLING_ACCOUNT environment variable not set${NC}"
    echo "Please set it to the Ovarian Cancer PI's grant billing account ID"
    echo "Example: export HOSPITAL_BILLING_ACCOUNT=00B597-858846-408197"
    exit 1
fi

if [ -z "$HOSPITAL_NAME" ]; then
    echo -e "${YELLOW}Warning: HOSPITAL_NAME not set, using default 'research-hospital'${NC}"
    HOSPITAL_NAME="research-hospital"
fi

# Set project variables
PROJECT_ID="${HOSPITAL_NAME}-precision-medicine"
PROJECT_NAME="Precision Medicine - Ovarian Cancer Research"
REGION="us-central1"

echo -e "${GREEN}Configuration:${NC}"
echo "  Organization ID: $HOSPITAL_ORG_ID"
echo "  Billing Account: $HOSPITAL_BILLING_ACCOUNT"
echo "  Project ID: $PROJECT_ID"
echo "  Project Name: $PROJECT_NAME"
echo "  Region: $REGION"
echo ""

read -p "Continue with project creation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 1
fi

# Step 1: Create GCP Project
echo -e "${GREEN}Step 1/5: Creating GCP project...${NC}"
if gcloud projects describe $PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Project $PROJECT_ID already exists, skipping creation${NC}"
else
    gcloud projects create $PROJECT_ID \
        --organization=$HOSPITAL_ORG_ID \
        --name="$PROJECT_NAME" \
        --labels=env=production,project=ovarian-spatial,compliance=hipaa

    echo -e "${GREEN}✅ Project created successfully${NC}"
fi

# Step 2: Link Billing Account
echo -e "${GREEN}Step 2/5: Linking billing account...${NC}"
gcloud beta billing projects link $PROJECT_ID \
    --billing-account=$HOSPITAL_BILLING_ACCOUNT

echo -e "${GREEN}✅ Billing account linked${NC}"

# Step 3: Enable Required APIs
echo -e "${GREEN}Step 3/5: Enabling required APIs...${NC}"
gcloud services enable --project=$PROJECT_ID \
    run.googleapis.com \
    compute.googleapis.com \
    vpcaccess.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    storage.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"

# Step 4: Set Default Project
echo -e "${GREEN}Step 4/5: Setting default project...${NC}"
gcloud config set project $PROJECT_ID

echo -e "${GREEN}✅ Default project set${NC}"

# Step 5: Create Budget Alert
echo -e "${GREEN}Step 5/5: Creating budget alert...${NC}"
# Note: Budget creation requires the billing account to be accessible
# This may need to be done manually in the Cloud Console if permissions are restricted

cat > /tmp/budget-config.json <<EOF
{
  "displayName": "Precision Medicine MCP Budget",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"]
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "1000"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.75,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.9,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 1.0,
      "spendBasis": "CURRENT_SPEND"
    }
  ]
}
EOF

echo -e "${YELLOW}Budget configuration created at /tmp/budget-config.json${NC}"
echo -e "${YELLOW}Please create the budget manually in Cloud Console if you have billing permissions${NC}"
echo -e "${YELLOW}Or ask hospital finance team to create it using the config file${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Project Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Run ./setup-vpc.sh to configure VPC networking"
echo "  2. Run ./setup-secrets.sh to create Secret Manager secrets"
echo "  3. Run ./setup-audit-logging.sh to configure HIPAA audit logs"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""
