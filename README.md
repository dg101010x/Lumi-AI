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
