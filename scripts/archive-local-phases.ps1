# Preserve historic Spotify Desk ZIPs in Git without replacing the current source.
param(
    [string]$DownloadsPath = (Join-Path $HOME 'Downloads'),
    [switch]$Publish
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ArchiveRelative = 'archives/phase-zips'
$ArchiveDirectory = Join-Path $Repo 'archives\phase-zips'
$ManifestRelative = 'docs/history/ARCHIVED-PHASE-ZIPS.md'
$ManifestPath = Join-Path $Repo 'docs\history\ARCHIVED-PHASE-ZIPS.md'
$NamePattern = '^spotify-desk-thing-(?:ui-)?phase[0-9]+(?:-[0-9]+)*(?:-fix)?\.zip$'

function Check-ExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit code $LASTEXITCODE)." }
}

if (-not (Test-Path -LiteralPath $DownloadsPath -PathType Container)) {
    throw "Downloads directory not found: $DownloadsPath"
}
$Files = @(Get-ChildItem -LiteralPath $DownloadsPath -Filter 'spotify-desk-thing*.zip' -File |
    Where-Object { $_.Name -match $NamePattern } | Sort-Object Name)
if ($Files.Count -eq 0) { throw "No Spotify Desk phase ZIPs found in $DownloadsPath" }

# Scan archive contents before copying ANY files to the repository.
$Entries = @()
foreach ($File in $Files) {
    if ($File.Length -gt 25MB) {
        throw "Archive over 25 MiB: $($File.Name). Inspect before publishing."
    }
    $Zip = [System.IO.Compression.ZipFile]::OpenRead($File.FullName)
    try {
        foreach ($Entry in $Zip.Entries) {
            $Relative = $Entry.FullName.Replace('\', '/')
            if ($Relative.StartsWith('/') -or $Relative -match '(^|/)\.\.(/|$)' -or $Relative -match '^[A-Za-z]:') {
                throw "Unsafe archive path in $($File.Name): $Relative"
            }
            if ($Relative -match '(?i)(^|/)(?:\.env(?:\.[^/]*)?|\.spotify_token\.json|\.desk_config\.json(?:\.tmp)?|\.desk_devices\.json(?:\.tmp)?|\.cache(?:-[^/]*)?|\.git|\.venv|venv|__pycache__|id_rsa|id_ed25519|[^/]+\.(?:pem|p12|pfx))(/|$)') {
                throw "Possible private data in $($File.Name): $Relative. Inspect manually."
            }
        }
    }
    finally { $Zip.Dispose() }
    $Entries += [pscustomobject]@{
        Name = $File.Name
        FullName = $File.FullName
        Bytes = $File.Length
        Hash = (Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

Push-Location $Repo
try {
    if ((git branch --show-current).Trim() -ne 'main') {
        throw 'Expected the main branch; inspect the repository branch before continuing.'
    }
    $Dirty = @(git status --porcelain)
    Check-ExitCode 'git status'
    if ($Dirty.Count -ne 0) { throw 'Working tree is not clean. Commit or stash changes first.' }
    if (-not (Test-Path -LiteralPath (Join-Path $Repo 'device_bridge.py') -PathType Leaf)) {
        throw 'Import the Phase 5.2 root application first with scripts/import-phase5-2.ps1 -Publish.'
    }

    git pull --ff-only origin main
    Check-ExitCode 'git pull'

    New-Item -ItemType Directory -Path $ArchiveDirectory -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path $ManifestPath -Parent) -Force | Out-Null

    foreach ($Item in $Entries) {
        $Dest = Join-Path $ArchiveDirectory $Item.Name
        if (Test-Path -LiteralPath $Dest) {
            $ExistingHash = (Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($ExistingHash -ne $Item.Hash) {
                throw "Existing archive has a different checksum: $($Item.Name). No files overwritten."
            }
        }
        else { Copy-Item -LiteralPath $Item.FullName -Destination $Dest }
    }

    $Lines = @(
        '# Archived Spotify Desk Thing phase ZIPs',
        '',
        'These are historical snapshots, not the current application source.',
        'The root-level files on the active development branch are authoritative.',
        '',
        '| ZIP archive | Bytes | SHA-256 |',
        '| --- | ---: | --- |'
    )
    foreach ($Item in $Entries) {
        $Lines += "| [$($Item.Name)](../../$ArchiveRelative/$($Item.Name)) | $($Item.Bytes) | $($Item.Hash) |"
    }
    $Lines += ''
    $Lines += '> The script checks archive file names for common credentials but cannot detect every secret embedded in file contents. Review historic archives before publishing them in a public repository.'
    [System.IO.File]::WriteAllText($ManifestPath, (($Lines -join [Environment]::NewLine) + [Environment]::NewLine), (New-Object System.Text.UTF8Encoding($false)))

    Write-Host "Prepared $($Entries.Count) historical ZIPs:" -ForegroundColor Cyan
    foreach ($Item in $Entries) { Write-Host ("  " + $Item.Name) }

    git add -- $ArchiveRelative $ManifestRelative
    Check-ExitCode 'git add'
    git diff --cached --check
    Check-ExitCode 'git diff --check'

    $Staged = @(git diff --cached --name-only)
    Check-ExitCode 'git diff --cached'
    if ($Staged.Count -eq 0) {
        Write-Host 'Archives already match the repository.' -ForegroundColor Green
        return
    }
    git diff --cached --stat

    if ($Publish) {
        git commit -m 'chore: archive historical Spotify Desk phase ZIPs'
        Check-ExitCode 'git commit'
        git push origin main
        Check-ExitCode 'git push'
        Write-Host 'Archived versions published to GitHub.' -ForegroundColor Green
    }
    else { Write-Host 'Changes staged for review. Pass -Publish to commit/push.' -ForegroundColor Yellow }
}
finally { Pop-Location }
