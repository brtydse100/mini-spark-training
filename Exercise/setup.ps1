$ErrorActionPreference = "Stop"
$package = Join-Path (Split-Path -Parent $PSScriptRoot) "Package"
& (Join-Path $package "scripts/setup.ps1")
if (-not $?) { throw "Package setup failed" }
& (Join-Path $package ".venv/Scripts/python.exe") -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Exercise dependency installation failed" }
