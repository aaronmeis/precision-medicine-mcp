# Docker Infrastructure for Precision Medicine Platform

This directory contains Docker-based infrastructure for the Precision Medicine platform, including containerized bioinformatics tools and analysis environments.

## Contents

### [base-images/](base-images/)
Docker base images for bioinformatics and machine learning workflows.

**Images Available:**
- **python-base** (~500MB) - Python 3.12 with bioinformatics libraries
- **r-base** (~2-3GB) - R with Bioconductor packages for genomics analysis
- **tensorflow-base** (~8-10GB GPU / ~4-5GB CPU) - TensorFlow with ML/DL tools

**Features:**
- ✅ Automated build scripts for Windows
- ✅ Integrated Trivy security scanning
- ✅ Size-optimized images
- ✅ Non-root user execution
- ✅ Local-only (not pushed to registries)

**Quick Start:**
```cmd
cd base-images
build-images.bat              # Build all images
build-single.bat python-base  # Build specific image
scan-images.bat               # Scan for vulnerabilities
```

📖 **[Full Documentation](base-images/README.md)**

## Architecture

All Docker images follow these principles:

### Security
- Run as non-root user (`biouser`)
- Regular vulnerability scanning with Trivy
- Minimal attack surface (slim base images)
- No unnecessary tools or dependencies

### Size Optimization
- Multi-stage builds where applicable
- Aggressive layer cleanup
- Combined RUN statements
- Removal of build dependencies post-installation
- No cache directories (`--no-cache-dir`)

### Local Development
- **IMPORTANT:** All images are for LOCAL USE ONLY
- Do NOT push to Docker Hub or any remote registry
- Tagged with `precision-medicine/` prefix for organization
- Designed for development and testing environments

## Requirements

- **Docker Desktop** - Latest version
- **Windows 10/11** or **Linux/macOS**
- **Disk Space:**
  - Minimum: 15GB free
  - Recommended: 30GB+ (for all images)
- **Memory:** 8GB+ RAM (16GB+ recommended for TensorFlow)

## Installation & Setup

### 1. Install Docker Desktop

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop
- Install and restart
- Ensure WSL 2 backend is enabled (Settings → General)

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install --cask docker
```

### 2. Install Trivy (Optional but Recommended)

**Windows:**
```cmd
choco install trivy
```

**Linux:**
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**macOS:**
```bash
brew install trivy
```

📖 **[Detailed Trivy Installation Guide](base-images/INSTALL_TRIVY.md)**

### 3. Build Images

```cmd
cd base-images
build-images.bat  # Windows
# or
./build-images.sh  # Linux/macOS (if provided)
```

## Usage Examples

### Running Containers

**Python Environment:**
```cmd
docker run -it --rm -v "%CD%:/data" precision-medicine/python-base:latest
```

**R Environment:**
```cmd
docker run -it --rm -v "%CD%:/data" precision-medicine/r-base:latest
```

**TensorFlow (GPU):**
```cmd
docker run -it --rm --gpus all -v "%CD%:/data" precision-medicine/tensorflow-base:latest
```

**TensorFlow (CPU):**
```cmd
docker run -it --rm -v "%CD%:/data" precision-medicine/tensorflow-base:latest
```

### Running Scripts

**Python Script:**
```cmd
docker run --rm -v "%CD%:/data" precision-medicine/python-base:latest python /data/script.py
```

**R Script:**
```cmd
docker run --rm -v "%CD%:/data" precision-medicine/r-base:latest Rscript /data/analysis.R
```

### Interactive Sessions

**Jupyter Notebook:**
```cmd
docker run -it --rm -p 8888:8888 -v "%CD%:/data" precision-medicine/python-base:latest bash -c "pip install jupyter && jupyter notebook --ip=0.0.0.0 --allow-root --no-browser"
```

**RStudio Server (if configured):**
```cmd
docker run -it --rm -p 8787:8787 -v "%CD%:/data" precision-medicine/r-base:latest
```

## Security Best Practices

### Vulnerability Scanning

All build scripts automatically scan images with Trivy:

```cmd
# Scan all images
cd base-images
scan-images.bat

# Scan specific image
scan-images.bat python-base

# View reports
type scan-reports\python-base-trivy.txt
```

### Regular Updates

1. **Rebuild monthly** or when base images update
2. **Review scan reports** after each build
3. **Update Trivy** database regularly:
   ```cmd
   trivy image --download-db-only
   ```

### Container Runtime Security

- Run as non-root user (built into images)
- Use read-only mounts when possible: `-v "%CD%:/data:ro"`
- Limit resources: `--memory=4g --cpus=2`
- Drop capabilities: `--cap-drop=ALL`

## Troubleshooting

### Docker Issues

**Docker daemon not running:**
- Windows: Check system tray for Docker icon, restart Docker Desktop
- Linux: `sudo systemctl start docker`

**Permission denied:**
- Linux: Add user to docker group: `sudo usermod -aG docker $USER`
- Windows: Run Docker Desktop as Administrator

**Out of disk space:**
```cmd
# Clean up unused containers, images, and volumes
docker system prune -a --volumes

# Check disk usage
docker system df
```

### Build Issues

**Build fails with network errors:**
- Check internet connection
- Configure Docker proxy if behind corporate firewall
- Try again (sometimes mirrors are temporarily down)

**Out of memory during build:**
- Increase Docker Desktop memory limit (Settings → Resources)
- Build images one at a time: `build-single.bat python-base`

**Slow builds:**
- First build downloads base images (one-time, can take 20-30 min)
- Subsequent builds use cache (much faster)
- R packages compilation is slow (use pre-built binaries when possible)

### Scanning Issues

**Trivy not found:**
- See [INSTALL_TRIVY.md](base-images/INSTALL_TRIVY.md)
- Builds work without Trivy (scanning is optional)

**Scan takes too long:**
- First scan downloads vulnerability database (~200MB)
- Subsequent scans are much faster (cached)

## Contributing

When adding new Docker images or tools:

1. **Follow naming conventions** - Use descriptive, lowercase names with hyphens
2. **Document packages** - List all installed packages in README
3. **Optimize size** - Use slim bases, multi-stage builds, cleanup
4. **Security first** - Non-root users, minimal dependencies
5. **Test thoroughly** - Build and scan before committing
6. **Update docs** - Add to this README and relevant documentation

## Additional Resources

- **[Base Images README](base-images/README.md)** - Detailed documentation
- **[Trivy Installation Guide](base-images/INSTALL_TRIVY.md)** - Security scanning setup
- **[Change Log](base-images/CHANGES.md)** - Recent updates and improvements
- **Docker Documentation:** https://docs.docker.com/
- **Trivy Documentation:** https://aquasecurity.github.io/trivy/

## Support

For issues or questions:
- Check the troubleshooting sections above
- Review the base-images documentation
- Check Docker Desktop logs
- Verify system requirements are met

## License

These Docker configurations are part of the Precision Medicine Platform.
