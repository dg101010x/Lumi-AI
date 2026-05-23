param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot),
    [string]$SupabaseProjectUrl = "https://gmmpltgvtonpnrfckrvy.supabase.co",
    [string]$SupabaseApiKey = "",
    [int]$Device = 0,
    [int]$Port = 8080,
    [switch]$EnablePublic
)

$ErrorActionPreference = "Stop"

if (-not $SupabaseApiKey) {
    throw "Pass -SupabaseApiKey with your service key."
}

$binDir = Join-Path $env:USERPROFILE "bin"
$configDir = Join-Path $env:USERPROFILE ".lumiai"
$launcherPath = Join-Path $binDir "lumiai.cmd"
$configPath = Join-Path $configDir "config.json"
$repoPathResolved = (Resolve-Path $RepoPath).Path
$lumiaiScript = Join-Path $repoPathResolved "windows\lumiai.ps1"

New-Item -ItemType Directory -Force -Path $binDir | Out-Null
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

$config = [ordered]@{
    repo_path = $repoPathResolved
    supabase_project_url = $SupabaseProjectUrl
    supabase_api_key = $SupabaseApiKey
    device = $Device
    port = $Port
    public_enabled = [bool]$EnablePublic
}
$config | ConvertTo-Json -Depth 4 | Set-Content -Path $configPath -Encoding UTF8

$launcher = @"
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "$lumiaiScript" %*
"@
Set-Content -Path $launcherPath -Value $launcher -Encoding ASCII

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = @()
if ($userPath) {
    $parts = $userPath -split ';' | Where-Object { $_ }
}
if ($parts -notcontains $binDir) {
    $newPath = @($parts + $binDir) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Host "Installed lumiai command."
Write-Host "Launcher: $launcherPath"
Write-Host "Config: $configPath"
Write-Host "Open a new terminal, then run: lumiai"
