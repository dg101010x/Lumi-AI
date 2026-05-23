# AegisAI Pi Scaffold

This branch contains the Raspberry Pi starting point for the Aegis hackathon build.

## First objective

Validate that the Pi can open and display the Limelight 3A live video stream.

## Quick start

1. Create a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the probe script against your Limelight IP.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python pi\limelight_probe.py --host 10.0.0.50
```

If the endpoint path differs on your Limelight pipeline, keep the script and swap only the URL path once you confirm the real API in the Limelight web UI.

For this branch, do not add any processing. Just show the raw live feed.

## Live video feed only

If you just want to display the Limelight live feed on the Pi, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python pi/limelight_video_viewer.py
```

The viewer now tries to auto-discover the Limelight IP and a common MJPEG stream path.

If auto-discovery misses, try either of these:

```bash
python pi/limelight_video_viewer.py --host limelight.local
python pi/limelight_video_viewer.py --url "http://<LIMELIGHT_IP>:5800/<STREAM_PATH>"
```

## Local web preview

If you want a simple webpage and MJPEG endpoint for the raw Limelight feed, run:

```bash
source .venv/bin/activate
python pi/limelight_web_preview.py --source-host limelight.local
```

This exposes:

- `http://<PI_IP>:8080/`
- `http://<PI_IP>:8080/stream.mjpg`
- `http://<PI_IP>:8080/healthz`

For a fast public demo tunnel without router changes, you can proxy the local preview with:

```bash
npx localtunnel --port 8080
```

That returns a public `https://...loca.lt` URL that forwards to the local preview page.

## Keep it running

To keep the preview server and tunnel running across logouts and reboots on the Pi:

```bash
cd /home/pranav/Documents/AeigisAI/AegisAI
chmod +x scripts/localtunnel-watch.sh scripts/install_user_services.sh
./scripts/install_user_services.sh
```

Check service status:

```bash
systemctl --user status aegis-preview.service
systemctl --user status aegis-localtunnel.service
```

Get the current public tunnel URL:

```bash
cat /run/user/1000/aegisai/localtunnel-url.txt
```

The install script stores the current working Limelight stream URL in:

```bash
cat ~/.config/aegis-preview.env
```

View recent tunnel logs:

```bash
journalctl --user -u aegis-localtunnel.service -n 50 --no-pager
```

## Cloud Run deployment

The same preview server can run on Cloud Run, but it must be given a source that Cloud Run can actually reach.

Environment variables:

- `PORT`: injected by Cloud Run
- `LIMELIGHT_SOURCE_URL`: full upstream MJPEG URL
- `LIMELIGHT_SOURCE_HOST`: optional host/IP for local probing when the service runs on a machine that can see the camera

Build and deploy:

```bash
gcloud config set project synthesis-hack26svl-105

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

gcloud run deploy aegisai-limelight-preview \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LIMELIGHT_SOURCE_URL=http://REACHABLE_HOST:5800/stream.mjpg
```

Important: if your Limelight feed is only reachable on the Raspberry Pi LAN at addresses like `172.29.0.1` or `limelight.local`, a Cloud Run service in Google Cloud cannot reach it directly. In that case, Cloud Run deployment is code-ready, but the upstream source must first be made reachable from Google Cloud.

## Windows face matching against Supabase

This repo also includes a Windows receiver that matches incoming face embeddings against the Supabase `known_faces` table.

Observed public table shape in the target Supabase project:

- `known_faces.id`
- `known_faces.embedding`
- `known_faces.photo_url`
- `known_faces.person_name`
- `known_faces.label`
- `known_faces.created_at`
- `known_faces.last_seen_at`

### Windows receiver

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt
$env:SUPABASE_PROJECT_URL="https://gmmpltgvtonpnrfckrvy.supabase.co"
$env:SUPABASE_PUBLISHABLE_KEY="<your publishable key>"
python windows\face_receiver.py --host 0.0.0.0 --port 5000
```

Defaults:

- metric: `euclidean`
- threshold: `0.6`
- table: `known_faces`

Use `--metric cosine --threshold 0.65` if your stored embeddings were produced by an OpenCV SFace-style pipeline instead of `face_recognition`.

### Pi sender

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-face.txt
python pi/face_capture_sender.py \
  --upload-url http://<WINDOWS_PC_IP>:5000/upload \
  --device /dev/video0 \
  --show
```

The sender:

- captures webcam frames
- detects faces with `face_recognition.face_locations`
- computes embeddings with `face_recognition.face_encodings`
- uploads an annotated frame plus JSON metadata to the Windows receiver

The Windows receiver:

- refreshes `known_faces` from Supabase
- matches each incoming embedding against stored embeddings
- tries to create a new `known_faces` row when no match is found
- saves a `.jpg` and matching `.json` under `received_faces/`
- returns the match result in the upload response

## Windows-only stack

If the webcam is plugged directly into this Windows PC, you can skip the Raspberry Pi entirely and run local capture plus Supabase matching on one machine.

Install:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-windows-camera.txt
```

Run:

```powershell
python windows\webcam_supabase_match.py `
  --api-key "sb_publishable_6JWerc5NPf-fNmzEoGAiYw_B9OGynLb" `
  --project-url "https://gmmpltgvtonpnrfckrvy.supabase.co" `
  --device 0
```

This path:

- opens the local Windows webcam
- detects faces with `face_recognition`
- computes face embeddings locally
- loads known embeddings from Supabase `known_faces`
- matches each face locally on the PC
- skips recently seen repeats
- tries to create a new `known_faces` row when no match is found
- draws labels on the live webcam view
- saves annotated `.jpg` and `.json` results into `received_faces_local/`

Notes:

- default metric is `euclidean` with threshold `0.6`, which matches the usual `face_recognition` convention
- recent-face suppression defaults to distance `0.25` and `45` seconds, similar to the FamiliarAI pattern
- if your Supabase `known_faces.embedding` values came from an OpenCV SFace pipeline instead, try `--metric cosine --threshold 0.65`
- if `known_faces` is empty or not readable through the publishable key, all detections will show as `unknown`
- if Supabase insert is blocked by RLS, the script will keep running and save the exact insert error in the JSON output

### Windows-only live web view

If you want the same Windows webcam stack plus a browser-accessible live view:

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\Activate.ps1
pip install -r requirements-windows-live.txt
python windows\webcam_supabase_live.py `
  --api-key "<your Supabase key>" `
  --project-url "https://gmmpltgvtonpnrfckrvy.supabase.co" `
  --device 0 `
  --port 8080
```

This exposes:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/stream.mjpg`
- `http://127.0.0.1:8080/healthz`

To make it public quickly on Windows:

```powershell
npx localtunnel --port 8080
```

Use the returned URL for the page and append `/stream.mjpg` for the raw stream.

### `lumiai` command from anywhere on Windows

Install the global launcher once:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_lumiai_command.ps1 `
  -SupabaseApiKey "<your Supabase service key>"
```

Then open a new terminal and run:

```powershell
lumiai
```

Useful commands:

```powershell
lumiai
lumiai status
lumiai url
lumiai stop
```

Default behavior:

- starts the Windows webcam live matcher on port `8080`
- starts `localtunnel`
- prints the local and public live-view links
- if Supabase insert is blocked by RLS, the scripts keep running and store the exact insert error in the JSON output

## Gemini prompt

Use [prompts/gemini_system_prompt.txt](C:/Users/emmad/Downloads/Hackathon-synthesis/AegisAI/prompts/gemini_system_prompt.txt:1) as the system instruction for the Pi-side Gemini request.

At runtime, send the live room context as the user payload, for example:

```json
{
  "current_time": "2026-05-23T14:00:00-07:00",
  "transcript": "",
  "recent_events": [],
  "meds_due_now": [],
  "fall_detected": false,
  "distress_detected": false,
  "silence_after_activity": false,
  "face_detected": true,
  "face_count": 1,
  "face_confidence": 0.94,
  "room_presence": true
}
```

Success condition: Gemini returns JSON only, which your Pi code can parse directly into speech, backend action, and severity.
