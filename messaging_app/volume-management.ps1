param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("backup", "restore", "clean", "info", "list")]
    [string]$Action = "info"
)

Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker Volume Management Tool" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

function Show-VolumeInfo {
    Write-Host ""
    Write-Host "Volume Information:" -ForegroundColor Yellow
    Write-Host "  • Database data: ./data/mysql" -ForegroundColor White
    Write-Host "  • MySQL config: ./data/mysql-config" -ForegroundColor White
    Write-Host "  • MySQL logs: ./data/mysql-logs" -ForegroundColor White
    Write-Host "  • Database backups: ./data/mysql-backup" -ForegroundColor White
    Write-Host "  • Static files: ./data/staticfiles" -ForegroundColor White
    Write-Host "  • Media files: ./data/media" -ForegroundColor White
    Write-Host "  • phpMyAdmin config: ./data/phpmyadmin" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Container Status:" -ForegroundColor Yellow
    try {
        $containers = docker-compose ps
        Write-Host $containers -ForegroundColor White
    } catch {
        Write-Host "No containers running or Docker Compose not available" -ForegroundColor Red
    }
}

function Backup-Database {
    Write-Host ""
    Write-Host "Creating database backup..." -ForegroundColor Yellow
    
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupFile = "data/mysql-backup/backup_$timestamp.sql"
    
    try {
        # Stop containers to ensure data consistency
        Write-Host "Stopping containers for consistent backup..." -ForegroundColor Cyan
        docker-compose stop
        
        # Create backup directory if it doesn't exist
        if (!(Test-Path "data/mysql-backup")) {
            New-Item -ItemType Directory -Path "data/mysql-backup" -Force | Out-Null
        }
        
        # Create backup using mysqldump
        Write-Host "Creating backup: $backupFile" -ForegroundColor Cyan
        docker-compose run --rm db mysqldump -u messaging_user -pmessaging_password123 messaging_db > $backupFile
        
        Write-Host "✓ Database backup created: $backupFile" -ForegroundColor Green
        
        # Restart containers
        Write-Host "Restarting containers..." -ForegroundColor Cyan
        docker-compose up -d
        
    } catch {
        Write-Host "✗ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
        docker-compose up -d
    }
}

function Restore-Database {
    Write-Host ""
    Write-Host "Available backups:" -ForegroundColor Yellow
    
    $backupFiles = Get-ChildItem "data/mysql-backup" -Filter "*.sql" | Sort-Object LastWriteTime -Descending
    
    if ($backupFiles.Count -eq 0) {
        Write-Host "No backup files found in data/mysql-backup/" -ForegroundColor Red
        return
    }
    
    for ($i = 0; $i -lt $backupFiles.Count; $i++) {
        Write-Host "  $($i + 1). $($backupFiles[$i].Name) - $($backupFiles[$i].LastWriteTime)" -ForegroundColor White
    }
    
    $selection = Read-Host "Select backup to restore (1-$($backupFiles.Count))"
    $index = [int]$selection - 1
    
    if ($index -ge 0 -and $index -lt $backupFiles.Count) {
        $selectedFile = $backupFiles[$index]
        Write-Host "Restoring from: $($selectedFile.Name)" -ForegroundColor Yellow
        
        try {
            # Stop containers
            docker-compose stop
            
            # Restore database
            Get-Content $selectedFile.FullName | docker-compose run --rm -T db mysql -u messaging_user -pmessaging_password123 messaging_db
            
            Write-Host "✓ Database restored successfully" -ForegroundColor Green
            
            # Restart containers
            docker-compose up -d
            
        } catch {
            Write-Host "✗ Restore failed: $($_.Exception.Message)" -ForegroundColor Red
            docker-compose up -d
        }
    } else {
        Write-Host "Invalid selection" -ForegroundColor Red
    }
}

function Clean-Volumes {
    Write-Host ""
    Write-Host "Cleaning volumes..." -ForegroundColor Yellow
    Write-Host "This will remove all data. Are you sure? (y/N)" -ForegroundColor Red
    
    $confirmation = Read-Host
    if ($confirmation -eq "y" -or $confirmation -eq "Y") {
        try {
            # Stop and remove containers
            docker-compose down -v
            
            # Remove data directories
            $dataDirs = @("data/mysql", "data/mysql-config", "data/mysql-logs", "data/mysql-backup", "data/staticfiles", "data/media", "data/phpmyadmin")
            
            foreach ($dir in $dataDirs) {
                if (Test-Path $dir) {
                    Remove-Item -Path $dir -Recurse -Force
                    Write-Host "✓ Removed: $dir" -ForegroundColor Green
                }
            }
            
            Write-Host "✓ All volumes cleaned" -ForegroundColor Green
            
        } catch {
            Write-Host "✗ Clean failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "Clean cancelled" -ForegroundColor Yellow
    }
}

function List-Volumes {
    Write-Host ""
    Write-Host "Docker Volumes:" -ForegroundColor Yellow
    try {
        $volumes = docker volume ls
        Write-Host $volumes -ForegroundColor White
    } catch {
        Write-Host "No volumes found or Docker not available" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Data Directories:" -ForegroundColor Yellow
    $dataDirs = @("data/mysql", "data/mysql-config", "data/mysql-logs", "data/mysql-backup", "data/staticfiles", "data/media", "data/phpmyadmin")
    
    foreach ($dir in $dataDirs) {
        if (Test-Path $dir) {
            $size = (Get-ChildItem $dir -Recurse | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  ✓ $dir - $sizeMB MB" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $dir - Not found" -ForegroundColor Red
        }
    }
}

# Main execution
switch ($Action) {
    "backup" { Backup-Database }
    "restore" { Restore-Database }
    "clean" { Clean-Volumes }
    "list" { List-Volumes }
    "info" { Show-VolumeInfo }
    default { Show-VolumeInfo }
}

Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  .\volume-management.ps1 info    - Show volume information" -ForegroundColor White
Write-Host "  .\volume-management.ps1 backup  - Create database backup" -ForegroundColor White
Write-Host "  .\volume-management.ps1 restore - Restore database from backup" -ForegroundColor White
Write-Host "  .\volume-management.ps1 clean   - Clean all volumes (DESTRUCTIVE)" -ForegroundColor White
Write-Host "  .\volume-management.ps1 list    - List volumes and data directories" -ForegroundColor White 