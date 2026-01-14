# Complete Workflow Prompts

End-to-end multi-modal precision medicine analyses.

**Servers used:** All 10 MCP servers

---

## PatientOne Complete Analysis

### 1. Comprehensive Multi-Modal Analysis (35 minutes)

```
Perform comprehensive multi-modal analysis for PatientOne (PAT001-OVC-2025)
to identify top 3 treatment targets:

STEP 1: Clinical Context (5 minutes)
- Get patient demographics from mcp-mockepic
- Extract diagnosis: Stage, histology, grade
- Review treatment history: Prior therapies and responses
- Key biomarkers: CA-125, BRCA status

STEP 2: Genomic Analysis (7 minutes)
- Load VCF file: /data/patient-data/PAT001-OVC-2025/genomic/variants.vcf
- Identify pathogenic variants in cancer genes: TP53, BRCA1, PIK3CA, PTEN
- Interpret clinical significance of each variant
- Map variants to pathways

STEP 3: Multi-Omics Integration (10 minutes)
- Load RNA, protein, phospho data from multiomics folder
- Run Stouffer meta-analysis for concordant changes
- Identify activated pathways (KEGG, Hallmark) with FDR < 0.05
- Find upstream regulators (kinases, transcription factors)

STEP 4: Spatial Transcriptomics (10 minutes)
- Load Visium data from spatial folder
- Perform spatial differential expression (tumor vs. normal)
- Run spatial pathway enrichment focusing on tumor regions
- Identify spatially variable genes (Moran's I, p < 0.05)
- Cell type deconvolution (tumor, stroma, immune)

STEP 5: Treatment Synthesis (3 minutes)
- Map activated pathways to FDA-approved drugs
- Prioritize by: Genomic evidence + Multi-omics + Spatial concordance
- Rank top 3 treatment options with rationale

RETURN: Structured report with:
- Clinical summary (1 paragraph)
- Key genomic findings (bullet list)
- Top 3 activated pathways (with p-values)
- Spatial heterogeneity summary
- Treatment recommendations (ranked 1-3 with evidence levels)
- Visualizations: Volcano plot, pathway heatmap, spatial map
```

**Expected Results:**
- **Clinical:** 58F, Stage IV HGSOC, platinum-resistant
- **Genomic:** TP53 mutated, BRCA1 germline variant
- **Pathways:** PI3K/AKT/mTOR (p=8.2e-5), DNA repair (p=1.3e-4)
- **Spatial:** Hypoxic core, immune exclusion
- **Recommendations:**
  1. Olaparib (PARP inhibitor) - BRCA1 variant
  2. Everolimus (mTOR inhibitor) - Pathway activation
  3. Pembrolizumab (Checkpoint inhibitor) - Immune edges

**Time:** 35 minutes
**Cost:** ~$87 (compute + API tokens)

---

## Research Workflows

### 2. Tumor Microenvironment Characterization

```
Characterize the tumor microenvironment for PatientOne:

STEP 1: Spatial Analysis
- Load Visium spatial data
- Identify tumor regions (T1 core, T2 edge) vs. normal (N1)
- Cell type deconvolution: Tumor, stroma, immune, hypoxic
- Spatial neighborhoods: Cluster spots by expression similarity

STEP 2: Cell-Cell Interactions
- Ligand-receptor analysis (tumor-stroma, tumor-immune)
- Identify communication pathways (VEGF, PD-L1/PD-1, TGF-β)
- Map interaction zones spatially

STEP 3: Immune Profiling
- Quantify immune infiltration (T-cells, macrophages)
- Identify immune-excluded vs. inflamed regions
- Check immune checkpoint expression (PD-L1, CTLA4, LAG3)

STEP 4: Imaging Integration
- Load H&E histology slide
- Correlate gene expression with histological features
- Validate cell type annotations with pathologist

RETURN:
- Microenvironment map (cell types, neighborhoods, interactions)
- Immune landscape summary (hot vs. cold vs. excluded)
- Therapeutic implications (immunotherapy candidates, combination strategies)
```

**Use Case:** Understanding treatment resistance, immunotherapy candidacy

---

### 3. Drug Resistance Mechanism Identification

```
Identify mechanisms of platinum resistance in PatientOne:

STEP 1: Genomic Resistance Markers
- Check for BRCA1/2 reversion mutations (restore HR)
- Drug efflux pumps: MDR1, MRP1 overexpression
- Cell cycle alterations: TP53, RB1 status

STEP 2: Multi-Omics Resistance Signatures
- Compare tumor pre-treatment vs. progression (if longitudinal)
- Identify upregulated resistance pathways:
  * Drug efflux
  * DNA repair restoration
  * EMT activation
  * Anti-apoptotic signaling

STEP 3: Spatial Heterogeneity
- Map resistance signatures spatially
- Identify resistant subclones (regional expression patterns)
- Check if resistance is uniform or focal

STEP 4: Treatment Bypass Strategies
- Activated pathways not targeted by platinum
- PI3K/AKT/mTOR, MAPK as escape routes
- Suggest combination therapies

RETURN:
- Resistance mechanisms identified (ranked by evidence)
- Spatial map of resistant regions
- Alternative treatment recommendations
```

**Use Case:** Second-line treatment selection, clinical trial matching

---

### 4. Biomarker Discovery Workflow

```
Discover prognostic/predictive biomarkers from PatientOne (as pilot):

STEP 1: Candidate Identification
- Multi-omics differential expression (responders vs. non-responders)
- Spatial biomarkers (immune infiltration, pathway scores)
- Genomic biomarkers (variants, mutational signatures)

STEP 2: Feature Selection
- Rank candidates by:
  * Effect size (fold change, odds ratio)
  * Statistical significance (FDR < 0.01)
  * Biological plausibility (known cancer roles)

STEP 3: Validation Planning
- Select top 10 candidates for validation
- Recommend validation cohort (TCGA ovarian cancer)
- Suggest assay platforms (IHC for protein, qPCR for RNA)

STEP 4: Clinical Utility Assessment
- ROC curves (sensitivity, specificity)
- Survival analysis (if outcome data available)
- Clinical decision curve analysis

RETURN:
- Top 10 biomarker candidates
- Validation plan with sample size calculations
- Clinical utility assessment framework
```

**Use Case:** Companion diagnostic development, patient stratification

---

### 5. Patient Stratification for Clinical Trial

```
Assess PatientOne's eligibility for precision oncology clinical trials:

STEP 1: Molecular Profile Summary
- Genomic: TP53 mutant, BRCA1 germline
- Pathways: PI3K/AKT/mTOR activated, DNA repair deficient
- Spatial: Immune-excluded tumor microenvironment
- Resistance: Platinum-resistant

STEP 2: Trial Matching
- Search ClinicalTrials.gov for:
  * BRCA-mutated ovarian cancer trials
  * PI3K/AKT/mTOR inhibitor trials
  * PARP inhibitor combinations
  * Immunotherapy + targeted therapy combinations

STEP 3: Eligibility Assessment
- Check inclusion criteria:
  * Stage IV HGSOC ✓
  * BRCA germline variant ✓
  * Platinum-resistant ✓
  * ECOG performance status (assume 0-1) ✓

STEP 4: Prioritization
- Rank trials by:
  * Molecular match score (how well profile fits)
  * Distance from patient location
  * Enrollment status (actively recruiting)

RETURN:
- Top 5 matching clinical trials
- Eligibility summary for each
- Contact information for trial coordinators
```

**Use Case:** Clinical trial enrollment, precision treatment access

---

## Educational Workflows

### 6. PatientOne Teaching Case (25 minutes, $0.32)

```
DRY_RUN MODE: Complete PatientOne analysis for classroom demonstration.

STEP 1: Clinical Review (3 min)
- Review FHIR data (demographics, diagnosis, treatment)
- Identify key clinical questions

STEP 2: Genomic Analysis (5 min)
- Analyze VCF for TP53, BRCA1 variants
- Interpret clinical significance

STEP 3: Multi-Omics Quick Analysis (7 min)
- Load RNA, protein data
- Run differential expression
- Pathway enrichment (top 3 pathways)

STEP 4: Spatial Overview (7 min)
- Load Visium data
- Spatial DE and pathway enrichment
- Visualize on tissue

STEP 5: Treatment Summary (3 min)
- Synthesize findings
- Generate 3 treatment recommendations

RETURN: Student-friendly report (suitable for presentation)
```

**Use Case:** Undergraduate/graduate courses, workshops

---

## Troubleshooting Workflows

### 7. Diagnostic Workflow for Failed Analysis

```
If previous analysis failed, run diagnostic workflow:

STEP 1: Data Availability Check
- List all available files for patient
- Verify file formats (VCF valid? CSV readable?)
- Check file sizes (empty files?)

STEP 2: Server Status Check
- Test each MCP server individually
- Check which tools are available
- Verify DRY_RUN mode status

STEP 3: Parameter Validation
- Verify patient ID is correct
- Check file paths exist
- Confirm thresholds are reasonable (FDR < 0.05 standard)

STEP 4: Incremental Analysis
- Start with simplest analysis (load data)
- Add complexity step by step
- Identify where failure occurs

STEP 5: Error Interpretation
- Parse error messages for actionable info
- Check common issues:
  * File not found → path typo
  * No significant results → threshold too strict
  * Server timeout → analysis too complex, break into steps

RETURN: Diagnostic report with recommended fixes
```

**Use Case:** Debugging, user support

---

## Validation Workflows

### 8. Cross-Platform Validation

```
Validate PatientOne results against external data:

STEP 1: Internal Validation
- Compare RNA-seq to protein (concordance check)
- Spatial vs. bulk RNA (regional vs. average)
- Multiple pathway databases (KEGG, Hallmark, GO)

STEP 2: Literature Validation
- Top findings (TP53, BRCA1, PI3K pathway)
- Compare to published HGSOC studies
- Check expected prevalence (TP53 in 96% of HGSOC)

STEP 3: Cohort Validation
- Query TCGA ovarian cancer cohort (mcp-tcga)
- Compare PatientOne pathway activation to cohort
- Identify if patient is typical or outlier

STEP 4: Cross-Method Validation
- Confirm protein with IHC (if available)
- Validate spatial patterns with H&E histology
- Cross-check variants with orthogonal sequencing

RETURN: Validation report (concordance scores, literature support, cohort comparison)
```

**Use Case:** Quality assurance, publication preparation

---

## Time-Saving Workflows

### 9. Quick Screening Workflow (10 minutes)

```
Quick PatientOne screening for triaging:

STEP 1: Genomic Quick Screen (3 min)
- Load VCF, check key genes only: TP53, BRCA1, BRCA2, PIK3CA
- Flag: Pathogenic variants YES/NO

STEP 2: Pathway Quick Screen (4 min)
- Load RNA data only (skip protein/phospho)
- Run pathway enrichment (KEGG only, top 5)
- Flag: Druggable pathways YES/NO

STEP 3: Spatial Quick Look (3 min)
- Load spatial data
- Cell type deconvolution (tumor % , immune %)
- Flag: Immune-infiltrated YES/NO

RETURN: Triage decision (High priority / Standard / Low priority for detailed analysis)
```

**Use Case:** High-throughput screening, resource allocation

---

### 10. Update Analysis with New Data

```
PatientOne has new post-treatment biopsy. Update analysis:

STEP 1: Load New Data
- New VCF (check for new mutations)
- New spatial data (compare tumor evolution)

STEP 2: Comparative Analysis
- Pre-treatment vs. Post-treatment
- What changed? (new mutations, pathway shifts, spatial reorganization)

STEP 3: Resistance Analysis
- Identify acquired resistance mechanisms
- Check for target loss, pathway bypass, microenvironment changes

STEP 4: Revised Treatment Plan
- Update recommendations based on new molecular state
- Suggest next-line therapies

RETURN: Updated report (changes highlighted, revised recommendations)
```

**Use Case:** Longitudinal monitoring, treatment adaptation

---

## Quality Metrics

**For any workflow, track:**
- Time to completion (target: < 60 min for comprehensive)
- Cost (target: < $100)
- Number of significant findings
- Clinical actionability (% findings with drug implications)
- Reproducibility (re-run should give identical results)

---

**Related Prompts:**
- [Clinical-Genomic](clinical-genomic.md)
- [Multi-Omics](multiomics.md)
- [Spatial Transcriptomics](spatial-transcriptomics.md)

---

**Last Updated:** 2026-01-14
