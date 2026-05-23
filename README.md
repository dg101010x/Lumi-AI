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
