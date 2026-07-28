[CmdletBinding()]
param(
    [string[]]$ModelId = @(),
    [string]$CacheRoot = (Join-Path $env:LOCALAPPDATA 'open-model-weights-archive'),
    [switch]$SkipPublish
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$lock = Get-Content -Raw (Join-Path $repoRoot 'models.lock.json') | ConvertFrom-Json
$selected = @($lock.models | Where-Object {
    $ModelId.Count -eq 0 -or $ModelId -contains $_.id
})
if ($selected.Count -eq 0) { throw 'No model matched -ModelId.' }

foreach ($command in @('huggingface-cli')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command is required. Install it with: pip install huggingface_hub[cli]"
    }
}
if (-not $SkipPublish -and -not (Get-Command 'oras' -ErrorAction SilentlyContinue)) {
    throw 'oras is required for publication: https://oras.land/docs/installation'
}

New-Item -ItemType Directory -Force -Path $CacheRoot | Out-Null
foreach ($model in $selected) {
    $destination = Join-Path $CacheRoot $model.id
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    & huggingface-cli download $model.source --revision $model.revision `
        --local-dir $destination
    if ($LASTEXITCODE -ne 0) { throw "Download failed for $($model.id)." }

    $actual = (Get-ChildItem -LiteralPath $destination -File -Recurse |
        Measure-Object -Property Length -Sum).Sum
    if ($actual -lt $model.measuredBytes) {
        throw "Snapshot for $($model.id) is smaller than its locked measurement."
    }
    if ($SkipPublish) { continue }

    $tag = "$($model.artifact):$($model.revision.Substring(0, 12))"
    Push-Location $destination
    try {
        $files = Get-ChildItem -File -Recurse | ForEach-Object {
            $_.FullName.Substring($destination.Length + 1).Replace('\', '/')
        }
        & oras push $tag --artifact-type 'application/vnd.huggingface.snapshot.v1' @files
        if ($LASTEXITCODE -ne 0) { throw "OCI publication failed for $($model.id)." }
        & oras tag $tag latest
        if ($LASTEXITCODE -ne 0) { throw "OCI latest tag failed for $($model.id)." }
    } finally {
        Pop-Location
    }
}
