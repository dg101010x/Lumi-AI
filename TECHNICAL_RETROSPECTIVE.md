# Lumi AI Technical Retrospective

This document is the technical postmortem for the Lumi AI hackathon build. It
is based on:

- the full commit graph across all local and remote branches
- the actual diffs that landed in each phase
- the current file layout in `main`
- the Discord timeline that captured idea changes, tunnel sharing, and late
  handoffs

This is intentionally more technical than `README.md`. The README tells the
story. This file explains how the codebase evolved, what classes of problems
kept reappearing, what each branch was really for, and what the final repo is
actually preserving.

## 1. Executive technical summary

Lumi AI started as an elder-care room assistant concept with four intended
technical pillars:

- in-room perception
- caregiver-facing software
- backend state and identity
- fall detection / event interpretation

By the end of the hackathon, the repo had three serious implementation lines:

1. a **Raspberry Pi + Limelight preview path**
2. a **Windows webcam + Supabase face recognition path**
3. a **preserved fall-detection lineage** in both `guardiancare/` and
   `guardiancare_late/`

The project did not converge to one pristine architecture. It converged to one
architecture that was most likely to demo, while preserving the other branches
of work instead of deleting them.

The most important engineering truth from the diffs is:

> the main technical battle was not model quality first. It was system
> survivability: camera access, public reachability, image transport,
> Supabase correctness, and a fallback architecture that could run on one
> machine when the Pi path became too risky.

## 2. Branch topology and what each branch really meant

The branch graph is not noise. Each branch corresponds to a different technical
problem space.

### `main`

`main` is the preservation branch. It is not a pure deployment branch. It
contains:

- merged Pi/Limelight preview work
- merged Windows/Supabase face matching work
- merged or preserved caregiver app scaffolds
- earlier GuardianCare prototype code
- unpacked late-stage GuardianCare bundle
- the documentation layer that reconstructs the sprint

### `raw-limelight-feed`

This branch is about **camera visibility and public preview**.

Its main responsibilities became:

- prove that the Pi could discover and open the Limelight stream
- proxy the stream to a local browser page
- expose a shareable preview path through tunnels
- keep that preview alive with service wrappers

It is the branch that captures the realization that a working stream and a
demoable stream are not the same thing.

### `windows-face-supabase-match`

This branch is about **face identity and a Windows-only fallback path**.

Its main responsibilities became:

- webcam capture on the laptop
- face embedding generation
- live local preview
- Supabase lookup and insert flows
- dashboard/gallery rendering
- launcher and operator convenience

It is the branch where the most repeated debugging happened.

### `pi-limelight-orchestrator`

This branch points at the later end of the Windows/Supabase lineage even though
the name sounds Pi-centric. In practice, it became the branch where the final
face sync, dashboard wiring, and image update fixes lived before merge.

This mismatch between branch naming and actual contents is itself a hackathon
artifact. The work moved faster than the branch taxonomy.

### `openpose-pose-integration`

This is an exploration branch, not a full production path.

Important detail from the graph:

- it points at `63b6a42`
- there is a stash on top of it
- there are untracked/index stash entries

That means OpenPose was a real technical exploration, but it did not become a
fully landed committed branch the way the Windows/Supabase path did.

### `guardiancare/` and `guardiancare_late/`

These are not branches now, but they represent two separate fall-detection
lineages:

- `guardiancare/` is the earlier prototype path brought in by `39f6c42`
- `guardiancare_late/` is the late shared zip handoff that was unpacked and
  preserved later

Technically, this means the repo preserves both:

- an earlier integrated prototype
- a later isolated fall-detection bundle

## 3. Architecture evolution by phase

### Phase A: Camera discovery and raw streaming

Core files:

- `pi/limelight_probe.py`
- `pi/limelight_video_viewer.py`
- `pi/limelight_web_preview.py`

Initial technical assumption:

- if the Pi can see the Limelight, the rest of the stack can be built on top

What the code actually did:

- attempted host discovery
- tried multiple stream path candidates
- opened MJPEG sources in OpenCV
- later proxied those sources into a browser-viewable preview page

What this phase taught:

- camera IO was achievable
- browser preview was achievable
- but neither implied public reachability

### Phase B: Public-preview experiments

Core files:

- `Dockerfile`
- `.dockerignore`
- `deploy/systemd/aegis-preview.service`
- `deploy/systemd/aegis-localtunnel.service`
- `deploy/systemd/aegis-ngrok.service`
- `scripts/install_user_services.sh`
- `scripts/localtunnel-watch.sh`
- `scripts/ngrok-watch.sh`

Initial technical assumption:

- if the preview server can be containerized or tunneled, the demo path is
  solved

What the diffs revealed:

- the preview service itself was straightforward to host
- the upstream camera source was not internet-native
- Cloud Run could host a preview application, but not magically read
  `limelight.local` or a LAN-only IP
- tunnels solved some problems but introduced their own fragility

Main engineering conclusion:

- public video transport became its own subsystem

### Phase C: Pi sender / Windows receiver split

Core files:

- `pi/face_capture_sender.py`
- `windows/face_receiver.py`

Initial technical assumption:

- the Pi could remain the producer while a more convenient machine handled
  identity and storage

What was added:

- sender-side face crop / embedding flow
- receiver endpoints
- multipart and later JSON-base64 upload paths

Main engineering gain:

- responsibilities were separable
- the Pi did not have to do every hard task locally

Main engineering risk:

- transport shape became part of the problem
- image payload format now mattered as much as embedding logic

### Phase D: Windows-only fallback becomes the primary demo path

Core files:

- `windows/webcam_supabase_live.py`
- `windows/webcam_supabase_match.py`
- `windows/face_matching.py`
- `windows/supabase_known_faces.py`
- `windows/lumiai.ps1`

This phase is the real center of the late-day repo.

It solved:

- direct webcam access on the demo machine
- local browser preview
- face matching without Pi build pain
- one-command launch ergonomics

It also introduced the densest cluster of bugs:

- preview lag
- unstable camera indices
- missing uploads
- repeated uploads / duplicates
- ambiguous image storage semantics
- matched-face update failures
- dashboard image rendering errors

### Phase E: Preserved fall-detection lineages

Core files:

- `guardiancare/fall_detection.py`
- `guardiancare/main.py`
- `guardiancare_late/fall_detection.py`
- `guardiancare_late/main.py`

These lineages matter because they show the perception goal never disappeared.
The team kept pursuing fall detection even while the recognition/demo-survival
path was being debugged.

The late bundle shows:

- MediaPipe Pose-based logic
- torso-angle checks
- hip-drop heuristics
- cooldown logic
- registration image capture

That means the fall-detection part of Lumi AI was not merely conceptual. It
survived in code, just not as the one final consolidated runtime path.

## 4. Root-cause problem categories from the diffs

The diffs across branches cluster into a handful of repeated technical themes.

### A. Reachability problems

Symptoms:

- local stream works
- browser preview works locally
- public or cloud-hosted preview still fails to show real camera data

Root causes:

- upstream source bound to LAN-only hostnames or IPs
- tunnel dependency
- Cloud Run can serve the app but cannot see the source camera

Evidence in repo:

- preview bridge
- Cloud Run prep
- tunnel services
- repeated preview link sharing in Discord

### B. Transport format problems

Symptoms:

- image flow works in one path but not another
- file URIs are convenient locally but poor for backend sync
- preview/gallery cannot reliably render stored images

Root causes:

- mixed use of file paths, local URIs, raw base64 strings, and image table rows
- `photo_url` semantics drifting between “real URL,” “raw base64,” and later
  “image row identifier”

Evidence in repo:

- `b4cff0d`
- `78f28eb`
- `349ce49`
- `9484893`

### C. Identity and state consistency problems

Symptoms:

- unknown faces get created but matched faces do not update correctly
- names/labels are inconsistent
- dashboard state diverges from backend truth

Root causes:

- insert path landed before stable update path
- `person_name`, `label`, and `display_name` semantics were refined over time
- the dashboard initially mixed local and remote state assumptions

Evidence in repo:

- `cf5dd81`
- `d6dd6f3`
- `e233891`
- `78f7a8a`
- `9484893`

### D. Observability problems

Symptoms:

- “it is running” did not mean “it is working”
- failures were hard to localize
- debugging required more than terminal output

Root causes:

- pipeline had multiple stages:
  - camera read
  - encode
  - match
  - upload
  - gallery/render
- failures could occur silently in different places

Evidence in repo:

- `0238dc7`
- `436ab6b`
- `ad6a6f9`

### E. Performance / responsiveness problems

Symptoms:

- laggy local browser view
- over-processing frames
- duplicate or overly frequent detections

Root causes:

- recognition too expensive to run every frame at full scale
- cooldown/recent-face heuristics not yet tuned
- preview cadence and processing cadence were initially coupled too tightly

Evidence in repo:

- `8e963d5`
- `436ab6b`
- `9ced36a`

### F. Branch and merge debt

Symptoms:

- branch names no longer matched the real content
- useful code existed in parallel lineages
- preservation itself became work

Root causes:

- the team was optimizing for progress, not tidy history
- the repo captured pivots, not just polished decisions

Evidence in repo:

- merged branch graph
- OpenPose stash rather than final committed route
- late GuardianCare preservation commits

## 5. Detailed technical reading of the Windows face pipeline

This was the most heavily iterated subsystem.

### Initial form

The initial Windows path established:

- webcam capture
- live preview
- Supabase lookup
- basic face insertion and matching

At this point, the pipeline existed but was still brittle.

### First hardening wave

`8e963d5` changed the runtime model materially:

- added JPEG helper logic
- discovered LAN IP automatically
- served saved images through HTTP
- separated stream cadence from recognition cadence
- reused detections across frames
- exposed tuning knobs like `--process-every-n` and `--detect-scale`

Technical meaning:

- this commit turned the live preview from a naive demo loop into a more
  practical video-processing application

### Upload correctness wave

`9ced36a` addressed a real logic flaw:

- uploads could be skipped before the encoding step happened in the unknown-face
  path

Technical meaning:

- visible detections were not sufficient
- the pipeline still needed explicit control-flow repair

### Matched-face update wave

`d6dd6f3` and `9484893` addressed the biggest identity flaw:

- unknown faces could create rows
- but matched faces were not yet first-class update events

Technical meaning:

- the project initially solved “can I detect a new person”
- before fully solving “can I keep an existing person’s backend record current”

### Gallery truthfulness wave

`78f7a8a` and `9484893` brought the dashboard closer to reality:

- image rendering now came from Supabase-backed data
- not just whatever local state happened to exist in the running process

Technical meaning:

- the dashboard became less of a local convenience page
- and more of a real backend reflection layer

## 6. Detailed technical reading of the Pi / Limelight line

This subsystem solved the first hardware problem but exposed the network and
deployment problem.

### What it did well

- host and path discovery
- raw MJPEG consumption
- simple browser proxying
- service wrapping for repeatability

### What it did not fully solve

- robust, permanent public video reachability
- cloud-hostable access to a LAN-only upstream source
- a clean bridge from raw stream access to reliable recognition + backend sync

This is why the Windows fallback became primary instead of the Pi path simply
being extended forever.

## 7. Detailed technical reading of the fall-detection artifacts

There are two important preserved fall-detection states.

### `guardiancare/`

This looks like the earlier integrated prototype version of the product. It
bundles:

- caregiver-facing app shells
- Supabase pieces
- face recognition module
- fall detection module

Its value is architectural: it shows that the elder-care idea was already being
built as a more complete product concept, not just as camera scripts.

### `guardiancare_late/`

This is more like a late handoff snapshot. Its value is forensic:

- it proves fall detection was still being worked on near the end
- it contains fresh registration images from the event window
- it captures a concrete pose-based fall approach

Its main weakness is that it is a preserved bundle, not a fully re-integrated
branch of the main runtime path.

## 8. What the diffs say about the real decision points

There were four decisive technical pivots.

### Pivot 1: from “camera access” to “browser-accessible preview”

This created the preview server path.

### Pivot 2: from “local preview is enough” to “demo shareability is a separate problem”

This created the tunnel/service/deployment work.

### Pivot 3: from “Pi is the center” to “Windows can carry the full demo if needed”

This created the strongest working face path in the repo.

### Pivot 4: from “face inserts exist” to “Supabase must become the actual source of truth”

This created the later dashboard, gallery, and update-path hardening.

## 9. What was solved by the end

By the end of the hackathon and post-hoc preservation work, the repo clearly
solved:

- caregiver app scaffolding
- Limelight stream discovery and preview
- local video proxying
- tunnel/service support for preview experiments
- Windows webcam-based recognition loop
- Supabase-backed face lookup and unknown creation
- a workable path for matched-face updates
- a local dashboard/gallery backed by Supabase data
- preservation of both early and late fall-detection implementations

## 10. What remained unresolved or only partially resolved

The diffs also show what did **not** converge to one clean final answer.

### Unresolved or partially resolved areas

- one single production architecture for the whole product
- a permanent public video hosting path that did not depend on local network
  tricks or tunnels
- a fully integrated final fall-detection runtime merged into the same main
  recognition/dashboard execution path
- a completely clean semantic model for every face/image field from the very
  beginning
- a branch structure that cleanly mirrors the product structure

### Important nuance

These are not failures in the hackathon sense. They are exactly what the diffs
show when a team keeps the right work instead of deleting it just because it
arrived on different branches or at different times.

## 11. If this were continued after the hackathon

Based strictly on the diffs, the best cleanup path would be:

1. split runtime targets explicitly:
   - Pi preview/runtime
   - Windows recognition runtime
   - caregiver app/web surfaces
   - fall-detection module
2. normalize the face/image storage model:
   - one meaning for `photo_url`
   - one meaning for image rows
   - one meaning for current-vs-historical images
3. choose one perception backbone for fall detection:
   - MediaPipe pose
   - OpenPose
   - or a hybrid, but not three overlapping preserved paths
4. decide whether the Pi remains the production edge device or becomes an input
   node feeding a stronger workstation/cloud path
5. extract observability/logging into a deliberate telemetry surface instead of
   leaving it embedded mainly in one Python runtime

## 12. Final technical conclusion

The code diffs across all branches tell a very consistent story:

Lumi AI was not primarily blocked by lack of ideas. It was blocked by the
hardest kind of hackathon engineering problems:

- unstable IO surfaces
- transport mismatches
- backend truth drift
- public reachability
- and the need to pivot to a more demoable architecture without discarding
  earlier work

That is why the final repo looks like a merged technical archive instead of a
single narrow app. It is preserving the actual engineering path:

- the original product vision
- the Pi-centered attempt
- the Windows-centered fallback
- the repeated Supabase hardening
- and the preserved fall-detection work that never should have been lost.
