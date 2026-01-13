"""
Integration tests for Clinician-in-the-Loop (CitL) end-to-end workflow.

Tests complete workflow:
1. Generate draft report with quality checks (PatientOne data)
2. Create mock clinician review (APPROVE/REVISE/REJECT)
3. Submit review with signature and audit logging
4. Finalize approved report OR handle revision

Prerequisites:
- PatientOne spatial data must be available
- Scripts must be executable: generate_patient_report.py, citl_submit_review.py, finalize_patient_report.py

Run tests:
    pytest tests/integration/test_citl_end_to_end.py -v -s
    pytest tests/integration/test_citl_end_to_end.py::TestCitlApproveWorkflow -v
"""

import pytest
import json
import subprocess
from pathlib import Path
import tempfile
import shutil
from datetime import datetime


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
PATIENT_ID = "PAT001-OVC-2025"
VENV_PYTHON = PROJECT_ROOT / "servers/mcp-spatialtools/venv/bin/python3"

# Check if venv exists
if not VENV_PYTHON.exists():
    pytest.skip("spatialtools venv not found", allow_module_level=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_script(script_name: str, args: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a Python script with the spatialtools venv."""
    script_path = SCRIPTS_DIR / script_name
    cmd = [str(VENV_PYTHON), str(script_path)] + args

    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    return result


def create_mock_review(patient_id: str, decision_status: str = "APPROVE") -> dict:
    """Create mock review JSON."""
    review = {
        'patient_id': patient_id,
        'report_date': datetime.now().isoformat(),
        'reviewer': {
            'name': 'Dr. Integration Test',
            'email': 'integration.test@hospital.org',
            'credentials': 'MD, Medical Oncology',
            'role': 'oncologist'
        },
        'review_date': datetime.now().isoformat(),
        'decision': {
            'status': decision_status,
            'rationale': f'Integration test with {decision_status} decision.'
        },
        'per_finding_validation': [
            {
                'finding_id': 'DEG_1',
                'gene': 'TP53',
                'validation_status': 'CONFIRMED',
                'comments': 'Test validation'
            }
        ],
        'guideline_compliance': {
            'nccn_aligned': 'ALIGNED',
            'institutional_aligned': 'ALIGNED'
        },
        'quality_flags_assessment': [],
        'treatment_recommendations_review': [],
        'attestation': {
            'reviewed_all_findings': True,
            'assessed_compliance': True,
            'clinical_judgment': True,
            'medical_record_acknowledgment': True
        },
        'revision_count': 0
    }

    # Add revision_instructions if REVISE or REJECT
    if decision_status in ['REVISE', 'REJECT']:
        review['revision_instructions'] = {
            'issues_to_address': ['Integration test issue'],
            'reanalysis_parameters': {
                'fdr_threshold': 0.01,
                'min_spots_per_region': 50
            },
            'resubmission_date': '2026-01-20'
        }

    return review


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for test results."""
    temp_dir = tempfile.mkdtemp(prefix='citl_test_')
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def patient_output_dir(temp_output_dir):
    """Create patient-specific output directory."""
    patient_dir = temp_output_dir / PATIENT_ID
    patient_dir.mkdir(parents=True, exist_ok=True)
    return patient_dir


# ============================================================================
# TESTS: APPROVE Workflow
# ============================================================================

class TestCitlApproveWorkflow:
    """Test complete CitL workflow with APPROVE decision."""

    def test_step1_generate_draft_report(self, temp_output_dir):
        """Step 1: Generate draft report with quality checks."""
        result = run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ],
            timeout=120
        )

        # Check success
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "DRAFT REPORT COMPLETE" in result.stdout

        # Verify output files exist
        patient_dir = temp_output_dir / PATIENT_ID
        assert (patient_dir / "draft_report.json").exists()
        assert (patient_dir / "quality_checks.json").exists()
        assert (patient_dir / "clinical_summary.txt").exists()

        # Verify draft report structure
        with open(patient_dir / "draft_report.json") as f:
            draft = json.load(f)

        assert draft['report_metadata']['status'] == 'pending_review'
        assert draft['report_metadata']['patient_id'] == PATIENT_ID
        assert 'quality_checks' in draft
        assert 'key_molecular_findings' in draft
        assert len(draft['key_molecular_findings']) > 0

    def test_step2_submit_approve_review(self, temp_output_dir, patient_output_dir):
        """Step 2: Submit APPROVE review with digital signature."""
        # Generate draft first
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Create mock review
        review = create_mock_review(PATIENT_ID, 'APPROVE')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        # Submit review
        result = run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )

        # Check success
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "Review submitted successfully" in result.stdout
        assert "APPROVE" in result.stdout

        # Verify signed review exists
        signed_review_file = patient_output_dir / "citl_review_completed_signed.json"
        assert signed_review_file.exists()

        # Verify signature was added
        with open(signed_review_file) as f:
            signed_review = json.load(f)

        assert 'signature_hash' in signed_review['attestation']
        assert len(signed_review['attestation']['signature_hash']) == 64

    def test_step3_finalize_approved_report(self, temp_output_dir, patient_output_dir):
        """Step 3: Finalize approved report."""
        # Generate draft
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Submit APPROVE review
        review = create_mock_review(PATIENT_ID, 'APPROVE')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )

        # Finalize report
        result = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )

        # Check success
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "Report finalization complete" in result.stdout
        assert "clinically_approved" in result.stdout

        # Verify final report exists
        final_report_file = patient_output_dir / "final_report_approved.json"
        assert final_report_file.exists()

        # Verify final report structure
        with open(final_report_file) as f:
            final_report = json.load(f)

        assert final_report['report_metadata']['status'] == 'clinically_approved'
        assert final_report['report_metadata']['reviewer'] == 'Dr. Integration Test'
        assert 'approval_date' in final_report['report_metadata']
        assert 'clinical_attestation' in final_report

    def test_complete_approve_workflow(self, temp_output_dir, patient_output_dir):
        """Test complete workflow: draft → review → approve → finalize."""
        # Step 1: Generate draft
        result1 = run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )
        assert result1.returncode == 0

        # Step 2: Submit APPROVE review
        review = create_mock_review(PATIENT_ID, 'APPROVE')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        result2 = run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )
        assert result2.returncode == 0

        # Step 3: Finalize
        result3 = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )
        assert result3.returncode == 0

        # Verify all expected files exist
        assert (patient_output_dir / "draft_report.json").exists()
        assert (patient_output_dir / "quality_checks.json").exists()
        assert (patient_output_dir / "citl_review_completed_signed.json").exists()
        assert (patient_output_dir / "final_report_approved.json").exists()


# ============================================================================
# TESTS: REVISE Workflow
# ============================================================================

class TestCitlReviseWorkflow:
    """Test CitL workflow with REVISE decision."""

    def test_revise_blocks_finalization(self, temp_output_dir, patient_output_dir):
        """Test that REVISE decision blocks report finalization."""
        # Generate draft
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Submit REVISE review
        review = create_mock_review(PATIENT_ID, 'REVISE')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )

        # Try to finalize - should fail
        result = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )

        # Should exit with error or print warning
        assert "REVISE" in result.stdout or result.returncode != 0
        assert not (patient_output_dir / "final_report_approved.json").exists()

    def test_revise_includes_instructions(self, temp_output_dir, patient_output_dir):
        """Test that REVISE review includes revision_instructions."""
        # Generate draft
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Submit REVISE review
        review = create_mock_review(PATIENT_ID, 'REVISE')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        result = run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )

        assert result.returncode == 0

        # Verify revision_instructions in signed review
        signed_review_file = patient_output_dir / "citl_review_completed_signed.json"
        with open(signed_review_file) as f:
            signed_review = json.load(f)

        assert 'revision_instructions' in signed_review
        assert 'issues_to_address' in signed_review['revision_instructions']


# ============================================================================
# TESTS: REJECT Workflow
# ============================================================================

class TestCitlRejectWorkflow:
    """Test CitL workflow with REJECT decision."""

    def test_reject_blocks_finalization(self, temp_output_dir, patient_output_dir):
        """Test that REJECT decision blocks report finalization."""
        # Generate draft
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Submit REJECT review
        review = create_mock_review(PATIENT_ID, 'REJECT')
        review_file = patient_output_dir / "citl_review_completed.json"

        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)

        run_script(
            'citl_submit_review.py',
            [
                '--patient-id', PATIENT_ID,
                '--review-file', str(review_file),
                '--skip-cloud-logging'
            ]
        )

        # Try to finalize - should fail
        result = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )

        # Should exit with error or print warning
        assert "REJECT" in result.stdout or result.returncode != 0
        assert not (patient_output_dir / "final_report_approved.json").exists()


# ============================================================================
# TESTS: Quality Checks Integration
# ============================================================================

class TestQualityChecksIntegration:
    """Test quality checks integration with real PatientOne data."""

    def test_quality_checks_run_automatically(self, temp_output_dir):
        """Test that quality checks run automatically during draft generation."""
        result = run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        assert result.returncode == 0

        # Verify quality checks file exists
        patient_dir = temp_output_dir / PATIENT_ID
        quality_checks_file = patient_dir / "quality_checks.json"
        assert quality_checks_file.exists()

        # Verify quality checks structure
        with open(quality_checks_file) as f:
            quality_checks = json.load(f)

        assert 'all_checks_passed' in quality_checks
        assert 'flags' in quality_checks
        assert 'checks_detail' in quality_checks

        # Should have 4 checks
        expected_checks = [
            'sample_size_adequate',
            'fdr_thresholds_met',
            'data_completeness',
            'consistency_cross_modal'
        ]

        for check in expected_checks:
            assert check in quality_checks['checks_detail']


# ============================================================================
# TESTS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling in CitL workflow."""

    def test_missing_patient_data(self, temp_output_dir):
        """Test error handling when patient data is missing."""
        result = run_script(
            'generate_patient_report.py',
            [
                '--patient-id', 'NONEXISTENT-PATIENT',
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Current behavior: Falls back to PatientOne data with warning
        # Future improvement: Could fail with error if strict mode enabled
        assert result.returncode == 0
        assert "Could not fetch patient data (using mock data)" in result.stdout or \
               "using mock data" in result.stdout.lower()

    def test_missing_draft_report(self, temp_output_dir, patient_output_dir):
        """Test error handling when trying to finalize without draft report."""
        # Try to finalize without generating draft
        result = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )

        # Should fail gracefully
        assert result.returncode != 0 or "not found" in result.stderr.lower() or "not found" in result.stdout.lower()

    def test_missing_signed_review(self, temp_output_dir, patient_output_dir):
        """Test error handling when trying to finalize without signed review."""
        # Generate draft but don't submit review
        run_script(
            'generate_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir),
                '--generate-draft'
            ]
        )

        # Try to finalize without review
        result = run_script(
            'finalize_patient_report.py',
            [
                '--patient-id', PATIENT_ID,
                '--output-dir', str(temp_output_dir)
            ]
        )

        # Should fail gracefully
        assert result.returncode != 0 or "No signed review" in result.stdout or "not found" in result.stdout.lower()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])
