Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Troubleshooting Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($dockerInfo -like "*error during connect*") {
        Write-Host "✗ Docker Desktop not running or misconfigured" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Cannot connect to Docker daemon" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Checking Docker contexts..." -ForegroundColor Yellow
try {
    $contexts = docker context ls
    Write-Host "Available contexts:" -ForegroundColor Cyan
    Write-Host $contexts -ForegroundColor White
} catch {
    Write-Host "✗ Cannot list contexts" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Trying to build with simple Dockerfile..." -ForegroundColor Yellow
try {
    docker build -f Dockerfile.simple -t messaging-app-simple .
    Write-Host "✓ Build successful with simple Dockerfile" -ForegroundColor Green
} catch {
    Write-Host "✗ Build failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Recommendations:" -ForegroundColor Yellow
Write-Host "- Start Docker Desktop manually" -ForegroundColor Cyan
Write-Host "- Run PowerShell as Administrator" -ForegroundColor Cyan
Write-Host "- Check Docker Desktop settings" -ForegroundColor Cyan
Write-Host "- Try Hyper-V instead of WSL 2" -ForegroundColor Cyan

Read-Host "Press Enter to continue" 