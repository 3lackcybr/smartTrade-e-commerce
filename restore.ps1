param(
    [Parameter(Mandatory=$true)]
    [string]$Name
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupDir = Join-Path $root "backups\$Name"

if (-not (Test-Path $backupDir)) {
    Write-Host "Snapshot not found: $Name" -ForegroundColor Red
    Write-Host "Available snapshots:" -ForegroundColor Yellow
    Get-ChildItem -Path (Join-Path $root "backups") -Directory | ForEach-Object { Write-Host "  $($_.Name)" }
    exit 1
}

Write-Host "Restoring snapshot: $Name" -ForegroundColor Cyan

# Restore all files from backup
Get-ChildItem -Path $backupDir -Recurse -File | ForEach-Object {
    $relPath = $_.FullName.Substring($backupDir.Length + 1)
    $dest = Join-Path $root $relPath
    $parent = Split-Path -Parent $dest
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Copy-Item -Path $_.FullName -Destination $dest -Force
}

Write-Host "Restored $((Get-ChildItem -Path $backupDir -Recurse -File).Count) files" -ForegroundColor Green
Write-Host "Kill any running server and re-run 'py run.py' to apply." -ForegroundColor Yellow
