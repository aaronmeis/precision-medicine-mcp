# Spatial Transcriptomics Architecture

**Last Updated:** January 9, 2026
**Status:** Production - 2 servers deployed with visualization tools

---

## Quick Navigation

### 📋 Core Documentation
- **[OVERVIEW.md](OVERVIEW.md)** - System architecture, design principles, and data flow
- **[SERVERS.md](SERVERS.md)** - All 9 MCP servers with accurate tool inventories
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - GCP Cloud Run deployment guide and status

### 🔬 Workflows
- **[CSV_WORKFLOW.md](CSV_WORKFLOW.md)** - **⭐ Current Implementation** - PatientOne tabular data workflow (what you actually run)
- **[FASTQ_WORKFLOW.md](FASTQ_WORKFLOW.md)** - FASTQ alignment pipeline (implemented but not in PatientOne tests)

### 🛠️ Tool Documentation
- **[TOOL_REFERENCE.md](TOOL_REFERENCE.md)** - All 14 mcp-spatialtools tools with parameters and examples
- **[VISUALIZATION.md](VISUALIZATION.md)** - 4 visualization tools (heatmaps, charts, spatial plots)

### 📚 Reference
- **[GLOSSARY.md](GLOSSARY.md)** - Terms, acronyms, and definitions
- **[TESTING.md](TESTING.md)** - Test strategy and PatientOne test workflows

---

## What's In This Architecture

This architecture describes the **Spatial Transcriptomics** component of the Precision Medicine MCP system. The system supports **two workflows**:

### 1. CSV/Tabular Data Workflow (Current - PatientOne Tests)
**Status:** ✅ Production-ready, actively tested

Processes pre-processed spatial transcriptomics data in CSV format:
- 900 spatial spots with (x,y) coordinates
- 31 genes measured per spot
- 6 annotated tissue regions
- Statistical analysis, batch correction, pathway enrichment
- 4 visualization tools for heatmaps and plots

**Used in:** PatientOne end-to-end tests (TEST_3_SPATIAL.txt)
**Tools:** 10 analysis tools + 4 visualization tools
**Server:** mcp-spatialtools (deployed to GCP Cloud Run)

See [CSV_WORKFLOW.md](CSV_WORKFLOW.md) for complete documentation.

### 2. FASTQ Alignment Workflow (Implemented, Not Tested)
**Status:** ⚠️ Implemented but not used in current tests

Processes raw sequencing data from FASTQ files:
- Quality filtering of spatial barcodes
- STAR alignment to reference genome
- UMI counting and deduplication
- Expression matrix generation

**Used in:** Not currently tested (requires STAR aligner, genome indices)
**Tools:** filter_quality, align_spatial_data, merge_tiles
**Server:** mcp-spatialtools (alignment tools available)

See [FASTQ_WORKFLOW.md](FASTQ_WORKFLOW.md) for complete documentation.

---

## Server Status

| Server | Tools | Status | Deployed | Use Case |
|--------|-------|--------|----------|----------|
| **mcp-spatialtools** | 14 (10 analysis + 4 viz) | ✅ Production | GCP Cloud Run | Spatial data analysis, visualizations |
| **mcp-openimagedata** | 5 (3 analysis + 2 viz) | ✅ 60% Real | GCP Cloud Run | H&E morphology, MxIF compositing |
| **mcp-fgbio** | 4 | ✅ Production | GCP Cloud Run | FASTQ/VCF QC, genome references |
| **mcp-multiomics** | 9 | ✅ Production | GCP Cloud Run | HAllA integration, Stouffer meta-analysis |
| **mcp-deepcell** | 4 | ❌ Mocked | Not deployed | MxIF cell segmentation (future) |
| **mcp-tcga** | 7 | ❌ Mocked | Not deployed | TCGA comparison (future) |
| **mcp-seqera** | 6 | ❌ Mocked | Not deployed | Nextflow workflows (future) |
| **mcp-huggingface** | 5 | ❌ Mocked | Not deployed | ML models (future) |
| **mcp-mockepic** | 6 | ✅ Mock by design | GCP Cloud Run | Synthetic FHIR data |

See [SERVERS.md](SERVERS.md) for detailed server documentation.

---

## PatientOne Integration

The spatial transcriptomics component is part of the comprehensive **PatientOne** precision medicine workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATIENTONE WORKFLOW                           │
│              Stage IV Ovarian Cancer Use Case                    │
└─────────────────────────────────────────────────────────────────┘

Clinical Data → Genomic Data → Multi-Omics → Spatial Data → Imaging
(mcp-epic)    (mcp-fgbio)     (mcp-multi)   (mcp-spatial) (mcp-open)
                (mcp-tcga)      omics)        tools)        imagedata)
                                                            (mcp-deep
                                                             cell)
              ↓                 ↓             ↓             ↓
        ┌─────────────────────────────────────────────────────────┐
        │           Integration & Treatment Recommendations        │
        │        • TP53/BRCA1/PIK3CA mutation impact              │
        │        • Spatial heterogeneity of resistance markers    │
        │        • Immune exclusion phenotype                     │
        │        • PI3K/AKT/mTOR pathway activation              │
        └─────────────────────────────────────────────────────────┘
```

See [PatientOne README](../../tests/manual_testing/PatientOne-OvarianCancer/README.md) for complete workflow.

---

## Key Features

### Analysis Capabilities
- ✅ **Differential Expression** - Wilcoxon, t-test, DESeq2-style statistical testing
- ✅ **Batch Correction** - ComBat, Harmony, Scanorama methods
- ✅ **Pathway Enrichment** - GO, KEGG, Reactome, Hallmark gene sets
- ✅ **Spatial Autocorrelation** - Moran's I, Geary's C spatial statistics
- ✅ **Cell Type Deconvolution** - CIBERSORTx, EPIC, quanTIseq methods (synthetic)

### Visualization Tools
- ✅ **Spatial Heatmap** - Gene expression overlaid on tissue coordinates
- ✅ **Gene Expression Heatmap** - Clustered heatmap (genes × regions)
- ✅ **Region Composition Chart** - Bar chart of spot counts per region
- ✅ **Spatial Autocorrelation Plot** - Moran's I visualization

### Data Integration
- ✅ **Bridge to Multi-Omics** - `get_spatial_data_for_patient` tool integrates with mcp-multiomics
- ✅ **Clinical Linkage** - Connects spatial patterns to clinical outcomes
- ✅ **Imaging Registration** - Links spatial coordinates to histology images (via mcp-openimagedata)

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **MCP Server Framework** | FastMCP | 0.6.0+ |
| **Programming Language** | Python | 3.11+ |
| **Statistical Analysis** | scipy, statsmodels | 1.11+, 0.14+ |
| **Visualization** | matplotlib, seaborn | 3.8+, 0.13+ |
| **Alignment (FASTQ workflow)** | STAR aligner | 2.7.11+ |
| **Deployment** | GCP Cloud Run | - |
| **Transport** | SSE (HTTP streaming) | MCP 2025-11-20 |

---

## Getting Started

### For Users (Running PatientOne Tests)
1. Read [CSV_WORKFLOW.md](CSV_WORKFLOW.md) to understand the tabular data workflow
2. Review [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for available analysis tools
3. See [PatientOne TEST_3_SPATIAL.txt](../../tests/manual_testing/PatientOne-OvarianCancer/implementation/TEST_3_SPATIAL.txt)

### For Developers (Implementing FASTQ Pipeline)
1. Read [FASTQ_WORKFLOW.md](FASTQ_WORKFLOW.md) for alignment pipeline details
2. Install STAR aligner and genome indices (see FASTQ_WORKFLOW.md)
3. Test with small FASTQ samples before production data

### For Deployers (GCP Cloud Run)
1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment procedures
2. Current deployment: mcp-spatialtools with 14 tools (Jan 9, 2026)
3. Use provided deployment scripts in `/scripts/deployment/`

---

## Documentation Accuracy

**What This Documentation Describes:**
- ✅ **Current Implementation** - CSV workflow used in PatientOne tests
- ✅ **Deployed Servers** - mcp-spatialtools, mcp-openimagedata on GCP Cloud Run
- ✅ **14 Production Tools** - All tools documented with accurate parameters
- ✅ **4 Visualization Tools** - Recently added (Jan 8-9, 2026)

**What Has Changed Since Original Doc:**
- 🔄 Added 4 visualization tools (Jan 8-9, 2026)
- 🔄 Deployed mcp-spatialtools and mcp-openimagedata to GCP (Dec 30, 2025; Jan 9, 2026)
- 🔄 Clarified H&E vs MxIF imaging workflows
- 🔄 Updated to reflect CSV workflow as primary use case

**See Also:**
- [Main Architecture README](../README.md) - Overall system architecture
- [PatientOne README](../../tests/manual_testing/PatientOne-OvarianCancer/README.md) - Complete end-to-end workflow

---

**Questions or Issues?** See [GitHub Issues](https://github.com/lynnlangit/precision-medicine-mcp/issues)
