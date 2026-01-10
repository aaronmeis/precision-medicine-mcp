# System Architecture Overview

**Last Updated:** January 9, 2026

---

## Executive Summary

The Spatial Transcriptomics component processes gene expression data with spatial context to enable precision medicine insights. The system supports two workflows:

1. **CSV/Tabular Workflow** (Current) - Processes pre-processed spatial data for immediate analysis
2. **FASTQ Alignment Workflow** (Available) - Processes raw sequencing data from scratch

The architecture uses the **Model Context Protocol (MCP)** to enable AI-orchestrated bioinformatics workflows through specialized microservices.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   MCP HOST (Claude Desktop or API)               │
│             Orchestrates Workflow Execution & Analysis           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ MCP Protocol (JSON-RPC 2.0)
                         │ Transport: SSE (HTTP Streaming)
                         │
        ┌────────────────┼────────────────────────────┐
        │                │                            │
        ▼                ▼                            ▼
┌───────────────┐ ┌───────────────┐         ┌───────────────┐
│  Data Input   │ │  Processing   │         │  Visualization│
│  MCP Servers  │ │  MCP Servers  │         │  MCP Servers  │
└───────────────┘ └───────────────┘         └───────────────┘
│               │ │               │         │               │
│ mcp-fgbio     │ │ mcp-spatial   │         │ mcp-spatial   │
│ (references)  │ │ tools         │         │ tools (viz)   │
│               │ │ (analysis)    │         │               │
│ mcp-epic      │ │ mcp-multiomics│         │ mcp-openimage │
│ (clinical)    │ │ (integration) │         │ data (imaging)│
└───────────────┘ └───────────────┘         └───────────────┘
```

---

## Design Principles

### 1. Single Responsibility
Each MCP server handles one specific domain:
- **mcp-spatialtools**: Spatial transcriptomics analysis only
- **mcp-multiomics**: Multi-omics integration only
- **mcp-openimagedata**: Image processing only

### 2. Modular & Composable
Servers can be:
- Used independently or combined
- Deployed selectively (not all 9 required)
- Replaced without affecting others

### 3. AI-Orchestrated
Claude (MCP host) coordinates:
- Tool selection and sequencing
- Data flow between servers
- Error handling and retries
- Result interpretation

### 4. Production-Ready
- Input validation with JSON schemas
- Comprehensive error handling
- DRY_RUN mode for safe testing
- Resource limits and monitoring

### 5. Cloud-Native
- Containerized deployment (Docker)
- Serverless execution (GCP Cloud Run)
- Horizontal scaling
- SSE transport for streaming

---

## Data Flow: CSV Workflow (Current)

```
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 1: Data Loading                                            │
├──────────────────────────────────────────────────────────────────┤
│ Input: 3 CSV files (coordinates, expression, annotations)        │
│ Tool: Load data from patient-data directory                      │
│ Output: In-memory spatial dataset (900 spots, 31 genes)          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 2: Spatial Analysis                                        │
├──────────────────────────────────────────────────────────────────┤
│ Tools:                                                            │
│ • calculate_spatial_autocorrelation (Moran's I)                  │
│ • perform_differential_expression (Wilcoxon test)                │
│ • perform_pathway_enrichment (GO/KEGG)                           │
│ Output: Statistical results, enriched pathways                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 3: Visualization                                           │
├──────────────────────────────────────────────────────────────────┤
│ Tools:                                                            │
│ • generate_spatial_heatmap                                        │
│ • generate_gene_expression_heatmap                                │
│ • generate_region_composition_chart                               │
│ • visualize_spatial_autocorrelation                               │
│ Output: PNG visualizations with timestamps                        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 4: Integration                                             │
├──────────────────────────────────────────────────────────────────┤
│ Tool: get_spatial_data_for_patient (bridge to mcp-multiomics)    │
│ Output: Spatial findings integrated with genomic/proteomic data  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: FASTQ Workflow (Available)

```
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 1: Quality Control                                         │
├──────────────────────────────────────────────────────────────────┤
│ Input: Raw FASTQ files + spatial barcodes                        │
│ Tool: filter_quality                                              │
│ Output: Filtered reads with valid barcodes                        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 2: Alignment                                               │
├──────────────────────────────────────────────────────────────────┤
│ Input: Filtered FASTQ files                                      │
│ Tool: align_spatial_data (STAR aligner)                          │
│ Dependencies: Reference genome (hg38), STAR indices              │
│ Output: Aligned BAM file with spatial tags                        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STAGE 3: Expression Quantification                               │
├──────────────────────────────────────────────────────────────────┤
│ Input: Aligned BAM file                                           │
│ Tool: Count UMIs per spot/gene                                   │
│ Output: Gene × Spot expression matrix (CSV)                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
      (Proceeds to CSV Workflow Stage 2 for analysis)
```

---

## Security Architecture

### Authentication & Authorization
- **Development**: No auth (stdio transport, local only)
- **Production**: Bearer tokens, OAuth 2.0 (GCP Cloud Run with IAM)

### Data Protection
- **At Rest**: Encrypted storage (GCP default encryption)
- **In Transit**: TLS 1.3 for SSE transport
- **PHI/PII**: Synthetic data only (mcp-mockepic), no real patient data

### Input Validation
- JSON schema validation for all tool inputs
- File path sanitization (prevent directory traversal)
- Resource limits (memory, CPU, file size)

### Audit Logging
- All tool invocations logged
- Request ID tracking
- Error conditions captured
- Performance metrics collected

---

## Scalability

### Horizontal Scaling
- Stateless MCP servers (can run multiple instances)
- Load balancing (GCP Cloud Run handles automatically)
- Shared state via cloud storage (GCS buckets)

### Vertical Scaling
- Memory: 2-4 Gi per server
- CPU: 1-2 cores per server
- Storage: NVMe-backed persistent disks

### Performance Targets
| Operation | Target Latency | Throughput |
|-----------|---------------|------------|
| Load CSV data | < 2s | 10 datasets/min |
| Differential expression | < 5s | 20 analyses/min |
| Spatial autocorrelation | < 3s | 15 analyses/min |
| Pathway enrichment | < 10s | 10 analyses/min |
| Generate visualization | < 5s | 20 images/min |
| FASTQ alignment (50M reads) | < 10 min | 1-2 samples/hour |

---

## Technology Stack

### MCP Layer
- **Protocol**: Model Context Protocol 2025-11-20
- **Transport**: SSE (Server-Sent Events over HTTP)
- **Framework**: FastMCP 0.6.0+
- **Host**: Claude Desktop (local), Claude API (cloud)

### Processing Layer
- **Language**: Python 3.11+
- **Data**: NumPy, Pandas, SciPy
- **Stats**: statsmodels, scikit-learn
- **Viz**: matplotlib, seaborn
- **Bio**: STAR (FASTQ workflow), samtools, bedtools

### Deployment Layer
- **Platform**: GCP Cloud Run
- **Containers**: Docker (python:3.11-slim base)
- **Storage**: GCS buckets
- **Monitoring**: Cloud Logging, Cloud Monitoring

---

## Error Handling Strategy

### Error Categories
1. **Transient** (Network timeout, temp file lock)
   - Auto-retry with exponential backoff (3 attempts max)

2. **Data Quality** (Missing genes, low alignment rate)
   - Log warning, continue with available data
   - Return partial results with quality flags

3. **User Input** (Invalid parameters, missing files)
   - Return clear error message
   - Suggest corrective actions

4. **Resource** (Out of memory, disk full)
   - Fail gracefully with cleanup
   - Log for operator intervention

5. **Critical** (Data corruption, system failure)
   - Halt pipeline immediately
   - Alert monitoring system
   - Preserve state for debugging

### Retry Configuration
```python
retry_config = {
    "max_attempts": 3,
    "initial_delay_seconds": 1,
    "max_delay_seconds": 30,
    "exponential_base": 2,
    "jitter": True
}
```

---

## Monitoring & Observability

### Metrics Collected
- **Request metrics**: Rate, latency (p50/p95/p99), error rate
- **Tool metrics**: Invocation counts, success rate, duration
- **Resource metrics**: CPU, memory, disk I/O
- **Business metrics**: Datasets processed, visualizations generated

### Logging Format
```json
{
  "timestamp": "2026-01-09T10:30:00Z",
  "level": "INFO",
  "server": "mcp-spatialtools",
  "tool": "calculate_spatial_autocorrelation",
  "request_id": "req_abc123",
  "patient_id": "PAT001-OVC-2025",
  "metrics": {
    "genes_analyzed": 8,
    "spots_processed": 900,
    "morans_i": 0.42,
    "p_value": 0.001,
    "duration_seconds": 2.3
  }
}
```

### Health Checks
```bash
# Each server exposes health endpoint
curl https://mcp-spatialtools-ondu7mwjpa-uc.a.run.app/health

{
  "status": "healthy",
  "version": "0.1.0",
  "revision": "mcp-spatialtools-00005-r4s",
  "uptime_seconds": 86400,
  "tools_available": 14,
  "dependencies": {
    "python": "3.11.13",
    "numpy": "1.26.4",
    "matplotlib": "3.8.3"
  }
}
```

---

## Future Enhancements

### Short-Term (Q1 2026)
- [ ] Real-time streaming analysis
- [ ] Interactive visualization dashboard
- [ ] Automated report generation
- [ ] Multi-sample batch processing

### Medium-Term (Q2-Q3 2026)
- [ ] Deploy remaining servers (deepcell, tcga, seqera, huggingface)
- [ ] Production Epic FHIR integration (replace mockepic)
- [ ] Support for additional spatial platforms (Visium HD, MERFISH, Xenium)
- [ ] Federated analysis across institutions

### Long-Term (Q4 2026+)
- [ ] Real-time clinical decision support
- [ ] Multi-modal integration (proteomics, metabolomics, ATAC-seq)
- [ ] Automated hypothesis generation
- [ ] Integration with lab information systems (LIMS)

---

## References

### MCP Protocol
- [MCP Specification 2025-11-20](https://modelcontextprotocol.io/specification/2025-11-20)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)

### Bioinformatics
- [10x Genomics Visium](https://www.10xgenomics.com/products/spatial-gene-expression)
- [STAR Aligner](https://github.com/alexdobin/STAR)
- [Spatial Transcriptomics Review](https://academic.oup.com/nar/article/53/12/gkaf536/8174767)

### Deployment
- [GCP Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**See Also:**
- [CSV_WORKFLOW.md](CSV_WORKFLOW.md) - Current PatientOne workflow details
- [SERVERS.md](SERVERS.md) - All 9 MCP servers documented
- [DEPLOYMENT.md](DEPLOYMENT.md) - GCP deployment procedures
