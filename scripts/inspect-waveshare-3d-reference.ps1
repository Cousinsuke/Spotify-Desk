# Inspect the manufacturer-supplied Waveshare 4.3-inch 3D drawing archive.
# Download is to Downloads ONLY; not added to the GitHub repository.
[CmdletBinding()]
param(
    [string]$OutputFolder = (Join-Path $HOME "Downloads\SpotifyDesk-Waveshare-Official-3D"),
    [switch]$Extract
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Uri = "https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip"
$ZipPath = Join-Path $OutputFolder "ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip"
New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
Write-Host "Downloading official Waveshare drawing archive..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $Uri -OutFile $ZipPath -UseBasicParsing
$Hash = Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath
Write-Host ("Archive: " + $ZipPath)
Write-Host ("Bytes: " + (Get-Item -LiteralPath $ZipPath).Length)
Write-Host ("SHA-256: " + $Hash.Hash)
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Archive = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
try {
    $Entries = @($Archive.Entries |
        Where-Object { -not [string]::IsNullOrEmpty($_.Name) } |
        Sort-Object FullName |
        ForEach-Object { [pscustomobject]@{Name=$_.FullName;Bytes=$_.Length} })
}
finally { $Archive.Dispose() }
if ($Entries.Count -eq 0) { throw "Archive has no regular files." }
Write-Host ""
Write-Host "Archive contents:" -ForegroundColor Cyan
$Entries | Format-Table -AutoSize | Out-Host
$Models = @($Entries | Where-Object { $_.Name -match '\.(step|stp|stl|igs|iges|x_t|x_b|dxf|dwg)$' })
if ($Models.Count -gt 0) {
    Write-Host "Potential CAD models:" -ForegroundColor Green
    $Models | Format-Table -AutoSize | Out-Host
}
else { Write-Warning "No familiar CAD extensions; review the archive listing." }
if ($Extract) {
    $ExtractFolder = Join-Path $OutputFolder "extracted"
    New-Item -ItemType Directory -Path $ExtractFolder -Force | Out-Null
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractFolder -Force
    Write-Host ("Extracted to: " + $ExtractFolder) -ForegroundColor Green
}
Write-Host "Reference only: verify touch SKU 25948, PCB revision, connectors and dimensions before use."
