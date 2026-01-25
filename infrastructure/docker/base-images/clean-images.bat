@echo off
REM =============================================================================
REM Clean Precision Medicine Docker Base Images (Windows)
REM =============================================================================
REM This script removes all base Docker images for the Precision Medicine platform
REM =============================================================================

setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo Clean Precision Medicine Docker Base Images
echo ===============================================================================
echo.

REM Local images only - these are never pushed to remote registries
set IMAGE_PREFIX=precision-medicine

REM Check if images exist
docker images | findstr %IMAGE_PREFIX% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo No Precision Medicine images found.
    echo.
    pause
    exit /b 0
)

echo Current images:
echo.
docker images | findstr %IMAGE_PREFIX%
echo.

set /p CONFIRM="Are you sure you want to remove these images? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo.
    echo Operation cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo Removing images...
echo.

docker rmi %IMAGE_PREFIX%/python-base:latest 2>nul
docker rmi %IMAGE_PREFIX%/r-base:latest 2>nul
docker rmi %IMAGE_PREFIX%/tensorflow-base:latest 2>nul

echo.
echo Images removed.
echo.

REM Optionally prune dangling images
set /p PRUNE="Do you want to prune dangling images? (y/N): "
if /i "%PRUNE%"=="y" (
    echo.
    echo Pruning dangling images...
    docker image prune -f
    echo Done.
)

echo.
pause
