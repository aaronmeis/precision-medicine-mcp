# Tool Reference - mcp-spatialtools

All 14 tools with parameters, examples, and expected outputs.

---

## Analysis Tools

### 1. filter_quality
Quality filtering of spatial barcodes and reads.
- **Status:** Implemented (requires FASTQ input)
- **Use Case:** FASTQ workflow only
- See [FASTQ_WORKFLOW.md](FASTQ_WORKFLOW.md)

### 2. split_by_region
Segment spatial data by tissue regions.
- **Status:** Implemented
- **Use Case:** Both CSV and FASTQ workflows
- Splits spots into user-defined regions

### 3. align_spatial_data  
STAR alignment of spatial transcriptomics reads.
- **Status:** Implemented (requires STAR aligner + genome indices)
- **Use Case:** FASTQ workflow only
- See [FASTQ_WORKFLOW.md](FASTQ_WORKFLOW.md)

### 4. merge_tiles
Combine multiple spatial tiles into single dataset.
- **Status:** Implemented
- **Use Case:** Multi-tile experiments
-Used when tissue spans multiple capture areas

### 5. calculate_spatial_autocorrelation
**Status:** ✅ Production (CSV Workflow)

Compute Moran's I or Geary's C spatial autocorrelation statistics.

**Parameters:**
- `gene`: Gene name to analyze
- `method`: "morans_i" or "gearys_c"
- `weight_type`: "distance" or "knn"

**Returns:**
```json
{
  "gene": "CD8A",
  "method": "morans_i",
  "statistic": 0.42,
  "p_value": 0.001,
  "z_score": 3.2
}
```

### 6. perform_differential_expression
**Status:** ✅ Production (CSV Workflow)

Statistical testing between sample groups.

**Parameters:**
- `group1_spots`: List of spot barcodes for group 1
- `group2_spots`: List of spot barcodes for group 2
- `method`: "wilcoxon", "ttest", or "deseq2_style"

**Returns:** List of genes with fold change, p-value, adjusted p-value

### 7. perform_batch_correction
**Status:** ✅ Production (Multi-sample)

Remove batch effects across samples.

**Methods:** ComBat, Harmony, Scanorama
**Use Case:** Cross-patient or multi-section analysis

### 8. perform_pathway_enrichment
**Status:** ✅ Production (CSV Workflow)

Gene set enrichment analysis.

**Databases:** GO, KEGG, Reactome, Hallmark
**Method:** Fisher's exact test with FDR correction

### 9. deconvolve_cell_types
**Status:** ⚠️ Synthetic (returns mock signatures)

Cell type deconvolution from bulk spatial data.

**Methods:** CIBERSORTx, EPIC, quanTIseq (mocked)
**Future:** Will integrate real deconvolution algorithms

### 10. get_spatial_data_for_patient
**Status:** ✅ Production (Bridge Tool)

Extract spatial metrics for multi-omics integration.

**Returns:** JSON with spatial findings for mcp-multiomics

---

## Visualization Tools

### 11. generate_spatial_heatmap
**Status:** ✅ Production (Added Jan 8, 2026)

Create spatial heatmap with gene expression overlaid on tissue coordinates.

**Parameters:**
- `gene`: Gene to visualize
- `colormap`: matplotlib colormap (default: "viridis")
- `output_filename`: Optional custom filename

**Output:** PNG file with timestamp

### 12. generate_gene_expression_heatmap
**Status:** ✅ Production (Added Jan 8, 2026)

Clustered heatmap showing genes × regions.

**Parameters:**
- `genes`: List of gene names
- `cluster_genes`: Boolean (default: True)
- `cluster_regions`: Boolean (default: True)

**Output:** Clustered PNG heatmap

### 13. generate_region_composition_chart
**Status:** ✅ Production (Added Jan 8, 2026)

Bar chart showing spot counts per region.

**Output:** Bar chart PNG

### 14. visualize_spatial_autocorrelation
**Status:** ✅ Production (Added Jan 9, 2026)

Visualize Moran's I spatial autocorrelation results.

**Parameters:**
- `gene`: Gene name
- `morans_i`: Moran's I value
- `p_value`: Statistical significance

**Output:** Scatter plot with spatial pattern visualization

---

See [VISUALIZATION.md](VISUALIZATION.md) for detailed visualization tool guide.
