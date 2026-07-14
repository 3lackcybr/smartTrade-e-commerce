param(
    [string]$Name = (Get-Date -Format "yyyyMMdd_HHmmss")
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupDir = Join-Path $root "backups\$Name"

# Files to track (all source code, configs, templates, static assets)
$include = @(
    "*.py", "*.html", "*.css", "*.js", "*.json", "*.cfg", "*.txt",
    "*.env", "*.ps1", "*.bat", "*.sh", "*.pem", "*.key"
)

Write-Host "Creating snapshot: $Name" -ForegroundColor Cyan

# Create backup dir
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Copy tracked files preserving directory structure
Get-ChildItem -Path $root -Include $include -Recurse |
    Where-Object { $_.FullName -notmatch '\\backups\\' -and $_.FullName -notmatch '\\__pycache__\\' -and $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\venv\\' -and $_.FullName -notmatch '\\node_modules\\' } |
    ForEach-Object {
        $relPath = $_.FullName.Substring($root.Length + 1)
        $dest = Join-Path $backupDir $relPath
        $parent = Split-Path -Parent $dest
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }

# Also snapshot the database
$dbPath = Join-Path $root "instance\ecommerce.db"
if (Test-Path $dbPath) {
    $dbDest = Join-Path $backupDir "instance"
    New-Item -ItemType Directory -Path $dbDest -Force | Out-Null
    Copy-Item -Path $dbPath -Destination (Join-Path $dbDest "ecommerce.db") -Force
}

Write-Host "Snapshot saved to: $backupDir" -ForegroundColor Green
Write-Host "Files: $((Get-ChildItem -Path $backupDir -Recurse -File).Count)" -ForegroundColor Green
