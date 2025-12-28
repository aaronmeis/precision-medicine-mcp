#!/usr/bin/env python3
"""Test mcp-epic server with live FHIR data from GCP Healthcare API."""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_epic.server import (
    get_patient_demographics,
    get_patient_conditions,
    get_patient_observations,
    get_patient_medications,
)


async def main():
    """Test all FHIR tools with real data."""
    print("=" * 80)
    print("Testing mcp-epic server with live FHIR data from GCP")
    print("=" * 80)
    print()

    patient_id = "patient-001"

    # Test 1: Get patient demographics
    print("1. Testing get_patient_demographics...")
    result = await get_patient_demographics.fn(patient_id)
    if result["status"] == "success":
        data = result["data"]
        print(f"   ✅ Success!")
        print(f"   - ID: {data.get('id', 'N/A')}")
        print(f"   - Gender: {data.get('gender', 'N/A')}")
        print(f"   - Birth Year: {data.get('birthDate', 'N/A')}")
        print(f"   - De-identified: {data.get('_deidentified', False)}")
        print(f"   - Method: {data.get('_deidentification_method', 'N/A')}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        print(f"   Message: {result.get('message', '')}")

    print()

    # Test 2: Get patient conditions
    print("2. Testing get_patient_conditions...")
    result = await get_patient_conditions.fn(patient_id)
    if result["status"] == "success":
        count = result["count"]
        print(f"   ✅ Success! Found {count} condition(s)")
        if count > 0 and "entry" in result["data"]:
            for entry in result["data"]["entry"]:
                cond = entry["resource"]
                print(f"   - {cond.get('code', {}).get('text', 'N/A')}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # Test 3: Get patient observations
    print("3. Testing get_patient_observations...")
    result = await get_patient_observations.fn(patient_id)
    if result["status"] == "success":
        count = result["count"]
        print(f"   ✅ Success! Found {count} observation(s)")
        if count > 0 and "entry" in result["data"]:
            for entry in result["data"]["entry"]:
                obs = entry["resource"]
                code_text = obs.get("code", {}).get("text", "N/A")
                value = obs.get("valueQuantity", obs.get("valueCodeableConcept", {}))
                print(f"   - {code_text}: {value}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

    print()

    # Test 4: Get patient medications
    print("4. Testing get_patient_medications...")
    result = await get_patient_medications.fn(patient_id)
    if result["status"] == "success":
        count = result["count"]
        print(f"   ✅ Success! Found {count} medication(s)")
        if count > 0 and "entry" in result["data"]:
            for entry in result["data"]["entry"]:
                med = entry["resource"]
                med_text = med.get("medicationCodeableConcept", {}).get("text", "N/A")
                status = med.get("status", "N/A")
                print(f"   - {med_text} ({status})")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 80)
    print("Live FHIR Testing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
