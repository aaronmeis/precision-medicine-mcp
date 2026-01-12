# Ethics & Bias Framework - Implementation Plan

**Priority:** 1 (Colleague Feedback)
**Target Audiences:** Clinicians, Researchers
**Estimated Timeline:** 3-4 weeks
**Status:** Planning Phase

---

## Executive Summary

**Goal:** Add dedicated "Ethics & Bias" section to repository demonstrating how to audit precision medicine workflows for algorithmic bias across diverse populations.

**Why:** Trust is the primary barrier to clinical AI adoption. This framework aligns PatientOne demo with emerging global standards for ethical healthcare AI (WHO, FDA, EU AI Act).

**Current Gap:** Repository has strong HIPAA compliance and data privacy coverage, but lacks systematic approach to detecting and mitigating algorithmic bias in precision medicine.

---

## Scope

### What We're Adding

1. **Ethics & Bias Framework** - Comprehensive guide to ethical AI in precision medicine
2. **Bias Audit Methodology** - Step-by-step process for detecting bias
3. **PatientOne Bias Audit** - Concrete demonstration on existing workflow
4. **Bias Detection Tools** - Python utilities for ongoing monitoring
5. **Audit Checklist** - Practical checklist for clinicians/researchers

### What We're Auditing For

**Genomics Bias (Ancestral Populations):**
- BRCA1/BRCA2 variant interpretation: Are databases Euro-centric?
- Gene expression reference ranges: Do they account for ancestral variation?
- Pathway enrichment databases: Are they representative?
- Drug-gene interaction data: Tested in diverse genetic backgrounds?

**Clinical Bias (Socioeconomic Factors):**
- Insurance status: Does it influence treatment recommendations?
- Geographic location: Used as proxy for socioeconomic status?
- Race/ethnicity coding: Appropriate use (ancestry for genomics) vs. inappropriate (proxy for biology)?
- Language barriers: Are non-English speakers considered?

**Spatial Transcriptomics Bias:**
- Reference cell type signatures: From diverse populations?
- Deconvolution algorithms: Work equally well across tissue types?

**Multiomics Bias:**
- PDX models: Representative of patient populations?
- Drug sensitivity data: Diverse genetic backgrounds?

---

## Deliverables

### Phase 1: Core Documentation (Week 1)

#### 1. `docs/ethics/ETHICS_AND_BIAS.md` (~800 lines)

**Purpose:** Comprehensive ethical AI framework for precision medicine

**Sections:**
1. **Introduction** (100 lines)
   - Why ethics & bias matter in precision medicine
   - Trust as barrier to adoption
   - Legal/regulatory landscape
   - Relationship to HIPAA compliance

2. **Global Standards & Frameworks** (150 lines)
   - WHO Ethics and Governance of AI for Health (2021)
   - FDA AI/ML-Based Software as Medical Device (SaMD) guidance
   - EU AI Act (Regulation 2024/1689) - Medical AI as high-risk
   - ISO/IEC 23894:2023 AI Risk Management
   - NIH All of Us Research Program diversity requirements

3. **Types of Bias in Precision Medicine** (200 lines)
   - **Data bias**: Representation bias, selection bias, measurement bias
   - **Algorithmic bias**: Model training bias, feature selection bias
   - **Interpretation bias**: Clinical decision bias, confirmation bias
   - Examples specific to:
     * Genomics (variant calling, ancestry inference)
     * Spatial transcriptomics (cell type deconvolution)
     * Multiomics (pathway enrichment, drug target prediction)
     * Clinical data (treatment recommendations)

4. **Bias Audit Methodology** (200 lines)
   - **Step 1:** Data representation analysis
     * Demographic stratification
     * Ancestry distribution in genomic datasets
     * Geographic/socioeconomic coverage
   - **Step 2:** Algorithm fairness testing
     * Fairness metrics (demographic parity, equalized odds, calibration)
     * Performance stratification by subgroup
   - **Step 3:** Output stratification analysis
     * Treatment recommendations by demographic
     * Confidence intervals by subgroup
   - **Step 4:** Clinical validation
     * Expert review across populations
     * Real-world performance monitoring

5. **Fairness Metrics** (100 lines)
   - Demographic parity
   - Equalized odds (equal FPR/TPR across groups)
   - Calibration (predicted probabilities match observed rates)
   - Clinical utility parity (equal benefit across groups)
   - When to use which metric

6. **Transparency & Explainability** (100 lines)
   - Model explainability (SHAP values, feature importance)
   - Decision provenance (audit logs)
   - Uncertainty quantification
   - Disclaimers and limitations

7. **Mitigation Strategies** (100 lines)
   - Data augmentation for underrepresented groups
   - Fairness-aware training (fairness constraints)
   - Post-hoc calibration
   - Human-in-the-loop validation
   - Diverse reference datasets

8. **Continuous Monitoring** (50 lines)
   - Ongoing bias detection
   - Feedback loops
   - Model retraining criteria
   - Performance dashboards

---

#### 2. `docs/ethics/BIAS_AUDIT_CHECKLIST.md` (~300 lines)

**Purpose:** Practical checklist for conducting bias audits

**Sections:**

1. **Pre-Analysis Checklist** (100 lines)
   - [ ] Dataset demographics documented
   - [ ] Ancestral population representation >10% for each major group
   - [ ] Socioeconomic factors recorded (if applicable)
   - [ ] Reference databases reviewed for diversity
   - [ ] Model training data stratified by subgroup
   - [ ] Known limitations documented
   - [ ] IRB approval for bias analysis (if applicable)

2. **During Analysis Checklist** (100 lines)
   - [ ] Stratify results by ancestry/ethnicity
   - [ ] Stratify results by socioeconomic indicators
   - [ ] Check for performance disparities >10% between groups
   - [ ] Validate reference ranges across populations
   - [ ] Review feature importance for demographic proxies
   - [ ] Test edge cases in underrepresented groups
   - [ ] Document all stratified analyses

3. **Post-Analysis Checklist** (100 lines)
   - [ ] Bias metrics calculated and documented
   - [ ] Disparities >10% flagged for review
   - [ ] Mitigation strategies implemented (if bias found)
   - [ ] Results validated by domain experts
   - [ ] Audit report generated with findings
   - [ ] Recommendations incorporated into workflow
   - [ ] Continuous monitoring plan established

---

#### 3. `docs/ethics/PATIENTONE_BIAS_AUDIT.md` (~500 lines)

**Purpose:** Concrete demonstration of bias audit on PatientOne workflow

**Sections:**

1. **Overview** (50 lines)
   - PatientOne profile: 63-year-old woman, Stage IV HGSOC, platinum-resistant
   - Workflow scope: Genomics, spatial transcriptomics, multiomics, clinical data
   - Audit objectives: Identify potential biases, document findings, propose mitigations

2. **Genomics Bias Analysis** (150 lines)

   **2.1 BRCA1/BRCA2 Variant Interpretation**
   - **Data Source:** ClinVar, COSMIC databases
   - **Bias Check:** Are pathogenic variants primarily from European studies?
   - **PatientOne Finding:** BRCA1 variant (c.5266dupC) well-studied in European populations, limited data in others
   - **Potential Impact:** Pathogenicity classification may be less certain in non-European ancestries
   - **Mitigation:**
     * Flag variants with <5 studies in patient's ancestry
     * Recommend genetic counseling for ancestry-specific interpretation
     * Reference gnomAD for population-specific allele frequencies

   **2.2 Gene Expression Reference Ranges**
   - **Data Source:** GTEx (Genotype-Tissue Expression project)
   - **Bias Check:** GTEx is 85% European ancestry, 10% African, 5% other
   - **PatientOne Finding:** Differential expression analysis uses GTEx normal tissue baseline
   - **Potential Impact:** Reference ranges may not reflect true variation in underrepresented ancestries
   - **Mitigation:**
     * Document GTEx ancestry distribution in report
     * Consider ancestry-matched reference data when available
     * Apply larger thresholds (log2FC >2 instead of >1.5) for conservatism

   **2.3 Pathway Enrichment Databases**
   - **Data Source:** KEGG, Reactome, GO databases
   - **Bias Check:** Are pathway definitions universal or population-specific?
   - **PatientOne Finding:** Pathways based on aggregate human data, not population-stratified
   - **Potential Impact:** Pathway relevance may vary by ancestry
   - **Mitigation:**
     * Cross-validate with multiple databases (KEGG + Reactome + GO)
     * Flag pathways with >30% of genes showing ancestry-specific expression

3. **Clinical Bias Analysis** (150 lines)

   **3.1 Insurance Status & Treatment Recommendations**
   - **Data Source:** FHIR CoverageResource
   - **Bias Check:** Does insurance type affect treatment recommendations?
   - **PatientOne Finding:** Treatment recommendations based ONLY on molecular/clinical data (BRCA status, platinum resistance, tumor markers)
   - **Verification:** Removed `Coverage` resource from analysis prompts
   - **Result:** ✅ No insurance bias detected

   **3.2 Geographic & Socioeconomic Factors**
   - **Data Source:** FHIR Patient address
   - **Bias Check:** Is zip code used as proxy for treatment eligibility?
   - **PatientOne Finding:** Address used ONLY for healthcare provider coordination
   - **Verification:** Reviewed mcp-epic tool calls - no zip code filtering
   - **Result:** ✅ No geographic bias detected

   **3.3 Race/Ethnicity Coding**
   - **Data Source:** FHIR Patient.extension (US Core Race/Ethnicity)
   - **Bias Check:** Is race used appropriately?
   - **PatientOne Finding:**
     * Race/ethnicity recorded as "White/European ancestry"
     * Used for genomic variant interpretation (appropriate)
     * NOT used for treatment eligibility (appropriate)
   - **Best Practice:** Use ancestry for genomics, NOT race as biology
   - **Result:** ✅ Appropriate use confirmed

4. **Spatial Transcriptomics Bias Analysis** (100 lines)

   **4.1 Cell Type Reference Signatures**
   - **Data Source:** SingleR reference datasets
   - **Bias Check:** Are reference cell types from diverse tissues?
   - **PatientOne Finding:** Using generic immune cell references (pan-tissue)
   - **Potential Impact:** May miss ovarian cancer-specific cell states
   - **Mitigation:**
     * Use ovarian-specific reference when available (GSE146026)
     * Validate deconvolution with H&E pathology review

   **4.2 Spatial Autocorrelation Algorithms**
   - **Data Source:** Moran's I implementation
   - **Bias Check:** Does algorithm perform equally across tissue types?
   - **PatientOne Finding:** Moran's I is tissue-agnostic statistical method
   - **Result:** ✅ No tissue-specific bias

5. **Multiomics Bias Analysis** (50 lines)

   **5.1 PDX Model Representativeness**
   - **Data Source:** Xenograft PDX models
   - **Bias Check:** Are PDX models representative?
   - **PatientOne Finding:** PDX models are from diverse ovarian cancer patients
   - **Limitation:** PDX models may not capture immune microenvironment
   - **Mitigation:** Combine with patient's own spatial transcriptomics

6. **Summary & Recommendations** (50 lines)

   **Biases Detected:**
   1. BRCA variant databases: Euro-centric (MEDIUM risk)
   2. GTEx reference ranges: 85% European (MEDIUM risk)
   3. Cell type references: Generic, not cancer-specific (LOW risk)

   **Biases NOT Detected:**
   1. Insurance status: Not used in recommendations ✅
   2. Geographic location: Not used in treatment decisions ✅
   3. Race/ethnicity: Appropriately used for genomics only ✅

   **Recommendations:**
   1. Add ancestry diversity warnings to genomic reports
   2. Flag variants with limited non-European data
   3. Use ancestry-matched reference data when available
   4. Document reference database ancestry distributions
   5. Implement continuous monitoring for bias drift

---

### Phase 2: Bias Detection Tools (Week 2)

#### 4. `shared/utils/bias_detection.py` (~400 lines)

**Purpose:** Reusable Python utilities for bias detection

**Functions:**

```python
def check_dataset_representation(
    df: pd.DataFrame,
    demographic_col: str,
    min_representation: float = 0.10
) -> Dict[str, Any]:
    """
    Check if each demographic group has minimum representation.

    Args:
        df: DataFrame with data
        demographic_col: Column with demographic labels
        min_representation: Minimum fraction required (default 10%)

    Returns:
        {
            "underrepresented_groups": [...],
            "representation": {"group1": 0.45, "group2": 0.08, ...},
            "meets_threshold": True/False
        }
    """

def calculate_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray
) -> Dict[str, Dict[str, float]]:
    """
    Calculate fairness metrics stratified by group.

    Returns demographic parity, equalized odds, calibration.
    """

def flag_demographic_proxy_features(
    feature_importance: Dict[str, float],
    proxy_features: List[str]
) -> List[str]:
    """
    Flag if demographic proxy features (zip code, language, etc.)
    have high feature importance.
    """

def audit_reference_database_diversity(
    database_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Audit ancestry diversity in reference databases
    (e.g., ClinVar, GTEx, gnomAD).
    """

def stratify_results_by_group(
    results: pd.DataFrame,
    group_col: str,
    metrics: List[str]
) -> pd.DataFrame:
    """
    Stratify analysis results by demographic group.
    Calculate performance metrics per group.
    """
```

**Tests:** `tests/test_bias_detection.py` (~200 lines)

---

#### 5. `scripts/audit/audit_bias.py` (~300 lines)

**Purpose:** Standalone script to run bias audit on workflows

**Usage:**
```bash
# Audit PatientOne workflow
python scripts/audit/audit_bias.py \
  --workflow patientone \
  --genomics-data data/genomics/patient001.vcf \
  --clinical-data data/fhir/patient001.json \
  --output reports/bias_audit_patient001.html

# Audit with custom thresholds
python scripts/audit/audit_bias.py \
  --workflow patientone \
  --min-representation 0.15 \
  --max-disparity 0.10 \
  --output reports/bias_audit_custom.html
```

**Output:** HTML report with:
- Demographic representation summary
- Fairness metrics by group
- Flagged disparities
- Mitigation recommendations
- Visualizations (bar charts, heatmaps)

---

### Phase 3: Integration & Cross-References (Week 3)

#### 6. Update Existing Documentation

**6.1 Update `docs/hospital-deployment/HIPAA_COMPLIANCE.md`**
- Add new section: "§8. Ethical AI & Bias Mitigation"
- Cross-reference to `docs/ethics/ETHICS_AND_BIAS.md`
- Position ethics as complementary to privacy compliance

**6.2 Update `docs/hospital-deployment/OPERATIONS_MANUAL.md`**
- Add bias audit to monthly compliance checklist
- Include bias monitoring in incident response procedures

**6.3 Update `docs/hospital-deployment/ADMIN_GUIDE.md`**
- Add "Bias Audit Dashboard" to monitoring section
- Document how to run `audit_bias.py` script

**6.4 Update `docs/EXECUTIVE_SUMMARY.md`**
- Add "Ethical AI & Bias Mitigation" to key features
- Highlight alignment with WHO/FDA/EU AI Act standards
- Emphasize trust-building for clinical adoption

**6.5 Update `tests/manual_testing/PatientOne-OvarianCancer/README.md`**
- Add reference to PATIENTONE_BIAS_AUDIT.md
- Document expected findings and mitigations

**6.6 Update `architecture/README.md`**
- Add "Ethics & Bias Framework" to architecture overview
- Link to detailed documentation

---

### Phase 4: Validation & Reporting (Week 4)

#### 7. Run PatientOne Bias Audit

1. Execute `audit_bias.py` on PatientOne workflow
2. Generate comprehensive bias audit report
3. Document all findings (positive and negative)
4. Validate mitigations are effective

#### 8. Create Example Reports

- `reports/patientone_bias_audit_2026-01-12.html` - Full HTML report
- `reports/patientone_bias_summary.csv` - CSV with metrics
- `reports/patientone_bias_findings.md` - Markdown summary for docs

---

## Implementation Order

### Week 1: Core Documentation
**Day 1-2:** Write ETHICS_AND_BIAS.md (comprehensive framework)
**Day 3:** Write BIAS_AUDIT_CHECKLIST.md (practical checklist)
**Day 4-5:** Write PATIENTONE_BIAS_AUDIT.md (concrete demonstration)

### Week 2: Tools & Automation
**Day 1-2:** Implement `bias_detection.py` utilities
**Day 3:** Write tests for bias detection
**Day 4-5:** Create `audit_bias.py` script and test

### Week 3: Integration
**Day 1-2:** Update hospital deployment docs (HIPAA, OPERATIONS_MANUAL, ADMIN_GUIDE)
**Day 3:** Update EXECUTIVE_SUMMARY and architecture docs
**Day 4:** Update PatientOne README and test docs
**Day 5:** Review all cross-references for consistency

### Week 4: Validation
**Day 1-2:** Run bias audit on PatientOne, document findings
**Day 3:** Generate example reports
**Day 4:** Create summary documentation
**Day 5:** Final review and polish

---

## Success Criteria

1. ✅ Comprehensive ethics framework documented (ETHICS_AND_BIAS.md)
2. ✅ Practical audit checklist for clinicians/researchers
3. ✅ PatientOne workflow audited with concrete findings
4. ✅ Python utilities for ongoing bias detection
5. ✅ Standalone audit script with HTML report generation
6. ✅ Integration with existing compliance documentation
7. ✅ Alignment with global standards (WHO, FDA, EU AI Act)
8. ✅ Clear mitigations for identified biases
9. ✅ Transparency about limitations and data sources
10. ✅ Continuous monitoring framework established

---

## Open Questions for Review

1. **Scope:** Is the proposed scope comprehensive enough? Should we add more bias types?
2. **Tools:** Do we need real-time bias monitoring dashboards, or is batch auditing sufficient?
3. **Validation:** Should we get external review from ethics board or clinicians before finalizing?
4. **Reference Data:** Should we recommend specific diverse reference datasets (e.g., gnomAD, All of Us)?
5. **Automation:** Should bias audit be integrated into CI/CD pipeline as automated check?

---

## References

1. WHO Ethics and Governance of AI for Health (2021) - https://www.who.int/publications/i/item/9789240029200
2. FDA AI/ML-Based SaMD Action Plan (2021) - https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices
3. EU AI Act (Regulation 2024/1689) - https://artificialintelligenceact.eu/
4. ISO/IEC 23894:2023 AI Risk Management - https://www.iso.org/standard/77304.html
5. NIH All of Us Research Program - https://allofus.nih.gov/
6. Mehrabi et al., "A Survey on Bias and Fairness in Machine Learning" (2021)
7. Obermeyer et al., "Dissecting racial bias in an algorithm used to manage the health of populations" Science 2019

---

**Next Step:** Review this plan and provide feedback. Once approved, I'll begin implementation with Week 1 documentation.
