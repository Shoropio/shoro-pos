# start-pos-dev.ps1
# Detener procesos existentes
Write-Host "Deteniendo procesos existentes..."
Get-Process -Name uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

$BASE = "C:\Users\Shoropio\Desktop\shoro-pos"

# Iniciar backend (8000)
$backendPath = "$BASE\backend"
$venvPath = "$BASE\.venv\Scripts\uvicorn.exe"

Write-Host "Iniciando backend (uvicorn 8000)..."
Push-Location $backendPath
$env:PYTHONPATH = "$backendPath"  # Ensure Python can import the backend package
Start-Process -FilePath $venvPath -ArgumentList "app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $backendPath -NoNewWindow
Pop-Location

# Esperar a que 8000 esté listo
Write-Host "Esperando que 8000 esté disponible..."
$maxWait = 60
$ready = $false
for ($i = 0; $i -lt $maxWait; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    }
    catch {
        # ignore
    }
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Write-Host "Advertencia: backend no respondió en 60s"
}

# Iniciar frontend (5173)
$frontendPath = "$BASE\frontend\web"
Write-Host "Iniciando frontend (Vite 5173)..."
Push-Location $frontendPath
npm ci --silent
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $frontendPath -NoNewWindow
Pop-Location

Write-Host "Listo. Backend en 8000 y frontend en 5173."
