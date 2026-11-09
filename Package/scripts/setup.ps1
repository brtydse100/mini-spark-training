$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    if (-not (Test-Path -LiteralPath ".venv/Scripts/python.exe")) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed" }
    }
    & ./.venv/Scripts/python.exe -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
} finally { Pop-Location }
