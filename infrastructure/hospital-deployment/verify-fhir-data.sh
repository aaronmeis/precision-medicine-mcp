#!/bin/bash

# Verify FHIR data uploaded to GCP Healthcare API

PROJECT_ID="precision-medicine-poc"
REGION="us-central1"
TOKEN=$(gcloud auth print-access-token 2>/dev/null)

echo "=== FHIR Store Data Summary ==="
echo ""

# Patient
echo "1. Patient:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://healthcare.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/datasets/precision-medicine-dataset/fhirStores/identified-fhir-store/fhir/Patient/patient-001" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Name: {data['name'][0]['given'][0]} {data['name'][0]['family']}\"); print(f\"   Gender: {data['gender']}\"); print(f\"   Birth Date: {data['birthDate']}\")"

echo ""

# Conditions
echo "2. Conditions:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://healthcare.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/datasets/precision-medicine-dataset/fhirStores/identified-fhir-store/fhir/Condition?patient=patient-001" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Total: {data['total']}\"); [print(f\"   - {entry['resource']['code']['text']}\") for entry in data.get('entry', [])]"

echo ""

# Observations
echo "3. Observations:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://healthcare.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/datasets/precision-medicine-dataset/fhirStores/identified-fhir-store/fhir/Observation?patient=patient-001" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Total: {data['total']}\"); [print(f\"   - {entry['resource']['code']['text']}\") for entry in data.get('entry', [])]"

echo ""

# Medications
echo "4. Medications:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://healthcare.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/datasets/precision-medicine-dataset/fhirStores/identified-fhir-store/fhir/MedicationStatement?patient=patient-001" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Total: {data['total']}\"); [print(f\"   - {entry['resource']['medicationCodeableConcept']['text']} ({entry['resource']['status']})\") for entry in data.get('entry', [])]"

echo ""
echo "=== Verification Complete ==="
