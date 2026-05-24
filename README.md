# AegisAI / Lumi AI

AegisAI is the hackathon build log, codebase, and demo stack for an elder-care assistant we built during **Synthesis Hacks**, a free in-person 12-hour high school hackathon held on **May 23, 2026** at **Google Humboldt in Sunnyvale, California**. Teams had to build and submit between check-in and the 5 PM deadline, then demo in person to judges that evening.

Hackathon page:

- [Synthesis Hacks on Devpost](https://synthesishacks.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Recently+ended)

This repository is not a polished single-product repo. It is the merged result of the actual sprint:

- original app scaffolds
- Raspberry Pi + Limelight experiments
- Windows webcam + Supabase recognition workflows
- browser live preview tools
- fall-detection and earlier prototype code that we did not want to lose

That is why `main` now looks like a monorepo. It is one branch containing the real evolution of the project.

## The idea

The product pitch was simple:

> an always-on room assistant for elder care that watches, listens, logs, and escalates when something is wrong

The demo vision centered around three moments:

1. fall detected
2. resident asks for something simple like food
3. medication reminder gets confirmed and logged

The intended hardware/software story was:

- **in-room edge**: Raspberry Pi 5 + Limelight 3A
- **caregiver experience**: phone-friendly dashboard
- **AI layer**: Gemini / Vertex AI style assistant behavior
- **state and sync**: Supabase

## Why the architecture looks like this

We did not build this in one straight line. We built it the way hackathon teams actually build:

1. start from the clean story and planned architecture
2. get blocked by hardware/network/auth
3. reduce scope to preserve the demo
4. keep the original path alive while creating a fallback that is more likely to work live

That is exactly what happened here.

## The hackathon context that shaped the build

Two workshop artifacts influenced the technical direction:

- `AI Workshop Synthesis Hacks.pdf`
- `GCP commands.pdf`

The workshop emphasized a practical Google Cloud split:

- frontend separated from backend
- Cloud Run for backend logic
- Firestore or Cloud SQL for state
- Vertex AI for structured language tasks
- Pub/Sub and tasks for async work

The command sheet provided the standard hackathon bootstrap:

- `gcloud auth login`
- `gcloud config set project ...`
- enabling `run.googleapis.com`, `firestore.googleapis.com`, `aiplatform.googleapis.com`, and other core APIs
- deploying with `gcloud run deploy --source .`

That cloud-first guidance shows up in the repo in:

- `Dockerfile`
- `.dockerignore`
- Cloud Run notes in the scripts and preview server
- early attempts to make the camera stream public through GCP instead of only local LAN tooling

## The real build story

### Phase 1: the repo started as app scaffolding

The earliest `main` history was app-facing:

- `f5c4e7d` Initial commit
- `c3d7038` Add SwiftUI iOS app and bootstrap Next.js onboarding web app
- `ffa3713` and `f06b742` README revisions around the Lumi AI caregiver app story

This was the polished caregiver-facing layer:

- SwiftUI app in [`ios/`](./ios)
- Next.js onboarding web scaffold in [`web/`](./web)

At that point, the repo mostly told the product story, not the sensor story.

### Phase 2: the Pi / Limelight path became the priority

Once the camera/hardware side took over, the first requirement was not “AI”. It was just:

> can the Pi actually see the Limelight feed reliably?

That led to:

- `3a3f618` Add Raspberry Pi Limelight viewer scaffold
- `a220cf9` Add public Limelight web preview bridge
- `63b6a42` Prepare Limelight preview for Cloud Run
- `c9e0f2f` Add managed services for Limelight preview tunnel
- `7aeebc1` Add webcam face sender and ngrok service

The Pi work became:

- probe the Limelight
- auto-discover the IP when possible
- render the raw MJPEG feed
- expose a local preview page
- keep it alive with user services
- make it shareable without changing routers

That produced:

- [`pi/limelight_probe.py`](./pi/limelight_probe.py)
- [`pi/limelight_video_viewer.py`](./pi/limelight_video_viewer.py)
- [`pi/limelight_web_preview.py`](./pi/limelight_web_preview.py)
- [`deploy/systemd/`](./deploy/systemd)

### Phase 3: reality forced a fallback away from “Pi does everything”

The original idea was to keep the Pi central. In practice, several things made that risky for a live hackathon demo:

- network discovery and local-only camera URLs
- the difficulty of making the feed reachable from Cloud Run
- slow or fragile installs on ARM
- `dlib` / `face_recognition` build pain on Raspberry Pi
- fast-changing device indexes and camera availability

So the architecture pivoted:

> keep the Pi path alive, but build a Windows-only path that can do local webcam capture, face matching, Supabase sync, and browser preview on one machine

That was the single most important engineering decision in this sprint. It traded elegance for demo survivability.

### Phase 4: the Windows face stack became the working demo path

The Windows branch history shows that pivot clearly:

- `04927dd` Add Windows face matching and LumiAI launcher
- `8e963d5` fix(windows): resolve live view issues by adding missing dependencies and updating configuration
- `cf5dd81` fix(windows): set default unknown person name to `unidentified`
- `3c07a54` Add Supabase test face insert script
- `b4cff0d` Add base64 face upload flow and harden secret hygiene
- `eb9bc05` Add live local face receiver view
- `2337100` improve face matching and preview with browser-side camera and embedding normalization
- `78f28eb` add base64 insert/update path and name new faces `unidentified`
- `349ce49` sync faces to Supabase with raw base64 and update existing matches
- `0238dc7` add real-time event log and telemetry status
- `436ab6b`, `9ced36a`, `ad6a6f9`, `d6dd6f3` multiple debugging and reliability passes
- `e233891` stable working face sync to Supabase
- `78f7a8a` add recognized faces gallery with base64 decoding
- `9484893` fix face upload errors and wire dashboard entirely to Supabase

That line of work created the most practical demo stack in this repo:

- webcam plugged into Windows machine
- live local browser view on `127.0.0.1:8080`
- face detection and embedding locally
- Supabase lookup against `known_faces`
- unknown faces inserted into `known_faces` and `images`
- local launcher command `lumiai`

## The biggest problems we hit

These were the real blockers, not theoretical ones:

### 1. Branches split faster than the product converged

The repo history split into:

- app scaffold work
- Pi / Limelight work
- Windows face-recognition work

They did not land on one clean branch naturally. That is why `main` later needed manual unrelated-history merging.

### 2. Camera streaming was easy locally and awkward remotely

The live feed worked locally much earlier than it worked publicly. The hard part was not rendering MJPEG. The hard part was making a local room camera reachable in a demo-safe way.

That produced several parallel approaches:

- local preview page
- localtunnel
- ngrok
- Cloud Run preparation

### 3. Cloud Run was code-ready before it was network-ready

The preview server could be containerized, but Cloud Run could not directly read:

- `limelight.local`
- `172.29.x.x`
- other LAN-only camera addresses

So the cloud path was structurally blocked until the source became publicly reachable or reverse-proxied.

### 4. Supabase auth was one of the nastiest practical blockers

At different points:

- reads worked
- writes failed because of RLS
- publishable keys were insufficient
- service-role keys were needed for reliable inserts

That forced a lot of the later scripts and fixes:

- explicit insert tests
- base64 image paths
- `known_faces` vs `images` schema alignment
- exact update flows for unidentified faces

### 5. `face_recognition` on Pi was a real-time tax

The code path was valid, but the build/install/runtime cost on the Pi was much worse than on Windows. That is one reason the Windows-only fallback became the demo-safe route.

### 6. Camera devices were inconsistent even on Windows

The live stack broke multiple times simply because the selected camera index was wrong or disappeared. The launcher and health checks mattered because `127.0.0.1:8080` being up did not mean the camera was actually healthy.

## What the repo contains now

## Current product scaffolds

- [`ios/`](./ios)  
  SwiftUI caregiver app scaffold
- [`web/`](./web)  
  Next.js onboarding scaffold

## Raspberry Pi / Limelight path

- [`pi/limelight_probe.py`](./pi/limelight_probe.py)
- [`pi/limelight_video_viewer.py`](./pi/limelight_video_viewer.py)
- [`pi/limelight_web_preview.py`](./pi/limelight_web_preview.py)
- [`deploy/systemd/aegis-preview.service`](./deploy/systemd/aegis-preview.service)
- [`deploy/systemd/aegis-localtunnel.service`](./deploy/systemd/aegis-localtunnel.service)
- [`deploy/systemd/aegis-ngrok.service`](./deploy/systemd/aegis-ngrok.service)

## Windows face / Supabase / live preview path

- [`windows/face_receiver.py`](./windows/face_receiver.py)
- [`windows/face_matching.py`](./windows/face_matching.py)
- [`windows/supabase_known_faces.py`](./windows/supabase_known_faces.py)
- [`windows/webcam_supabase_match.py`](./windows/webcam_supabase_match.py)
- [`windows/webcam_supabase_live.py`](./windows/webcam_supabase_live.py)
- [`windows/lumiai.ps1`](./windows/lumiai.ps1)

## Legacy prototype retained for reference

- [`guardiancare/`](./guardiancare)

This older directory is not dead weight. It preserves:

- earlier fall-detection logic
- earlier face-recognition logic
- duplicated app scaffolds from the prototype phase

## Directory map

```text
.
├── guardiancare/          Earlier prototype and experiments
├── ios/                   Current SwiftUI app scaffold
├── web/                   Current Next.js scaffold
├── pi/                    Raspberry Pi + Limelight tools
├── windows/               Windows webcam, live preview, Supabase sync
├── deploy/systemd/        Pi keepalive services
├── prompts/               Gemini prompts
├── scripts/               Installers and utilities
├── vendor/                Vendored helper tools
├── prd.md                 Hackathon PRD
└── README.md
```

## Current practical architecture

There are two real operating modes:

### Mode A: Pi-centered

- Limelight 3A or USB webcam -> Pi
- Pi shows raw preview
- optional tunnel makes preview public
- Pi can upload face data downstream

### Mode B: Windows-centered

- webcam directly on Windows machine
- local recognition with `face_recognition`
- Supabase-backed identity store
- browser live preview at `127.0.0.1:8080`
- optional speaker / Gemini-assisted prompt flow

For a hackathon demo, Mode B was usually the safer path.

## Supabase schema used by the face workflows

Current face flows rely on:

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

Operational notes:

- publishable keys may be enough for reads
- service-role keys are the reliable write path
- RLS was a real blocker during development
- keep secrets out of tracked repo files

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

Exposes:

- `http://<PI_IP>:8080/`
- `http://<PI_IP>:8080/stream.mjpg`
- `http://<PI_IP>:8080/healthz`

### Pi -> Windows face sender / receiver

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

Endpoints:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/stream.mjpg`
- `http://127.0.0.1:8080/healthz`

## `lumiai` global Windows command

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

This launcher exists because the local demo stack changed frequently and needed one stable entry point.

## Public preview and tunnels

Quick local tunnel:

```powershell
npx localtunnel --port 8080
```

Pi keepalive helpers:

- [`scripts/install_user_services.sh`](./scripts/install_user_services.sh)
- [`scripts/localtunnel-watch.sh`](./scripts/localtunnel-watch.sh)
- [`scripts/ngrok-watch.sh`](./scripts/ngrok-watch.sh)

## Cloud Run notes

This repo includes:

- [`Dockerfile`](./Dockerfile)
- [`.dockerignore`](./.dockerignore)

That reflects the GCP workshop direction. In practice, the important limitation was:

> Cloud Run can only help if the camera source is reachable from Google Cloud

LAN-only addresses like `limelight.local` or `172.29.x.x` are not enough on their own.

Main preview env vars:

- `PORT`
- `LIMELIGHT_SOURCE_URL`
- `LIMELIGHT_SOURCE_HOST`
- `WEBCAM_DEVICE`
- `WEBCAM_WIDTH`
- `WEBCAM_HEIGHT`
- `WEBCAM_FPS`
- `WEBCAM_JPEG_QUALITY`

## Gemini prompt

[`prompts/gemini_system_prompt.txt`](./prompts/gemini_system_prompt.txt) contains the current system prompt draft for the Pi-side assistant path.

## Useful helper scripts

- [`scripts/install_lumiai_command.ps1`](./scripts/install_lumiai_command.ps1)
- [`scripts/insert_test_face_to_supabase.ps1`](./scripts/insert_test_face_to_supabase.ps1)
- [`scripts/send_random_image_to_supabase.py`](./scripts/send_random_image_to_supabase.py)
- [`scripts/upload_download_jpg.py`](./scripts/upload_download_jpg.py)
- [`scripts/install_user_services.sh`](./scripts/install_user_services.sh)
- [`scripts/localtunnel-watch.sh`](./scripts/localtunnel-watch.sh)
- [`scripts/ngrok-watch.sh`](./scripts/ngrok-watch.sh)

## What `main` means now

`main` is not “the one perfect architecture.”

It is the merged history of the actual hackathon:

- the polished caregiver app story
- the Pi + Limelight path
- the Windows-only survival path
- the Supabase sync/debug cycle
- the fall-detection prototype work

That is intentional. We merged all branches into `main` so the whole sprint is preserved in one place instead of leaving the winning pieces stranded on separate branches.
