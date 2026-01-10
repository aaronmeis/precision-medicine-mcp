# CSV/Tabular Data Workflow

**Status:** ✅ Production - Current Implementation
**Last Updated:** January 9, 2026
**Used In:** PatientOne end-to-end tests (TEST_3_SPATIAL.txt)

---

## Overview

The CSV workflow processes **pre-processed spatial transcriptomics data** in tabular format (CSV files). This is the **current implementation** used in all PatientOne tests and production deployments.

**Why CSV Instead of FASTQ?**
- Faster iteration (no alignment needed)
- Focuses on analysis rather than data processing
- Suitable for pre-processed Visium data
- Enables immediate statistical and visualization insights

---

## Data Format

### Input Files (3 CSV files required)

#### 1. `visium_spatial_coordinates.csv`
Spatial location of each spot on the tissue.

```csv
barcode,x,y
AAACAAGTATCTCCCA-1,2150,1300
AAACACCAATAACTGC-1,1800,2400
AAACAGAGCGACTCCT-1,2500,1800
...
```

**Columns:**
- `barcode`: Unique spot identifier (900 spots)
- `x`: X-coordinate in tissue space
- `y`: Y-coordinate in tissue space

**File Size:** ~34 KB
**Rows:** 901 (header + 900 spots)

#### 2. `visium_gene_expression.csv`
Gene expression values for each spot.

```csv
barcode,MKI67,PCNA,PIK3CA,AKT1,ABCB1,CD3D,CD8A,CD68,...
AAACAAGTATCTCCCA-1,450.2,320.5,180.3,220.1,95.4,15.2,8.3,45.6,...
AAACACCAATAACTGC-1,380.1,290.3,170.8,200.5,85.2,12.8,6.1,38.2,...
...
```

**Columns:**
- `barcode`: Spot identifier (matches coordinates file)
- 31 gene columns with normalized expression values

**Key Genes:**
- **Proliferation:** MKI67, PCNA, TOP2A
- **Resistance:** PIK3CA, AKT1, ABCB1, BCL2L1
- **Immune:** CD3D, CD8A, CD68, PDCD1

**File Size:** ~117 KB
**Rows:** 901 (header + 900 spots)

#### 3. `visium_region_annotations.csv`
Tissue region assignment for each spot.

```csv
barcode,region
AAACAAGTATCTCCCA-1,tumor_core
AAACACCAATAACTGC-1,tumor_proliferative
AAACAGAGCGACTCCT-1,tumor_interface
...
```

**Columns:**
- `barcode`: Spot identifier
- `region`: Tissue region annotation

**Regions (6 total):**
1. `tumor_core` - Central tumor mass
2. `tumor_proliferative` - High proliferation zone
3. `tumor_interface` - Tumor-stroma boundary
4. `stroma_immune` - Immune-rich stroma
5. `stroma` - General stromal tissue
6. `necrotic_hypoxic` - Necrotic/hypoxic areas

**File Size:** ~18 KB
**Rows:** 901 (header + 900 spots)

---

## Workflow Steps

### Step 1: Data Loading
**What happens:** Load CSV files into memory

```python
# Claude prompts mcp-spatialtools to load data
# Files are read from patient-data/PAT001-OVC-2025/spatial/

coordinates = pd.read_csv("visium_spatial_coordinates.csv")
expression = pd.read_csv("visium_gene_expression.csv")
regions = pd.read_csv("visium_region_annotations.csv")

# Result: 900 spots × 31 genes with (x,y) coordinates and region labels
```

**Validation:**
- ✅ All barcodes match across 3 files
- ✅ No missing values in coordinates
- ✅ All 31 expected genes present
- ✅ All 6 regions represented

### Step 2: Exploratory Analysis
**What happens:** Understand data distribution and spatial patterns

**Questions Claude can answer:**
- How many spots per region?
- What's the mean expression of MKI67 in tumor_core?
- Which genes show high variability?
- Are there spatial patterns in CD8A expression?

**Tools used:** Basic data queries (built into analysis tools)

### Step 3: Differential Expression Analysis
**Tool:** `perform_differential_expression`

**Purpose:** Identify genes with statistically significant differences between regions

**Example:**
```
Compare tumor_core vs stroma_immune regions:
- Which genes are upregulated in tumor_core?
- What's the statistical significance (p-value)?
- Which method to use? (Wilcoxon rank-sum test)
```

**Output:**
```json
{
  "comparison": "tumor_core vs stroma_immune",
  "method": "wilcoxon",
  "significant_genes": [
    {
      "gene": "MKI67",
      "mean_group1": 420.5,
      "mean_group2": 45.2,
      "fold_change": 9.3,
      "p_value": 0.0001,
      "adjusted_p_value": 0.003
    },
    ...
  ]
}
```

**Key Findings (PatientOne):**
- MKI67, PCNA highly expressed in tumor_proliferative
- CD8A LOW in tumor regions (immune exclusion)
- PIK3CA, AKT1 elevated in tumor_core (resistance)

### Step 4: Spatial Autocorrelation
**Tool:** `calculate_spatial_autocorrelation`

**Purpose:** Detect spatial clustering patterns (are similar values near each other?)

**Method:** Moran's I statistic
- Moran's I = +1: Perfect positive autocorrelation (clustering)
- Moran's I = 0: Random spatial pattern
- Moran's I = -1: Perfect negative autocorrelation (checkerboard)

**Example:**
```
Calculate Moran's I for CD8A expression:
- Are CD8+ cells clustered or dispersed?
- Is the pattern statistically significant?
```

**Output:**
```json
{
  "gene": "CD8A",
  "morans_i": 0.42,
  "p_value": 0.001,
  "interpretation": "Significant positive spatial autocorrelation - CD8+ cells are clustered"
}
```

**Key Findings (PatientOne):**
- CD8A: Clustered at tumor periphery (Moran's I = 0.42)
- MKI67: Strong clustering in proliferative zones (Moran's I = 0.68)
- Resistance genes: Heterogeneous distribution

### Step 5: Pathway Enrichment
**Tool:** `perform_pathway_enrichment`

**Purpose:** Identify enriched biological pathways from gene lists

**Databases:**
- GO (Gene Ontology): Biological processes, cellular components, molecular functions
- KEGG: Metabolic and signaling pathways
- Reactome: Curated biological pathways
- Hallmark: Cancer-relevant gene sets

**Example:**
```
Enrich genes upregulated in tumor_core:
- Input: [MKI67, PCNA, TOP2A, PIK3CA, AKT1, ABCB1, ...]
- Database: KEGG
- Method: Fisher's exact test with FDR correction
```

**Output:**
```json
{
  "pathway": "PI3K-AKT signaling pathway",
  "genes_in_pathway": ["PIK3CA", "AKT1", "mTOR", "RPS6KB1"],
  "p_value": 0.0001,
  "adjusted_p_value": 0.003,
  "enrichment_score": 4.2
}
```

**Key Findings (PatientOne):**
- PI3K/AKT/mTOR pathway activated (drug resistance)
- Cell cycle pathways enriched (proliferation)
- Immune response pathways depleted (exclusion)

### Step 6: Batch Correction (Optional)
**Tool:** `perform_batch_correction`

**Purpose:** Remove technical batch effects when analyzing multiple samples

**Methods:**
- ComBat: Empirical Bayes batch correction
- Harmony: Fast integration of datasets
- Scanorama: Mutual nearest neighbors

**When to use:**
- Multiple tissue sections
- Different sequencing runs
- Cross-patient comparisons

**Example:**
```
Correct batch effects across 3 patient samples:
- Method: ComBat
- Preserve biological variation
- Remove technical artifacts
```

**Note:** PatientOne uses single patient, so batch correction not needed in current tests.

### Step 7: Visualization
**Tools:** 4 visualization tools (see [VISUALIZATION.md](VISUALIZATION.md))

**Available visualizations:**
1. **Spatial Heatmap** - Expression overlaid on (x,y) coordinates
2. **Gene Expression Heatmap** - Clustered heatmap (genes × regions)
3. **Region Composition Chart** - Bar chart of spot counts
4. **Spatial Autocorrelation Plot** - Moran's I visualization

**Example:**
```
Generate spatial heatmap for CD8A:
- Show CD8+ T cell distribution across tissue
- Color scale: Low (blue) to High (red)
- Overlay on tissue coordinates
```

**Output:** PNG file with timestamp (e.g., `spatial_heatmap_CD8A_20260109_103000.png`)

### Step 8: Integration with Multi-Omics
**Tool:** `get_spatial_data_for_patient`

**Purpose:** Bridge spatial findings to multi-omics analysis

**What it does:**
- Extracts key spatial metrics
- Formats for mcp-multiomics consumption
- Enables cross-modality integration

**Output sent to mcp-multiomics:**
```json
{
  "patient_id": "PAT001-OVC-2025",
  "spatial_metrics": {
    "immune_infiltration": "LOW",
    "cd8_density": 5.2,
    "proliferation_index": 0.52,
    "resistance_score": 0.78,
    "spatial_heterogeneity": "HIGH"
  },
  "top_genes_by_region": {...}
}
```

---

## Expected Results (PatientOne)

### Spatial Patterns
- **Immune Exclusion:** CD8+ cells LOW in tumor core (~5-15 cells/mm²)
- **Proliferation:** MKI67, PCNA HIGH in tumor_proliferative region (45-55% positive)
- **Resistance:** PIK3CA, AKT1 elevated in tumor_core
- **Heterogeneity:** Spatial variation in resistance markers

### Statistical Findings
- **Differential Expression:** 8 genes significantly different between tumor vs stroma
- **Spatial Autocorrelation:** CD8A clustered (Moran's I = 0.42, p < 0.001)
- **Pathway Enrichment:** PI3K/AKT/mTOR pathway activated (p < 0.001)

### Clinical Implications
- Immune exclusion phenotype → immunotherapy may have limited efficacy
- PI3K/AKT activation → consider PI3K inhibitors (alpelisib)
- Spatial heterogeneity → tumor sampling bias considerations

---

## Running the Workflow

### Via Claude Desktop (Local)
1. Configure `claude_desktop_config.json` with mcp-spatialtools
2. Open Claude Desktop
3. Copy TEST_3_SPATIAL.txt prompt
4. Claude orchestrates analysis automatically

### Via Claude API (Cloud)
```python
import anthropic

client = anthropic.Anthropic(api_key="your_key")

response = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Analyze spatial transcriptomics data for patient PAT001-OVC-2025..."
    }],
    mcp_servers=[{
        "type": "url",
        "url": "https://mcp-spatialtools-ondu7mwjpa-uc.a.run.app/sse",
        "name": "spatialtools"
    }],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "spatialtools"}],
    betas=["mcp-client-2025-11-20"]
)
```

---

## Data Requirements

### Minimum Requirements
- 3 CSV files (coordinates, expression, regions)
- At least 100 spots (900 is typical for Visium)
- At least 10 genes (31 is typical)
- At least 2 regions for differential expression

### Recommended Format
- UTF-8 encoding
- Comma-separated (not tab or semicolon)
- Header row with column names
- Consistent barcode identifiers across files

### Quality Checks
- ✅ No duplicate barcodes
- ✅ No missing values in coordinates
- ✅ Expression values > 0
- ✅ Region labels are consistent

---

## Troubleshooting

### Common Issues

**Issue:** "Barcode mismatch between files"
- **Cause:** Different barcode sets in coordinates vs expression files
- **Fix:** Ensure all 3 CSV files use the same barcode identifiers

**Issue:** "Gene not found in expression matrix"
- **Cause:** Requested gene doesn't exist in the 31-gene panel
- **Fix:** Check available genes with `list_genes` query

**Issue:** "Insufficient spots in region"
- **Cause:** Region has < 10 spots (too small for statistics)
- **Fix:** Combine small regions or exclude from analysis

**Issue:** "Visualization output not generated"
- **Cause:** Output directory doesn't exist or lacks permissions
- **Fix:** Check `SPATIAL_OUTPUT_DIR` environment variable

---

## Performance

### Typical Execution Times (900 spots, 31 genes)
| Operation | Time | Notes |
|-----------|------|-------|
| Load CSV files | 1-2s | In-memory loading |
| Differential expression | 2-5s | Per comparison |
| Spatial autocorrelation | 1-3s | Per gene |
| Pathway enrichment | 5-10s | Database lookup + stats |
| Generate visualization | 2-5s | Per plot |
| **Full PatientOne TEST_3** | **3-5 min** | Complete analysis |

### Scalability
- ✅ Handles up to 5,000 spots efficiently
- ✅ Supports up to 500 genes
- ✅ Multiple patients processed sequentially
- ⚠️ Parallel processing requires multiple server instances

---

## Next Steps

### After CSV Analysis
1. Review visualization outputs
2. Interpret statistical findings
3. Integrate with multi-omics data (mcp-multiomics)
4. Link to clinical data (mcp-epic)
5. Compare to histology (mcp-openimagedata)

### See Also
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - Detailed tool documentation
- [VISUALIZATION.md](VISUALIZATION.md) - Visualization tool guide
- [PatientOne TEST_3](../../tests/manual_testing/PatientOne-OvarianCancer/implementation/TEST_3_SPATIAL.txt) - Complete test workflow
