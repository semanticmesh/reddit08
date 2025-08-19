# Installation script for PostgreSQL and Redis
# Run this script with administrative privileges

Write-Host "Starting installation of PostgreSQL and Redis..." -ForegroundColor Green

# Install PostgreSQL
Write-Host "Installing PostgreSQL 15..." -ForegroundColor Yellow
try {
    # Check if PostgreSQL is already installed
    $psqlPath = "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    if (Test-Path $psqlPath) {
        Write-Host "PostgreSQL is already installed at: $psqlPath" -ForegroundColor Green
    } else {
        # Download installer
        $pgUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.8-1-windows-x64.exe"
        $pgInstaller = "$env:TEMP\postgresql-15.8-1-windows-x64.exe"
        
        Write-Host "Downloading PostgreSQL installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $pgUrl -OutFile $pgInstaller
        
        # Install with unattended mode
        Write-Host "Installing PostgreSQL..." -ForegroundColor Yellow
        Start-Process -FilePath $pgInstaller -ArgumentList "--mode=unattended --superpassword=postgres --serverport=5432" -Wait
        
        # Clean up installer
        Remove-Item $pgInstaller
        
        # Add to PATH
        $pgPath = "C:\Program Files\PostgreSQL\15\bin"
        if (-not $env:PATH.Contains($pgPath)) {
            $env:PATH = "$pgPath;$env:PATH"
            [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
            Write-Host "Added PostgreSQL to PATH" -ForegroundColor Green
        }
        
        Write-Host "PostgreSQL installation completed successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "PostgreSQL installation failed: $_" -ForegroundColor Red
}

# Install Redis
Write-Host "Installing Redis..." -ForegroundColor Yellow
try {
    # Check if Redis is already installed
    $redisPath = "C:\Program Files\Redis\redis-server.exe"
    if (Test-Path $redisPath) {
        Write-Host "Redis is already installed at: $redisPath" -ForegroundColor Green
    } else {
        # Download Redis
        $redisUrl = "https://github.com/redis-windows/redis-windows/releases/download/v3.0.504/Redis-x64-3.0.504.msi"
        $redisInstaller = "$env:TEMP\Redis-x64-3.0.504.msi"
        
        Write-Host "Downloading Redis installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $redisUrl -OutFile $redisInstaller
        
        # Install MSI
        Write-Host "Installing Redis..." -ForegroundColor Yellow
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $redisInstaller /quiet" -Wait
        
        # Clean up installer
        Remove-Item $redisInstaller
        
        # Add to PATH
        $redisPath = "C:\Program Files\Redis"
        if (-not $env:PATH.Contains($redisPath)) {
            $env:PATH = "$redisPath;$env:PATH"
            [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
            Write-Host "Added Redis to PATH" -ForegroundColor Green
        }
        
        Write-Host "Redis installation completed successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "Redis installation failed: $_" -ForegroundColor Red
}

# Verify installations
Write-Host "Verifying installations..." -ForegroundColor Yellow

# Check PostgreSQL
$psqlPath = "C:\Program Files\PostgreSQL\15\bin\psql.exe"
if (Test-Path $psqlPath) {
    Write-Host "PostgreSQL verification: SUCCESS" -ForegroundColor Green
    # Test connection
    try {
        & $psqlPath --version
        Write-Host "PostgreSQL is accessible" -ForegroundColor Green
    } catch {
        Write-Host "PostgreSQL is installed but not accessible in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "PostgreSQL verification: FAILED" -ForegroundColor Red
}

# Check Redis
$redisPath = "C:\Program Files\Redis\redis-server.exe"
if (Test-Path $redisPath) {
    Write-Host "Redis verification: SUCCESS" -ForegroundColor Green
    # Test Redis
    try {
        & $redisPath --version
        Write-Host "Redis is accessible" -ForegroundColor Green
    } catch {
        Write-Host "Redis is installed but not accessible in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "Redis verification: FAILED" -ForegroundColor Red
}

Write-Host "Installation process completed." -ForegroundColor Green
