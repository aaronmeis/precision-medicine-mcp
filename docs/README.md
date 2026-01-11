# Documentation Index

Complete documentation for the Precision Medicine MCP system, organized by audience and purpose.

---

## 🎯 Start Here

| Document | Audience | Purpose |
|----------|----------|---------|
| **[Executive Summary](EXECUTIVE_SUMMARY.md)** | Funders, Decision-Makers | ROI analysis, budget, timeline, risk assessment |
| **[Production Roadmap](PRODUCTION_ROADMAP.md)** | Technical Leads, PMs | Path from POC to hospital production |
| **[Server Implementation Status](SERVER_IMPLEMENTATION_STATUS.md)** | Developers | Current state of all 10 MCP servers (9 deployed + mcp-epic local) |

---

## 📚 Documentation by Category

### Getting Started

| Document | Description |
|----------|-------------|
| [Claude Desktop Quickstart](guides/CLAUDE_DESKTOP_QUICKSTART.md) | Set up and run MCP servers locally with Claude Desktop |
| [Quick Test Prompts](../tests/manual_testing/QUICK_TEST_PROMPTS.md) | Sample queries to test each MCP server |
| [Automated Patient Reports](guides/AUTOMATED_PATIENT_REPORTS.md) | Generate comprehensive patient analysis reports |

### Deployment & Operations

| Document | Description |
|----------|-------------|
| **[deployment/](deployment/)** | POC deployment to GCP Cloud Run |
| └─ [Deployment Status](deployment/DEPLOYMENT_STATUS.md) | Current GCP Cloud Run deployment state (9 servers deployed) |
| └─ [GCP Testing Guide](deployment/GCP_TESTING_GUIDE.md) | Test deployed servers via Claude API |
| └─ [Security](deployment/SECURITY.md) | Security considerations for POC deployment |
| **[hospital-deployment/](hospital-deployment/)** | Production hospital deployment |
| └─ [Operations Manual](hospital-deployment/OPERATIONS_MANUAL.md) | System architecture, incident response |
| └─ [Admin Guide](hospital-deployment/ADMIN_GUIDE.md) | User management, monitoring, security |
| └─ [User Guide](hospital-deployment/USER_GUIDE.md) | For clinicians and bioinformaticians |
| └─ [HIPAA Compliance](hospital-deployment/HIPAA_COMPLIANCE.md) | Compliance validation and procedures |
| └─ [Audit Log Guide](hospital-deployment/AUDIT_LOG_GUIDE.md) | 10-year retention and reporting |
| └─ [Runbooks](hospital-deployment/RUNBOOKS/) | Troubleshooting procedures |

### Cost & Governance

| Document | Description |
|----------|-------------|
| **[operations/](operations/)** | Cost, governance, and operational docs |
| └─ [Cost Analysis](operations/COST_ANALYSIS.md) | Token pricing, cost per analysis, optimization strategies |
| └─ [Cost Tracking & Monitoring](operations/COST_TRACKING_MONITORING.md) | Real-time cost monitoring and budget management |
| └─ [Data Governance](operations/DATA_GOVERNANCE.md) | Data handling, privacy, retention policies |
| └─ [Risk Mitigation Summary](operations/RISK_MITIGATION_SUMMARY.md) | Risk assessment and mitigation strategies |

### Technical Deep Dives

| Document | Description |
|----------|-------------|
| **[technical/](technical/)** | Technical architecture and patterns |
| └─ [Error Handling & Retry Logic](technical/ERROR_HANDLING_RETRY_LOGIC.md) | Resilience patterns and error handling |
| **[guides/](guides/)** | User and integration guides |
| └─ [Clinical-Spatial Integration](guides/CLINICAL_SPATIAL_INTEGRATION.md) | How clinical and spatial data integrate |

### Reference Materials

| Document | Description |
|----------|-------------|
| [Disclaimers](DISCLAIMERS.md) | Research use only, liability, data disclaimers |
| [References](REFERENCES.md) | Citations, publications, external resources |

---

## 📂 Documentation Organization

**Organized structure (6 files at root + 5 subdirectories):**

```
docs/
├── README.md (this file)
│
├── Core Documentation (5 files - high visibility)
│   ├── EXECUTIVE_SUMMARY.md          # For funders
│   ├── PRODUCTION_ROADMAP.md         # Planning & roadmap
│   ├── SERVER_IMPLEMENTATION_STATUS.md # Server status
│   ├── DISCLAIMERS.md                # Foundational
│   └── REFERENCES.md                 # Citations
│
├── guides/ (3 files)
│   ├── CLAUDE_DESKTOP_QUICKSTART.md
│   ├── AUTOMATED_PATIENT_REPORTS.md
│   └── CLINICAL_SPATIAL_INTEGRATION.md
│
├── operations/ (4 files)
│   ├── COST_ANALYSIS.md
│   ├── COST_TRACKING_MONITORING.md
│   ├── DATA_GOVERNANCE.md
│   └── RISK_MITIGATION_SUMMARY.md
│
├── technical/ (1 file)
│   └── ERROR_HANDLING_RETRY_LOGIC.md
│
├── deployment/ (3 files)
│   ├── DEPLOYMENT_STATUS.md
│   ├── GCP_TESTING_GUIDE.md
│   └── SECURITY.md
│
└── hospital-deployment/ (5 files + runbooks)
    ├── OPERATIONS_MANUAL.md
    ├── ADMIN_GUIDE.md
    ├── USER_GUIDE.md
    ├── HIPAA_COMPLIANCE.md
    ├── AUDIT_LOG_GUIDE.md
    └── RUNBOOKS/
        ├── server-down.md
        ├── epic-connection-failure.md
        └── sso-issues.md
```

**Total:** 26 documentation files
**Root Level:** 6 files (down from 14) + 5 subdirectories

**Note:** Testing documentation has been consolidated into [tests/](../tests/) directory.

---

## 🎭 Documentation by Audience

### For Funders & Decision-Makers
1. [Executive Summary](EXECUTIVE_SUMMARY.md) - Start here for ROI, budget, timeline
2. [Production Roadmap](PRODUCTION_ROADMAP.md) - Path to production deployment
3. [Cost Analysis](operations/COST_ANALYSIS.md) - Detailed cost breakdown
4. [Risk Mitigation Summary](operations/RISK_MITIGATION_SUMMARY.md) - Risk assessment

### For Hospital Administrators
1. [Hospital Deployment Guide](hospital-deployment/OPERATIONS_MANUAL.md)
2. [HIPAA Compliance](hospital-deployment/HIPAA_COMPLIANCE.md)
3. [Admin Guide](hospital-deployment/ADMIN_GUIDE.md)
4. [Cost Tracking & Monitoring](operations/COST_TRACKING_MONITORING.md)
5. [Data Governance](operations/DATA_GOVERNANCE.md)

### For Clinicians & Researchers
1. [User Guide](hospital-deployment/USER_GUIDE.md) - How to use the system
2. [Automated Patient Reports](guides/AUTOMATED_PATIENT_REPORTS.md) - Generate analysis reports
3. [Clinical-Spatial Integration](guides/CLINICAL_SPATIAL_INTEGRATION.md) - How data integrates

### For Developers
1. [Server Implementation Status](SERVER_IMPLEMENTATION_STATUS.md) - Current server state
2. [Claude Desktop Quickstart](guides/CLAUDE_DESKTOP_QUICKSTART.md) - Local development setup
3. [Deployment Status](deployment/DEPLOYMENT_STATUS.md) - GCP Cloud Run deployment
4. [GCP Testing Guide](deployment/GCP_TESTING_GUIDE.md) - Test deployed servers
5. [Error Handling & Retry Logic](technical/ERROR_HANDLING_RETRY_LOGIC.md) - Resilience patterns

### For QA & Testing
1. [Testing Overview](../tests/README.md) - Complete testing documentation (167 automated tests)
2. [GCP Testing Guide](../tests/integration/GCP_TESTING_GUIDE.md) - Test deployed servers via Claude API
3. [Quick Test Prompts](../tests/manual_testing/QUICK_TEST_PROMPTS.md) - Copy-paste queries for rapid testing
4. [Phase 2 Features Guide](../tests/manual_testing/PHASE2_FEATURES_GUIDE.md) - Cell type deconvolution & DE testing
5. [PatientOne Tests](../tests/manual_testing/PatientOne-OvarianCancer/) - End-to-end integration tests

### For IT Operations
1. [Operations Manual](hospital-deployment/OPERATIONS_MANUAL.md) - System operations
2. [Admin Guide](hospital-deployment/ADMIN_GUIDE.md) - User and system management
3. [Audit Log Guide](hospital-deployment/AUDIT_LOG_GUIDE.md) - Logging and compliance
4. [Runbooks](hospital-deployment/RUNBOOKS/) - Incident response procedures
5. [Security](deployment/SECURITY.md) - Security considerations

---

## 🔍 Quick Links by Topic

### Cost & Budget
- [Cost Analysis](operations/COST_ANALYSIS.md) - $0.32 demo to $7-29 production per analysis
- [Cost Tracking & Monitoring](operations/COST_TRACKING_MONITORING.md) - Real-time monitoring
- [Executive Summary](EXECUTIVE_SUMMARY.md) - ROI: $3,187 savings per patient

### Deployment
- [Deployment Status](deployment/DEPLOYMENT_STATUS.md) - 9 servers deployed to GCP ✅
- [GCP Testing Guide](deployment/GCP_TESTING_GUIDE.md) - Test via Claude API
- [Production Roadmap](PRODUCTION_ROADMAP.md) - 12-16 week timeline

### Hospital Production
- [Hospital Deployment](hospital-deployment/) - Complete HIPAA-compliant setup
- [3-Month Timeline](PRODUCTION_ROADMAP.md#timeline) - MVP → Pilot → Production
- [HIPAA Compliance](hospital-deployment/HIPAA_COMPLIANCE.md) - De-identification, audit logs

### Security & Compliance
- [HIPAA Compliance](hospital-deployment/HIPAA_COMPLIANCE.md) - Safe Harbor de-identification
- [Security](deployment/SECURITY.md) - POC security considerations
- [Data Governance](operations/DATA_GOVERNANCE.md) - Privacy, retention, access control
- [Audit Log Guide](hospital-deployment/AUDIT_LOG_GUIDE.md) - 10-year retention

### Testing
- [Testing Overview](../tests/README.md) - 167 automated tests across all servers ✅
- [GCP Testing Guide](../tests/integration/GCP_TESTING_GUIDE.md) - Test 9 deployed servers via Claude API
- [Quick Test Prompts](../tests/manual_testing/QUICK_TEST_PROMPTS.md) - 10 copy-paste queries for rapid testing
- [PatientOne Integration Tests](../tests/manual_testing/PatientOne-OvarianCancer/) - End-to-end workflows

---

## 📖 Related Documentation

- **Main Project:** [README.md](../README.md) - Project overview and architecture
- **PatientOne:** [architecture/patient-one/](../architecture/patient-one/) - End-to-end workflow
- **Servers:** [servers/*/README.md](../servers/) - Individual server documentation
- **Testing:** [tests/](../tests/) - Test implementations and results

## 🏗️ Architecture Documentation

Detailed workflow architectures for each analysis modality:

- **[Multiomics Integration](../architecture/multiomics/README.md)** - RNA/Protein/Phospho integration workflow (mcp-multiomics)
- **[Spatial Transcriptomics](../architecture/spatial-transcriptomics/README.md)** - Visium spatial RNA-seq pipeline (mcp-spatialtools)
- **[Imaging Analysis](../architecture/imaging/README.md)** - H&E + MxIF workflows (mcp-openimagedata, mcp-deepcell)
- **[PatientOne Use Case](../architecture/patient-one/README.md)** - End-to-end precision medicine workflow

---

**Last Updated:** 2026-01-10
**Total Documents:** 30 files
**Status:** Documentation complete for POC and hospital deployment
