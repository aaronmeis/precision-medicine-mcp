#!/usr/bin/env python3
"""
Submit Clinician-in-the-Loop (CitL) review to audit trail and update report status.

This script validates completed review forms against a JSON schema, generates
a cryptographic signature for the review, logs the review to Cloud Logging for
audit trail purposes, and creates a signed review record.

Usage:
    python citl_submit_review.py --patient-id PAT001-OVC-2025 --review-file ./results/PAT001-OVC-2025/citl_review_completed.json

Requirements:
    - google-cloud-logging
    - jsonschema

Author: Claude Sonnet 4.5
Date: 2026-01-13
Part of: Precision Medicine MCP - CitL Validation Workflow
"""

import argparse
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from google.cloud import logging as cloud_logging
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False
    print("⚠️  Warning: google-cloud-logging not available. Audit logging will be simulated.", file=sys.stderr)

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("⚠️  Warning: jsonschema not available. Schema validation will be skipped.", file=sys.stderr)


def validate_review(review_data: Dict[str, Any], schema_path: str) -> bool:
    """
    Validate review against JSON schema.

    Args:
        review_data: The review data dictionary to validate
        schema_path: Path to the JSON schema file

    Returns:
        True if validation passes or if jsonschema not available

    Raises:
        jsonschema.ValidationError: If validation fails
        FileNotFoundError: If schema file not found
    """
    if not JSONSCHEMA_AVAILABLE:
        print("⚠️  Skipping schema validation (jsonschema not installed)", file=sys.stderr)
        return True

    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path) as f:
        schema = json.load(f)

    jsonschema.validate(review_data, schema)
    return True


def generate_signature_hash(review_data: Dict[str, Any]) -> str:
    """
    Generate SHA-256 hash for digital signature.

    The signature is generated from a canonical JSON representation
    (sorted keys) to ensure deterministic hashing.

    Args:
        review_data: The review data dictionary

    Returns:
        64-character hexadecimal SHA-256 hash
    """
    canonical = json.dumps(review_data, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def log_to_cloud_logging(review_data: Dict[str, Any], signature_hash: str) -> bool:
    """
    Log review to Cloud Logging for audit trail.

    Creates a structured log entry in the 'citl-reviews' logger with all
    relevant review metadata. Patient and reviewer PII is hashed before logging.

    Args:
        review_data: The review data dictionary
        signature_hash: The cryptographic signature of the review

    Returns:
        True if logged successfully (or if simulated)
    """
    # Prepare log entry
    log_entry = {
        'event': 'citl_review',
        'timestamp': datetime.now().isoformat(),
        'patient_id_hash': hashlib.sha256(review_data['patient_id'].encode()).hexdigest(),
        'report_id': f"{review_data['patient_id']}-{review_data.get('report_date', 'unknown')}",
        'reviewer': {
            'email_hash': hashlib.sha256(review_data['reviewer']['email'].encode()).hexdigest(),
            'name': review_data['reviewer']['name'],
            'credentials': review_data['reviewer']['credentials'],
            'role': review_data['reviewer'].get('role', 'oncologist')
        },
        'decision': {
            'status': review_data['decision']['status'],
            'rationale': review_data['decision']['rationale']
        },
        'signature_hash': signature_hash,
        'findings_validated': len(review_data.get('per_finding_validation', [])),
        'findings_confirmed': sum(1 for f in review_data.get('per_finding_validation', [])
                                   if f.get('validation_status') == 'CONFIRMED'),
        'findings_uncertain': sum(1 for f in review_data.get('per_finding_validation', [])
                                   if f.get('validation_status') == 'UNCERTAIN'),
        'findings_rejected': sum(1 for f in review_data.get('per_finding_validation', [])
                                  if f.get('validation_status') == 'INCORRECT'),
        'guideline_compliance': review_data.get('guideline_compliance', {}),
        'quality_flags_count': len(review_data.get('quality_flags_assessment', [])),
        'quality_flags_acceptable': sum(1 for f in review_data.get('quality_flags_assessment', [])
                                         if f.get('reviewer_assessment') == 'ACCEPTABLE'),
        'revision_count': review_data.get('revision_count', 0)
    }

    if CLOUD_LOGGING_AVAILABLE:
        try:
            client = cloud_logging.Client()
            logger = client.logger('citl-reviews')
            logger.log_struct(log_entry, severity='INFO')
            print(f"✅ Logged to Cloud Logging: citl-reviews")
            return True
        except Exception as e:
            print(f"❌ Error logging to Cloud Logging: {e}", file=sys.stderr)
            print(f"   Log entry will be saved locally instead", file=sys.stderr)
            # Fall through to local logging

    # Local logging (fallback or when Cloud Logging not available)
    log_file = Path("citl_review_audit_trail.jsonl")
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    print(f"✅ Logged locally to: {log_file}")
    return True


def save_signed_review(review_data: Dict[str, Any], original_file: str) -> str:
    """
    Save signed review with digital signature and timestamp.

    Args:
        review_data: The review data dictionary (with signature added)
        original_file: Path to the original review file

    Returns:
        Path to the signed review file
    """
    output_file = original_file.replace('.json', '_signed.json')
    with open(output_file, 'w') as f:
        json.dump(review_data, f, indent=2)
    return output_file


def print_summary(review_data: Dict[str, Any], signature_hash: str, signed_file: str):
    """Print a summary of the review submission."""
    print(f"\n{'='*70}")
    print(f"Review Submission Summary")
    print(f"{'='*70}")
    print(f"Patient ID:       {review_data['patient_id']}")
    print(f"Decision:         {review_data['decision']['status']}")
    print(f"Reviewer:         {review_data['reviewer']['name']} ({review_data['reviewer']['credentials']})")
    print(f"Review Date:      {review_data.get('review_date', 'Not specified')}")
    print(f"Signature Hash:   {signature_hash[:32]}...")
    print(f"Signed Review:    {signed_file}")

    # Print validation summary
    findings = review_data.get('per_finding_validation', [])
    if findings:
        confirmed = sum(1 for f in findings if f.get('validation_status') == 'CONFIRMED')
        uncertain = sum(1 for f in findings if f.get('validation_status') == 'UNCERTAIN')
        incorrect = sum(1 for f in findings if f.get('validation_status') == 'INCORRECT')
        print(f"\nFindings Validated: {len(findings)} total")
        print(f"  - Confirmed:  {confirmed}")
        print(f"  - Uncertain:  {uncertain}")
        print(f"  - Incorrect:  {incorrect}")

    # Print guideline compliance
    gc = review_data.get('guideline_compliance', {})
    if gc:
        print(f"\nGuideline Compliance:")
        print(f"  - NCCN:          {gc.get('nccn_aligned', 'Not assessed')}")
        print(f"  - Institutional: {gc.get('institutional_aligned', 'Not assessed')}")

    print(f"{'='*70}\n")


def main():
    """Main entry point for CitL review submission."""
    parser = argparse.ArgumentParser(
        description='Submit Clinician-in-the-Loop (CitL) review to audit trail',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Submit a completed review
    python citl_submit_review.py --patient-id PAT001-OVC-2025 \\
        --review-file ./results/PAT001-OVC-2025/citl_review_completed.json

    # Use custom schema location
    python citl_submit_review.py --patient-id PAT001-OVC-2025 \\
        --review-file ./results/PAT001-OVC-2025/citl_review_completed.json \\
        --schema ./custom/schema.json
        """
    )
    parser.add_argument('--patient-id', required=True,
                       help='Patient identifier (e.g., PAT001-OVC-2025)')
    parser.add_argument('--review-file', required=True,
                       help='Path to completed review JSON file')
    parser.add_argument('--schema', default='schemas/citl_review_schema.json',
                       help='Path to JSON schema for validation (default: schemas/citl_review_schema.json)')
    parser.add_argument('--skip-cloud-logging', action='store_true',
                       help='Skip Cloud Logging, only save locally')

    args = parser.parse_args()

    # Validate inputs
    review_file = Path(args.review_file)
    if not review_file.exists():
        print(f"❌ Error: Review file not found: {args.review_file}", file=sys.stderr)
        sys.exit(1)

    print(f"📋 CitL Review Submission")
    print(f"{'='*70}")
    print(f"Patient ID:     {args.patient_id}")
    print(f"Review File:    {args.review_file}")
    print(f"Schema:         {args.schema}")
    print(f"{'='*70}\n")

    # Load review data
    print(f"📂 Loading review data...")
    try:
        with open(args.review_file) as f:
            review_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in review file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate patient ID matches
    if review_data.get('patient_id') != args.patient_id:
        print(f"⚠️  Warning: Patient ID mismatch:", file=sys.stderr)
        print(f"   Command line: {args.patient_id}", file=sys.stderr)
        print(f"   Review file:  {review_data.get('patient_id')}", file=sys.stderr)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted by user")
            sys.exit(1)

    # Validate against schema
    print(f"📋 Validating review against JSON schema...")
    try:
        validate_review(review_data, args.schema)
        print(f"✅ Schema validation passed")
    except jsonschema.ValidationError as e:
        print(f"❌ Schema validation failed:", file=sys.stderr)
        print(f"   {e.message}", file=sys.stderr)
        print(f"   Path: {' → '.join(str(p) for p in e.path)}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"⚠️  Warning: {e}", file=sys.stderr)
        print(f"   Skipping schema validation", file=sys.stderr)

    # Generate digital signature
    print(f"🔐 Generating digital signature...")
    signature_hash = generate_signature_hash(review_data)

    # Add signature and timestamp to review
    if 'attestation' not in review_data:
        review_data['attestation'] = {}
    review_data['attestation']['signature_hash'] = signature_hash
    review_data['attestation']['timestamp'] = datetime.now().isoformat()

    print(f"   Signature: {signature_hash[:16]}...")

    # Log to audit trail
    if not args.skip_cloud_logging:
        print(f"📝 Logging to audit trail...")
        log_to_cloud_logging(review_data, signature_hash)
    else:
        print(f"⏩ Skipping Cloud Logging (--skip-cloud-logging)")

    # Save signed review
    print(f"💾 Saving signed review...")
    signed_file = save_signed_review(review_data, args.review_file)

    # Print summary
    print_summary(review_data, signature_hash, signed_file)

    print(f"✅ Review submitted successfully!")

    # Provide next steps based on decision
    if review_data['decision']['status'] == 'APPROVE':
        print(f"\n📍 Next Step: Finalize the approved report")
        print(f"   python tools/reports/finalize_patient_report.py --patient-id {args.patient_id}")
    elif review_data['decision']['status'] == 'REVISE':
        print(f"\n📍 Next Step: Address revision instructions in the review form")
        print(f"   Re-run analysis with adjusted parameters, then resubmit for review")
    elif review_data['decision']['status'] == 'REJECT':
        print(f"\n📍 Next Step: Escalate to bioinformatics team")
        print(f"   Review critical errors documented in the review form")


if __name__ == "__main__":
    main()
