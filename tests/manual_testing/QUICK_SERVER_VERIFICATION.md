# Quick MCP Server Verification Prompt

**Purpose:** Verify all 9 MCP servers are connected and working in Claude Desktop

**Time:** 2-3 minutes

**Copy-paste this prompt into Claude Desktop:**

---

## Quick Server Verification

Please help me verify all 9 MCP servers are working correctly. For each server, call ONE simple tool to confirm it's connected:

1. **fgbio** - List available reference genomes
2. **multiomics** - Show HAllA analysis capabilities
3. **spatialtools** - List available spatial analysis tools
4. **tcga** - Show TCGA project information
5. **openimagedata** - List available image datasets
6. **seqera** - Show Nextflow workflow capabilities
7. **huggingface** - List available genomic models
8. **deepcell** - Show cell segmentation model info
9. **mockepic** - Get patient demographics for patient-001

For each server, just confirm:
- ✅ Server connected
- ✅ Tool executed successfully
- ✅ Returned expected data format

Don't do any actual analysis - just verify connectivity and basic functionality.

---

## Expected Output Format

You should see output like:

```
1. fgbio ✅
   - Connected successfully
   - Available genomes: hg38, mm10, etc.

2. multiomics ✅
   - Connected successfully
   - HAllA tools available: integrate_multiomics, etc.

[... continues for all 9 servers ...]

Summary: 9/9 servers verified successfully
```

---

## If Any Server Fails

If a server doesn't respond:
1. Check Claude Desktop → Settings → Developer → MCP Servers
2. Look for red indicators
3. Restart Claude Desktop
4. Check server logs in ~/Library/Logs/Claude/

---

**After verification:** If all servers show ✅, you're ready for full PatientOne workflow testing!
