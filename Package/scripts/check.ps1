$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    & ./.venv/Scripts/python.exe tools/smoke.py
    if ($LASTEXITCODE -ne 0) { throw "Smoke checks failed" }
    & ./.venv/Scripts/python.exe -m workframe.launcher --report reports/smoke.json examples/local_driver.py
    if ($LASTEXITCODE -ne 0) { throw "Enforced execution check failed" }
} finally { Pop-Location }
