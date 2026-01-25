@echo off
REM =============================================================================
REM Build Single Docker Base Image (Windows)
REM =============================================================================
REM Usage: build-single.bat [python-base|r-base|tensorflow-base]
REM
REM FEATURES:
REM - Builds a single specified image
REM - Runs Trivy security scan if installed
REM - Saves vulnerability report to scan-reports/ directory
REM =============================================================================

setlocal enabledelayedexpansion

REM Local use only - DO NOT PUSH TO REMOTE REGISTRIES
set IMAGE_PREFIX=precision-medicine
set IMAGE_NAME=%1

if "%IMAGE_NAME%"=="" (
    echo.
    echo ERROR: No image name specified
    echo.
    echo Usage: build-single.bat [IMAGE_NAME]
    echo.
    echo Available images:
    echo   - python-base
    echo   - r-base
    echo   - tensorflow-base
    echo.
    exit /b 1
)

REM Validate image name
if not "%IMAGE_NAME%"=="python-base" (
    if not "%IMAGE_NAME%"=="r-base" (
        if not "%IMAGE_NAME%"=="tensorflow-base" (
            echo.
            echo ERROR: Invalid image name "%IMAGE_NAME%"
            echo.
            echo Valid options are:
            echo   - python-base
            echo   - r-base
            echo   - tensorflow-base
            echo.
            exit /b 1
        )
    )
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create scan-reports directory if it doesn't exist
if not exist "scan-reports" mkdir scan-reports

REM Check if Trivy is installed
set TRIVY_ENABLED=0
trivy --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set TRIVY_ENABLED=1
    echo [INFO] Trivy is installed - vulnerability scanning enabled
) else (
    echo [WARNING] Trivy is not installed - vulnerability scanning will be skipped
    echo [INFO] To install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/
)
echo.

echo.
echo ===============================================================================
echo Building %IMAGE_NAME% Docker Image
echo ===============================================================================
echo.

docker build -t %IMAGE_PREFIX%/%IMAGE_NAME%:latest ./%IMAGE_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to build %IMAGE_NAME% image
    echo Build failed - skipping security scan
    exit /b 1
) else (
    echo.
    echo SUCCESS: %IMAGE_NAME% image built successfully
    echo.
    echo Image: %IMAGE_PREFIX%/%IMAGE_NAME%:latest
    echo.

    REM Scan with Trivy if available
    if !TRIVY_ENABLED! EQU 1 (
        echo.
        echo ===============================================================================
        echo Running Trivy Security Scan
        echo ===============================================================================
        echo.
        echo Scanning for CRITICAL and HIGH severity vulnerabilities...
        echo.

        trivy image --exit-code 1 --no-progress --severity CRITICAL,HIGH --format table %IMAGE_PREFIX%/%IMAGE_NAME%:latest > scan-reports\%IMAGE_NAME%-trivy.txt 2>&1

        if !ERRORLEVEL! EQU 0 (
            echo [OK] No critical or high vulnerabilities found!
            echo.
            type scan-reports\%IMAGE_NAME%-trivy.txt
        ) else (
            echo [WARNING] Vulnerabilities detected!
            echo.
            echo Full report saved to: scan-reports\%IMAGE_NAME%-trivy.txt
            echo.
            echo Summary:
            type scan-reports\%IMAGE_NAME%-trivy.txt | findstr /C:"Total:" /C:"CRITICAL" /C:"HIGH"
            echo.
            echo Review the full report for details and remediation steps.
        )

        echo.
        echo Report location: scan-reports\%IMAGE_NAME%-trivy.txt
    ) else (
        echo [INFO] Trivy not installed - security scan skipped
        echo Install Trivy to enable vulnerability scanning:
        echo https://aquasecurity.github.io/trivy/latest/getting-started/installation/
    )
)

echo.
pause
