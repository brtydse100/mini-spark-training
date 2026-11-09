$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    & ./.venv/Scripts/python.exe -m build
    if ($LASTEXITCODE -ne 0) { throw "Package build failed" }
} finally { Pop-Location }
