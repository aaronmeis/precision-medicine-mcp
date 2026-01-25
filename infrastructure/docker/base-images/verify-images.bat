@echo off
REM =============================================================================
REM Verify Precision Medicine Docker Base Images (Windows)
REM =============================================================================
REM This script verifies that all base images were built successfully
REM =============================================================================

setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo Verifying Precision Medicine Docker Base Images
echo ===============================================================================
echo.

REM Local images only - these are never pushed to remote registries
set IMAGE_PREFIX=precision-medicine
set ALL_PRESENT=1

REM Check Python Base
echo Checking python-base...
docker images %IMAGE_PREFIX%/python-base:latest --format "{{.Repository}}:{{.Tag}}" | findstr python-base >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] python-base found
) else (
    echo [MISSING] python-base not found
    set ALL_PRESENT=0
)

REM Check R Base
echo Checking r-base...
docker images %IMAGE_PREFIX%/r-base:latest --format "{{.Repository}}:{{.Tag}}" | findstr r-base >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] r-base found
) else (
    echo [MISSING] r-base not found
    set ALL_PRESENT=0
)

REM Check TensorFlow Base
echo Checking tensorflow-base...
docker images %IMAGE_PREFIX%/tensorflow-base:latest --format "{{.Repository}}:{{.Tag}}" | findstr tensorflow-base >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] tensorflow-base found
) else (
    echo [MISSING] tensorflow-base not found
    set ALL_PRESENT=0
)

echo.
echo -------------------------------------------------------------------------------

if %ALL_PRESENT% EQU 1 (
    echo.
    echo All base images are present!
    echo.
    echo Image details:
    echo.
    docker images | findstr /C:"REPOSITORY" /C:"%IMAGE_PREFIX%"
    echo.
) else (
    echo.
    echo Some images are missing. Run build-images.bat to build them.
    echo.
)

pause
