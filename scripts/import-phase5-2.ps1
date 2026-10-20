param(
    [Parameter(Mandatory = $true)]
    [string]$ArchivePath,
    [switch]$Publish
)

$ErrorActionPreference = 'Stop'
$ExpectedSha256 = '1cf2c44e80001d0f48318fb25882792d1523892968ba08a36ae7991c1bfe7932'
$Repository = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$AllowList = @(
    'desk_ui.py', 'device_bridge.py',
    'linux_companion.py', 'linux_diagnostics.py',
    'windows_companion.py', 'windows_diagnostics.py',
    'requirements-ui.txt', 'requirements-windows.txt',
    'static/device.css', 'static/device.js', 'static/ui.css', 'static/ui.js',
    'templates/device.html', 'templates/index.html', 'templates/pair.html',
    'tests/test_artwork_routing.py', 'tests/test_device_bridge.py',
    'tests/test_device_ui_regression.py', 'tests/test_linux_companion.py',
    'tests/test_pairing_store.py', 'tests/test_volume_routing.py'
)
$History = @(
    'README-Phase4.1-Omarchy.md', 'README-Phase4.2-Volume.md',
    'README-Phase5-Device-Bridge.md',
    'README-Phase5.1-UI-Restore.md', 'README-Phase5.2-Artwork.md'
)

if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) {
    throw "Missing Phase 5.2 ZIP: $ArchivePath"
}
$Actual = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $ExpectedSha256) {
    throw "Archive hash mismatch. Expected $ExpectedSha256, got $Actual. Stop before importing a different build."
}
Push-Location $Repository
try {
    if ((git status --porcelain) -or ($LASTEXITCODE -ne 0)) {
        throw 'Repository is not clean. Commit/stash changes before importing.'
    }
    if ((git branch --show-current).Trim() -ne 'main') {
        throw 'Expected main branch for one-time bootstrap. Stop and inspect branch state.'
    }

    $Temp = Join-Path $env:TEMP ("spotify-desk-phase5-2-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Temp -Force | Out-Null
    try {
        Expand-Archive -LiteralPath $ArchivePath -DestinationPath $Temp -Force
        foreach ($Relative in $AllowList) {
            $Source = Join-Path $Temp $Relative
            if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
                throw "Archive missing expected source: $Relative"
            }
            $Destination = Join-Path $Repository $Relative
            $Dir = Split-Path -Parent $Destination
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
            Copy-Item -LiteralPath $Source -Destination $Destination -Force
        }
        foreach ($Name in $History) {
            $Source = Join-Path $Temp $Name
            if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
                throw "Archive missing expected history note: $Name"
            }
            $Dir = Join-Path $Repository 'docs\history'
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
            Copy-Item -LiteralPath $Source -Destination (Join-Path $Dir $Name) -Force
        }
    }
    finally {
        Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
    }

    Write-Host ''
    Write-Host 'Files copied from exact Phase 5.2 archive. Review changes:' -ForegroundColor Cyan
    git status --short
    Write-Host ''
    Write-Host 'No secret/config files were copied. After reviewing and running tests:' -ForegroundColor Yellow
    Write-Host 'git add desk_ui.py device_bridge.py linux_companion.py linux_diagnostics.py windows_companion.py windows_diagnostics.py requirements-ui.txt requirements-windows.txt static templates tests docs/history'
    Write-Host 'git commit -m "feat: import accepted Phase 5.2 desktop and simulator baseline"'
    Write-Host 'git push origin main'
    if ($Publish) {
        Write-Host ''
        Write-Host 'Publishing allowlisted, verified Phase 5.2 source files...' -ForegroundColor Cyan
        $Paths = @(
            'desk_ui.py', 'device_bridge.py', 'linux_companion.py', 'linux_diagnostics.py',
            'windows_companion.py', 'windows_diagnostics.py', 'requirements-ui.txt',
            'requirements-windows.txt', 'static', 'templates', 'tests', 'docs/history'
        )
        git add -- $Paths
        if ($LASTEXITCODE -ne 0) { throw 'git add failed; nothing pushed.' }
        git diff --cached --check
        if ($LASTEXITCODE -ne 0) { throw 'git diff found whitespace issues; nothing pushed.' }
        git commit -m 'feat: import accepted Phase 5.2 desktop and simulator baseline'
        if ($LASTEXITCODE -ne 0) { throw 'git commit failed; nothing pushed.' }
        git push origin main
        if ($LASTEXITCODE -ne 0) { throw 'git push failed. Your local commit is retained; check authentication/conflicts.' }
        Write-Host 'Phase 5.2 source committed and pushed to GitHub.' -ForegroundColor Green
    }
}
finally {
    Pop-Location
}
