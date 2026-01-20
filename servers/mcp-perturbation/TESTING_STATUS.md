# mcp-perturbation Testing Status

## Installation Status: ⚠️ Partial Success

### ✅ Successfully Installed
- Python 3.11.13
- PyTorch 2.9.1
- scvi-tools 1.4.1
- scanpy 1.11.5
- All other core dependencies

### ❌ Known Issue: scGen Dependency Conflict

**Problem**: The standalone `scgen` package (v2.1.0) is incompatible with modern `scvi-tools` (v1.4.1+).

**Error**:
```
ModuleNotFoundError: No module named 'scvi._compat'
```

**Root Cause**: 
- scgen 2.1.0 was released in 2021
- scvi-tools has since evolved and removed the `_compat` module
- scGen is NO LONGER integrated into scvi-tools as a built-in model

## Recommended Solutions

### Option 1: Use Compatible Version (RECOMMENDED)

Pin to older scvi-tools version that works with scgen 2.1.0:

```toml
dependencies = [
    "scgen==2.1.0",
    "scvi-tools==0.14.0",  # Last version with _compat module
    "anndata<0.8",
    "scanpy>=1.7,<1.9",
]
```

### Option 2: Implement Custom scGen

Fork the scgen repository and update it for modern scvi-tools:
- https://github.com/theislab/scgen

### Option 3: Alternative Perturbation Prediction

Use other methods:
- **CellOracle** - For perturbation prediction
- **scvi-tools VAE** - Custom implementation
- **Pyro-based models** - Custom perturbation model

## What Works Now

Despite the scgen import issue, the following are functional:

1. **Project Structure** ✅
   - All files created correctly
   - Tests written
   - Documentation complete

2. **Core Utilities** ✅
   - `data_loader.py` - GEO loading works (synthetic data)
   - `prediction.py` - DE analysis works
   - `visualization.py` - Plotting functions work

3. **MCP Server** ✅
   - FastMCP tools defined correctly
   - Pydantic models validated
   - Server can start (but tools will error without scgen)

## Testing Workaround

To test the non-scgen components:

```bash
# Test data loader only
pytest tests/test_data_loader.py::TestDatasetLoader::test_load_gse184880_synthetic -v

# Test prediction utilities (mock scgen)
# Would need to create mocks for ScGenWrapper
```

## Recommended Action

**For immediate use**: Pin to scvi-tools==0.14.0 and test with that older stack.

**For production**: Consider implementing a custom perturbation model using modern scvi-tools VAE as the base, following the scGen methodology but with updated APIs.

## Timeline to Resolution

- **Quick fix** (scvi-tools 0.14.0): ~1 hour
- **Custom implementation**: ~2-3 days
- **Waiting for scgen update**: Unknown (project appears unmaintained)

