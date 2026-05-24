param(
    [Parameter(Position = 0)]
    [string]$Command = "start"
)

$ErrorActionPreference = "Stop"

function Get-FaceConfigDir {
    Join-Path $env:USERPROFILE ".aegis-face-receiver"
}

function Get-FaceConfigPath {
    Join-Path (Get-FaceConfigDir) "config.json"
}

function Ensure-FaceConfigDir {
    New-Item -ItemType Directory -Force -Path (Get-FaceConfigDir) | Out-Null
}

function Read-FaceConfig {
    $path = Get-FaceConfigPath
    if (-not (Test-Path $path)) {
        throw "Missing face receiver config at $path. Run scripts\\install_face_receiver_startup.ps1 first."
    }
    Get-Content $path -Raw | ConvertFrom-Json
}

function Get-PidPath {
    Join-Path (Get-FaceConfigDir) "face_receiver.pid"
}

function Get-LogPath {
    Join-Path (Get-FaceConfigDir) "face_receiver.log"
}

function Get-ErrPath {
    Join-Path (Get-FaceConfigDir) "face_receiver.err.log"
}

function Get-ProcessByPidFile {
    $pidPath = Get-PidPath
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

function Start-FaceReceiver {
    $config = Read-FaceConfig
    Ensure-FaceConfigDir

    $existing = Get-ProcessByPidFile
    if ($existing) {
        Write-Host "Face receiver is already running."
        Show-FaceReceiverStatus
        return
    }

    $repoPath = [string]$config.repo_path
    $pythonPath = Join-Path $repoPath ".venv311\\Scripts\\python.exe"
    $scriptPath = Join-Path $repoPath "windows\\face_receiver.py"
    if (-not (Test-Path $pythonPath)) {
        throw "Missing Python runtime at $pythonPath"
    }
    if (-not (Test-Path $scriptPath)) {
        throw "Missing face receiver script at $scriptPath"
    }

    $args = @(
        $scriptPath,
        "--host", "0.0.0.0",
        "--port", [string]$config.port,
        "--project-url", [string]$config.supabase_project_url,
        "--api-key", [string]$config.supabase_api_key
    )
    if ($config.autostart_camera) {
        $args += @("--autostart-camera", "--camera-device", [string]$config.camera_device)
    }

    $process = Start-Process -FilePath $pythonPath -ArgumentList $args -WorkingDirectory $repoPath -WindowStyle Hidden -RedirectStandardOutput (Get-LogPath) -RedirectStandardError (Get-ErrPath) -PassThru
    Set-Content -Path (Get-PidPath) -Value $process.Id -Encoding ASCII

    Start-Sleep -Seconds 5
    try {
        Invoke-RestMethod -Uri ("http://127.0.0.1:{0}/healthz" -f $config.port) -Method Get | Out-Null
    }
    catch {
        throw "Face receiver did not become healthy on port $($config.port). Check $(Get-ErrPath)"
    }

    if ($config.autostart_camera) {
        Start-Sleep -Seconds 2
    }

    Write-Host ("Face receiver started at http://127.0.0.1:{0}/" -f $config.port)
}

function Stop-FaceReceiver {
    $process = Get-ProcessByPidFile
    if ($process) {
        Stop-Process -Id $process.Id -Force
    }
    $pidPath = Get-PidPath
    if (Test-Path $pidPath) {
        Remove-Item $pidPath -Force
    }
    Write-Host "Face receiver stopped."
}

function Show-FaceReceiverStatus {
    $config = Read-FaceConfig
    $process = Get-ProcessByPidFile
    $status = [ordered]@{
        running = [bool]$process
        port = [int]$config.port
        repo_path = [string]$config.repo_path
        autostart_camera = [bool]$config.autostart_camera
        camera_device = [string]$config.camera_device
        local_page = ("http://127.0.0.1:{0}/" -f $config.port)
        log = Get-LogPath
        err_log = Get-ErrPath
    }
    $status | ConvertTo-Json -Depth 4
}

switch ($Command.ToLowerInvariant()) {
    "start" { Start-FaceReceiver }
    "stop" { Stop-FaceReceiver }
    "status" { Show-FaceReceiverStatus }
    default { throw "Unknown command '$Command'. Use: start, stop, status" }
}
