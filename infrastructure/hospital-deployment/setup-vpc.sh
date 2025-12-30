#!/bin/bash
set -e

# VPC and Networking Setup for Hospital Deployment
# Configures VPC connector for Cloud Run private networking

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VPC and Networking Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project set. Run setup-project.sh first${NC}"
    exit 1
fi

REGION=${REGION:-us-central1}
VPC_NETWORK=${HOSPITAL_VPC_NETWORK:-default}

echo -e "${GREEN}Configuration:${NC}"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  VPC Network: $VPC_NETWORK"
echo ""

# Option 1: Use existing hospital VPC (recommended)
echo -e "${YELLOW}VPC Network Options:${NC}"
echo "  1. Use existing hospital VPC network (recommended)"
echo "  2. Create new VPC network for this project"
echo ""
read -p "Select option (1 or 2): " -n 1 -r VPC_OPTION
echo ""

if [ "$VPC_OPTION" = "1" ]; then
    # Use existing VPC
    if [ "$VPC_NETWORK" = "default" ]; then
        echo -e "${YELLOW}Using default VPC network${NC}"
        echo -e "${YELLOW}For production, specify hospital VPC: export HOSPITAL_VPC_NETWORK=<vpc-name>${NC}"
    else
        echo -e "${GREEN}Using hospital VPC network: $VPC_NETWORK${NC}"
    fi
elif [ "$VPC_OPTION" = "2" ]; then
    # Create new VPC (only if hospital doesn't have existing one to use)
    VPC_NETWORK="mcp-vpc"
    echo -e "${GREEN}Creating new VPC network: $VPC_NETWORK${NC}"

    gcloud compute networks create $VPC_NETWORK \
        --project=$PROJECT_ID \
        --subnet-mode=custom \
        --bgp-routing-mode=regional

    echo -e "${GREEN}✅ VPC network created${NC}"

    # Create subnet
    echo -e "${GREEN}Creating subnet for MCP servers...${NC}"
    gcloud compute networks subnets create mcp-servers-subnet \
        --project=$PROJECT_ID \
        --network=$VPC_NETWORK \
        --region=$REGION \
        --range=10.10.0.0/24 \
        --enable-private-ip-google-access

    echo -e "${GREEN}✅ Subnet created${NC}"
else
    echo -e "${RED}Invalid option${NC}"
    exit 1
fi

# Create Serverless VPC Connector for Cloud Run
echo -e "${GREEN}Creating Serverless VPC Connector...${NC}"
echo "  This allows Cloud Run services to access VPC resources securely"
echo ""

CONNECTOR_NAME="mcp-connector"

if gcloud compute networks vpc-access connectors describe $CONNECTOR_NAME \
    --region=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}VPC connector $CONNECTOR_NAME already exists${NC}"
else
    gcloud compute networks vpc-access connectors create $CONNECTOR_NAME \
        --project=$PROJECT_ID \
        --region=$REGION \
        --network=$VPC_NETWORK \
        --range=10.10.1.0/28 \
        --min-instances=2 \
        --max-instances=10 \
        --machine-type=e2-micro

    echo -e "${GREEN}✅ VPC connector created${NC}"
fi

# Configure firewall rules for secure access
echo -e "${GREEN}Configuring firewall rules...${NC}"

# Allow health checks from Google Cloud (required for Cloud Run)
if ! gcloud compute firewall-rules describe allow-health-checks \
    --project=$PROJECT_ID &>/dev/null; then
    gcloud compute firewall-rules create allow-health-checks \
        --project=$PROJECT_ID \
        --network=$VPC_NETWORK \
        --allow=tcp \
        --source-ranges=130.211.0.0/22,35.191.0.0/16 \
        --description="Allow health checks from Google Cloud Load Balancing"

    echo -e "${GREEN}✅ Health check firewall rule created${NC}"
else
    echo -e "${YELLOW}Health check firewall rule already exists${NC}"
fi

# Allow internal traffic within VPC
if ! gcloud compute firewall-rules describe allow-internal \
    --project=$PROJECT_ID &>/dev/null; then
    gcloud compute firewall-rules create allow-internal \
        --project=$PROJECT_ID \
        --network=$VPC_NETWORK \
        --allow=tcp,udp,icmp \
        --source-ranges=10.10.0.0/20 \
        --description="Allow internal traffic within VPC"

    echo -e "${GREEN}✅ Internal traffic firewall rule created${NC}"
else
    echo -e "${YELLOW}Internal traffic firewall rule already exists${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ VPC Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "VPC Configuration:"
echo "  Network: $VPC_NETWORK"
echo "  Region: $REGION"
echo "  VPC Connector: $CONNECTOR_NAME"
echo ""
echo "Next steps:"
echo "  1. Run ./setup-secrets.sh to create Secret Manager secrets"
echo "  2. When deploying Cloud Run services, use these flags:"
echo "     --vpc-connector=$CONNECTOR_NAME"
echo "     --vpc-egress=all-traffic"
echo ""
