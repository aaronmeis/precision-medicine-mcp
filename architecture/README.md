# Precision Medicine MCP Server Architectures by Analysis Type

**Purpose:** Architecture documentation for modality-specific analysis workflows

**⚠️ Important:** Not all servers are production-ready. Check [Server Implementation Status](../docs/SERVER_IMPLEMENTATION_STATUS.md) before using for research or production.

---

## Architecture by Analysis Modality

This directory contains high-level architecture documentation organized by **analysis type** (not by use case):

| Modality | Servers | Tools | Status | Documentation |
|----------|---------|-------|--------|---------------|
| **Imaging** | mcp-openimagedata, mcp-deepcell | 9 | Partial (60%/0%) | [imaging/README.md](imaging/README.md) |
| **Multiomics** | mcp-multiomics | 10 | Production (85%) | [multiomics/README.md](multiomics/README.md) |
| **Spatial Transcriptomics** | mcp-fgbio, mcp-spatialtools | 18 | Production (95%) | [spatial-transcriptomics/README.md](spatial-transcriptomics/README.md) |

**Total:** 3 analysis modalities, 5 specialized servers, 37 tools

---

## 1. Imaging Analysis

**Purpose:** Histology and multiplexed immunofluorescence (MxIF) image processing

**Servers:**
- **mcp-openimagedata** (5 tools, 60% real) - Image loading, spatial registration, MxIF compositing, H&E annotation
- **mcp-deepcell** (4 tools, mocked) - Cell segmentation and phenotyping (future: DeepCell-TF)

**Key Workflows:**
- **H&E (Brightfield):** Morphology assessment, necrosis identification (chromogenic stains, RGB TIFF)
- **MxIF (Fluorescence):** Cell segmentation and quantification (fluorescent antibodies, multi-channel TIFF)

**See:** [imaging/README.md](imaging/README.md) for detailed architecture

---

## 2. Multiomics Integration

**Purpose:** PDX multi-omics data integration with preprocessing, association testing, and therapeutic target prediction

**Server:**
- **mcp-multiomics** (10 tools, 85% real) - Data validation, batch correction, HAllA, Stouffer's meta-analysis, upstream regulators

**Key Features:**
- **Preprocessing Pipeline:** Batch correction, KNN imputation, QC visualization (MANDATORY first step)
- **Association Testing:** HAllA with chunking (1000 features/chunk = ~5 min vs days)
- **Meta-Analysis:** Stouffer's method with correct FDR timing (AFTER combination, not before)
- **Therapeutic Targets:** Kinase/TF/drug prediction based on dysregulated pathways

**Workflow:**
```
RNA + Protein + Phospho Data
  ↓ Validate (batch effects, missing values)
  ↓ Preprocess (ComBat, KNN imputation)
  ↓ Visualize QC (PCA before/after)
  ↓ Integrate (align samples, normalize)
  ↓ HAllA (find associations, chunked)
  ↓ Stouffer's Meta-Analysis (combine p-values)
  ↓ FDR Correction (AFTER meta-analysis)
  ↓ Upstream Regulators (kinases, TFs, drugs)
  ↓ Visualizations (heatmaps, PCA)
```

**See:** [multiomics/README.md](multiomics/README.md) for detailed architecture

---

## 3. Spatial Transcriptomics

**Purpose:** Spatial gene expression analysis with tissue context

**Servers:**
- **mcp-fgbio** (4 tools, 95% real) - Reference genomes, FASTQ validation, UMI extraction, gene annotations
- **mcp-spatialtools** (14 tools, 95% real) - Spatial analysis, differential expression, pathway enrichment, visualizations

**Key Features:**
- **Analysis Tools (10):** Quality filtering, region segmentation, spatial autocorrelation (Moran's I), differential expression, batch correction, pathway enrichment, cell type deconvolution
- **Visualization Tools (4):** Spatial heatmaps, gene expression heatmaps, region composition charts, autocorrelation plots
- **Bridge Tool:** Integrates spatial findings with mcp-multiomics for cross-modality analysis

**Workflows:**
- **CSV Workflow** (current implementation) - Pre-processed tabular data (coordinates, expression, annotations)
- **FASTQ Workflow** (implemented, not tested) - Raw sequencing alignment with STAR

**See:** [spatial-transcriptomics/README.md](spatial-transcriptomics/README.md) for detailed architecture

---

## End-to-End Example: PatientOne Precision Medicine Workflow

For a complete example combining **all 10 MCP servers** across all modalities (imaging, multiomics, spatial, clinical, genomic):

**See:** [PatientOne Workflow](../tests/manual_testing/PatientOne-OvarianCancer/README.md)

**Use Case:** Stage IV High-Grade Serous Ovarian Cancer (HGSOC), platinum-resistant
**Patient:** PAT001-OVC-2025 (synthetic test case)
**Data Modalities:** Clinical (FHIR), Genomic (VCF), Multiomics (RNA/Protein/Phospho), Spatial (Visium), Imaging (H&E, MxIF)
**Test Location:** `/tests/manual_testing/PatientOne-OvarianCancer/`

**Architecture Documentation:** [PatientOne Architecture](../tests/manual_testing/PatientOne-OvarianCancer/architecture/README.md)

**Tests:**
- TEST_1: Clinical data retrieval (mcp-epic)
- TEST_2: Multiomics integration (mcp-multiomics)
- TEST_3: Spatial transcriptomics (mcp-spatialtools)
- TEST_4: Imaging analysis (mcp-openimagedata, mcp-deepcell)
- TEST_5: Complete end-to-end workflow

---

## 📖 Operations & Deployment Documentation

For deployment, testing, and production operations, see:

- **[Server Implementation Status](../docs/SERVER_IMPLEMENTATION_STATUS.md)** - Production readiness matrix for all 10 servers
- **[GCP Cloud Run Deployment](../docs/deployment/DEPLOYMENT_STATUS.md)** - Current deployment state (9 servers on GCP)
- **[Hospital Deployment Guide](../docs/hospital-deployment/)** - HIPAA-compliant production setup
- **[Cost Analysis](../docs/operations/COST_ANALYSIS.md)** - Token costs, compute estimates, ROI analysis
- **[Testing Guide](../docs/testing/GCP_SERVER_TEST_PLAN.md)** - Automated testing procedures

---

## Complete Server Inventory

| Server | Tools | Status | Primary Use |
|--------|-------|--------|-------------|
| **mcp-fgbio** | 4 | ✅ 95% real | Reference genomes, FASTQ QC |
| **mcp-multiomics** | 10 | ✅ 85% real | Multi-omics integration, preprocessing |
| **mcp-spatialtools** | 14 | ✅ 95% real | Spatial transcriptomics analysis |
| **mcp-openimagedata** | 5 | ⚠️ 60% real | Histology image processing |
| **mcp-deepcell** | 4 | ❌ Mocked | Cell segmentation (future) |
| **mcp-tcga** | 5 | ❌ Mocked | TCGA cohort comparison |
| **mcp-seqera** | 3 | ❌ Mocked | Nextflow workflows |
| **mcp-huggingface** | 3 | ❌ Mocked | ML model inference |
| **mcp-epic** | 4 | ✅ 100% real | Real Epic FHIR (local only) |
| **mcp-mockepic** | 3 | 🎭 Mock by design | Synthetic FHIR (GCP deployed) |

**TOTAL: 55 tools across 10 servers**

**Deployment:**
- **9 servers on GCP Cloud Run** (all except mcp-epic)
- **1 server local only** (mcp-epic - HIPAA compliance)

For detailed server specifications: See `/servers/*/README.md` for each server

---

**Last Updated:** 2026-01-10
**Organization:** Architecture by modality (imaging, multiomics, spatial)
**Use Case Examples:** See `/tests/manual_testing/PatientOne-OvarianCancer/`

**Principle:**
- `architecture/` = High-level design & workflows by modality
- `servers/` = Detailed tool specifications & implementation
- `docs/` = Operational guides & deployment
- `tests/` = End-to-end use cases & validation
