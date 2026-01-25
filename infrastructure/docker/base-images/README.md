# Base Docker Images for Precision Medicine

Three base images for bioinformatics tools.

**IMPORTANT: These images are for LOCAL USE ONLY. Do not push to Docker Hub or any remote registry.**

## Images

| Image | Purpose | Base | Size |
|-------|---------|------|------|
| `python-base` | Python bioinformatics tools | python:3.12-slim | ~500MB |
| `r-base` | R/Bioconductor analysis | rocker/r-ver:4.3.2 | ~2-3GB |
| `tensorflow-base` | ML/DL tools (GPU) | tensorflow:2.15.0 | ~8-10GB |
| `tensorflow-base` | ML/DL tools (CPU) | tensorflow:2.15.0-cpu | ~4-5GB |

## Build

### Windows

**Build all images:**
```cmd
build-images.bat
```

**Build a single image:**
```cmd
build-single.bat python-base
build-single.bat r-base
build-single.bat tensorflow-base
```

**Verify images:**
```cmd
verify-images.bat
```

**Clean/remove images:**
```cmd
clean-images.bat
```

**Security scanning:**
```cmd
scan-images.bat              # Scan all images
scan-images.bat python-base  # Scan specific image
```

### Linux/macOS

**Build all:**
```bash
docker build -t precision-medicine/python-base:latest ./python-base
docker build -t precision-medicine/r-base:latest ./r-base
docker build -t precision-medicine/tensorflow-base:latest ./tensorflow-base
```

**Build individual:**
```bash
docker build -t precision-medicine/python-base:latest ./python-base
```

## Security Scanning with Trivy

All build scripts automatically scan images for vulnerabilities using [Trivy](https://trivy.dev/) if it's installed.

### Installing Trivy

**Windows:**
```cmd
# Using Chocolatey (Recommended)
choco install trivy

# Or using winget (if available)
winget install Aqua.Trivy

# Or manual download from GitHub releases
# https://github.com/aquasecurity/trivy/releases
```

**Note:** For detailed Windows installation instructions including manual setup and PATH configuration, see [INSTALL_TRIVY.md](INSTALL_TRIVY.md)

**Linux:**
```bash
# Debian/Ubuntu
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Or using curl
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**macOS:**
```bash
brew install trivy
```

### How It Works

**Automatic Scanning:**
- When you run `build-images.bat` or `build-single.bat`, Trivy automatically scans images after successful builds
- Scans check for **CRITICAL** and **HIGH** severity vulnerabilities only
- Reports are saved to `scan-reports/` directory

**Manual Scanning:**
Use `scan-images.bat` to scan existing images without rebuilding:
```cmd
# Scan all images
scan-images.bat

# Scan specific image
scan-images.bat tensorflow-base
```

### Scan Reports

Reports are saved in the `scan-reports/` directory:
- `python-base-trivy.txt` - Python base image scan results
- `r-base-trivy.txt` - R base image scan results
- `tensorflow-base-trivy.txt` - TensorFlow base image scan results

**Reading Reports:**
Each report shows:
- Vulnerable packages and their versions
- CVE identifiers
- Severity levels (CRITICAL, HIGH)
- Fixed versions (if available)
- Links to vulnerability details

### Best Practices

1. **Run scans regularly** - Re-scan images periodically as new vulnerabilities are discovered
2. **Review reports** - Check `scan-reports/` after each build
3. **Update base images** - Rebuild with latest base images to get security patches
4. **Focus on CRITICAL/HIGH** - Scripts filter for serious vulnerabilities to reduce noise
5. **Keep Trivy updated** - Update Trivy regularly to get the latest vulnerability database

### Troubleshooting

**Trivy not found:**
- Make sure Trivy is installed and in your PATH
- Restart your terminal after installation
- Verify with: `trivy --version`

**Scan takes too long:**
- First scan downloads vulnerability database (~200MB)
- Subsequent scans use cached database and are much faster
- Update database manually: `trivy image --download-db-only`

**Exit code 1 errors:**
- This is normal when vulnerabilities are found
- Scripts handle this gracefully and continue
- Check the report files for details

## Important Notes

- These images are designed for **local development and testing only**
- **Do not push** these images to Docker Hub, GitHub Container Registry, or any other remote registry
- Images contain standard bioinformatics tools and should be rebuilt locally as needed
- The `precision-medicine/` prefix is just for local organization, not a registry path
- **Security**: Regularly scan images and rebuild with updated base images to address vulnerabilities

## Packages Included

### Python Base
- numpy, scipy, pandas, scikit-learn, statsmodels
- biopython, pysam, pyvcf3, h5py
- matplotlib, seaborn

### R Base
- tidyverse, data.table, Matrix
- DESeq2, edgeR, limma, clusterProfiler
- GenomicRanges, SummarizedExperiment

### TensorFlow Base
**Optimized for size** (reduced from ~18GB to ~8-10GB for GPU, ~4-5GB for CPU)

**Included:**
- tensorflow, keras, tensorflow-hub
- numpy, scipy, pandas, scikit-learn, scikit-image
- opencv-python-headless, Pillow, tifffile, imageio
- matplotlib, seaborn

**Removed to reduce size** (can be added back if needed):
- transformers, datasets (Hugging Face - adds ~3GB)
- cellpose (specialized imaging - adds ~500MB-1GB)

**GPU vs CPU:**
- Edit the Dockerfile to switch between GPU and CPU versions
- GPU: Full CUDA support (~8-10GB)
- CPU: Smaller, CPU-only (~4-5GB)
- Simply comment/uncomment the appropriate FROM line
