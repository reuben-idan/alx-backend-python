Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Volume Setup for Data Persistence" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Creating data directories for volume persistence..." -ForegroundColor Yellow

# Create data directories
$dataDirs = @(
    "data/mysql",
    "data/mysql-config", 
    "data/mysql-logs",
    "data/mysql-backup",
    "data/staticfiles",
    "data/media",
    "data/phpmyadmin",
    "mysql/init"
)

foreach ($dir in $dataDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✓ Directory already exists: $dir" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "2. Setting up MySQL initialization script..." -ForegroundColor Yellow

# Create MySQL initialization script
$initScript = @"
-- MySQL initialization script
-- This script runs when the MySQL container starts for the first time

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = 'utf8mb4_unicode_ci';

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS \`messaging_db\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON \`messaging_db\`.* TO 'messaging_user'@'%';
FLUSH PRIVILEGES;

-- Show databases
SHOW DATABASES;
"@

$initScript | Out-File -FilePath "mysql/init/01-init.sql" -Encoding UTF8
Write-Host "✓ Created MySQL initialization script" -ForegroundColor Green

Write-Host ""
Write-Host "3. Volume persistence configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Data will be persisted in the following locations:" -ForegroundColor Cyan
Write-Host "  • Database data: ./data/mysql" -ForegroundColor White
Write-Host "  • MySQL config: ./data/mysql-config" -ForegroundColor White
Write-Host "  • MySQL logs: ./data/mysql-logs" -ForegroundColor White
Write-Host "  • Database backups: ./data/mysql-backup" -ForegroundColor White
Write-Host "  • Static files: ./data/staticfiles" -ForegroundColor White
Write-Host "  • Media files: ./data/media" -ForegroundColor White
Write-Host "  • phpMyAdmin config: ./data/phpmyadmin" -ForegroundColor White

Write-Host ""
Write-Host "4. Next steps:" -ForegroundColor Yellow
Write-Host "  • Run: docker-compose up --build" -ForegroundColor Cyan
Write-Host "  • Access Django app: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • Access phpMyAdmin: http://localhost:8080" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Volume Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green 