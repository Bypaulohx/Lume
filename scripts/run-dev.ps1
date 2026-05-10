# Inicia backend (FastAPI) e frontend (Vite) para desenvolvimento local.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
    Write-Error "Não encontrado: $Root\.venv — crie o venv e instale dependências primeiro."
}
$Py = "$Root\.venv\Scripts\python.exe"
$backend = Start-Process -FilePath $Py -ArgumentList @(
    '-m', 'uvicorn', 'api.main:app', '--reload',
    '--reload-dir', '.',
    '--reload-dir', '..\lume',
    '--host', '127.0.0.1', '--port', '8000'
) -PassThru -WorkingDirectory "$Root\backend" -WindowStyle Minimized
Start-Sleep -Seconds 2
$frontend = Start-Process -FilePath 'npm' -ArgumentList @('run', 'dev') -PassThru -WorkingDirectory "$Root\frontend" -WindowStyle Normal
Write-Host "Backend PID $($backend.Id) | Frontend PID $($frontend.Id)"
Write-Host "API: http://127.0.0.1:8000/api/health"
Write-Host "UI:  http://127.0.0.1:5173"
