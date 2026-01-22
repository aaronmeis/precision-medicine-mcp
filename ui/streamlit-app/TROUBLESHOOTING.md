# Troubleshooting Guide

Common issues and solutions for the Streamlit MCP Chat interface.

---

## API Key Issues

### "API Key Missing" Error

```bash
# Set the environment variable
export ANTHROPIC_API_KEY=your_key_here

# Or create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### "Invalid API key" Error

```bash
# Check ANTHROPIC_API_KEY is set correctly
echo $ANTHROPIC_API_KEY

# Verify no extra spaces or quotes
# Should be: sk-ant-api03-...

# For Gemini provider:
echo $GEMINI_API_KEY
```

---

## Server Connection Issues

### Servers Not Responding

1. **Check server status:** [GCP Cloud Run Console](https://console.cloud.google.com/run)
2. **Verify URLs** in `utils/mcp_config.py` match deployed URLs
3. **Test individual server:**
   ```bash
   curl https://mcp-spatialtools-ondu7mwjpa-uc.a.run.app/sse
   ```

### Connection Errors

```python
# Error: "Connection refused"
# Fix: Verify server URLs are correct (check deployment docs)

# Error: "Rate limit exceeded"
# Fix: Wait 60 seconds, then retry (Anthropic API rate limits)

# Error: "Invalid API key"
# Fix: Check ANTHROPIC_API_KEY is set correctly
```

### Timeout Errors

```bash
# Error: "Request timeout after 300s"
# Fix: This is normal for long-running analyses (e.g., model training)
# The MCP server is still processing. For training tasks:
# - GEARS training: 5-10 minutes is normal
# - Spatial analysis: 2-5 minutes typical
# - Multi-omics: 10-20 minutes for full preprocessing

# Workaround:
# 1. Use smaller datasets for testing
# 2. Increase timeout in deploy script (--timeout 600)
# 3. Break workflow into smaller steps
```

---

## Performance Issues

### Slow Responses

**Optimization strategies:**
- Use **claude-haiku-4** for faster responses (vs Sonnet/Opus)
- Reduce **max_tokens** slider to 2048 or 1024
- Select fewer MCP servers (only enable what you need)
- Check GCP Cloud Run logs for server performance bottlenecks

**Check server logs:**
```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-mcp-chat" \
  --limit 50 --project precision-medicine-poc
```

### High Latency

**Typical response times:**
- Simple query (list tools): 1-3 seconds
- Spatial analysis: 5-15 seconds
- Multi-omics preprocessing: 30-120 seconds
- GEARS model training: 5-10 minutes

**If slower than expected:**
1. Check Cloud Run cold starts (first request after idle)
2. Verify sufficient memory allocation (1GB minimum)
3. Monitor Cloud Run metrics in GCP Console

---

## File Upload Issues

### File Validation Failed

```bash
# Error: "Invalid file - Magic bytes mismatch"
# Fix: Ensure file is not corrupted and matches the extension
# For FASTQ files: Check file starts with @ character
# For FASTA files: Check file starts with > character

# Error: "File too large (exceeded 100MB limit)"
# Fix: Use GCS integration for large files instead of local upload

# Error: "Invalid FASTQ format"
# Fix: Validate FASTQ headers follow format: @identifier description
# Example valid header: @SRR12345678.1 HWI-ST1234:123:ABCDEFG:1:1:1234:5678

# Error: "Unsupported file type"
# Fix: Check supported formats in FILE_HANDLING.md
# Only 21 bioinformatics formats are supported
```

### GCS Access Issues

```bash
# Error: "Invalid GCS URI"
# Fix: Use format gs://bucket-name/path/to/file
# Ensure no spaces, must start with gs://

# Error: "File not found in GCS"
# Fix: Verify the bucket and path are correct
# Check: gsutil ls gs://your-bucket/your-file

# Error: "Permission denied accessing GCS"
# Fix: Grant service account access to bucket
# Run: gsutil iam ch serviceAccount:SERVICE_ACCOUNT:objectViewer gs://bucket-name

# For local testing with GCS:
# Fix: Authenticate with application default credentials
# Run: gcloud auth application-default login
```

---

## Provider-Specific Issues

### Claude Provider Issues

```bash
# Error: "Provider not available"
# Fix: Ensure ANTHROPIC_API_KEY is set
# Check: echo $ANTHROPIC_API_KEY

# Error: "Model not found: claude-sonnet-4-20250514"
# Fix: Model IDs change over time, check latest available models
# Visit: https://docs.anthropic.com/claude/docs/models-overview
```

### Gemini Provider Issues

```bash
# Error: "Gemini provider not available"
# Fix: Ensure GEMINI_API_KEY is set and google-genai package installed
# Check key: echo $GEMINI_API_KEY
# Install: pip install google-genai>=1.55.0

# Error: "Connection to MCP server failed"
# Fix: Gemini uses SSE connections - check firewall rules
# Ensure outbound HTTPS allowed to *.run.app domains

# Error: "Maximum tool calling iterations reached"
# Fix: This happens with complex queries requiring many tool calls
# Workaround: Break query into smaller steps

# Error: "thought_signature missing in function call"
# Fix: This should be handled automatically. If persists:
# 1. Restart Streamlit app
# 2. Check you're using latest version (git pull)
# 3. Report as bug if continues
```

---

## Deployment Issues

### Local Development

```bash
# Error: "ModuleNotFoundError: No module named 'streamlit'"
# Fix: Install dependencies
pip install -r requirements.txt

# Error: "Port 8501 already in use"
# Fix: Kill existing Streamlit process
lsof -ti:8501 | xargs kill -9

# Error: ".env file not found"
# Fix: Create from template
cp .env.example .env
# Then edit .env with your API keys
```

### Cloud Run Deployment

```bash
# Error: "Failed to build container image"
# Fix: Check Dockerfile syntax and build locally first
docker build -t streamlit-mcp-chat .
docker run -p 8501:8501 streamlit-mcp-chat

# Error: "Service deployment failed with error 403"
# Fix: Check you have Cloud Run Admin role
gcloud projects get-iam-policy precision-medicine-poc

# Error: "Container failed to start"
# Fix: Check Cloud Run logs for startup errors
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

---

## Data Processing Errors

### Multiomics Server Errors

```bash
# Error: "Batch column not found in metadata"
# Fix: Ensure metadata CSV has 'Batch' column
# Required columns: Sample, Batch, Condition

# Error: "HAllA chunking failed"
# Fix: Dataset too large, reduce features
# Use top 1000 most variable genes instead of all genes

# Error: "No significant associations found"
# Fix: This may be expected with small datasets
# Try lowering FDR threshold or using NOMINAL p-values
```

### Spatial Server Errors

```bash
# Error: "Invalid H5AD format"
# Fix: Ensure file is valid AnnData object
# Required: obs (cell metadata), var (gene metadata), X (expression matrix)

# Error: "STAR alignment failed"
# Fix: STAR requires significant memory (32GB+)
# Use pre-aligned data or run STAR locally

# Error: "Cell type deconvolution failed"
# Fix: Requires gene expression data with proper format
# Ensure genes are in rows, spots in columns
```

### Perturbation Server Errors

```bash
# Error: "Dataset not found: GSE184880"
# Fix: Check internet connection for GEO download
# Or provide local H5AD file instead

# Error: "Model training failed with NaN loss"
# Fix: Data quality issue - check for:
# - Missing values (>50% per gene)
# - Insufficient cells (<1000)
# - Gene name mismatches

# Error: "Prediction failed: model not trained"
# Fix: Must run training before prediction
# Use complete workflow: load → setup → train → predict
```

---

## Orchestration Trace Issues

### Trace Not Showing

```bash
# Issue: "No MCP server calls in this response"
# Reason: Claude/Gemini answered without calling tools
# Fix: Rephrase query to be more specific about analysis needed
# Example: Instead of "Tell me about BRCA1"
# Use: "Query the gene annotations for BRCA1 and show its genomic coordinates"

# Issue: Trace shows 0 calls but tools were clearly used
# Reason: For Gemini, metadata not being captured
# Fix: Should be fixed in latest version. If persists:
# 1. Check you have latest code (git pull)
# 2. Restart Streamlit app
```

---

## Getting Help

### Check Logs

**Local development:**
```bash
# Streamlit logs in terminal where you ran `streamlit run app.py`
# Look for errors with "ERROR" or "WARNING"
```

**Cloud Run:**
```bash
# View recent logs
gcloud logging read \
  "resource.labels.service_name=streamlit-mcp-chat" \
  --limit 100 --project precision-medicine-poc

# Filter for errors only
gcloud logging read \
  "resource.labels.service_name=streamlit-mcp-chat AND severity>=ERROR" \
  --limit 50 --project precision-medicine-poc
```

### Report Issues

If you can't resolve the issue:

1. **Check GitHub Issues:** [precision-medicine-mcp/issues](https://github.com/lynnlangit/precision-medicine-mcp/issues)
2. **Gather diagnostic info:**
   - Error message (full text)
   - Steps to reproduce
   - Environment (local vs Cloud Run)
   - Provider (Claude vs Gemini)
   - MCP servers being used
3. **Create new issue** with template

---

## Common Gotchas

### ❌ Don't Do This

```bash
# Don't use relative paths for files
# Bad: ./data/file.fastq
# Good: /absolute/path/to/data/file.fastq

# Don't mix local and GCS files in same query
# Bad: "Analyze local file.csv and gs://bucket/file2.csv together"
# Good: Upload both to GCS or both locally

# Don't exceed rate limits
# Bad: Run 100 queries in rapid succession
# Good: Add delays between queries (1-2 seconds)

# Don't use production API keys in .env files committed to git
# Bad: Committing .env with real keys
# Good: Use .env.example as template, .gitignore .env
```

### ✅ Best Practices

- Start with small test datasets before scaling up
- Use appropriate model for task (Haiku for speed, Sonnet for quality)
- Enable only needed MCP servers to reduce latency
- Monitor costs using Cloud Run metrics dashboard
- Test locally before deploying to Cloud Run
- Keep API keys secure (never commit to git)

---

**Related Documentation:**
- [Main README](README.md)
- [File Handling Guide](FILE_HANDLING.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Provider Architecture](providers/README.md)
