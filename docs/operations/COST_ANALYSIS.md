# PatientOne Cost & Performance Analysis

## Executive Summary

### Demonstration Data (Small Synthetic Files)

| Mode | Total Time | Total Cost | Best For |
|------|-----------|------------|----------|
| **DRY_RUN** | 25-35 min | ~$1 | Demo, learning, CI/CD testing |
| **Automated Report** | ~12 seconds | ~$1 | Quick analysis with pre-aligned data |
| **Real Patient Data (Small Files)** | 1-2 hours | $7-19 | Workflow testing with small synthetic data |
| **Real Patient Data (with STAR, Small Files)** | 1.5-3 hours | $12-29 | Testing from raw FASTQ (small files) |

**Data size:** ~4.9 MB total (315 KB spatial, 505 KB multi-omics)

### Production Data (Realistic Hospital Volumes)

| Mode | Total Time | Total Cost | Best For |
|------|-----------|------------|----------|
| **Real Patient Data (Pre-aligned)** | 2-4 hours | **$25-75** | Production analysis with Space Ranger output |
| **Real Patient Data (Raw FASTQ)** | 4-8 hours | **$50-120** | Production analysis from raw sequencing data |

**Data size per patient:** ~3-8 GB total (100-500 MB spatial processed, 2.7 GB multi-omics raw, or 15-20 MB processed)

**Key differences:**
- **Spatial:** 315 KB demo → 100-500 MB production (300-1500x larger)
- **Multi-omics:** 505 KB demo → 15-20 MB processed matrices production (30-40x larger)
- **Processing time:** 1-3 hours demo → 4-8 hours production (realistic file sizes)
- **Compute cost:** $7-29 demo → $25-120 production (larger memory, longer runtime)

**Note:** SpatialTools upgraded to 95% real implementation (2025-12-29). STAR alignment functional but optional.

---

## DRY_RUN Mode (Synthetic Data)

### Overview
- Uses synthetic responses from all MCP servers
- No external API calls or computational processing
- Ideal for demonstration and workflow validation

### Per-Test Breakdown

| Test | Servers Used | Est. Tokens (In/Out) | Time | Cost |
|------|--------------|---------------------|------|------|
| **TEST_1: Clinical + Genomic** | MockEpic, FGbio, TCGA | 2,000 / 3,500 | 3-5 min | ~$1 |
| **TEST_2: Multi-Omics** | MultiOmics | 2,500 / 4,000 | 5-8 min | ~$1 |
| **TEST_3: Spatial** | SpatialTools, DeepCell | 2,000 / 3,500 | 4-6 min | ~$1 |
| **TEST_4: Imaging** | OpenImageData, DeepCell | 1,800 / 3,000 | 3-5 min | ~$1 |
| **TEST_5: Integration** | All 9 servers | 3,000 / 5,000 | 5-7 min | ~$1 |
| **TOTAL** | - | **11,300 / 19,000** | **25-35 min** | **~$1** |

### Token Usage Details

**Input Tokens (11,300 total):**
- User prompts: ~2,500 tokens
- File path references: ~500 tokens
- MCP tool definitions: ~4,000 tokens
- Context from previous tests: ~4,300 tokens

**Output Tokens (19,000 total):**
- Claude analysis & synthesis: ~8,000 tokens
- Synthetic MCP responses: ~6,000 tokens
- Recommendations & summaries: ~5,000 tokens

### Cost Calculation (Claude Sonnet 4 pricing)
- Input: 11,300 tokens × $3/M = **~$1**
- Output: 19,000 tokens × $15/M = **~$1**
- **Total: ~$1** (rounded up for simplicity)

### Time Breakdown
- Claude processing: 15-20 minutes
- User review & navigation: 10-15 minutes
- **Total wall-clock time: 25-35 minutes**

---

## Automated Patient Report Generator

### Overview
- **New capability added December 29, 2025**
- Standalone Python script for rapid patient analysis
- Requires pre-aligned spatial transcriptomics data
- Integrates FHIR clinical data from GCP Healthcare API

### Script Details

**Script:** `scripts/generate_patient_report.py`
**Documentation:** `docs/AUTOMATED_PATIENT_REPORTS.md`

**Capabilities:**
- Differential expression (Mann-Whitney U + FDR correction)
- Spatial autocorrelation (Moran's I with spatial weights)
- Cell type deconvolution (signature-based scoring)
- Publication-quality visualizations (5 PNG files, 300 DPI)
- Clinical summary reports (TXT, JSON, CSV)

### Performance & Cost

| Metric | Value |
|--------|-------|
| **Runtime** | ~12 seconds per patient |
| **Compute Cost** | ~$1 (local CPU processing) |
| **Token Cost** | ~$1 (FHIR data retrieval if using Claude) |
| **Total Cost** | ~$1 per patient |

### Output Files (10 total, ~3.4 MB)

**Data files (5):**
- differential_expression.csv (3.4 KB)
- spatial_autocorrelation.csv (1.5 KB)
- cell_deconvolution.csv (566 B)
- clinical_summary.txt (2.9 KB)
- metadata.json (396 B)

**Visualizations (5):**
- volcano_plot.png (158 KB)
- spatial_heatmap.png (1.8 MB)
- cell_composition_heatmap.png (217 KB)
- spatial_autocorrelation_plot.png (140 KB)
- summary_figure.png (1.0 MB)

### Use Cases

**Best for:**
- Quick patient analysis with pre-aligned data (Space Ranger output)
- Batch processing of multiple patients
- Automated report generation pipelines
- Research studies requiring standardized analysis

**Not suitable for:**
- Raw FASTQ alignment (STAR not integrated yet)
- Batch correction across multiple samples
- Pathway enrichment analysis

### Example Usage

```bash
cd /path/to/spatial-mcp
/path/to/servers/mcp-spatialtools/venv/bin/python3 \
  scripts/generate_patient_report.py \
  --patient-id patient-001 \
  --output-dir ./results
```

**Example Output:**
```
✅ Analysis complete!
   Runtime: 11.8 seconds
   Files generated: 10
   Total size: 3.4 MB
```

---

## Real Patient Data Mode (Small Synthetic Files)

### Overview
- Processes actual patient genomic, transcriptomic, and imaging data
- Executes computational workflows (alignment, segmentation, etc.)
- Makes external API calls (TCGA, HuggingFace, Seqera)
- **Data size:** Small synthetic files (~4.9 MB total)

### Per-Test Breakdown

| Test | Servers Used | Processing Time (Pre-aligned) | Processing Time (with STAR) | Compute Cost (Pre-aligned) | Compute Cost (with STAR) | API Cost | Total Cost (Pre-aligned) | Total Cost (with STAR) |
|------|--------------|-------------------------------|------------------------------|----------------------------|--------------------------|----------|--------------------------|------------------------|
| **TEST_1: Clinical + Genomic** | MockEpic, FGbio, TCGA | 10-15 min | 10-15 min | ~$1 | ~$1 | $0 | ~$1 | ~$1 |
| **TEST_2: Multi-Omics** | MultiOmics | 15-25 min | 15-25 min | $2-4 | $2-4 | $0 | $2-4 | $2-4 |
| **TEST_3: Spatial** | SpatialTools, DeepCell | 10-20 min | 40-80 min | $1-3 | $6-13 | $0 | $1-3 | $6-13 |
| **TEST_4: Imaging** | OpenImageData, DeepCell | 20-40 min | 20-40 min | $3-7 | $3-7 | ~$1 | $3-7 | $3-7 |
| **TEST_5: Integration** | All 9 servers | 5-10 min | 5-10 min | ~$1 | ~$1 | $0 | ~$1 | ~$1 |
| **TOTAL** | - | **1-2 hours** | **1.5-3 hours** | **$7-14** | **$12-24** | **~$1** | **$7-19** | **$12-29** |

---

## Production Patient Data Mode (Realistic Hospital Volumes)

### Overview
- Processes realistic hospital data volumes
- **Data size per patient:** ~3-8 GB total
  - Spatial: 100-500 MB (processed matrix from Space Ranger)
  - Multi-omics: 2.7 GB raw or 15-20 MB processed matrices
  - Imaging: 500 MB - 2 GB (full resolution)
- Significantly longer processing times
- Higher memory requirements (16-64 GB RAM)
- Larger Cloud Run instances needed

### Per-Test Breakdown (Production Volumes)

| Test | Servers Used | Processing Time (Pre-aligned) | Processing Time (Raw FASTQ) | Compute Cost (Pre-aligned) | Compute Cost (Raw FASTQ) | API Cost | Per-Test Cost (Pre-aligned) | Per-Test Cost (Raw FASTQ) |
|------|--------------|-------------------------------|------------------------------|----------------------------|--------------------------|----------|----------------------------|--------------------------|
| **TEST_1: Clinical + Genomic** | Epic, FGbio, TCGA | 15-30 min | 15-30 min | ~$1-2 | ~$1-2 | $0 | ~$1-2 | ~$1-2 |
| **TEST_2: Multi-Omics** | MultiOmics | 30-60 min | 30-60 min | $6-20 | $6-20 | $0 | $6-20 | $6-20 |
| **TEST_3: Spatial** | SpatialTools, DeepCell | 45-120 min | 90-240 min | $5-30 | $10-40 | $0 | $5-30 | $10-40 |
| **TEST_4: Imaging** | OpenImageData, DeepCell | 40-90 min | 40-90 min | $9-35 | $9-35 | ~$1 | $10-36 | $10-36 |
| **TEST_5: Integration** | All 9 servers | 10-20 min | 10-20 min | ~$1-2 | ~$1-2 | $0 | ~$1-2 | ~$1-2 |
| **Subtotal (Compute + API)** | - | **2-4 hours** | **4-8 hours** | **$22-89** | **$27-99** | **~$1** | **$23-90** | **$28-100** |
| **+ Claude Tokens** | - | - | - | - | - | - | **~$1-2** | **~$1-2** |
| **TOTAL** | - | **2-4 hours** | **4-8 hours** | - | - | - | **$24-92** | **$29-102** |

**Claude Token Usage (Production):**
- Input: 35-75K tokens × $3/M = $0.11-0.23
- Output: 40-80K tokens × $15/M = $0.60-1.20
- **Token total: ~$0.71-1.43** → rounds to **~$1-2**
- Note: MCP servers return summaries, not raw 3-8 GB files, so token costs stay low!

**Key differences from small files:**
- **Data volumes:** 300-1500× larger spatial, 400-500× larger multi-omics
- **Processing time:** 2-6× longer (not 300× due to optimized algorithms)
- **Compute costs:** 3-5× higher due to longer processing, larger memory requirements
- **Token costs:** Only ~2× higher despite massive data increase (servers return summaries!)
- **Total cost:** $7-29 → **$24-102** (3-4× more expensive for realistic hospital data)

### Detailed Cost Components

#### 1. Computational Processing ($7-14 pre-aligned, $12-24 with STAR)

**Spatial Transcriptomics (TEST_3):**
- ✅ **Note:** SpatialTools upgraded to 95% real implementation (Dec 29, 2025)
- STAR alignment (optional): 30-60 min = **$5-10** (r5.2xlarge @ $0.504/hr)
  - 50M reads × 100bp
  - Human genome (hg38) with GENCODE annotations
  - 8 threads, 32GB RAM
  - Output: Sorted BAM (~20-50GB)
- Batch correction (ComBat): 10-30 sec = $0.01
- Differential expression (Mann-Whitney U + FDR): 2-5 min = $0.20-0.50
- Spatial autocorrelation (Moran's I): 2-5 min = $0.20-0.50
- Cell type deconvolution (signature-based): 1-3 min = $0.10-0.30
- Pathway enrichment (Fisher's exact + FDR): <1 sec = $0.01
- ❌ DeepCell segmentation: Still mocked (not included in cost)

**Multi-Omics Integration (TEST_2):**
- HAllA analysis (chunked): 10-15 min = $1-2
- Stouffer's meta-analysis: 2-5 min = $0.20-0.50
- Upstream regulator prediction: 3-5 min = $0.30-0.50

**Imaging Analysis (TEST_4):**
- DeepCell cell segmentation: 15-30 min GPU = $3-5
- Image feature extraction: 5-10 min = $0.50-1

**Clinical/Genomic (TEST_1):**
- VCF processing: 5-10 min = $0.50

#### 2. External API Costs ($0-5)

**TCGA (TEST_1, TEST_3):**
- Free public API
- Rate-limited (10 requests/second)
- Cost: $0

**HuggingFace Inference API (TEST_3, TEST_4):**
- Cell type prediction: $0-1 per 1000 predictions
- Sequence embeddings: $0-1 per 1000 sequences
- Estimated: $0-2 total

**Seqera Platform (TEST_3):**
- Nextflow pipeline execution
- Free tier: 10 hours/month
- Paid tier: $0.10/compute-hour
- Estimated: $0-3 for spatial workflow

#### 3. Claude Token Usage (~$0.50-1.00)
Similar to DRY_RUN mode, but with larger context from real data files:
- Input: 15,000-20,000 tokens × $3/M = $0.045-0.06
- Output: 25,000-35,000 tokens × $15/M = $0.375-0.525
- **Total: ~$0.42-0.59**

### Time Breakdown

**Wall-clock time: 1-2 hours** (reduced from 2-4 hours due to spatialtools improvements)
- Computational processing: 60-110 minutes
- API calls & data transfer: 5-15 minutes
- Claude processing & user review: 20-45 minutes

**Parallelization opportunities:**
- Tests can run sequentially (2 hours) or with some parallelization (1.5 hours)
- Multi-omics HAllA analysis is now the bottleneck (10-15 min)
- **When STAR alignment implemented:** Add 30-60 min, making it the bottleneck again

---

## Cost Comparison by Use Case

### Academic Research Lab (Demonstration Data)
**Scenario:** 50 patient analyses per year with small synthetic files

| Mode | Cost per Patient | Annual Cost | Use Case |
|------|-----------------|-------------|----------|
| DRY_RUN | ~$1 | $50 | Workflow development, testing |
| Automated Report | ~$1 | $50 | Quick analysis (pre-aligned data) |
| Real Data (Small Files) | $13 (avg) | $650 | Full analysis with MCP orchestration |

**ROI:** Replaces ~40 hours of manual bioinformatics work per patient ($80/hr × 40 = $3,200)
**Savings:** $3,187 per patient using automated reports, or $159,350 annually
**Note:** Small synthetic files (315 KB spatial, 505 KB multi-omics)

### Academic Research Lab (Production Data)
**Scenario:** 50 patient analyses per year with realistic hospital data volumes

| Mode | Cost per Patient | Annual Cost | Use Case |
|------|-----------------|-------------|----------|
| Real Data (Pre-aligned) | $50 (avg) | $2,500 | Production analysis with Space Ranger output |
| Real Data (Raw FASTQ) | $85 (avg) | $4,250 | Production analysis from raw sequencing data |

**ROI:** Replaces ~40 hours of manual bioinformatics work per patient ($80/hr × 40 = $3,200)
**Savings:** $3,150 per patient (pre-aligned) or $3,115 per patient (raw FASTQ)
**Annual Savings:** $157,500 (pre-aligned) or $155,750 (raw FASTQ)
**Data volumes:** 3-8 GB per patient (100-500 MB spatial processed, 2.7 GB multi-omics raw)

### Clinical Genomics Center (Production Data)
**Scenario:** 500 patient analyses per year with realistic hospital data volumes

| Mode | Cost per Patient | Annual Cost |
|------|-----------------|-------------|
| Automated Report | ~$1 | $500 |
| Real Data (Pre-aligned) | $50 (avg) | $25,000 |
| Real Data (Raw FASTQ) | $85 (avg) | $42,500 |

**ROI:** Replaces manual analysis + reduces time-to-result from 2-3 weeks to 4-6 hours
**Value:** Faster treatment decisions, improved patient outcomes
**Annual Savings:** ~$1.6M using automated reports (vs manual $3,200/patient)
**Annual Savings:** ~$1.58M using pre-aligned production data (vs manual $3,200/patient)

### Pharmaceutical R&D (Production Data)
**Scenario:** 200 PDX model analyses per year with realistic data volumes

| Mode | Cost per Analysis | Annual Cost |
|------|------------------|-------------|
| Automated Report | ~$1 | $200 |
| Real Data (Pre-aligned) | $50 (avg) | $10,000 |
| Real Data (Raw FASTQ) | $85 (avg) | $17,000 |

**ROI:** Accelerates target identification and biomarker discovery
**Value:** Weeks → hours for multi-omics integration
**Throughput:** 200 samples analyzed in 400-800 hours using production data (vs weeks manually)
**Cost avoidance:** Reduces need for manual bioinformatics staff (~$500K/year for 3-5 FTEs)

---

## Infrastructure Requirements

### DRY_RUN Mode (Demonstration)
- **CPU:** Any modern laptop (2+ cores)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 5GB for MCP servers + Python dependencies
- **Network:** Internet for Claude Desktop API calls only
- **Data size:** ~5 MB total (minimal synthetic data)

### Real Patient Data Mode - Small Synthetic Files (Demonstration)

**Without STAR alignment (pre-aligned data):**
- **CPU:** 4-8 cores sufficient for DE, Moran's I, deconvolution, pathway enrichment
- **GPU:** ❌ Not needed (DeepCell still mocked as of Dec 29, 2025)
- **RAM:** 16GB minimum, 32GB recommended
- **Storage:** 20GB minimum for patient data + cache
- **Network:** Stable connection for TCGA API calls (if enabled)
- **Data size:** ~4.9 MB per patient (315 KB spatial, 505 KB multi-omics)

**With STAR alignment (from raw FASTQ, small files):**
- **CPU:** 8-16 cores recommended (STAR scales linearly)
- **RAM:** 32GB minimum, 64GB recommended
- **Storage:** 100GB minimum
- **Network:** Download genome index once (3GB compressed), then local
- **Data size:** ~4.9 MB per patient (synthetic small FASTQ files)

### Real Patient Data Mode - Production Volumes (Hospital Deployment)

**Without STAR alignment (pre-aligned data from Space Ranger):**
- **CPU:** 8-16 cores recommended for parallel processing of large matrices
- **GPU:** ❌ Not needed (DeepCell still mocked as of Dec 29, 2025)
- **RAM:** 32GB minimum, **64GB recommended** for production
  - Large spatial matrices: 3,000-5,000 spots × 18,000-30,000 genes
  - Multi-omics integration: RNA/Protein/Phospho matrices
  - Memory-intensive batch correction and deconvolution
- **Storage:** **300-800 GB for 100 patients**
  - Spatial data: 100-500 MB per patient (processed HDF5 matrices)
  - Multi-omics: 15-20 MB processed matrices per patient
  - Imaging: 500 MB - 2 GB per patient (full resolution)
  - Cache and intermediate files: ~100 GB
- **Network:** Stable high-bandwidth connection for GCS/S3 data transfer
- **Data size:** 3-8 GB per patient (processed data)

**With STAR alignment (from raw FASTQ, production):**
- **CPU:** 16-32 cores recommended (STAR scales linearly)
- **RAM:** 64GB minimum, **128GB recommended** for production
  - STAR loads entire genome index into RAM (~30GB for hg38)
  - Additional RAM for sorting large BAM files (2-5 GB per patient)
  - Memory-intensive multi-omics processing
- **Storage:** **500 GB - 1.5 TB for 100 patients**
  - Genome index: ~30GB (one-time)
  - Raw FASTQ: 10-30 GB per patient (compressed)
  - BAM output: 2-5 GB per patient (aligned, sorted)
  - Processed matrices: 100-500 MB per patient
  - Intermediate files: ~200 GB
- **Network:** High-bandwidth connection for raw data transfer (10-30 GB per patient)
- **Data size:** 12-35 GB per patient (raw FASTQ + aligned BAM + processed matrices)

**When DeepCell implemented (future):**
- **GPU:** NVIDIA with 16GB+ VRAM recommended for production histology image segmentation
- **Additional storage:** +500 MB - 2 GB per patient for full-resolution histology images

---

## Cost Optimization Strategies

### 1. Batch Processing
- Run multiple patients in sequence to amortize setup costs
- Cache reference genomes and model weights
- Estimated savings: 20-30% for 10+ patients

### 2. Pre-computed Data Reuse
- Store intermediate results (aligned BAMs, cell segmentation masks)
- Reuse for hypothesis testing without re-processing
- Estimated savings: 50-70% for follow-up analyses

### 3. Selective Analysis
- Run only relevant tests (e.g., skip imaging if not available)
- DRY_RUN mode for workflow validation before committing compute
- Estimated savings: 40-60% when only 2-3 tests needed

### 4. Cloud vs Local
- **Local processing:** One-time hardware cost, no per-analysis fees
- **Cloud (AWS/GCP):** Pay-per-use, scales easily
- **Hybrid:** Local for common workflows, cloud for large-scale parallel processing

---

## Frequently Asked Questions

### Q: Why is Real Data mode 25-120× more expensive than DRY_RUN?
**A:** Real data requires actual computational processing (sequence alignment, cell segmentation, statistical analysis) rather than returning synthetic responses. The cost reflects:
- **Scientific computation** (not just LLM orchestration)
- **Data volume**: Production data is 300-1500× larger than demonstration files
  - Spatial: 315 KB demo → 100-500 MB production
  - Multi-omics: 505 KB demo → 2.7 GB raw or 15-20 MB processed
- **Processing time**: 2-4 hours (pre-aligned) to 4-8 hours (raw FASTQ) vs 25-35 minutes in DRY_RUN
- **Memory requirements**: 64-128 GB RAM for production vs 4-8 GB for demonstration

### Q: Can I reduce costs by using smaller data files?
**A:** Yes! The costs scale with:
- **Number of spatial spots:** 900 in demo → 3,000-5,000 in production Visium
- **Number of genes profiled:** 31 in demo → 18,000-30,000 in whole transcriptome
- **Multi-omics data volume:** 505 KB demo → 2.7 GB raw production
- **Image resolution and number of markers:** 4.1 MB demo → 500 MB - 2 GB production

**Demonstration costs:** ~$1 (DRY_RUN) to $7-29 (small synthetic files)
**Production costs:** $25-75 (pre-aligned) to $50-120 (raw FASTQ)

### Q: What happens if a test fails midway?
**A:**
- DRY_RUN: No cost beyond Claude tokens consumed
- Real Data: You pay for compute time used, but intermediate results are cached for retry

### Q: Are there free tiers for external APIs?
**A:**
- TCGA: Always free (NIH public data)
- HuggingFace: Free tier with rate limits (30 requests/hour)
- Seqera: 10 compute-hours/month free

---

**Last Updated:** December 30, 2025

**Recent Updates:**
- **Major:** Updated all costs to reflect realistic hospital production data volumes (Dec 30, 2025)
  - **Demonstration data:** 4.9 MB per patient (315 KB spatial, 505 KB multi-omics)
  - **Production data:** 3-8 GB per patient (100-500 MB spatial, 2.7 GB multi-omics raw)
  - **Cost impact:** 3-4× increase for production volumes
- **Major:** SpatialTools upgraded from 70% → 95% real implementation (Dec 29, 2025)
  - STAR alignment now functional (adds 30-60 min, $5-10)
  - Batch correction validated with ComBat algorithm
  - Pathway enrichment statistically validated (Fisher's exact + FDR)
- Added automated patient report generator (~12 sec, ~$1)
- All costs < $1 rounded to ~$1 for scannability
- Updated costs:
  - **Demonstration (small synthetic files):** ~$1 (DRY_RUN), $7-29 (real data, 1-3 hours)
  - **Production (realistic hospital volumes):** $25-75 (pre-aligned, 2-4 hours), $50-120 (raw FASTQ, 4-8 hours)
- Updated infrastructure requirements:
  - **Demonstration:** 16-32GB RAM, 20-100GB storage
  - **Production:** 64-128GB RAM, 300-1500GB storage for 100 patients
  - **Data volumes:** 300-1500× larger spatial data, 400-500× larger multi-omics data

**Pricing basis:** Claude Sonnet 4 ($3/M input, $15/M output), AWS EC2 r5.2xlarge ($0.504/hr for STAR), c6i.2xlarge ($0.34/hr for other tasks), g4dn.xlarge ($0.526/hr for GPU when needed), Google Cloud Run with similar pricing
