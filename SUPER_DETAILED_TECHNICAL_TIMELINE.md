# Lumi AI Super Detailed Technical Timeline

This file is a technical timeline, not a general retrospective.

It is ordered primarily by timestamp and secondarily by branch context. The goal
is to reconstruct what the repo was technically becoming throughout the day.

This timeline is based on:

- exact git commit timestamps
- branch heads and merged branch graph
- diff contents, not just commit titles
- the Discord export timeline from the event day

## Source anchors used for this timeline

### Git timeline anchor

The relevant development window is concentrated on **May 23, 2026** from:

- `11:17:19 AM` local: `f5c4e7d` Initial commit
- through `5:57:38 PM` local: `9484893` final major code hardening commit

Later commits on the evening of May 23 and the morning of May 24 are mainly:

- merges
- preservation
- documentation

### Discord anchor

The Discord export provides event-side timing for idea changes and handoffs:

- `10:26 AM` track/idea discussion
- `10:34–10:36 AM` “canvas idea” rejection and hardware debate
- `10:37 AM` “recognize falls and remind you stuff”
- `11:34 AM` FamiliarAI link shared
- `1:20 PM` and `1:48 PM` public preview links shared
- `3:48 PM` OpenPose link shared
- `4:21 PM` med schedule shared
- `4:37 PM` technical summary shared
- `5:08 PM` `guardiancare.zip` shared

Those timestamps matter because they let us align:

- idea changes
- proof-of-concept changes
- public preview work
- late fall-detection handoff work

## 1. Branch map before reading the timeline

To understand the chronology, the branch meanings have to be clear first.

### `main`

`main` starts as the product shell and later becomes the merge/preservation
branch. It is not the branch where all the experimentation happened in real
time.

### `raw-limelight-feed`

This branch is the **Pi preview / public stream** branch.

Key technical themes:

- Limelight stream access
- browser preview bridge
- localtunnel/ngrok service support
- early sender/receiver split

### `windows-face-supabase-match`

This branch is the **Windows fallback / identity / Supabase** branch.

Key technical themes:

- webcam-based recognition
- Supabase integration
- live local dashboard
- browser preview
- face update and gallery correctness

### `pi-limelight-orchestrator`

Despite the name, this branch ends up containing the **latest face-sync and
dashboard hardening work** by the time it is merged.

Key technical themes:

- final Supabase update fixes
- dashboard entirely backed by Supabase
- image-row id semantics

### `openpose-pose-integration`

This is an **exploration branch** with evidence of live experimentation rather
than a fully landed committed implementation.

Evidence:

- branch pointer at `63b6a42`
- stash entry at `2:52:27 PM`

## 2. Chronological technical timeline

## 11:17:19 AM — `f5c4e7d` — `main`

**Commit:** `f5c4e7d`  
**Message:** `Initial commit`

### What existed technically

- almost nothing yet beyond the repository skeleton

### What this means

At this time, there is no meaningful split between:

- caregiver app
- perception stack
- face recognition
- fall detection
- cloud/backend wiring

This is the zero point of the technical timeline.

## 12:45:14 PM — `3a3f618` — `main`

**Commit:** `3a3f618`  
**Message:** `Add Raspberry Pi Limelight viewer scaffold`

### Files added

- `pi/limelight_probe.py`
- `pi/limelight_video_viewer.py`
- `requirements.txt`
- `prompts/gemini_system_prompt.txt`
- `README.md`
- `codex.md`

### Technical meaning

This is the first serious implementation commit.

The code focus is:

- can the Pi find the Limelight
- can it probe endpoints
- can it open the stream directly

### What the diff suggests about priorities

The project at this moment is still assuming:

- hardware proof first
- browser/UI later
- identity/backend later

The presence of the early Gemini prompt file shows that AI-conversation context
was already part of the product story, but not yet the engineering bottleneck.

### What is still absent

- no web preview
- no public shareability
- no Supabase face path
- no fall-detection runtime

## 12:45:28 PM — `a4c9fa3` — `main`

**Commit:** `a4c9fa3`  
**Message:** `Ignore Python cache files`

### Technical meaning

This is a repo hygiene correction immediately after the Pi scaffold landed.

### What it reveals

The first Pi work was moving fast enough that compiled cache artifacts were
committed before cleanup. This is minor technically, but it confirms the early
phase was fast, direct, and local-script driven.

## 1:07:07 PM — `a220cf9` — `main`

**Commit:** `a220cf9`  
**Message:** `Add public Limelight web preview bridge`

### Files added or materially changed

- `pi/limelight_web_preview.py`
- `pi/limelight_video_viewer.py`
- `README.md`

### Technical meaning

This is the first pivot from:

- “open the stream locally”

to:

- “serve the stream to a browser”

The preview bridge makes the feed accessible through:

- a root page
- a proxied MJPEG endpoint
- health-style endpoints

### Why this matters

This commit is where the project stops being only a dev-side camera tool and
starts becoming a demo surface.

### What is still missing

- no persistent public route
- no cloud host path
- no identity layer

## 1:11:45 PM — `63b6a42` — `main`, later branch base for `raw-limelight-feed` and `openpose-pose-integration`

**Commit:** `63b6a42`  
**Message:** `Prepare Limelight preview for Cloud Run`

### Files added or changed

- `Dockerfile`
- `.dockerignore`
- `pi/limelight_web_preview.py`
- `pi/limelight_video_viewer.py`

### Technical meaning

This commit tries to convert the local preview path into something cloud-hostable.

The preview app is made more compatible with:

- `$PORT`
- container execution
- deployment assumptions

### What this implies technically

By `1:11 PM`, the team is already confronting the question:

> how do we let other people see the video

This is a system-architecture question, not a perception question.

### Why this branch point matters

This commit becomes the base for:

- `raw-limelight-feed`
- `openpose-pose-integration`

So the later history is effectively diverging here:

- one path pushes harder on preview/accessibility
- one path later experiments with OpenPose

## 1:20 PM — Discord preview checkpoint

**Discord:** `https://calm-crabs-relate.loca.lt/stream.mjpg`

### Technical meaning

This is the first clear evidence that the preview/public-sharing work is not
just theoretical. A shareable tunnel-backed stream URL existed and was being
sent around.

This closely matches the preview/tunnel work that continues in the next commit.

## 1:27:25 PM — `c9e0f2f` — `main`

**Commit:** `c9e0f2f`  
**Message:** `Add managed services for Limelight preview tunnel`

### Files added

- `deploy/systemd/aegis-preview.service`
- `deploy/systemd/aegis-localtunnel.service`
- `scripts/install_user_services.sh`
- `scripts/localtunnel-watch.sh`

### Technical meaning

This is an operationalization commit, not a model or product commit.

It means the team already encountered a practical problem:

- a preview server that works once is not enough
- a tunnel that dies is not demoable

### What the code is doing

It creates:

- keepalive service logic
- auto-start behavior
- tunnel watcher mechanics

### What was still not solved

- upstream camera reachability from true cloud services
- recognition
- state/backend logic

## 1:48 PM and 1:56 PM — Discord preview checkpoint

**Discord:**

- `https://puny-houses-rest.loca.lt/`
- link repeated a few minutes later

### Technical meaning

By now, the stream/public link issue has become a recurring live concern. The
same preview URL being re-shared suggests the team was actively validating the
shareable path in real time.

## 2:50:58 PM — `7aeebc1` — `origin/raw-limelight-feed`

**Commit:** `7aeebc1`  
**Message:** `Add webcam face sender and ngrok service`

### Files added or changed

- `pi/face_capture_sender.py`
- `windows/face_receiver.py`
- `deploy/systemd/aegis-ngrok.service`
- `scripts/ngrok-watch.sh`
- `pi/limelight_web_preview.py`
- `requirements-face.txt`
- `requirements-windows.txt`

### Technical meaning

This is the first major architectural split.

The project is no longer just:

- Pi shows stream

It is becoming:

- Pi captures or forwards face data
- another machine can receive/process/store it

### Why this matters

This is the point where a distributed architecture starts to form:

- edge device
- receiver machine
- backend identity/store layer still to come

### Branch-specific importance

This is the last committed point on `origin/raw-limelight-feed`, which means the
raw branch stabilizes as:

- preview
- tunnel
- sender/receiver bridge

but does not continue into the full Supabase-heavy hardening path.

## 2:52:27 PM — `openpose-pose-integration` stash evidence

**Stash evidence:**

- `stash@{0}: On openpose-pose-integration: wip openpose overlay`

### Technical meaning

This is not a landed commit, but it matters a lot.

It means that by `2:52 PM`:

- OpenPose was not just an idea
- there was active, uncommitted exploratory work for overlay/integration

### Why this matters for the timeline

It shows a branch of work that never fully reached committed branch-head status
but was still part of the real engineering effort.

## 3:46:09 PM — `04927dd` — `windows-face-supabase-match`

**Commit:** `04927dd`  
**Message:** `Add Windows face matching and LumiAI launcher`

### Files added

- `windows/face_matching.py`
- `windows/face_receiver.py`
- `windows/webcam_supabase_live.py`
- `windows/webcam_supabase_match.py`
- `windows/supabase_known_faces.py`
- `windows/lumiai.ps1`
- `scripts/install_lumiai_command.ps1`
- Windows requirements files

### Technical meaning

This is the biggest architectural pivot of the day.

At this point, the project gains a true Windows-only fallback that can do:

- camera capture
- face embedding generation
- preview
- matching
- backend sync
- operator launch ergonomics

### Why this happened

The diff size and scope strongly suggest a change in risk posture:

- the Pi path was no longer trusted as the only demo center
- Windows became the environment where faster iteration was possible

### Branch-specific importance

From this point onward, `windows-face-supabase-match` becomes the most rapidly
iterated branch in the repo.

## 3:48 PM — Discord OpenPose checkpoint

**Discord:** OpenPose GitHub link shared

### Technical meaning

This proves that even after the Windows fallback architecture existed, the team
was still actively looking for stronger pose/fall/perception routes.

That means the fallback pivot did not kill perception exploration. Both were
happening in parallel.

## 4:11:40 PM — `8e963d5` — `windows-face-supabase-match`

**Commit:** `8e963d5`  
**Message:** `fix(windows): resolve live view issues by adding missing dependencies and updating configuration`

### Files changed

- `windows/webcam_supabase_live.py`
- `windows/lumiai.ps1`
- `scripts/install_lumiai_command.ps1`

### What the diff actually changed

This is not a tiny fix. It is a substantial runtime redesign:

- local IPv4 discovery
- explicit JPEG byte generation helper
- file-serving route for saved images
- frame reuse between processing passes
- `--process-every-n`
- `--detect-scale`
- faster stream cadence
- LAN image base URL generation
- optional Gemini description + speaker prompt support

### Technical meaning

The first version of the live view existed, but it was not good enough.

This commit says the earlier Windows live stack suffered from:

- lag
- over-processing
- weak image accessibility from other laptops
- too much coupling between recognition and preview freshness

### Why this matters in the timeline

This is the moment the Windows path stops being merely “possible” and starts
becoming “tuned for demo use.”

## 4:12:05 PM — `cf5dd81` — `windows-face-supabase-match`

**Commit:** `cf5dd81`  
**Message:** `fix(windows): set default unknown person name to 'unidentified'`

### Technical meaning

This is a semantic cleanup immediately after the larger runtime fix.

It tells us that identity naming conventions were still unstable right after the
fallback path was created.

## 4:18:38 PM — `3c07a54` — `windows-face-supabase-match`

**Commit:** `3c07a54`  
**Message:** `Add Supabase test face insert script`

### Technical meaning

This commit exists because backend uncertainty had become a real blocker.

The team needed a direct proof path for:

- key validity
- row shape validity
- insertion success/failure

### What this implies

By this time, “is the app wrong” and “is Supabase rejecting the payload” had
become separate questions that needed separate tooling.

## 4:21 PM — Discord medication checkpoint

**Discord:** med schedule shared

### Technical meaning

Even while face/sync/preview debugging was happening, the product was still
receiving actual care-domain input. The product scope had not collapsed down to
“just camera.” The room assistant narrative was still active.

## 4:22:17 PM — `c3d7038` — `main`

**Commit:** `c3d7038`  
**Message:** `Add SwiftUI iOS app and bootstrap Next.js onboarding web app`

### Technical meaning

This commit lands on `main` while the Windows fallback branch is already active.

That is important.

It means the codebase was truly developing in parallel:

- one line was hardening runtime/video/recognition
- another line was building the caregiver-facing shell

### Technical implication

This is not a neat product progression. It is a real hackathon progression:

- user-facing app scaffolds and core perception plumbing are being built in
  parallel because both are needed for a convincing demo.

## 4:24–4:26 PM — Discord pitch checkpoint

**Discord:** “Master hackathon pitch deck creator” prompt appears

### Technical meaning

By this point, the team was already compressing the architecture into pitch
language while the code was still being changed quickly.

This matters because later code changes have to be read in the context of:

- not just correctness
- but what could be said confidently in front of judges

## 4:31:29 PM — `b4cff0d` — `windows-face-supabase-match`

**Commit:** `b4cff0d`  
**Message:** `Add base64 face upload flow and harden secret hygiene`

### Files added or changed

- `windows/face_receiver.py`
- `windows/send_first_face_base64.py`
- `.gitignore`

### Technical meaning

This is a transport-layer pivot.

The system is shifting from:

- file-path-oriented / multipart assumptions

toward:

- JSON + base64 image payloads

### Why this matters

This is one of the first big clues that image transport itself had become a
technical problem worth redesigning.

### Problem class revealed

- local file URIs are easy to create
- but they are bad universal transport
- base64 is ugly but robust for quick backend/database moves

## 4:37:53 PM — Discord technical summary checkpoint

**Discord:** detailed technical summary shared

### Technical meaning

This is one of the most valuable timeline anchors because it captures a live
technical self-assessment at the time.

It says the stack was:

- Raspberry Pi + Windows webcam
- `face_recognition`
- Supabase `known_faces`
- MJPEG over Flask
- unknown auto-insert
- Gemini-assisted naming prompts

It also points out a real limitation at that exact time:

> matched users were not yet getting their most recent image updated correctly

This matters because the subsequent commits directly attack that limitation.

## 4:47:51 PM — `eb9bc05` — `windows-face-supabase-match`

**Commit:** `eb9bc05`  
**Message:** `Add live local face receiver view`

### Technical meaning

This improves operability and observability:

- startup script
- richer face receiver page
- local service ergonomics

### Why it matters

By late afternoon, the issue is not just whether the receiver works. It is
whether the team can inspect and restart it quickly enough during repeated demo
loops.

## 5:01:02 PM — `2337100` — `windows-face-supabase-match`

**Commit:** `2337100`  
**Message:** `feat(windows): improve face matching and preview with browser-side camera and embedding normalization`

### What the diff actually changed

- browser camera preview path
- `/known-faces` JSON route
- embedding normalization in `supabase_known_faces.py`
- better image source inference for rendered faces

### Technical meaning

This solves two quiet but serious bugs:

1. embeddings coming back from Supabase could be shaped inconsistently
2. server-side camera preview was not the best local UX for a laptop

### Why it matters

This is a compatibility and latency commit:

- compatibility for Supabase embedding payload shapes
- latency/UX improvement by shifting preview to browser media APIs

## 5:08:04 PM — `dd5a198` — `windows-face-supabase-match`

**Commit:** `dd5a198`  
**Message:** `Add vendored base64 CLI and Python helper`

### Technical meaning

By this point, base64 handling was important enough to standardize and vendor.

That means the team no longer treated base64 as a temporary hack. It became a
core transport/storage tool in the current architecture.

## 5:08 PM — Discord late artifact checkpoint

**Discord:** `guardiancare.zip` shared

### Technical meaning

This is the late fall-detection handoff point.

It means that while the Windows/Supabase path was still actively being hardened,
another perception/fall bundle was being delivered into the team workflow.

That is one of the strongest pieces of evidence that the project had parallel
technical centers right up to the end.

## 5:09:32 PM and 5:12:29 PM — `ffa3713`, `f06b742` — `main`

**Commits:**

- `ffa3713` `Revise README for Lumi AI project`
- `f06b742` `Revise README for improved clarity and organization`

### Technical meaning

Documentation/pitch polish starts while deep engineering is still in flight.

This matters because the repository was already serving two audiences:

- the team trying to make it work
- the judges/audience who would need to understand it quickly

## 5:14:34 PM — `78f28eb` — `windows-face-supabase-match`

**Commit:** `78f28eb`  
**Message:** `Use progers/base64 for image encoding; add Supabase image base64 insert/update; name new faces 'unidentified'`

### What the diff actually changed

- `insert_image_base64`
- `find_image_by_url`
- `update_image_by_id`
- `update_known_face_photo`
- raw-byte base64 helpers

### Technical meaning

This is the first mature attempt to make image handling in Supabase coherent.

### Problem being attacked

- images for new faces and matched faces needed a backend update path
- raw file URIs were not enough

### What was still imperfect

Photo semantics were still not fully clean. The repo was still using fields in
ways that later commits would refine.

## 5:21:31 PM — `349ce49` — `windows-face-supabase-match`

**Commit:** `349ce49`  
**Message:** `feat(windows): sync faces to Supabase with raw base64 and update existing matches`

### Technical meaning

This is the first explicit push to treat matched faces as update events, not
just unknowns as insert events.

### Why this matters

It aligns directly with the 4:37 PM Discord observation that matched faces were
still weak on update semantics.

### Technical reading

This commit is important not because it fully solved the issue, but because it
shows the team had correctly identified the gap and was coding toward it.

## 5:24:29 PM — `39f6c42` — `main`

**Commit:** `39f6c42`  
**Message:** `Fall detection`

### Technical meaning

This brings in the earlier GuardianCare line and massively expands `main` with:

- fall-detection code
- face-recognition code
- iOS and web shells
- Supabase client code

### Why it matters in the timeline

This is not late cleanup. This is an active branch of product history entering
the main line while the Windows branch is still evolving.

### Interpretation

The repo is now definitely preserving multiple valid paths to the same product:

- Pi/Limelight path
- Windows/Supabase path
- GuardianCare integrated prototype path

## 5:33:07 PM — `ae0cf6c` — `windows-face-supabase-match`

**Commit:** `ae0cf6c`  
**Message:** `feat: upload download.jpg and ensure unknown faces are registered as unidentified in Supabase`

### Technical meaning

This is a verification/proving commit.

It uses concrete artifacts and scripts to prove that:

- image upload path behaves
- unknown registration behavior is correct

This is a strong sign that the team was using targeted probe scripts to debug
the backend rather than relying only on the live app.

## 5:36:10 PM — `0238dc7` — `windows-face-supabase-match`

**Commit:** `0238dc7`  
**Message:** `feat(dashboard): add real-time event log and telemetry status`

### Technical meaning

The project adds observability infrastructure:

- real-time event log
- telemetry status

### Why it matters

At this stage, the team no longer just needs the app to “run.” They need to see
which internal stage is failing.

This commit marks the transition from:

- app as demo artifact

to:

- app as self-diagnosing debug surface

## 5:39:39 PM — `436ab6b` — `windows-face-supabase-match`

**Commit:** `436ab6b`  
**Message:** `feat(windows): enhance logging for encoding/uploads and tune sensitivity to prevent duplicates`

### What the diff actually changed

- server event buffer
- explicit upload/detection event messages
- threshold lowered to `0.55`
- recent distance lowered to `0.20`
- recent time window expanded to `90s`

### Technical meaning

This is a parameter-tuning and observability commit aimed at duplicate
suppression.

### What it implies

By this point, duplicate creation or over-frequent face reprocessing had become
a live issue.

## 5:42:43 PM — `9ced36a` — `windows-face-supabase-match`

**Commit:** `9ced36a`  
**Message:** `fix(windows): ensure face uploads occur by decoupling encoding from initial embedding check and reducing cooldown`

### What the diff actually fixed

- moved embedding gating deeper into the unknown-face branch
- reduced `save-cooldown` from `10.0` to `5.0`

### Technical meaning

This is one of the clearest logic-bug commits in the entire repo.

The bug was:

- detection could happen
- but upload could still be skipped because the control flow exited too early

This is not a configuration problem. It is a real pipeline logic flaw being
repaired.

## 5:44:40 PM — `ad6a6f9` — `windows-face-supabase-match`

**Commit:** `ad6a6f9`  
**Message:** `debug: add verbose logging and continue investigating supabase sync issues`

### Technical meaning

The previous fix was not enough. Sync issues still existed.

This commit is significant because it confirms:

- the team was still in active diagnosis mode after `9ced36a`
- Supabase sync was not yet stable

## 5:46:13 PM — `d6dd6f3` — `windows-face-supabase-match`

**Commit:** `d6dd6f3`  
**Message:** `fix(windows): ensure face data is sent to Supabase on matches and rename old entries to unidentified`

### What the diff actually changed

- explicit event when a match is found
- explicit matched-face update path
- fallback image insertion when old reference missing
- known-face photo update after new image record

### Technical meaning

This directly attacks the limitation identified in the Discord summary:

- unknown creation existed
- matched-face image/state updating was weaker

This is the first truly explicit fix for that matched-face update gap.

## 5:48:22 PM — `e233891` — `windows-face-supabase-match`

**Commit:** `e233891`  
**Message:** `stable: working face sync to supabase with unidentified naming and base64 storage`

### Technical meaning

This is the branch’s first explicit claim of stability.

Given the prior commits, that claim rests on:

- base64 transport
- direct test scripts
- telemetry
- duplicate suppression tuning
- upload control-flow repair
- matched-face update fixes

### Interpretation

This is the first point in the day where the Windows/Supabase path can be read
as technically converged enough to trust for demo use.

## 5:49:29 PM — `78f7a8a` — `origin/windows-face-supabase-match`

**Commit:** `78f7a8a`  
**Message:** `feat(dashboard): add recognized faces gallery with base64 decoding`

### Technical meaning

Once the sync path mostly worked, attention moved to rendering truthfully from
backend data.

This commit improves:

- recognized-face gallery
- base64 decoding for display

### Technical implication

The branch is now solving presentation fidelity on top of sync correctness.

## 5:57:38 PM — `9484893` — `origin/pi-limelight-orchestrator`

**Commit:** `9484893`  
**Message:** `Fix face upload errors and wire dashboard entirely to Supabase`

### What the diff actually changed

- added `find_image_by_id` to `windows/supabase_known_faces.py`
- changed gallery logic in `windows/webcam_supabase_live.py`
- stopped treating `photo_url` only as a direct URL lookup assumption
- allowed the dashboard to fetch actual image row content by id

### Technical meaning

This is the final major code hardening commit of the day.

It fixes a semantic mismatch:

- image identity
- image storage
- and dashboard rendering

had drifted apart

### Why this is a big deal

This commit is the best evidence that the team moved from:

- “we can create faces and images”

to:

- “the dashboard is actually reading the backend truth in a more coherent way”

### Branch naming note

The fact that this lands on `pi-limelight-orchestrator` even though it is
primarily Windows/Supabase dashboard hardening is itself telling:

- branch names no longer match subsystem ownership cleanly
- the engineering work had outrun the branch taxonomy

## 3. Evening merge and preservation timeline

## 9:44 PM — merge sequence begins

### `5662334` — `main`

- merge `pi-limelight-orchestrator` into `main`

### `aac1438` — `main`

- merge `raw-limelight-feed` into `main`

### Technical meaning

The hackathon code is no longer being treated as disposable side branches.
Preservation becomes an explicit technical act.

## 9:51 PM onward — documentation and artifact preservation

### `5034da5`

- README rewritten as hackathon narrative

### `11a2789`

- unpacked `guardiancare.zip` into `guardiancare_late/`

### `960f8ca`

- README rewritten using Discord timeline + commit history

### `5adf24e`

- README gains commit-level engineering timeline

### `3cd3788`

- README gains cross-branch analysis

### `f0446c7`

- added general technical retrospective

### Technical meaning

By this point the engineering day is over. The task is now:

- preserve branch meaning
- preserve late artifacts
- preserve technical lessons

## 4. Branch-level diff synthesis

This section summarizes what each branch contributed as a whole, based on its
effective diff against the common Pi-preview base at `63b6a42`.

## `origin/raw-limelight-feed` relative to `63b6a42`

Approximate contribution:

- ~625 insertions over the base
- preview/tunnel/service/sender additions

Key additions:

- preview and tunnel services
- `pi/face_capture_sender.py`
- ngrok support
- initial Windows receiver presence

Technical role:

- convert Pi stream proof into a remotely shareable/dev-operable subsystem

## `windows-face-supabase-match` relative to `63b6a42`

Approximate contribution:

- ~3025 insertions over the base

Key additions:

- full Windows recognition pipeline
- Supabase cache/matching code
- live preview/dashboard
- launcher/install scripts
- test utilities

Technical role:

- become the primary fallback architecture
- own the identity/state/demo-survival problem

## `origin/pi-limelight-orchestrator` relative to `63b6a42`

Approximate contribution:

- ~3638 insertions over the base

Key additions beyond the Windows branch:

- richer image/sync helpers
- dashboard entirely backed by Supabase
- more upload and gallery correctness
- test/sample upload scripts

Technical role:

- carry the latest hardening of the recognition + Supabase + dashboard line

## `openpose-pose-integration`

Committed branch state:

- still points at `63b6a42`

Live evidence:

- stash for `wip openpose overlay`

Technical role:

- active exploration for stronger pose/perception integration
- not a finalized landed runtime path

## 5. Final technical reading of the day

If the repo is read purely through timestamps and diffs, the day looks like
this:

### Morning

- idea narrowing
- hardware vs non-hardware debate
- product sentence forms around falls + reminders

### Early afternoon

- Pi stream proof
- browser preview bridge
- first public/tunnel attempts

### Mid afternoon

- sender/receiver split
- Windows fallback becomes real
- OpenPose exploration exists in parallel

### Late afternoon

- base64 transport pivot
- Supabase test tooling
- telemetry and debug surfaces
- duplicate suppression tuning
- matched-face update bug fixing
- gallery/dashboard semantics cleanup

### End of day

- late fall-detection artifact arrives
- branches merged
- technical story preserved in docs

## 6. Most important timeline-level conclusion

The codebase did not evolve in a straight line from idea to product.

It evolved in three overlapping loops:

1. **perception loop**
   - Pi, Limelight, OpenPose, fall detection
2. **demo survivability loop**
   - browser preview, tunnels, Windows fallback, launcher
3. **backend truth loop**
   - Supabase inserts, updates, image transport, dashboard correctness

The Windows branch converged fastest on demo survivability and backend truth.
The Pi and fall-detection lines stayed technically important, but they were
never the only live center of the project after mid-afternoon.

That is the most accurate technical reading of the repository when you respect:

- the branch graph
- the diffs
- and the timestamps together.
