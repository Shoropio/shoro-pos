param(
  [string]$DatabasePath = "database\shoro_pos.db",
  [string]$BackupDir = "backups"
)

if (!(Test-Path $DatabasePath)) {
  throw "No existe la base de datos: $DatabasePath"
}

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$target = Join-Path $BackupDir "shoro_pos-$timestamp.db"
Copy-Item -LiteralPath $DatabasePath -Destination $target
Write-Output "Backup creado: $target"
