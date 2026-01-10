# Testing Strategy

---

## Test Workflows

### PatientOne End-to-End Tests

**Location:** `/tests/manual_testing/PatientOne-OvarianCancer/`

**TEST_3_SPATIAL.txt** - Spatial Transcriptomics Analysis
- **Status:** ✅ Production test
- **Data:** CSV files (coordinates, expression, annotations)
- **Workflow:** CSV/tabular workflow
- **Duration:** 3-5 minutes
- **Validations:** 
  - ✅ 900 spots loaded
  - ✅ 31 genes present
  - ✅ 6 regions annotated
  - ✅ Statistical results (differential expression, Moran's I, pathway enrichment)
  - ✅ 4 visualizations generated

---

## Unit Tests

**Location:** `/servers/mcp-spatialtools/tests/`

**Test Coverage:** >80% for production tools

**Key test files:**
- `test_differential_expression.py`
- `test_spatial_autocorrelation.py`
- `test_pathway_enrichment.py`
- `test_batch_correction.py`
- `test_visualizations.py`

**Running tests:**
```bash
cd servers/mcp-spatialtools
pytest tests/ -v
```

---

## Integration Tests

**Test complete workflows:**
1. Load CSV data
2. Run analysis tools
3. Generate visualizations
4. Integrate with mcp-multiomics

**Location:** `/tests/integration/`

---

## Test Data

**Synthetic Data:** `/data/patient-data/PAT001-OVC-2025/spatial/`
- visium_spatial_coordinates.csv (900 spots)
- visium_gene_expression.csv (31 genes)
- visium_region_annotations.csv (6 regions)

**Characteristics:**
- Realistic expression distributions
- Spatial patterns (immune exclusion, proliferation zones)
- Statistical power for analysis

---

See [PatientOne README](../../tests/manual_testing/PatientOne-OvarianCancer/README.md) for complete test documentation.
