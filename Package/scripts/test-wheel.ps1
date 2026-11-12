$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    & ./.venv/Scripts/python.exe tools/verify_wheel.py
    if ($LASTEXITCODE -ne 0) { throw "Built wheel verification failed" }
} finally { Pop-Location }
