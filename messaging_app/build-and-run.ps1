Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Setup for Django Messaging App" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "2. Building Docker image..." -ForegroundColor Yellow
try {
    docker build -t messaging-app .
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Docker build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "3. Running Docker container..." -ForegroundColor Yellow
Write-Host "Container will be accessible at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Cyan
Write-Host ""
try {
    docker run -p 8000:8000 messaging-app
} catch {
    Write-Host "✗ ERROR: Failed to run container" -ForegroundColor Red
}

Read-Host "Press Enter to exit" 