# Testing mcp-epic in Claude Desktop

## ✅ Configuration Complete!

The mcp-epic server has been added to your Claude Desktop configuration and is ready to test with **real patient data** from GCP Healthcare API.

---

## 🔄 Step 1: Restart Claude Desktop

**IMPORTANT:** You must restart Claude Desktop for the new server to load.

1. Quit Claude Desktop completely (⌘+Q on Mac)
2. Relaunch Claude Desktop
3. Wait for it to fully start

---

## 🧪 Step 2: Test the Tools

Once Claude Desktop restarts, you can test the 4 FHIR tools with real patient data. Copy and paste these prompts one at a time:

### Test 1: Patient Demographics (De-identified)

```
Get patient demographics for patient-001 using the epic server
```

**Expected Result:**
- De-identified patient ID (hashed)
- Gender: female
- Birth year: 1968 (not full date)
- NO personal identifiers (name, address, phone removed)
- De-identification metadata showing HIPAA Safe Harbor method

---

### Test 2: Patient Conditions

```
Get patient conditions for patient-001 using the epic server
```

**Expected Result:**
- 1 condition found
- Stage IV High-Grade Serous Ovarian Carcinoma (HGSOC), Platinum-Resistant
- Clinical details preserved
- Patient references de-identified

---

### Test 3: Patient Observations (Lab Results)

```
Get patient observations for patient-001 using the epic server
```

**Expected Result:**
- 2 observations found:
  1. **BRCA1/2 Mutation Analysis**: Negative (no pathogenic variants)
  2. **CA-125**: 487 U/mL (critically high)
- Clinical values preserved
- Dates reduced to year only

---

### Test 4: Patient Medications

```
Get patient medications for patient-001 using the epic server
```

**Expected Result:**
- 3 medications found:
  1. **Bevacizumab (Avastin)** - Status: active (current treatment)
  2. **Paclitaxel** - Status: completed (first-line therapy)
  3. **Carboplatin** - Status: completed (first-line therapy)
- Treatment dates shown as year only
- Medication details preserved

---

## 🔍 Step 3: Verify De-identification

After running the tools, verify that:

✅ **PHI Removed:**
- No patient names
- No addresses
- No phone numbers
- No full dates (only years)
- Patient IDs are hashed

✅ **Clinical Data Preserved:**
- Diagnosis details intact
- Lab values accurate
- Medication information complete
- Gender and birth year retained

✅ **De-identification Metadata:**
- `_deidentified: true` flag present
- `_deidentification_method: "HIPAA Safe Harbor"` specified

---

## 🎯 Advanced Testing

### Test with Category Filter

```
Get laboratory observations for patient-001 using the epic server with category "laboratory"
```

### Test Combined Analysis

```
For patient-001, get their demographics, conditions, and current medications using the epic server. Then summarize their clinical status.
```

---

## 📊 What You're Testing

This demonstrates:
- ✅ Real FHIR data retrieval from GCP Healthcare API
- ✅ HIPAA-compliant de-identification
- ✅ MCP tool integration in Claude Desktop
- ✅ End-to-end precision medicine data pipeline

---

## 🐛 Troubleshooting

### Server Not Loading
- Check Claude Desktop logs: `~/Library/Logs/Claude/`
- Look for mcp-server-epic.log
- Verify environment variables are set correctly

### Authentication Errors
- Ensure service account key exists: `/Users/lynnlangit/Documents/GitHub/spatial-mcp/infrastructure/deployment/mcp-server-key.json`
- Check GCP permissions (should have healthcare.fhirResourceReader role)

### No Data Returned
- Verify patient-001 exists in FHIR store
- Check FHIR_STORE environment variable points to "identified-fhir-store"

---

## 📝 Next Steps After Testing

Once testing is complete, you can:
1. Add more patient data to the FHIR store
2. Connect spatial analysis (mcp-spatialtools) with clinical data
3. Build end-to-end analysis workflows
4. Deploy to hospital infrastructure

---

**Ready to test?** Restart Claude Desktop and try the prompts above! 🚀
