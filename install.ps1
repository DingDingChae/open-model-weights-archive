[CmdletBinding()]
param([string]$Destination = (Join-Path $env:LOCALAPPDATA 'OpenModelWeightsApi'))

$ErrorActionPreference = 'Stop'
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'app') -Destination $Destination -Recurse -Force
Copy-Item -LiteralPath (Join-Path $source 'requirements.txt') -Destination $Destination -Force
py -3 -m venv (Join-Path $Destination '.venv')
& (Join-Path $Destination '.venv\Scripts\python.exe') -m pip install `
    -r (Join-Path $Destination 'requirements.txt')
Write-Output "Installed at $Destination"
Write-Output "Run: $Destination\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080"
