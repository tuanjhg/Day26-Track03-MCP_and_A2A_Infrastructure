param(
    [string]$PythonPath = "python",
    [switch]$OfflineMode
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$env:REGISTRY_URL = if ($env:REGISTRY_URL) { $env:REGISTRY_URL } else { "http://localhost:10000" }
if ($OfflineMode) {
    $env:LAB_OFFLINE_MODE = "1"
}

$services = @(
    @{ Name = "registry"; Module = "registry"; Port = 10000; Delay = 2 },
    @{ Name = "tax_agent"; Module = "tax_agent"; Port = 10102; Delay = 0 },
    @{ Name = "compliance_agent"; Module = "compliance_agent"; Port = 10103; Delay = 3 },
    @{ Name = "law_agent"; Module = "law_agent"; Port = 10101; Delay = 3 },
    @{ Name = "customer_agent"; Module = "customer_agent"; Port = 10100; Delay = 0 }
)

$pids = @()
foreach ($service in $services) {
    $stdout = Join-Path $logDir "$($service.Name).out.log"
    $stderr = Join-Path $logDir "$($service.Name).err.log"
    Write-Host "Starting $($service.Name) on port $($service.Port)..."
    $process = Start-Process `
        -FilePath $PythonPath `
        -ArgumentList @("-m", $service.Module) `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru
    $pids += $process.Id
    Start-Sleep -Seconds $service.Delay
}

$pidFile = Join-Path $logDir "service-pids.txt"
$pids | Set-Content -Path $pidFile

Write-Host ""
Write-Host "All services started."
Write-Host "PID file: $pidFile"
Write-Host "Logs: $logDir"
Write-Host ""
Write-Host "Run:"
Write-Host "  & `"$PythonPath`" test_client.py"
Write-Host ""
Write-Host "Stop:"
Write-Host "  Get-Content logs/service-pids.txt | ForEach-Object { Stop-Process -Id `$_ }"
