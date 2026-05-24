# AegisAI / Lumi AI

Hackathon monorepo for an elder-care assistant demo. This repo now combines four active tracks:

- caregiver-facing iOS and web product scaffolds
- Raspberry Pi + Limelight camera utilities
- Windows face recognition, Supabase syncing, and live preview tools
- the older `guardiancare/` prototype kept for reference and reuse

## What is in this repo

### 1. Product app scaffolds

- [`ios/`](./ios) contains the SwiftUI app scaffold for the caregiver experience.
- [`web/`](./web) contains the Next.js onboarding web scaffold.

### 2. Raspberry Pi / Limelight path

- [`pi/limelight_probe.py`](./pi/limelight_probe.py) probes the Limelight endpoints.
- [`pi/limelight_video_viewer.py`](./pi/limelight_video_viewer.py) opens the raw live feed.
- [`pi/limelight_web_preview.py`](./pi/limelight_web_preview.py) serves a simple MJPEG preview site.
- [`deploy/systemd/`](./deploy/systemd) contains user services for keeping the preview/tunnel alive on a Pi.

### 3. Windows face recognition path

- [`windows/face_receiver.py`](./windows/face_receiver.py) accepts uploaded face frames and syncs with Supabase.
- [`windows/webcam_supabase_match.py`](./windows/webcam_supabase_match.py) runs local webcam recognition on Windows.
- [`windows/webcam_supabase_live.py`](./windows/webcam_supabase_live.py) exposes the Windows webcam matcher through a local browser view.
- [`windows/lumiai.ps1`](./windows/lumiai.ps1) is the local launcher used by the global `lumiai` command.

### 4. Legacy GuardianCare prototype

- [`guardiancare/`](./guardiancare) is a separate older prototype with its own Python backend plus duplicated iOS/web app scaffolds.
- Keep it because it contains earlier fall-detection and face-recognition experiments that are still useful for hackathon iteration.

## Top-level structure

```text
.
├── guardiancare/          Legacy prototype
├── ios/                   Current SwiftUI app scaffold
├── web/                   Current Next.js onboarding scaffold
├── pi/                    Raspberry Pi + Limelight utilities
├── windows/               Windows capture / matching / live preview tools
├── deploy/systemd/        Pi user services
├── prompts/               Gemini system prompts
├── scripts/               Installers, helpers, Supabase utilities
├── vendor/                Vendored helper tools
├── prd.md                 Hackathon PRD
└── README.md
```

## Architecture summary

For the hackathon, there are two practical camera stacks:

1. Pi stack
   - Limelight 3A or USB webcam -> Raspberry Pi
   - Pi serves raw preview and/or uploads face data
   - Windows machine or cloud handles downstream matching/UI

2. Windows-only stack
   - webcam plugged into this PC
   - `face_recognition` computes embeddings locally
   - Supabase `known_faces` and `images` store matches/new faces
   - optional local browser view on `127.0.0.1:8080`

## Prerequisites

Depending on the path you run, you may need:

- Python 3.11 for the Windows live-view stack
- Python 3 on Linux for the Pi tools
- `face_recognition` and `dlib` for face matching paths
- Node.js if you want `localtunnel`
- Xcode for the iOS app
- a Supabase project for face storage/matching
- a Limelight 3A or USB webcam

## Supabase schema used by the face workflows

The current Windows face stack is wired against these tables:

- `known_faces`
  - `id`
  - `embedding`
  - `photo_url`
  - `person_name`
  - `label`
  - `created_at`
  - `last_seen_at`
- `images`
  - `image_name`
  - `image_url`

Important:

- publishable keys are enough for some reads, but not reliable for writes under RLS
- service-role keys work for verified inserts
- do not commit raw service-role keys into tracked files

## Quick starts

### iOS app

```text
Open ios/Lumi.xcodeproj in Xcode
Add your GoogleService-Info.plist
Add Supabase credentials locally
Build and run
```

### Web app

```powershell
cd web
npm install
npm run dev
```

### Pi: raw Limelight viewer

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python pi/limelight_video_viewer.py
```

If autodiscovery fails:

```bash
python pi/limelight_video_viewer.py --host limelight.local
python pi/limelight_video_viewer.py --url "http://<LIMELIGHT_IP>:5800/<STREAM_PATH>"
```

### Pi: local web preview

```bash
source .venv/bin/activate
python pi/limelight_web_preview.py --source-host limelight.local
```

This exposes:

- `http://<PI_IP>:8080/`
- `http://<PI_IP>:8080/stream.mjpg`
- `http://<PI_IP>:8080/healthz`

### Pi -> Windows face sender/receiver

Windows receiver:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt
$env:SUPABASE_PROJECT_URL="https://<project>.supabase.co"
$env:SUPABASE_PUBLISHABLE_KEY="<publishable-or-service-key>"
python windows\face_receiver.py --host 0.0.0.0 --port 5000
```

Pi sender:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-face.txt
python pi/face_capture_sender.py \
  --upload-url http://<WINDOWS_PC_IP>:5000/upload \
  --device /dev/video0 \
  --show
```

### Windows-only webcam matching

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-windows-camera.txt
python windows\webcam_supabase_match.py `
  --api-key "<supabase key>" `
  --project-url "https://<project>.supabase.co" `
  --device 0
```

This path:

- opens the webcam on this PC
- detects faces with `face_recognition`
- compares embeddings against Supabase `known_faces`
- skips recently seen repeats
- creates new unknown faces when no match is found

### Windows-only browser live view

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\Activate.ps1
pip install -r requirements-windows-live.txt
python windows\webcam_supabase_live.py `
  --api-key "<supabase key>" `
  --project-url "https://<project>.supabase.co" `
  --device 0 `
  --port 8080
```

Local endpoints:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/stream.mjpg`
- `http://127.0.0.1:8080/healthz`

## Global `lumiai` launcher on Windows

Install once:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_lumiai_command.ps1 `
  -SupabaseApiKey "<service key>" `
  -GeminiApiKey "<gemini key>" `
  -Device 0
```

Then from any new terminal:

```powershell
lumiai
lumiai status
lumiai url
lumiai stop
```

Current launcher behavior:

- starts the Windows webcam live matcher on port `8080`
- can optionally start a public tunnel if enabled in config
- stores local config in `%USERPROFILE%\.lumiai\config.json`

## Public preview / tunnels

For fast demo exposure of the local preview:

```powershell
npx localtunnel --port 8080
```

On Pi, the systemd services under [`deploy/systemd/`](./deploy/systemd) and the shell helpers under [`scripts/`](./scripts) keep the preview/tunnel running.

Also included from the raw-feed branch:

- [`deploy/systemd/aegis-ngrok.service`](./deploy/systemd/aegis-ngrok.service)
- [`scripts/ngrok-watch.sh`](./scripts/ngrok-watch.sh)

## Cloud Run notes

The repo includes a `Dockerfile` and `.dockerignore` so the preview service can be containerized. Cloud Run only works if the upstream camera stream is reachable from Google Cloud. A Pi-local address like `limelight.local` or `172.29.x.x` is not enough by itself.

Main env vars used by the preview service:

- `PORT`
- `LIMELIGHT_SOURCE_URL`
- `LIMELIGHT_SOURCE_HOST`
- `WEBCAM_DEVICE`
- `WEBCAM_WIDTH`
- `WEBCAM_HEIGHT`
- `WEBCAM_FPS`
- `WEBCAM_JPEG_QUALITY`

## Gemini prompt

[`prompts/gemini_system_prompt.txt`](./prompts/gemini_system_prompt.txt) contains the current system prompt draft for the Pi-side assistant flow.

## Important helper scripts

- [`scripts/install_lumiai_command.ps1`](./scripts/install_lumiai_command.ps1)
- [`scripts/insert_test_face_to_supabase.ps1`](./scripts/insert_test_face_to_supabase.ps1)
- [`scripts/send_random_image_to_supabase.py`](./scripts/send_random_image_to_supabase.py)
- [`scripts/upload_download_jpg.py`](./scripts/upload_download_jpg.py)
- [`scripts/install_user_services.sh`](./scripts/install_user_services.sh)
- [`scripts/localtunnel-watch.sh`](./scripts/localtunnel-watch.sh)
- [`scripts/ngrok-watch.sh`](./scripts/ngrok-watch.sh)

## Current merged state

`main` now contains:

- the current Lumi iOS/web scaffold
- the Pi Limelight preview path
- the Windows face matching / Supabase path
- the launcher and local live view path
- the older GuardianCare prototype

That gives you one branch with all hackathon work instead of split branch-only setups.
