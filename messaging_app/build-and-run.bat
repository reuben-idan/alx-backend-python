@echo off
echo ========================================
echo Docker Setup for Django Messaging App
echo ========================================

echo.
echo 1. Checking Docker installation...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo 2. Building Docker image...
docker build -t messaging-app .
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo.
echo 3. Running Docker container...
echo Container will be accessible at http://localhost:8000
echo Press Ctrl+C to stop the container
echo.
docker run -p 8000:8000 messaging-app

pause 