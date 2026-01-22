# File Upload & Data Access

The Streamlit UI supports two methods for providing data files to MCP servers for analysis.

---

## Method 1: Local File Upload

Upload bioinformatics files directly from your computer with comprehensive validation.

### Supported Formats (21+)

- **Sequence Data:** FASTA (.fasta, .fa, .fna), FASTQ (.fastq, .fq)
- **Genomic Variants:** VCF (.vcf)
- **Annotations:** GFF (.gff), GTF (.gtf), BED (.bed)
- **Tabular Data:** CSV (.csv), TSV (.tsv), Tab-delimited (.tab), Text (.txt)
- **Structured Data:** JSON (.json)
- **Single-cell/Spatial:** H5AD (.h5ad), HDF5 (.h5)
- **Images:** PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)
- **Alignment:** BAM (.bam)

### Security Features

- ✅ File extension whitelist validation
- ✅ Magic bytes verification for binary formats
- ✅ Content format validation for text files
- ✅ Filename sanitization (path traversal protection)
- ✅ Size limits (default 100MB, configurable)
- ✅ FASTQ/FASTA header validation
- ✅ VCF format validation

### How to Use

1. In the sidebar, find the **"📁 File Upload"** section
2. Click **"Browse files"** or drag and drop files
3. Files are validated automatically - validation results shown with checkmarks or errors
4. For small files (< 50KB), content is included inline for Claude to analyze directly
5. Ask Claude to analyze: "Perform QC analysis on the uploaded FASTQ file"

### Example

```bash
# Upload a FASTQ file
patient_001.fastq (5.2 MB)

# Then ask:
"Validate the quality of this FASTQ file and summarize the read statistics"
```

---

## Method 2: Google Cloud Storage (GCS) Access

Provide GCS URIs to access files stored in Google Cloud Storage buckets. This is ideal for:
- Large files that exceed upload limits
- Files already stored in GCS from previous analyses
- Cloud-to-cloud data transfer (faster than local upload)
- MCP servers running on Cloud Run with GCS service account access

### How to Use

1. In the sidebar, below the file upload section, find **"Or provide GCS bucket path"**
2. Enter a GCS URI in the format: `gs://bucket-name/path/to/file.fastq`
3. The app validates the URI format and displays metadata
4. For small text files (< 50KB), content is automatically downloaded and included inline
5. For large files, the GCS URI is passed directly to MCP tools on Cloud Run
6. MCP servers access the file using their service account permissions

### Example

```bash
# Enter GCS URI:
gs://precision-medicine-data/patient-001/spatial_data.h5ad

# Then ask:
"Perform cell type deconvolution on the spatial transcriptomics data"
```

### GCS Setup Requirements

For Cloud Run MCP servers to access GCS files, ensure:
1. GCS bucket exists in the same GCP project (or has proper IAM permissions)
2. Cloud Run service account has `roles/storage.objectViewer` on the bucket
3. Files are in supported formats

### Grant Access

```bash
# Grant Cloud Run service account access to GCS bucket
PROJECT_NUMBER=$(gcloud projects describe precision-medicine-poc --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectViewer gs://your-bucket-name
```

---

## File Access Architecture

```
Local Files (< 50KB):
  User Upload → Streamlit → File Content Inline → Claude API → Response

Local Files (Large):
  User Upload → Streamlit → File Metadata → Claude API → "File available for analysis"

GCS Files (Small):
  GCS URI → Streamlit → Download Content → Inline → Claude API → Response

GCS Files (Large):
  GCS URI → Streamlit → Metadata → Claude API → MCP Server → GCS Direct Access → Analysis Results
```

### Key Points

- **Small files** (< 50KB): Content included inline for Claude to analyze directly
- **Large files**: Metadata passed to Claude; MCP tools access files directly
- **GCS files**: Best for Cloud Run MCP servers (cloud-to-cloud access)
- **Local files**: Best for quick testing with small datasets

---

## Troubleshooting File Issues

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

**Related Documentation:**
- [Main README](README.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Guide](DEPLOYMENT.md)
