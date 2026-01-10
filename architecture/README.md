# Precision Medicine MCP Servers

See each subfolder for architectures. See also main Repo README.md for list of tools for each custom MCP server

**⚠️ Important:** Not all servers are production-ready. Check [Server Implementation Status](../docs/SERVER_IMPLEMENTATION_STATUS.md) before using for research or production.

## Architecture Workflows

### 1) Multiomics (custom mcp servers + tools)

**Purpose:** PDX multi-omics data integration with preprocessing, association testing, and therapeutic target prediction

```
┌─────────────────────────────────────────────────────────────────────────┐
│         MULTIOMICS WORKFLOW ARCHITECTURE (10 tools)                      │
│         Enhanced with bioinformatician feedback (2025)                   │
└─────────────────────────────────────────────────────────────────────────┘

                         Claude Desktop (MCP Host)
                                    │
                    ┌───────────────┼───────────────┐
                    │                               │
                    ▼                               ▼
         ┌──────────────────────┐        ┌──────────────────────┐
         │  mcp-multiomics      │        │  mcp-epic            │
         │  ─────────────────   │        │  ───────────────     │
         │  PREPROCESSING:      │        │  • Patient Data      │
         │  • Validate Data ⭐  │        │  • Clinical Metadata │
         │  • Batch Correction  │        │  • Batch Info        │
         │  • KNN Imputation    │        └──────────────────────┘
         │  • QC Visualization  │
         │                      │
         │  ANALYSIS:           │
         │  • Data Integration  │
         │  • HAllA (chunked)   │
         │  • Stouffer's Meta   │
         │  • Upstream Regs ⭐  │
         │  • Visualizations    │
         └──────────┬───────────┘
                    │
    ┌───────────────┼───────────────────────┐
    │               │                       │
    ▼               ▼                       ▼
┌────────┐    ┌──────────┐         ┌────────────┐
│  RNA   │    │ Protein  │         │  Phospho   │
│  Data  │    │   Data   │         │    Data    │
│ (raw)  │    │ (raw)    │         │   (raw)    │
└────────┘    └──────────┘         └────────────┘
    │               │                       │
    │  STEP 1: VALIDATE (batch effects, missing values)
    └───────────────┼───────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Data Validation ⭐ │
         │  • Batch detection  │
         │  • Missing patterns │
         │  • Outliers         │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Preprocessing ⭐   │
         │  • ComBat batch cor │
         │  • KNN imputation   │
         │  • Normalization    │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  QC Visualization ⭐│
         │  • PCA before/after │
         │  • Verify batch fix │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Data Integration   │
         │  • Align samples    │
         │  • Normalize        │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  HAllA Analysis     │
         │  • Chunked (1000)   │
         │  • NOMINAL p-values │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Stouffer's Meta    │
         │  • Combine p-values │
         │  • FDR AFTER ✓      │
         │  • Directionality   │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Upstream Regs ⭐   │
         │  • Kinases          │
         │  • TFs              │
         │  • Drug targets     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   Visualization     │
         │  • Heatmaps         │
         │  • PCA plots        │
         │  • Pathway results  │
         └─────────────────────┘

Key Features:
  ⭐ NEW: Preprocessing pipeline (validate → preprocess → visualize)
  ⭐ NEW: Upstream regulator prediction (IPA-like kinase/TF/drug analysis)
  • Enhanced HAllA with chunking (1000 features/chunk = ~5 min vs days)
  • Correct FDR workflow (applied AFTER Stouffer's combination)
  • Integrates RNA, Protein, Phosphorylation data
  • Statistical meta-analysis across modalities
  • Identifies multi-modal resistance signatures & therapeutic targets
  • Suitable for clinical PDX treatment response studies
```

### 2) Spatial (custom mcp servers + tools)

**Purpose:** Spatial transcriptomics bioinformatics pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│               SPATIAL TRANSCRIPTOMICS WORKFLOW ARCHITECTURE              │
└─────────────────────────────────────────────────────────────────────────┘

                         Claude Desktop (MCP Host)
                      AI-Orchestrated Workflow Execution
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼──────────┐    ┌──────────▼─────────┐    ┌───────────▼────────┐
│  STAGE 1:        │    │   STAGE 2:         │    │   STAGE 3:         │
│  Data Ingestion  │───▶│   Spatial          │───▶│   Sequence         │
│  & QC            │    │   Segmentation     │    │   Alignment        │
└──────────────────┘    └────────────────────┘    └────────────────────┘
│ • mcp-fgbio      │    │ • mcp-spatialtools │    │ • mcp-fgbio        │
│   - validate_    │    │   - split_by_      │    │   - fetch_ref      │
│     fastq        │    │     region         │    │ • mcp-spatialtools │
│   - extract_     │    │ • mcp-openimagedata│    │   - align_spatial  │
│     umis         │    │   - fetch_         │    │ • mcp-seqera       │
│ • mcp-spatial    │    │     histology      │    │   - launch_nf      │
│   - filter_      │    │   - register_      │    │                    │
│     quality      │    │     image          │    │ Output: BAM files  │
│                  │    │                    │    │         w/ spatial │
│ Input: FASTQ +   │    │ Output: Segmented  │    │         tags       │
│        barcodes  │    │         regions    │    │                    │
└──────────────────┘    └────────────────────┘    └────────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼──────────┐    ┌──────────▼─────────┐                │
│  STAGE 4:        │    │   STAGE 5:         │                │
│  Expression      │───▶│   Analysis &       │                │
│  Quantification  │    │   Integration      │                │
└──────────────────┘    └────────────────────┘                │
│ • mcp-spatialtools│   │ • mcp-seqera       │                │
│   - count_umis    │   │   - run_rnaseq     │                │
│ • mcp-deepcell    │   │ • mcp-huggingface  │                │
│   - segment_cells │   │   - predict_cell   │                │
│ • mcp-huggingface │   │     _type          │                │
│   - embed_        │   │ • mcp-mockepic     │                │
│     sequences     │   │   - link_spatial   │                │
│                   │   │ • mcp-tcga         │                │
│ Output: Gene x    │   │   - compare_to     │                │
│         Spot/Cell │   │     _tcga          │                │
│         matrix    │   │                    │                │
│                   │   │ Output: Analysis   │                │
│                   │   │         results,   │                │
│                   │   │         reports    │                │
└───────────────────┘   └────────────────────┘                │
                                    │                          │
                                    ▼                          │
                        ┌────────────────────┐                 │
                        │  Final Deliverable │                 │
                        │  ────────────────  │                 │
                        │  • Spatial maps    │                 │
                        │  • Differential    │                 │
                        │    expression      │                 │
                        │  • Cell types      │                 │
                        │  • Visualizations  │                 │
                        └────────────────────┘                 │
                                                               │
┌──────────────────────────────────────────────────────────────┘
│  MCP Servers Used (8):
│  ├─ mcp-fgbio          (Reference data, FASTQ validation)
│  ├─ mcp-tcga           (Cancer genomics reference)
│  ├─ mcp-spatialtools   (Core spatial processing)
│  ├─ mcp-huggingface    (ML models)
│  ├─ mcp-epic           (Clinical data)
│  ├─ mcp-openimagedata  (Histology images)
│  ├─ mcp-seqera         (Workflow orchestration)
│  └─ mcp-deepcell       (Cell segmentation)
└──────────────────────────────────────────────────────────────┘

Key Features:
  • End-to-end FASTQ → Analysis pipeline
  • Spatial coordinate preservation throughout
  • Integration with histology images
  • AI-assisted cell type identification
  • Comparison to TCGA reference cohorts
```

### 3) PatientOne (combine spatial + multiomics mcp servers) - end-to-end use case

**Purpose:** Comprehensive precision medicine analysis (Stage IV Ovarian Cancer)

```
┌─────────────────────────────────────────────────────────────────────────┐
│            PATIENTONE END-TO-END WORKFLOW ARCHITECTURE                   │
│              (Stage IV Ovarian Cancer Use Case)                          │
└─────────────────────────────────────────────────────────────────────────┘

                         Claude Desktop (MCP Host)
                  Complete Precision Medicine Workflow Orchestration
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        │                           │                           │
┌───────▼──────────┐    ┌──────────▼─────────┐    ┌───────────▼────────┐
│  CLINICAL DATA   │    │   GENOMIC DATA     │    │  MULTIOMICS DATA   │
│  ──────────────  │    │   ────────────     │    │  ──────────────    │
│                  │    │                    │    │                    │
│ mcp-epic         │    │ mcp-fgbio          │    │ mcp-multiomics     │
│ • Demographics   │    │ • FASTQ validation │    │ • RNA-seq (PDX)    │
│ • CA-125 trends  │    │ • VCF processing   │    │ • Proteomics       │
│ • Treatment Hx   │    │                    │    │ • Phosphoproteomics│
│                  │    │ mcp-tcga           │    │ • Integration      │
│ Output:          │    │ • TCGA comparison  │    │ • Stouffer's meta  │
│ • Patient profile│    │ • Mutation data    │    │                    │
│ • Clinical       │    │                    │    │ Output:            │
│   context        │    │ Output:            │    │ • Resistance genes │
│                  │    │ • Mutations        │    │ • Pathway analysis │
│                  │    │   (TP53, BRCA1,    │    │ • Multi-modal      │
│                  │    │    PIK3CA)         │    │   signatures       │
│                  │    │ • TCGA subtype     │    │                    │
└──────────────────┘    └────────────────────┘    └────────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼──────────┐    ┌──────────▼─────────┐    ┌───────────▼────────┐
│  SPATIAL DATA    │    │   IMAGING DATA     │    │  ANALYSIS & Rx     │
│  ────────────    │    │   ────────────     │    │  ─────────────     │
│                  │    │                    │    │                    │
│ mcp-spatialtools │    │ mcp-openimagedata  │    │ Integration of     │
│ • Visium data    │    │ • H&E (brightfield)│    │ ALL data streams   │
│ • 900 spots      │    │   - Morphology     │    │                    │
│ • 31 genes       │    │   - Necrosis ID    │    │ • Treatment        │
│ • 6 regions      │    │ • MxIF (fluoresc.) │    │   recommendations  │
│                  │    │   - Load channels  │    │ • Pathway targets  │
│ • Spatial        │    │   - Compositing    │    │   (PI3K/AKT/mTOR)  │
│   heterogeneity  │    │                    │    │ • Clinical trials  │
│ • Immune         │    │ mcp-deepcell       │    │ • Monitoring plan  │
│   localization   │    │ • MxIF segmentation│    │                    │
│                  │    │   (fluoresc. only) │    │ • Synthetic results│
│ Output:          │    │ • Cell counting    │    │   across all       │
│ • Expression     │    │   (CD8, Ki67)      │    │   modalities       │
│   maps           │    │                    │    │                    │
│ • Region         │    │ Output:            │    │                    │
│   analysis       │    │ • Immune infiltrate│    │                    │
└──────────────────┘    └────────────────────┘    └────────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  PRECISION MEDICINE       │
                    │  RECOMMENDATIONS          │
                    │  ───────────────────────  │
                    │                           │
                    │  Molecular Profile:       │
                    │  • TP53 R175H (hotspot)   │
                    │  • BRCA1 germline mut     │
                    │  • PIK3CA E545K (resist)  │
                    │                           │
                    │  Resistance Mechanisms:   │
                    │  • PI3K/AKT activation    │
                    │  • MDR1 upregulation      │
                    │  • Anti-apoptotic signals │
                    │                           │
                    │  Treatment Recommendations│
                    │  • PI3K inhibitors        │
                    │    (alpelisib)            │
                    │  • AKT inhibitors         │
                    │    (capivasertib)         │
                    │  • mTOR inhibitors        │
                    │  • Clinical trials        │
                    │                           │
                    │  Monitoring Strategy:     │
                    │  • CA-125 every 3 weeks   │
                    │  • Imaging every 6 weeks  │
                    │  • PDX model validation   │
                    └───────────────────────────┘

**Key Imaging Workflow Distinction:**

**H&E (Hematoxylin & Eosin):**
- Brightfield microscopy with chromogenic stains (NOT fluorescence)
- Server: mcp-openimagedata only
- Purpose: Morphology assessment, necrosis identification, cellularity estimation
- No cell segmentation required for PatientOne workflow (visual assessment)

**MxIF (Multiplexed Immunofluorescence):**
- Fluorescence microscopy with multiple antibody markers
- Servers: mcp-openimagedata (loading, compositing) → mcp-deepcell (segmentation)
- Purpose: Quantitative cell phenotyping (CD8+ T cells, Ki67+ proliferation, TP53 expression)
- DeepCell uses the open-source DeepCell-TF library for AI-based cell segmentation
- Enables single-cell spatial analysis with multiple marker co-expression

┌──────────────────────────────────────────────────────────────────────────┐
│  ALL 10 MCP Servers:                                                     │
│  ├─ mcp-epic           (Real Epic FHIR - local only)                    │
│  ├─ mcp-mockepic       (Mock EHR - deployed to GCP)                     │
│  ├─ mcp-fgbio          (Genomic QC & validation)                        │
│  ├─ mcp-tcga           (TCGA cohort comparison)                         │
│  ├─ mcp-multiomics     (PDX multi-omics integration)                    │
│  ├─ mcp-spatialtools   (Spatial transcriptomics)                        │
│  ├─ mcp-openimagedata  (Histology imaging)                              │
│  ├─ mcp-deepcell       (AI cell segmentation)                           │
│  ├─ mcp-seqera         (Workflow orchestration)                         │
│  └─ mcp-huggingface    (ML model inference)                             │
│                                                                           │
│  Note: mcp-epic runs locally for hospital production with real Epic     │
│        FHIR. mcp-mockepic runs on GCP for demos with synthetic data.    │
│                                                                           │
│  Synthetic Data (17 files):                                              │
│  • Clinical: 2 files (demographics, labs)                                │
│  • Genomics: 1 file (VCF with mutations)                                 │
│  • Multiomics: 4 files (RNA/Protein/Phospho + metadata)                  │
│  • Spatial: 3 files (coordinates, expression, annotations)               │
│  • Imaging: 7 files (H&E, IF markers, multiplex)                         │
│                                                                           │
│  Test Location: /tests/manual_testing/PatientOne-OvarianCancer/          │
└──────────────────────────────────────────────────────────────────────────┘

Key Features:
  • Complete precision medicine workflow
  • Synthetic patient: PAT001-OVC-2025 (58yo, Stage IV HGSOC)
  • Integration of 5 data modalities
  • Resistance mechanism identification
  • Treatment recommendations based on molecular profile
  • Demonstrates all MCP servers working together
```

---

## 📖 Operations & Deployment Documentation

For deployment, testing, and production operations, see:

- **[Server Implementation Status](../docs/SERVER_IMPLEMENTATION_STATUS.md)** - Production readiness matrix for all 10 servers
- **[GCP Cloud Run Deployment](../docs/deployment/DEPLOYMENT_STATUS.md)** - Current deployment state (9 servers on GCP)
- **[Hospital Deployment Guide](../docs/hospital-deployment/)** - HIPAA-compliant production setup
- **[Cost Analysis](../docs/operations/COST_ANALYSIS.md)** - Token costs, compute estimates, ROI analysis
- **[Testing Guide](../docs/testing/GCP_SERVER_TEST_PLAN.md)** - Automated testing procedures

---

**See subfolder READMEs for detailed architecture documentation:**
- `multiomics/README.md` - Multiomics server architecture (TEST_2)
- `spatial-transcriptomics/README.md` - Spatial transcriptomics pipeline architecture (TEST_3)
- `imaging/README.md` - Imaging analysis architecture (TEST_4)
- `patient-one/README.md` - PatientOne end-to-end use case (TEST_1-5)

---

**Last Updated:** 2026-01-10
**Status:** Architecture documentation complete for 10 MCP servers

**⚠️ Note on Tool References:** ASCII diagrams above may show abbreviated tool names. For complete tool counts from source code:

| Server | Tools | Implementation Status |
|--------|-------|----------------------|
| **mcp-fgbio** | **4** | 95% real - Reference genome, FASTQ validation, UMI extraction, gene annotations |
| **mcp-multiomics** | **10** | 85% real - Integration, validation, preprocessing, HAllA, Stouffer, upstream regulators, visualizations, cost estimation |
| **mcp-spatialtools** | **14** | 95% real - 10 analysis + 4 visualization tools (batch correction, pathway enrichment, spatial autocorrelation, cell deconvolution) |
| **mcp-tcga** | **5** | 0% mocked - TCGA cohort queries, expression data, survival data, mutation data |
| **mcp-openimagedata** | **5** | 60% real - Image loading, multiplex composite, H&E annotation (3 real); registration, feature extraction (2 mocked) |
| **mcp-deepcell** | **4** | 0% mocked - Cell segmentation, phenotype classification, overlay generation |
| **mcp-seqera** | **3** | 0% mocked - Nextflow pipeline launch, workflow monitoring |
| **mcp-huggingface** | **3** | 0% mocked - Model loading, cell type prediction, sequence embedding |
| **mcp-epic** | **4** | 100% real (local only) - Patient demographics, conditions, observations, medications from Epic FHIR API |
| **mcp-mockepic** | **3** | 0% by design - Synthetic patient records, spatial-clinical linking, diagnosis search |

**TOTAL: 55 tools across 10 servers**

See each server's README or source code for detailed tool documentation.
