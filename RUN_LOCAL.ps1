$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "AcroConnect - Local Launcher"
Write-Host "This starts the Django API (8000) and Streamlit portal (8501)."
Write-Host "The ONLY user-facing website is Streamlit at: http://127.0.0.1:8501"
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

if (!(Test-Path $backend)) { throw "Backend folder not found: $backend" }
if (!(Test-Path $frontend)) { throw "Frontend folder not found: $frontend" }

function Resolve-PythonExe([string]$workDir) {
  $venvPy = Join-Path $workDir ".venv\Scripts\python.exe"
  if (Test-Path $venvPy) { return $venvPy }

  $repoVenvPy = Join-Path $root ".venv\Scripts\python.exe"
  if (Test-Path $repoVenvPy) { return $repoVenvPy }

  return "python"
}

$backendPy = Resolve-PythonExe $backend
$frontendPy = Resolve-PythonExe $frontend

Write-Host "Backend Python: $backendPy"
Write-Host "Frontend Python: $frontendPy"
Write-Host ""

Write-Host "Starting Django backend (API)..." -ForegroundColor Cyan
$backendProc = Start-Process powershell -PassThru -WorkingDirectory $backend -ArgumentList @(
  "-NoExit",
  "-Command",
  "& '$backendPy' manage.py runserver 127.0.0.1:8000"
)

# Wait briefly for port 8000 to open
$started = $false
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 300
  $conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
  if ($conn) { $started = $true; break }
}

if (-not $started) {
  Write-Host ""
  Write-Host "ERROR: Django backend did not start on port 8000." -ForegroundColor Red
  Write-Host "A new PowerShell window was opened for the backend; check it for the exact error." -ForegroundColor Yellow
  Write-Host ""
  Write-Host "Common fix:" -ForegroundColor Yellow
  Write-Host "  cd `"$backend`""
  Write-Host "  $backendPy -m pip install -r requirements.txt"
  Write-Host "  $backendPy manage.py runserver 127.0.0.1:8000"
  Write-Host ""
  throw "Backend not running. Cannot launch UI login."
}

Write-Host "Starting Streamlit portal (UI)..." -ForegroundColor Cyan
$frontendProc = Start-Process powershell -PassThru -WorkingDirectory $frontend -ArgumentList @(
  "-NoExit",
  "-Command",
  "`$env:API_URL='http://127.0.0.1:8000'; & '$frontendPy' -m streamlit run app.py --server.port 8501"
)

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Open: http://127.0.0.1:8501" -ForegroundColor Green
Write-Host "Note: Django admin (http://127.0.0.1:8000/admin) is developer-only."
Write-Host ""

