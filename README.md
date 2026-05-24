# Lumi AI

Lumi AI is the build log, codebase, and demo stack for our project at **Synthesis Hacks**, a free in-person 12-hour high school hackathon held on **May 23, 2026** at **Google Humboldt in Sunnyvale, California**. Teams had to build during the event, submit by 5 PM, and then present live to judges.

Hackathon page:

- [Synthesis Hacks on Devpost](https://synthesishacks.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Recently+ended)

This repository is not a polished single-product repo. It is the merged result of the actual sprint:

- original app scaffolds
- Raspberry Pi + Limelight experiments
- Windows webcam + Supabase recognition workflows
- browser live preview tools
- fall-detection and earlier prototype code that we did not want to lose

That is why `main` now looks like a monorepo. It is one branch containing the real evolution of the project.

## What tools we could use

The event rules were permissive. We could use:

- any language
- any framework
- any library
- any API
- AI tools, as long as anything not written by us was cited in the submission

That mattered because Lumi AI ended up using a very mixed stack:

- Python
- SwiftUI
- Next.js
- Supabase
- Google Cloud / Cloud Run ideas from the workshop
- Gemini
- Raspberry Pi hardware
- Limelight camera tooling
- Windows webcam tooling

## Our constraints and guidelines

These were the real constraints that shaped the build:

- everything had to be built during the event window
- the final system had to be demoable live, not just theoretically correct
- local hardware had to work under time pressure
- network accessibility mattered as much as code quality
- anything cloud-based had to be simple enough to wire up fast
- if one path got too fragile, we had to pivot without losing progress

Practical team constraints that emerged during the sprint:

- Pi-side installs were slower and more fragile than Windows
- camera URLs were often local-only
- Supabase auth and schema details were not frictionless
- we had to optimize for “what can be shown to judges in a few minutes”

## Themes and tracks

Synthesis Hacks was effectively **open-ended**. It was not a hackathon with one strict required theme or narrow track list for what you were allowed to build.

What the event page did emphasize were the prize and judging lenses:

- Grand Prize
- Best Technical Implementation
- Most Creative Concept
- Best First Hackathon
- Best UI/UX Design
- Audience Favorite

So instead of building to a narrow official track, we built to a practical intersection of:

- AI
- caregiving / health-adjacent support
- hardware perception
- live demo impact

## Our core idea

The product pitch was:

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

## Our brainstorming

The idea did not start as “just build face recognition.”

The broader brainstorm was around elder care anxiety:

- family members do not know if an older relative is okay
- staff and caregivers are stretched thin
- wearables and panic buttons depend on compliance
- the most valuable thing is often simple awareness: did someone fall, ask for help, or stop responding

From there, the team converged on a system with three layers:

1. perception in the room
2. an AI layer that could interpret events or prompts
3. a caregiver-facing interface that could show status and alerts

That is why the repo spans:

- room sensors and camera feeds
- AI prompts and event logic
- caregiver dashboard and app scaffolds

## Why the architecture ended up looking like this

We did not build this in one straight line. We built it the way hackathon teams actually build:

1. start from the clean story and planned architecture
2. get blocked by hardware/network/auth
3. reduce scope to preserve the demo
4. keep the original path alive while creating a fallback that is more likely to work live

That is exactly what happened here.

## Hackathon context that shaped the technical choices

We had access to Google Cloud workshop material and a GCP command/reference sheet during the event, and that influenced the technical direction.

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

## Problems we ran into +

These were the main issues that forced architecture and scope changes:

### 1. The repo split into multiple valid directions

We ended up with:

- caregiver app scaffold work
- Pi / Limelight work
- Windows face-recognition work
- older GuardianCare prototype code

That was not clean from a git-history perspective, but it was honest to how the team was actually moving.

### 2. Local camera access was easier than public camera access

We could get local MJPEG previews much earlier than we could get a clean public demo endpoint. Making the feed reachable outside the room was a much bigger problem than simply displaying the feed.

### 3. Cloud Run was not the hard part; reachability was

The preview service could be containerized, but Cloud Run could not directly read LAN-only camera sources such as:

- `limelight.local`
- `172.29.x.x`

So the blocker was not “can we deploy code to Cloud Run?” It was “can Cloud Run actually see the upstream feed?”

### 4. Supabase auth and schema details took real time

At different times:

- reads worked
- writes failed under RLS
- publishable keys were not enough for inserts
- service-role keys were needed for reliable creation/update flows

That pushed a lot of later work into debugging:

- `known_faces`
- `images`
- base64 image handling
- insert/update verification scripts

### 5. Pi-side face stack cost more time than Windows-side face stack

`face_recognition` on Windows was far easier to make demoable quickly than the same stack on Raspberry Pi. That forced the Windows fallback to become a first-class path instead of just a backup.

### 6. Camera selection was fragile even on the “easy” path

The Windows live stack broke multiple times simply because the configured camera index was wrong or disappeared. Health checks and launcher scripts mattered because a running server was not the same as a working camera.

## Our product steps and each step what we did to get there

### Step 1: caregiver product shell

We first established the product-facing side:

The earliest `main` history was app-facing:

- `f5c4e7d` Initial commit
- `c3d7038` Add SwiftUI iOS app and bootstrap Next.js onboarding web app
- `ffa3713` and `f06b742` README revisions around the Lumi AI caregiver app story

What we did:

- SwiftUI app in [`ios/`](./ios)
- Next.js onboarding web scaffold in [`web/`](./web)

This gave us the caregiver story and UI surface, even before the room-perception layer was reliable.

### Step 2: prove room-camera access on Pi

Once the camera/hardware side took over, the first requirement was not “AI”. It was just:

> can the Pi actually see the Limelight feed reliably?

What we did:

- `3a3f618` Add Raspberry Pi Limelight viewer scaffold
- `a220cf9` Add public Limelight web preview bridge
- `63b6a42` Prepare Limelight preview for Cloud Run
- `c9e0f2f` Add managed services for Limelight preview tunnel
- `7aeebc1` Add webcam face sender and ngrok service

This step focused on:

- probe the Limelight
- auto-discover the IP when possible
- render the raw MJPEG feed
- expose a local preview page
- keep it alive with user services
- make it shareable without changing routers

Artifacts:

- [`pi/limelight_probe.py`](./pi/limelight_probe.py)
- [`pi/limelight_video_viewer.py`](./pi/limelight_video_viewer.py)
- [`pi/limelight_web_preview.py`](./pi/limelight_web_preview.py)
- [`deploy/systemd/`](./deploy/systemd)

### Step 3: attempt to make the feed demo-shareable

What we did:

- built local web preview endpoints
- added localtunnel and ngrok service paths
- added Cloud Run preparation files
- tested “public demo” approaches instead of assuming LAN-only was enough

This is where the gap between “working locally” and “usable in front of judges” became obvious.

### Step 4: create a fallback that avoids the Pi bottleneck

The original idea was to keep the Pi central. In practice, several things made that risky for a live hackathon demo:

- network discovery and local-only camera URLs
- the difficulty of making the feed reachable from Cloud Run
- slow or fragile installs on ARM
- `dlib` / `face_recognition` build pain on Raspberry Pi
- fast-changing device indexes and camera availability

So the architecture pivoted:

> keep the Pi path alive, but build a Windows-only path that can do local webcam capture, face matching, Supabase sync, and browser preview on one machine

What we did:

- built receiver paths on Windows
- built local webcam recognition
- built a browser live-view page
- built one-command launcher behavior

This was the biggest practical decision of the sprint. It traded elegance for demo survivability.

### Step 5: wire the identity store and unknown-face flow

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

What we did:

- webcam plugged into Windows machine
- live local browser view on `127.0.0.1:8080`
- face detection and embedding locally
- Supabase lookup against `known_faces`
- unknown faces inserted into `known_faces` and `images`
- local launcher command `lumiai`

### Step 6: keep the earlier prototype work instead of discarding it

The commit `39f6c42` brought in the older GuardianCare prototype and fall-detection work.

What we did:

- preserved the older fall-detection code
- preserved earlier face-recognition experiments
- preserved duplicate app scaffolds that reflected prior iterations

This made `main` messier, but it prevented useful hackathon work from getting stranded.

### Step 7: preserve the late-stage fall-detection handoff

Near the end of the hackathon, fall-detection work was also preserved as a zip artifact:

- [`guardiancare.zip`](../guardiancare.zip)

What we did:

- kept the late-stage fall-detection handoff instead of treating it as throwaway output
- tied it back to the earlier `guardiancare/` prototype and the `Fall detection` commit
- treated it as part of the real project history, because that work happened late in the sprint rather than in the clean early scaffold phase

### Step 8: unpack the late GuardianCare fall-detection bundle into the repo

We then unpacked the zip into a normal tracked folder:

- [`guardiancare_late/`](./guardiancare_late)

What we verified:

- it is actually late-stage fall-detection work
- it contains `fall_detection.py`, `main.py`, `face_recognition_module.py`, `supabase_client.py`, and `config.py`
- it also contains same-day registered face images from the sprint
- the original `.env` from the zip was converted to `.env.example` before adding it to the repo

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
- [`guardiancare_late/`](./guardiancare_late)

These older directories are not dead weight. They preserve:

- earlier fall-detection logic
- earlier face-recognition logic
- duplicated app scaffolds from the prototype phase
- the unpacked late-stage GuardianCare fall-detection handoff

## Directory map

```text
.
├── guardiancare/          Earlier prototype and experiments
├── guardiancare_late/     Unpacked late-stage fall-detection bundle
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
