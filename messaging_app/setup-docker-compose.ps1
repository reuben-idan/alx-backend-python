Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Compose Setup for Django + MySQL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Checking if .env file exists..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "✗ .env file not found" -ForegroundColor Red
    Write-Host "Creating .env file from env.example..." -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "✓ .env file created from env.example" -ForegroundColor Green
        Write-Host "Please review and update the .env file with your own values" -ForegroundColor Cyan
    } else {
        Write-Host "✗ env.example not found" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "2. Checking Docker Compose installation..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found" -ForegroundColor Red
    Write-Host "Please install Docker Compose and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "3. Building and starting services..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Cyan

try {
    docker-compose up --build
} catch {
    Write-Host "✗ Docker Compose failed" -ForegroundColor Red
    Write-Host "You can try running manually:" -ForegroundColor Yellow
    Write-Host "docker-compose up --build" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "Your app should be available at http://localhost:8000" -ForegroundColor Cyan
Write-Host "MySQL database is available at localhost:3306" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green 