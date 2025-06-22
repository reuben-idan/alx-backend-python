# Docker Implementation Script for Django Messaging App
# Run this script to complete the Docker setup

Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Implementation for Django App" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Step 1: Check current directory
Write-Host ""
Write-Host "1. Checking current directory..." -ForegroundColor Yellow
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Cyan

# Step 2: Verify required files exist
Write-Host ""
Write-Host "2. Verifying required files..." -ForegroundColor Yellow
$requiredFiles = @("Dockerfile", "requirements.txt", "manage.py")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "Missing files: $($missingFiles -join ', ')" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Check Docker installation
Write-Host ""
Write-Host "3. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($dockerVersion -like "*Docker version*") {
        Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker not found or not responding" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually" -ForegroundColor Yellow
        Read-Host "Press Enter after starting Docker Desktop"
    }
} catch {
    Write-Host "✗ Docker not found" -ForegroundColor Red
    Read-Host "Please install Docker Desktop and press Enter"
}

# Step 4: Test Docker connectivity
Write-Host ""
Write-Host "4. Testing Docker connectivity..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($dockerInfo -like "*error during connect*") {
        Write-Host "✗ Docker Desktop not running or misconfigured" -ForegroundColor Red
        Write-Host "Please start Docker Desktop and configure it properly" -ForegroundColor Yellow
        Read-Host "Press Enter after Docker Desktop is running"
    } else {
        Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Cannot connect to Docker daemon" -ForegroundColor Red
    Read-Host "Please start Docker Desktop and press Enter"
}

# Step 5: Build Docker image
Write-Host ""
Write-Host "5. Building Docker image..." -ForegroundColor Yellow
try {
    Write-Host "Building with simple Dockerfile..." -ForegroundColor Cyan
    docker build -f Dockerfile.simple -t messaging-app-simple .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker image built successfully (simple)" -ForegroundColor Green
        $imageName = "messaging-app-simple"
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ Simple Dockerfile build failed, trying original..." -ForegroundColor Yellow
    try {
        docker build -t messaging-app .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Docker image built successfully (original)" -ForegroundColor Green
            $imageName = "messaging-app"
        } else {
            throw "Build failed"
        }
    } catch {
        Write-Host "✗ Docker build failed" -ForegroundColor Red
        Write-Host "Please check Docker Desktop settings and try again" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 6: Run Docker container
Write-Host ""
Write-Host "6. Running Docker container..." -ForegroundColor Yellow
Write-Host "Container will be accessible at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Cyan
Write-Host ""

try {
    docker run -p 8000:8000 $imageName
} catch {
    Write-Host "✗ Failed to run container" -ForegroundColor Red
    Write-Host "You can try running manually:" -ForegroundColor Yellow
    Write-Host "docker run -p 8000:8000 $imageName" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Implementation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "Press Enter to exit" 