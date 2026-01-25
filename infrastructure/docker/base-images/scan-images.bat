@echo off
REM =============================================================================
REM Scan Docker Images with Trivy (Windows)
REM =============================================================================
REM This script scans existing Docker images for security vulnerabilities
REM using Trivy. It does NOT rebuild the images.
REM
REM Usage:
REM   scan-images.bat              - Scan all base images
REM   scan-images.bat IMAGE_NAME   - Scan a specific image
REM
REM Reports are saved to scan-reports/ directory
REM =============================================================================

setlocal enabledelayedexpansion

set IMAGE_PREFIX=precision-medicine
set SPECIFIC_IMAGE=%1

REM Check if Trivy is installed
trivy --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Trivy is not installed!
    echo.
    echo Trivy is required for vulnerability scanning.
    echo.
    echo Installation instructions:
    echo   Windows: winget install Aqua.Trivy
    echo   Or download from: https://aquasecurity.github.io/trivy/latest/getting-started/installation/
    echo.
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create scan-reports directory if it doesn't exist
if not exist "scan-reports" mkdir scan-reports

echo.
echo ===============================================================================
echo Trivy Security Scanner for Docker Images
echo ===============================================================================
echo.
echo Scanning for: CRITICAL and HIGH severity vulnerabilities
echo Reports saved to: scan-reports\
echo.

set SCAN_SUCCESS=0
set SCAN_FAILED=0

if "%SPECIFIC_IMAGE%"=="" (
    REM Scan all images
    echo Scanning all base images...
    echo.
    call :ScanImage python-base
    call :ScanImage r-base
    call :ScanImage tensorflow-base
) else (
    REM Scan specific image
    call :ScanImage %SPECIFIC_IMAGE%
)

REM Summary
echo.
echo ===============================================================================
echo Scan Summary
echo ===============================================================================
echo.
echo Clean scans (no CRITICAL/HIGH):  %SCAN_SUCCESS%
echo Scans with vulnerabilities:      %SCAN_FAILED%
echo.

if %SCAN_FAILED% GTR 0 (
    echo [WARNING] Some images have vulnerabilities!
    echo Review the reports in scan-reports\ directory for details.
    echo.
) else (
    echo [OK] All scanned images are clean!
    echo.
)

echo All reports saved in: scan-reports\
echo.
pause
exit /b 0

REM =============================================================================
REM Function: Scan a single image
REM =============================================================================
:ScanImage
set IMG_NAME=%1
set FULL_IMAGE=%IMAGE_PREFIX%/%IMG_NAME%:latest

echo -------------------------------------------------------------------------------
echo Scanning: %FULL_IMAGE%
echo -------------------------------------------------------------------------------

REM Check if image exists
docker images %FULL_IMAGE% --format "{{.Repository}}:{{.Tag}}" | findstr %IMG_NAME% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [SKIP] Image not found: %FULL_IMAGE%
    echo Build the image first using: build-single.bat %IMG_NAME%
    echo.
    goto :eof
)

REM Run Trivy scan
trivy image --exit-code 1 --no-progress --severity CRITICAL,HIGH --format table %FULL_IMAGE% > scan-reports\%IMG_NAME%-trivy.txt 2>&1

if !ERRORLEVEL! EQU 0 (
    echo [OK] No critical or high vulnerabilities found
    set /a SCAN_SUCCESS+=1
) else (
    echo [WARNING] Vulnerabilities detected! See scan-reports\%IMG_NAME%-trivy.txt
    set /a SCAN_FAILED+=1
)

echo Report: scan-reports\%IMG_NAME%-trivy.txt
echo.
goto :eof
