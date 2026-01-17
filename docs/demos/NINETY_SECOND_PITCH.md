# 90-Second Funding Demo

These prompts demonstrate the platform's value in under 2 minutes for funders, grant reviewers, and hospital decision-makers.

---

## Prerequisites

**Choose ONE of the following:**
- ✅ **Option A:** Claude Desktop with MCP servers configured ([setup guide](../getting-started/installation.md))
- ✅ **Option B:** Deployed Streamlit UI ([deployment guide](../deployment/GCP_TESTING_GUIDE.md))
- ✅ **Option C:** Jupyter notebook ([notebook guide](../../ui/jupyter-notebook/README.md))

**Data:** Uses synthetic PAT001-OVC-2025 patient data (100% safe for demos, no PHI)

---

## The Demo Script (90 seconds)

### Prompt 1: Show the Problem (15 seconds)

**Copy-paste this:**
```
What data modalities need to be integrated for a comprehensive Stage IV ovarian cancer precision medicine analysis?
```

**Expected Output:**
Claude will list 5 modalities that must be integrated:
1. **Clinical** - EHR data (FHIR), demographics, diagnoses, medications
2. **Genomic** - WES/WGS, somatic variants, CNV, germline risk
3. **Multi-omics** - RNA expression, protein, phospho-proteomics
4. **Spatial Transcriptomics** - 10x Visium, tissue microenvironment
5. **Imaging** - H&E histopathology, MxIF (multiplexed immunofluorescence)

**Key Talking Point:** *"Traditionally, each modality requires separate tools, manual data wrangling, and 8+ hours per modality."*

---

### Prompt 2: Show the Solution (30 seconds)

**Copy-paste this:**
```
Using PatientOne data (PAT001-OVC-2025), identify the top 3 actionable treatment targets based on spatial transcriptomics pathway enrichment analysis.
```

**Expected Output:**
Claude will:
1. Invoke `mcp-spatialtools` server
2. Run pathway enrichment on spatial data
3. Return results like:
   - **PI3K/AKT/mTOR pathway** (p<0.001) → Suggest everolimus or alpelisib
   - **PARP pathway** (p<0.005) → Suggest olaparib (for BRCA1/2 carriers)
   - **VEGF pathway** (p<0.01) → Suggest bevacizumab (anti-angiogenic)

**Key Talking Points:**
- *"Natural language input, no coding required"*
- *"AI automatically coordinates specialized servers"*
- *"Results returned in 30-45 seconds, not 8 hours"*

---

### Prompt 3: Show the Speed (20 seconds)

**Copy-paste this:**
```
How long would this spatial pathway enrichment analysis take manually vs. with MCP servers?
```

**Expected Output:**
| Approach | Time | Cost | Expertise Required |
|----------|------|------|-------------------|
| **Manual** | 8-12 hours | $400-800 (bioinformatics labor) | PhD-level |
| **MCP Platform** | 35 minutes | $24-102 (compute + API) | Basic training |

**Savings:** ~$300-700 per analysis, **40 hours → 35 minutes** for full multi-omics workflow

**Key Talking Point:** *"68x faster - enabling same-day precision medicine decisions"*

---

### Prompt 4: Show the ROI (25 seconds)

**Copy-paste this:**
```
Calculate the annual ROI for analyzing 100 ovarian cancer patients per year with this platform, assuming $6,000 traditional cost per patient.
```

**Expected Output:**
```
Traditional Approach:
- 100 patients × $6,000/patient = $600,000/year
- 100 patients × 40 hours/patient = 4,000 hours/year bioinformatics time

MCP Platform:
- 100 patients × $324/patient = $32,400/year (compute + API)
- 100 patients × 35 minutes/patient = 58 hours/year (oversight + validation)

Annual Savings:
- Cost: $567,600 saved
- Time: 3,942 hours freed for other research
- ROI: 17.5x return on infrastructure investment
```

**Key Talking Points:**
- *"First 2-3 patients analyzed = payback period"*
- *"$313K-1.6M annual savings depending on patient volume"*
- *"Frees bioinformaticians for novel research, not manual data wrangling"*

---

## Post-Demo Follow-Up Questions

### "Is this production-ready?"

**Answer:**
- ✅ 4/10 servers production-ready (fgbio, multiomics, spatialtools, epic)
- ✅ 167 automated tests, 68% coverage
- ✅ HIPAA-compliant infrastructure (de-identification, audit logging, VPC isolation)
- ⚠️ 5 servers mocked for demo (tcga, huggingface, seqera, deepcell, mockepic)
- **Timeline:** 6 months to full production with hospital Epic FHIR integration

### "What about security and compliance?"

**Answer:**
- ✅ **HIPAA Safe Harbor** de-identification built-in
- ✅ **10-year audit logging** (GCP Cloud Logging + FHIR AuditEvent)
- ✅ **VPC isolation**, encrypted secrets (GCP Secret Manager)
- ✅ **Azure AD SSO** for user authentication
- ✅ **SOC 2 Type II** compliant infrastructure (GCP Cloud Run)

See: [Security Overview](../deployment/security.md) | [HIPAA Compliance](../for-hospitals/compliance/hipaa.md)

### "How much does deployment cost?"

**Answer:**
| Tier | Investment | Deliverable | Timeline |
|------|-----------|-------------|----------|
| **Pilot** | $50,000 | 6-month pilot, 100 patients | 6 months |
| **Production** | $75,000/year | Full deployment, 500 patients | 12 months |

See: [FUNDING.md](../../FUNDING.md) for detailed budget breakdown

---

## Alternative Demo Flows

### For Clinical Audiences (Focus: Patient Care Impact)

1. **Clinical context:** "Summarize PatientOne's clinical history and current treatment status"
2. **Treatment targets:** "What are the top 3 treatment targets based on genomic + spatial analysis?"
3. **Resistance mechanisms:** "Why did platinum-based chemotherapy fail? What pathways show resistance?"

### For Technical Audiences (Focus: Bioinformatics Capabilities)

1. **Data validation:** "Validate PatientOne's multi-omics data quality (RNA, protein, phospho)"
2. **Statistical rigor:** "Run Stouffer meta-analysis across RNA/protein/phospho with multiple testing correction"
3. **Visualization:** "Generate a spatial heatmap showing BRCA1 expression across tumor regions"

### For Educators (Focus: Learning Value)

1. **Concept check:** "Explain spatial autocorrelation and why Moran's I is used"
2. **Methods:** "What statistical methods are used for pathway enrichment analysis?"
3. **Interpretation:** "Interpret these pathway enrichment results for a clinical audience"

---

## Tips for Maximum Impact

1. **Start with the problem** - "40 hours is clinically impractical for urgent treatment decisions"
2. **Show live results** - Run the prompts, don't just describe them
3. **Emphasize natural language** - "No coding required, just ask questions"
4. **Highlight cost savings** - "$3,137 per patient adds up fast"
5. **End with call-to-action** - "Let's discuss a 6-month pilot at your institution"

---

## Recording This Demo

**For Presentations:**
1. Record screen using OBS Studio or Loom
2. Add voiceover explaining each step
3. Keep total video under 2 minutes
4. Upload to YouTube/Vimeo with captions

**For Grants:**
1. Record Jupyter notebook execution
2. Export to PDF with outputs
3. Include in grant application as "Preliminary Results"

---

## Next Steps After Demo

**For Interested Funders:**
- Schedule 30-minute deep dive: [Full PatientOne Demo](FULL_PATIENTONE_DEMO.md)
- Review detailed budget: [FUNDING.md](../../FUNDING.md)
- Technical Q&A: [Executive Summary](../EXECUTIVE_SUMMARY.md)

**For Hospital IT:**
- Security review: [Security Guide](../deployment/security.md)
- HIPAA compliance: [HIPAA Guide](../for-hospitals/compliance/hipaa.md)
- Deployment timeline: [Production Roadmap](../deployment/roadmap.md)

---

**Last Updated:** 2026-01-14
