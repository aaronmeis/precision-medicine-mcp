# Test Documentation

This directory contains all documentation related to testing the Precision Medicine MCP system.

**📍 Note:** Test **code** (`.py` files, test fixtures, scripts) remains in `/tests`. This directory contains test **documentation** only.

## Contents

### [Test Coverage](./test-coverage.md)
Overview of test coverage, test structure, and testing guidelines for the project.

### [Integration Testing](./integration-testing/)
- [GCP Testing Guide](./integration-testing/gcp-testing-guide.md) - Testing deployed servers via Claude API

### [Manual Testing](./manual-testing/)
- [README](./manual-testing/README.md) - Manual testing overview
- [Quick Test Prompts](./manual-testing/quick-test-prompts.md) - 10 copy-paste prompts for Claude Desktop
- [Server Verification](./manual-testing/server-verification.md) - Quick verification prompts
- [Example Prompts (Spatial)](./manual-testing/example-prompts-spatial.md) - Spatial analysis examples
- [Claude Desktop Setup](./manual-testing/claude-desktop-setup.md) - File access configuration

### [PatientOne Scenario](./patient-one-scenario/)
Complete testing scenario using synthetic ovarian cancer patient data.

- [Overview](./patient-one-scenario/README.md) - PatientOne testing scenario
- [Quick Reference](./patient-one-scenario/quick-reference.md) - Quick test reference
- [CITL Quick Test](./patient-one-scenario/citl-quick-test.md) - Clinician-in-the-Loop workflow test
- [Data Modes Guide](./patient-one-scenario/data-modes-guide.md) - Data mode configuration
- [Test All Servers](./patient-one-scenario/test-all-servers.md) - Complete server testing
- [End-to-End Test](./patient-one-scenario/end-to-end-test.md) - Full workflow test

#### Test Prompts
Ready-to-use test prompts for the complete PatientOne workflow:

1. [Test 1: Clinical Genomic](./patient-one-scenario/test-prompts/test-1-clinical-genomic.md)
2. [Test 2: Multiomics Enhanced](./patient-one-scenario/test-prompts/test-2-multiomics-enhanced.md)
3. [Test 3: Spatial](./patient-one-scenario/test-prompts/test-3-spatial.md)
4. [Test 4: Imaging](./patient-one-scenario/test-prompts/test-4-imaging.md)
5. [Test 5: Integration](./patient-one-scenario/test-prompts/test-5-integration.md)
6. [Test 6: CitL Review](./patient-one-scenario/test-prompts/test-6-citl-review.md)


---

## Quick Start

**For automated testing:** See `/tests` directory for pytest unit and integration tests.

**For manual testing:**
1. Start with [Quick Test Prompts](./manual-testing/quick-test-prompts.md) for rapid verification
2. Run [PatientOne scenario](./patient-one-scenario/README.md) for comprehensive end-to-end testing
3. Follow [CitL Quick Test](./patient-one-scenario/citl-quick-test.md) to validate clinical review workflow

---

**Last Updated:** 2026-01-13
