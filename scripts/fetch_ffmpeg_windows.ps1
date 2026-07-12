# Downloads the Windows ffmpeg/ffprobe binaries bundled into the .exe by
# packaging/windows.spec, so end users don't need to install ffmpeg
# separately. Not checked into git (~200MB) -- re-run this whenever
# vendor/ffmpeg-windows is missing. Called automatically by
# scripts/build_windows.bat.
#
# Source: Gyan Doshi's "essentials" Windows builds, mirrored on GitHub
# Releases (much faster than gyan.dev directly). ffmpeg is GPL-licensed;
# see https://github.com/GyanD/codexffmpeg for full source/build scripts.

$ErrorActionPreference = "Stop"

$FfmpegVersion = "8.1.2"
$Url = "https://github.com/GyanD/codexffmpeg/releases/download/$FfmpegVersion/ffmpeg-$FfmpegVersion-essentials_build.zip"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VendorDir = Join-Path $ProjectRoot "vendor\ffmpeg-windows"
$FfmpegExe = Join-Path $VendorDir "ffmpeg.exe"
$FfprobeExe = Join-Path $VendorDir "ffprobe.exe"

if ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe)) {
    Write-Host "ffmpeg already present at $VendorDir, skipping download."
    exit 0
}

New-Item -ItemType Directory -Force -Path $VendorDir | Out-Null

$ZipPath = Join-Path $env:TEMP "ffmpeg-essentials.zip"
Write-Host "Downloading $Url ..."
Invoke-WebRequest -Uri $Url -OutFile $ZipPath

$ExtractDir = Join-Path $env:TEMP "ffmpeg-essentials-extract"
if (Test-Path $ExtractDir) { Remove-Item -Recurse -Force $ExtractDir }
Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir

$BinDir = Get-ChildItem -Path $ExtractDir -Filter "bin" -Recurse -Directory | Select-Object -First 1
Copy-Item (Join-Path $BinDir.FullName "ffmpeg.exe") $FfmpegExe
Copy-Item (Join-Path $BinDir.FullName "ffprobe.exe") $FfprobeExe

Remove-Item $ZipPath
Remove-Item -Recurse -Force $ExtractDir

Write-Host "ffmpeg.exe / ffprobe.exe ready at $VendorDir"
