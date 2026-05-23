param(
    [Parameter(Position = 0)]
    [string]$Command = "start"
)

$ErrorActionPreference = "Stop"

function Get-LumiAiConfigDir {
    Join-Path $env:USERPROFILE ".lumiai"
}

function Get-LumiAiConfigPath {
    Join-Path (Get-LumiAiConfigDir) "config.json"
}

function Read-LumiAiConfig {
    $path = Get-LumiAiConfigPath
    if (-not (Test-Path $path)) {
        throw "Missing LumiAI config at $path. Run scripts\install_lumiai_command.ps1 first."
    }
    Get-Content $path -Raw | ConvertFrom-Json
}

function Ensure-Directory([string]$Path) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Get-PidPath([string]$name) {
    Join-Path (Get-LumiAiConfigDir) "$name.pid"
}

function Get-LogPath([string]$name) {
    Join-Path (Get-LumiAiConfigDir) "$name.log"
}

function Get-ErrPath([string]$name) {
    Join-Path (Get-LumiAiConfigDir) "$name.err.log"
}

function Get-ProcessByPidFile([string]$name) {
    $pidPath = Get-PidPath $name
    if (-not (Test-Path $pidPath)) {
        return $null
    }

    $pidValue = Get-Content $pidPath -Raw
    if (-not $pidValue) {
        return $null
    }

    try {
        return Get-Process -Id ([int]$pidValue)
    }
    catch {
        return $null
    }
}

function Start-LumiAi {
    $config = Read-LumiAiConfig
    Ensure-Directory (Get-LumiAiConfigDir)
    $publicEnabled = [bool]$config.public_enabled

    $webcamProcess = Get-ProcessByPidFile "webcam"
    $tunnelProcess = Get-ProcessByPidFile "localtunnel"
    if ($webcamProcess -and (($publicEnabled -and $tunnelProcess) -or (-not $publicEnabled))) {
        Write-Host "LumiAI is already running."
        Show-LumiAiStatus
        return
    }

    $repoPath = [string]$config.repo_path
    $pythonPath = Join-Path $repoPath ".venv311\Scripts\python.exe"
    $scriptPath = Join-Path $repoPath "windows\webcam_supabase_live.py"
    if (-not (Test-Path $pythonPath)) {
        throw "Missing Python runtime at $pythonPath"
    }
    if (-not (Test-Path $scriptPath)) {
        throw "Missing LumiAI script at $scriptPath"
    }

    $webcamArgs = @(
        $scriptPath,
        "--api-key", [string]$config.supabase_api_key,
        "--project-url", [string]$config.supabase_project_url,
        "--device", [string]$config.device,
        "--port", [string]$config.port
    )

    $webcam = Start-Process -FilePath $pythonPath -ArgumentList $webcamArgs -WorkingDirectory $repoPath -WindowStyle Hidden -RedirectStandardOutput (Get-LogPath "webcam") -RedirectStandardError (Get-ErrPath "webcam") -PassThru
    Set-Content -Path (Get-PidPath "webcam") -Value $webcam.Id

    Start-Sleep -Seconds 8

    try {
        Invoke-RestMethod -Uri ("http://127.0.0.1:{0}/healthz" -f $config.port) -Method Get | Out-Null
    }
    catch {
        throw "Webcam server did not become healthy on port $($config.port). Check $(Get-ErrPath 'webcam')"
    }

    $publicUrl = $null
    if ($publicEnabled) {
        $npxPath = (Get-Command npx.cmd -ErrorAction Stop).Source
        $tunnelArgs = @("localtunnel", "--port", [string]$config.port)

        $tunnel = Start-Process -FilePath $npxPath -ArgumentList $tunnelArgs -WorkingDirectory $repoPath -WindowStyle Hidden -RedirectStandardOutput (Get-LogPath "localtunnel") -RedirectStandardError (Get-ErrPath "localtunnel") -PassThru
        Set-Content -Path (Get-PidPath "localtunnel") -Value $tunnel.Id

        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 500
            $logPath = Get-LogPath "localtunnel"
            if (-not (Test-Path $logPath)) {
                continue
            }
            $content = Get-Content $logPath -Raw
            if ($content -match 'https://[^\s]+') {
                $publicUrl = $Matches[0]
                break
            }
        }
    }

    Write-Host "LumiAI started."
    Write-Host ("Local page: http://127.0.0.1:{0}/" -f $config.port)
    Write-Host ("Local stream: http://127.0.0.1:{0}/stream.mjpg" -f $config.port)
    if ($publicEnabled -and $publicUrl) {
        Write-Host ("Public page: {0}/" -f $publicUrl.TrimEnd('/'))
        Write-Host ("Public stream: {0}/stream.mjpg" -f $publicUrl.TrimEnd('/'))
    }
    elseif ($publicEnabled) {
        Write-Host "Localtunnel started but URL has not been parsed yet. Run 'lumiai url' in a few seconds."
    }
}

function Stop-LumiAi {
    foreach ($name in @("localtunnel", "webcam")) {
        $process = Get-ProcessByPidFile $name
        if ($process) {
            Stop-Process -Id $process.Id -Force
        }
        $pidPath = Get-PidPath $name
        if (Test-Path $pidPath) {
            Remove-Item $pidPath -Force
        }
    }
    Write-Host "LumiAI stopped."
}

function Show-LumiAiStatus {
    $config = Read-LumiAiConfig
    $publicEnabled = [bool]$config.public_enabled
    $webcam = Get-ProcessByPidFile "webcam"
    $tunnel = Get-ProcessByPidFile "localtunnel"
    $status = [ordered]@{
        webcam_running = [bool]$webcam
        localtunnel_running = [bool]$tunnel
        public_enabled = $publicEnabled
        local_page = ("http://127.0.0.1:{0}/" -f $config.port)
        local_stream = ("http://127.0.0.1:{0}/stream.mjpg" -f $config.port)
        public_url = $null
    }

    $logPath = Get-LogPath "localtunnel"
    if ($publicEnabled -and (Test-Path $logPath)) {
        $content = Get-Content $logPath -Raw
        if ($content -match 'https://[^\s]+') {
            $status.public_url = $Matches[0]
        }
    }

    $status | ConvertTo-Json -Depth 4
}

function Show-LumiAiUrl {
    $status = Show-LumiAiStatus | ConvertFrom-Json
    if ($status.public_url) {
        Write-Host ("Public page: {0}/" -f $status.public_url.TrimEnd('/'))
        Write-Host ("Public stream: {0}/stream.mjpg" -f $status.public_url.TrimEnd('/'))
    }
    else {
        Write-Host "No public URL found yet."
    }
}

switch ($Command.ToLowerInvariant()) {
    "start" { Start-LumiAi }
    "stop" { Stop-LumiAi }
    "status" { Show-LumiAiStatus }
    "url" { Show-LumiAiUrl }
    default { throw "Unknown command '$Command'. Use: start, stop, status, url" }
}
