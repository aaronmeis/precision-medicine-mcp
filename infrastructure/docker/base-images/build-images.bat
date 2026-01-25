@echo off
REM =============================================================================
REM Build Script for Precision Medicine Docker Base Images (Windows)
REM =============================================================================
REM This script builds all base Docker images for the Precision Medicine platform
REM
REM IMPORTANT: These images are for LOCAL USE ONLY
REM            DO NOT PUSH to Docker Hub or any remote registry
REM
REM FEATURES:
REM - Builds all three base images (python-base, r-base, tensorflow-base)
REM - Runs Trivy security scans on successfully built images
REM - Saves vulnerability reports to scan-reports/ directory
REM =============================================================================

setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo Building Precision Medicine Docker Base Images
echo ===============================================================================
echo.

REM Set the image prefix for local use only (DO NOT PUSH TO REMOTE REGISTRIES)
set IMAGE_PREFIX=precision-medicine

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create scan-reports directory if it doesn't exist
if not exist "scan-reports" mkdir scan-reports

REM Track build and scan status
set BUILD_SUCCESS=0
set BUILD_FAILED=0
set SCAN_SUCCESS=0
set SCAN_FAILED=0
set SCAN_SKIPPED=0

REM Check if Trivy is installed
set TRIVY_ENABLED=0
trivy --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Trivy is installed - vulnerability scanning enabled
    set TRIVY_ENABLED=1
) else (
    echo [WARNING] Trivy is not installed - vulnerability scanning will be skipped
    echo [INFO] To install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/
)
echo.

REM =============================================================================
REM Build Python Base Image
REM =============================================================================
echo.
echo [1/3] Building Python Base Image...
echo -------------------------------------------------------------------------------
docker build -t %IMAGE_PREFIX%/python-base:latest ./python-base
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build python-base image
    set /a BUILD_FAILED+=1
    set /a SCAN_SKIPPED+=1
) else (
    echo SUCCESS: python-base image built successfully
    set /a BUILD_SUCCESS+=1

    REM Scan with Trivy if available
    if !TRIVY_ENABLED! EQU 1 (
        echo.
        echo [SCAN] Running Trivy security scan on python-base...
        echo -------------------------------------------------------------------------------
        trivy image --exit-code 1 --no-progress --severity CRITICAL,HIGH --format table %IMAGE_PREFIX%/python-base:latest > scan-reports\python-base-trivy.txt 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo [OK] No critical or high vulnerabilities found
            set /a SCAN_SUCCESS+=1
        ) else (
            echo [WARNING] Vulnerabilities detected! See scan-reports\python-base-trivy.txt
            set /a SCAN_FAILED+=1
        )
        echo Report saved to: scan-reports\python-base-trivy.txt
    ) else (
        set /a SCAN_SKIPPED+=1
    )
)

REM =============================================================================
REM Build R Base Image
REM =============================================================================
echo.
echo [2/3] Building R Base Image...
echo -------------------------------------------------------------------------------
docker build -t %IMAGE_PREFIX%/r-base:latest ./r-base
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build r-base image
    set /a BUILD_FAILED+=1
    set /a SCAN_SKIPPED+=1
) else (
    echo SUCCESS: r-base image built successfully
    set /a BUILD_SUCCESS+=1

    REM Scan with Trivy if available
    if !TRIVY_ENABLED! EQU 1 (
        echo.
        echo [SCAN] Running Trivy security scan on r-base...
        echo -------------------------------------------------------------------------------
        trivy image --exit-code 1 --no-progress --severity CRITICAL,HIGH --format table %IMAGE_PREFIX%/r-base:latest > scan-reports\r-base-trivy.txt 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo [OK] No critical or high vulnerabilities found
            set /a SCAN_SUCCESS+=1
        ) else (
            echo [WARNING] Vulnerabilities detected! See scan-reports\r-base-trivy.txt
            set /a SCAN_FAILED+=1
        )
        echo Report saved to: scan-reports\r-base-trivy.txt
    ) else (
        set /a SCAN_SKIPPED+=1
    )
)

REM =============================================================================
REM Build TensorFlow Base Image
REM =============================================================================
echo.
echo [3/3] Building TensorFlow Base Image...
echo -------------------------------------------------------------------------------
docker build -t %IMAGE_PREFIX%/tensorflow-base:latest ./tensorflow-base
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build tensorflow-base image
    set /a BUILD_FAILED+=1
    set /a SCAN_SKIPPED+=1
) else (
    echo SUCCESS: tensorflow-base image built successfully
    set /a BUILD_SUCCESS+=1

    REM Scan with Trivy if available
    if !TRIVY_ENABLED! EQU 1 (
        echo.
        echo [SCAN] Running Trivy security scan on tensorflow-base...
        echo -------------------------------------------------------------------------------
        trivy image --exit-code 1 --no-progress --severity CRITICAL,HIGH --format table %IMAGE_PREFIX%/tensorflow-base:latest > scan-reports\tensorflow-base-trivy.txt 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo [OK] No critical or high vulnerabilities found
            set /a SCAN_SUCCESS+=1
        ) else (
            echo [WARNING] Vulnerabilities detected! See scan-reports\tensorflow-base-trivy.txt
            set /a SCAN_FAILED+=1
        )
        echo Report saved to: scan-reports\tensorflow-base-trivy.txt
    ) else (
        set /a SCAN_SKIPPED+=1
    )
)

REM =============================================================================
REM Summary
REM =============================================================================
echo.
echo ===============================================================================
echo Build Summary
echo ===============================================================================
echo.
echo BUILD RESULTS:
echo   Successful builds: %BUILD_SUCCESS%
echo   Failed builds:     %BUILD_FAILED%
echo.

if !TRIVY_ENABLED! EQU 1 (
    echo SECURITY SCAN RESULTS:
    echo   Clean scans:       %SCAN_SUCCESS%
    echo   Vulnerabilities:   %SCAN_FAILED%
    echo   Skipped:           %SCAN_SKIPPED%
    echo.
)

if %BUILD_FAILED% EQU 0 (
    echo All images built successfully!
    echo.
    echo Available images ^(LOCAL USE ONLY^):
    echo   - %IMAGE_PREFIX%/python-base:latest
    echo   - %IMAGE_PREFIX%/r-base:latest
    echo   - %IMAGE_PREFIX%/tensorflow-base:latest
    echo.

    if !TRIVY_ENABLED! EQU 1 (
        if !SCAN_FAILED! GTR 0 (
            echo [WARNING] Some images have vulnerabilities!
            echo Review the reports in scan-reports\ directory for details.
            echo.
        )
    )

    echo To list images:
    echo   docker images ^| findstr %IMAGE_PREFIX%
    echo.
    echo IMPORTANT: These images are for local use only.
    echo            Do NOT push to Docker Hub or any remote registry.
    echo.
) else (
    echo Some builds failed. Please check the error messages above.
    exit /b 1
)

echo Build process completed.
echo.
pause
