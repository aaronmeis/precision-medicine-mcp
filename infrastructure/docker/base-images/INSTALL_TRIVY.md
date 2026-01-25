# Installing Trivy on Windows

## Method 1: Using Chocolatey (Recommended)

If you have Chocolatey installed:
```cmd
choco install trivy
```

## Method 2: Direct Download (Manual) - Detailed Steps

### Step-by-Step Installation

1. **Download the latest release:**
   - Go to: https://github.com/aquasecurity/trivy/releases
   - Download `trivy_<version>_windows-64bit.zip`
   - Latest stable: https://github.com/aquasecurity/trivy/releases/latest

2. **Extract and install:**
   ```cmd
   # Open Command Prompt or PowerShell
   # Create directory
   mkdir C:\trivy

   # Using File Explorer:
   # - Navigate to your Downloads folder
   # - Right-click the downloaded trivy_*_windows-64bit.zip
   # - Select "Extract All..."
   # - Extract to C:\trivy
   # - You should now have C:\trivy\trivy.exe
   ```

   **Or using PowerShell:**
   ```powershell
   # Extract using PowerShell
   Expand-Archive -Path "$env:USERPROFILE\Downloads\trivy_*_windows-64bit.zip" -DestinationPath "C:\trivy" -Force
   ```

3. **Add to PATH:**

   **Option A: Using System Properties (GUI)**
   - Press `Windows Key + Pause/Break` OR right-click "This PC" → Properties
   - Click "Advanced system settings" on the left
   - Click "Environment Variables..." button at the bottom
   - In the "System variables" section (bottom half), scroll to find "Path"
   - Select "Path" and click "Edit..."
   - Click "New" button
   - Type: `C:\trivy`
   - Click "OK" on all dialogs (3 times)
   - **Important:** Close and reopen any open terminals for changes to take effect

   **Option B: Using PowerShell (Quick)**
   - Open PowerShell as Administrator
   - Run this command:
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\trivy", [EnvironmentVariableTarget]::Machine)
   ```
   - Close and reopen your terminal

4. **Verify installation:**
   ```cmd
   # Close and reopen your terminal, then test:
   trivy --version

   # You should see output like:
   # Version: 0.x.x

   # If you see "trivy is not recognized", check:
   where trivy
   # This should show: C:\trivy\trivy.exe

   # If not found, verify PATH was updated:
   echo %PATH%
   # Look for C:\trivy in the output
   ```

## Method 3: Using Scoop

If you have Scoop package manager:
```cmd
scoop install trivy
```

## Method 4: Using Windows Package Manager (winget) - Alternative Package Name

Try these alternative package names:
```cmd
# Try the full package ID
winget install AquaSecurity.Trivy

# Or search for available packages
winget search trivy
```

## Method 5: Using Docker (No Installation Required)

If you only want to use Trivy without installing it locally:
```cmd
# Scan an image using Docker
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image precision-medicine/python-base:latest

# Create an alias for easier use (PowerShell)
function trivy { docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy $args }
```

## Recommended: Chocolatey Installation

The most reliable method is using Chocolatey:

1. **Install Chocolatey** (if not already installed):
   - Open PowerShell as Administrator
   - Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install Trivy:**
   ```cmd
   choco install trivy
   ```

3. **Verify:**
   ```cmd
   trivy --version
   ```

## After Installation

Once Trivy is installed, you can use the build scripts:

```cmd
# Build with automatic scanning
build-images.bat

# Or scan existing images
scan-images.bat
```

## Troubleshooting

**"trivy is not recognized as an internal or external command"**
- Make sure Trivy is in your PATH
- Restart your terminal after installation
- Verify with: `where trivy`

**winget package not found**
- The package might not be available in winget yet
- Use Chocolatey or manual download instead

**Permission denied errors**
- Run PowerShell or Command Prompt as Administrator
- Check Windows Defender isn't blocking the download

**PATH not updated / trivy not found after adding to PATH**
- Make sure you closed and reopened your terminal
- Verify PATH was added correctly: `echo %PATH%` (should include C:\trivy)
- If using PowerShell, try: `$env:Path -split ';'` to see all PATH entries
- Restart your computer if PATH still not recognized
- Try using the full path temporarily: `C:\trivy\trivy.exe --version`

## Skip Trivy (Optional)

If you prefer not to install Trivy, the build scripts will still work:
- They detect if Trivy is installed
- If not found, they skip scanning and just build the images
- You'll see: `[WARNING] Trivy is not installed - vulnerability scanning will be skipped`
