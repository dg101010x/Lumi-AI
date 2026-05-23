param(
    [string]$ProjectUrl = "https://gmmpltgvtonpnrfckrvy.supabase.co",
    [string]$ApiKey = $env:SUPABASE_PUBLISHABLE_KEY,
    [string]$TableName = "known_faces"
)

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    throw "Set SUPABASE_PUBLISHABLE_KEY or pass -ApiKey before running this script."
}

Add-Type -AssemblyName System.Drawing

$size = 128
$bitmap = New-Object System.Drawing.Bitmap $size, $size
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([System.Drawing.Color]::FromArgb(245, 245, 245))

$faceBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 224, 189))
$eyeBrush = [System.Drawing.Brushes]::Black
$smilePen = New-Object System.Drawing.Pen ([System.Drawing.Color]::Black, 3)

$graphics.FillEllipse($faceBrush, 16, 12, 96, 104)
$graphics.FillEllipse($eyeBrush, 42, 44, 10, 14)
$graphics.FillEllipse($eyeBrush, 76, 44, 10, 14)
$graphics.DrawArc($smilePen, 40, 54, 48, 30, 15, 150)

$memory = New-Object System.IO.MemoryStream
$bitmap.Save($memory, [System.Drawing.Imaging.ImageFormat]::Png)
$pngBytes = $memory.ToArray()
$base64 = [Convert]::ToBase64String($pngBytes)
$dataUrl = "data:image/png;base64,$base64"

$embedding = @(for ($i = 0; $i -lt 128; $i++) { [Math]::Round($i / 1000.0, 3) })
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")

$payload = @{
    person_name = "quick-test-face-$timestamp"
    label = "quick-test-face"
    embedding = $embedding
    photo_url = $dataUrl
    last_seen_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 6

$headers = @{
    apikey = $ApiKey
    Authorization = "Bearer $ApiKey"
    "Content-Type" = "application/json"
    Prefer = "return=representation"
}

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "$($ProjectUrl.TrimEnd('/'))/rest/v1/$TableName" `
    -Headers $headers `
    -Body $payload

$row = $response | Select-Object -First 1

[PSCustomObject]@{
    id = $row.id
    person_name = $row.person_name
    label = $row.label
    photo_url_prefix = if ($row.photo_url) { $row.photo_url.Substring(0, [Math]::Min(32, $row.photo_url.Length)) } else { "" }
    photo_url_length = if ($row.photo_url) { $row.photo_url.Length } else { 0 }
}
