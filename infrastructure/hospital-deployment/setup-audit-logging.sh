#!/bin/bash
set -e

# Audit Logging Setup for HIPAA Compliance
# Configures 10-year log retention and audit sinks

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Audit Logging Setup${NC}"
echo -e "${GREEN}HIPAA-Compliant 10-Year Retention${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project set. Run setup-project.sh first${NC}"
    exit 1
fi

REGION=${REGION:-us-central1}

echo -e "${GREEN}Configuration:${NC}"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Retention: 3650 days (10 years - HIPAA requirement)"
echo ""

# Step 1: Create Log Bucket with 10-year retention
echo -e "${GREEN}Step 1/4: Creating HIPAA audit log bucket...${NC}"

LOG_BUCKET_ID="hipaa-audit-logs"

if gcloud logging buckets describe $LOG_BUCKET_ID \
    --location=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Log bucket $LOG_BUCKET_ID already exists${NC}"
else
    gcloud logging buckets create $LOG_BUCKET_ID \
        --location=$REGION \
        --project=$PROJECT_ID \
        --retention-days=3650 \
        --description="HIPAA audit logs - 10 year retention for compliance"

    echo -e "${GREEN}✅ Log bucket created with 10-year retention${NC}"
fi

echo ""

# Step 2: Create Log Sink for Cloud Run
echo -e "${GREEN}Step 2/4: Creating log sink for Cloud Run services...${NC}"

SINK_NAME="mcp-audit-sink"
SINK_DESTINATION="logging.googleapis.com/projects/$PROJECT_ID/locations/$REGION/buckets/$LOG_BUCKET_ID"

if gcloud logging sinks describe $SINK_NAME --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Log sink $SINK_NAME already exists${NC}"
else
    gcloud logging sinks create $SINK_NAME $SINK_DESTINATION \
        --project=$PROJECT_ID \
        --log-filter='resource.type="cloud_run_revision"
severity>=INFO'

    echo -e "${GREEN}✅ Log sink created for Cloud Run services${NC}"
fi

echo ""

# Step 3: Create Log Sink for User Authentication Events
echo -e "${GREEN}Step 3/4: Creating log sink for authentication events...${NC}"

AUTH_SINK_NAME="mcp-auth-audit-sink"

if gcloud logging sinks describe $AUTH_SINK_NAME --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Log sink $AUTH_SINK_NAME already exists${NC}"
else
    gcloud logging sinks create $AUTH_SINK_NAME $SINK_DESTINATION \
        --project=$PROJECT_ID \
        --log-filter='protoPayload.serviceName="run.googleapis.com"
protoPayload.methodName=~"google.cloud.run.*"
severity>=INFO'

    echo -e "${GREEN}✅ Log sink created for authentication events${NC}"
fi

echo ""

# Step 4: Configure Data Access Audit Logs
echo -e "${GREEN}Step 4/4: Enabling Data Access audit logs...${NC}"

cat > /tmp/audit-config.yaml <<EOF
auditConfigs:
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: run.googleapis.com
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: storage.googleapis.com
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: secretmanager.googleapis.com
EOF

echo -e "${YELLOW}Audit log configuration created at /tmp/audit-config.yaml${NC}"
echo -e "${YELLOW}To enable data access logs, run:${NC}"
echo ""
echo "  gcloud projects get-iam-policy $PROJECT_ID > /tmp/policy.yaml"
echo "  # Manually merge /tmp/audit-config.yaml into /tmp/policy.yaml"
echo "  gcloud projects set-iam-policy $PROJECT_ID /tmp/policy.yaml"
echo ""
echo -e "${YELLOW}Or use Cloud Console: IAM & Admin -> Audit Logs${NC}"

echo ""

# Step 5: Create custom log-based metrics
echo -e "${GREEN}Creating custom log-based metrics...${NC}"

# Metric 1: De-identification success
if gcloud logging metrics describe deidentification_success --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Metric deidentification_success already exists${NC}"
else
    gcloud logging metrics create deidentification_success \
        --project=$PROJECT_ID \
        --description="Count of successful de-identification operations" \
        --log-filter='jsonPayload.event="deidentification" AND jsonPayload.success=true'

    echo -e "${GREEN}✅ Metric created: deidentification_success${NC}"
fi

# Metric 2: Epic FHIR failures
if gcloud logging metrics describe epic_fhir_failures --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Metric epic_fhir_failures already exists${NC}"
else
    gcloud logging metrics create epic_fhir_failures \
        --project=$PROJECT_ID \
        --description="Count of Epic FHIR API failures" \
        --log-filter='jsonPayload.event="epic_fhir_call" AND jsonPayload.status="error"'

    echo -e "${GREEN}✅ Metric created: epic_fhir_failures${NC}"
fi

# Metric 3: User access events
if gcloud logging metrics describe user_access_events --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Metric user_access_events already exists${NC}"
else
    gcloud logging metrics create user_access_events \
        --project=$PROJECT_ID \
        --description="Count of user access events" \
        --log-filter='jsonPayload.event="user_login" OR jsonPayload.event="mcp_query"'

    echo -e "${GREEN}✅ Metric created: user_access_events${NC}"
fi

echo ""

# Display log viewing instructions
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Audit Logging Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Log Configuration:"
echo "  Bucket: $LOG_BUCKET_ID"
echo "  Location: $REGION"
echo "  Retention: 3650 days (10 years)"
echo "  Cloud Run Sink: $SINK_NAME"
echo "  Auth Sink: $AUTH_SINK_NAME"
echo ""
echo "Custom Metrics:"
echo "  - deidentification_success"
echo "  - epic_fhir_failures"
echo "  - user_access_events"
echo ""
echo "HIPAA Compliance Notes:"
echo "  ✅ Logs retained for 10 years (HIPAA requirement)"
echo "  ✅ All Cloud Run requests captured"
echo "  ✅ Authentication events logged"
echo "  ✅ Logs encrypted at rest and in transit"
echo ""
echo "View Logs:"
echo "  Cloud Console: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
echo ""
echo "  CLI:"
echo "    # View Cloud Run logs"
echo "    gcloud logging read 'resource.type=\"cloud_run_revision\"' --limit=50"
echo ""
echo "    # View user access logs"
echo "    gcloud logging read 'jsonPayload.event=\"user_login\" OR jsonPayload.event=\"mcp_query\"' --limit=50"
echo ""
echo "    # Export logs to local file"
echo "    gcloud logging read 'resource.type=\"cloud_run_revision\"' --format=json > audit-logs.json"
echo ""
echo "Next steps:"
echo "  1. Deploy OAuth2 Proxy with audit logging"
echo "  2. Deploy MCP servers with structured logging"
echo "  3. Test log collection with sample queries"
echo "  4. Set up monitoring alerts for log-based metrics"
echo ""
