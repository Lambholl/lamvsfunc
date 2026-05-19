param(
    [Parameter(Mandatory=$true)][string]$CaseId,
    [string[]]$Files = @()
)

# Resolve fixture root.
# $PSScriptRoot = tests\scripts, so tests\fixtures is one level up + 'fixtures'.
$testsDir = Split-Path -Parent $PSScriptRoot
$defaultFixtureDir = Join-Path $testsDir "fixtures"
$cfg = Join-Path $defaultFixtureDir ".path-config"
$root = if (Test-Path $cfg) {
    (Get-Content $cfg -Encoding utf8 |
        Where-Object { $_ -and -not $_.TrimStart().StartsWith('#') } |
        Select-Object -First 1).Trim()
} else {
    $defaultFixtureDir
}

# Recreate per-case tmp dir.
$tmp = "tests\.tmp\$CaseId"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Force $tmp | Out-Null

# Copy each requested fixture (file or directory) into the tmp dir.
foreach ($f in $Files) {
    $src = Join-Path $root $f
    if (-not (Test-Path $src)) {
        Write-Host "SKIP: missing fixture $src"
        exit 77
    }
    $dst = Join-Path $tmp $f
    if ((Get-Item $src).PSIsContainer) {
        Copy-Item $src $dst -Recurse
    } else {
        Copy-Item $src $dst
    }
}

# Export for downstream scripts.
$env:CASE_ID = $CaseId
$env:CASE_TMP = (Resolve-Path $tmp).Path
$env:CASE_ROOT = (Resolve-Path $root).Path
Write-Host "case $CaseId tmp=$env:CASE_TMP fixtures=$root"
