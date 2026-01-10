# Visualization Tools

4 visualization tools added Jan 8-9, 2026.

All tools generate publication-quality PNG images with timestamps.

---

## 1. generate_spatial_heatmap

**Purpose:** Visualize gene expression overlaid on tissue spatial coordinates

**Parameters:**
- `gene` (string, required): Gene name to visualize
- `colormap` (string, optional): Matplotlib colormap (default: "viridis")
- `output_filename` (string, optional): Custom filename (default: auto-generated with timestamp)

**Output:**
```json
{
  "status": "success",
  "output_file": "/path/to/spatial_heatmap_CD8A_20260109_103000.png",
  "gene": "CD8A",
  "spots_plotted": 900
}
```

**Example Usage:**
```
Generate a spatial heatmap for CD8A expression showing T cell distribution across the tissue.
```

---

## 2. generate_gene_expression_heatmap

**Purpose:** Clustered heatmap showing genes × regions with hierarchical clustering

**Parameters:**
- `genes` (list, required): List of gene names (e.g., ["MKI67", "CD8A", "PIK3CA"])
- `cluster_genes` (boolean, optional): Cluster genes (default: True)
- `cluster_regions` (boolean, optional): Cluster regions (default: True)
- `colormap` (string, optional): Matplotlib colormap (default: "RdBu_r")

**Output:** PNG with clustered heatmap showing mean expression per region

**Example Usage:**
```
Generate clustered heatmap for 8 key genes (MKI67, PCNA, PIK3CA, AKT1, ABCB1, CD3D, CD8A, CD68) across all 6 tissue regions.
```

---

## 3. generate_region_composition_chart

**Purpose:** Bar chart showing number of spots per tissue region

**Parameters:**
- `output_filename` (string, optional): Custom filename

**Output:** Bar chart PNG showing spot counts for each of the 6 regions

**Example Usage:**
```
Show the distribution of 900 spots across the 6 tissue regions.
```

---

## 4. visualize_spatial_autocorrelation

**Purpose:** Visualize Moran's I spatial autocorrelation results

**Parameters:**
- `gene` (string, required): Gene name
- `morans_i` (float, required): Moran's I statistic value
- `p_value` (float, required): Statistical significance
- `output_filename` (string, optional): Custom filename

**Output:** Scatter plot showing spatial pattern with Moran's I annotation

**Example Usage:**
```
Visualize spatial autocorrelation for CD8A showing Moran's I = 0.42 (p < 0.001), indicating significant clustering of CD8+ T cells.
```

---

## Output Location

**Default directory:** `SPATIAL_OUTPUT_DIR` environment variable
- Local: `/workspace/output/visualizations/`
- GCP: `/app/data/output/visualizations/`

**Filename format:** `{tool_name}_{gene}_{timestamp}.png`
- Example: `spatial_heatmap_CD8A_20260109_103000.png`

---

## Technical Details

**Dependencies:**
- matplotlib >= 3.8.0
- seaborn >= 0.13.0 (for heatmaps)
- pandas >= 2.2.0 (for data manipulation)

**Image specifications:**
- Format: PNG
- DPI: 300 (publication quality)
- Size: 10×8 inches (default)
- Color depth: 24-bit RGB

---

See [CSV_WORKFLOW.md](CSV_WORKFLOW.md) Step 7 for workflow integration.
