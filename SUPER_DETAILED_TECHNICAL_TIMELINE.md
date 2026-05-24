# Lumi AI Super Detailed Technical Timeline

This file is a chronological technical timeline by event and timestamp.

It is not a general retrospective and it is not organized by topic first. The
goal here is to reconstruct the day in order:

- what happened
- when it happened
- what branch or source it came from
- what changed in code at that moment
- what that change meant technically
- what problem was still unresolved after that event

This timeline is built from:

- exact git commit timestamps
- branch heads and merged history
- diff contents
- Discord timestamps from the downloaded export

## Branch key used in this timeline

- `main`: product shell, fall-detection import, later merge/preservation branch
- `raw-limelight-feed`: Pi stream / preview / tunnel branch
- `windows-face-supabase-match`: Windows webcam + Supabase branch
- `pi-limelight-orchestrator`: later branch carrying final dashboard/sync hardening
- `openpose-pose-integration`: exploration branch with stash evidence

---

## Saturday, May 23, 2026

### 10:26 AM — Discord — Track and idea positioning starts

**Source:** Discord export  
**Messages around this time:**

- `about these tracks`
- `and any ideas they might have`

### What this means technically

At this point there is no meaningful code yet, but the team is already thinking
about how the project will need to fit the hackathon judging environment.

This matters because the later repo shape only makes sense if you realize the
team was optimizing for:

- demo impact
- technical differentiation
- not just correctness

### What is not decided yet

- whether the project will be hardware-heavy or software-only
- what exact perception backbone will be used
- how much of the product will be room sensing vs caregiver UI

---

### 10:34 AM — Discord — The earlier non-hardware direction gets rejected

**Source:** Discord export  
**Messages around this time:**

- `can we not do the canvas idea?`
- `Clunky school interface`
- `no hardware component`

### What this means technically

This is the first strong architecture-shaping decision of the day even though no
commit exists yet.

The team is explicitly moving away from a purely interface-centric idea and
toward something that includes real sensing or hardware interaction.

### Why this matters later

The repo’s eventual complexity comes directly from this choice. A non-hardware
idea would not have forced:

- camera IO
- Limelight integration
- tunnel/public preview issues
- Pi vs Windows fallback tradeoffs

---

### 10:35–10:36 AM — Discord — Hardware becomes a differentiation strategy

**Source:** Discord export  
**Messages around this time:**

- `there's barely anyone with hardware`
- `And is hardware a requirement`
- `no`
- `but its how we win`

### What this means technically

The team is explicitly deciding that hardware is not mandatory but could be a
competitive advantage.

### Technical implication

This is a crucial constraint for the rest of the day:

- the team wants hardware for differentiation
- but because it is optional, they also need a fallback if the hardware path
  becomes too fragile

That exact tension is what later creates the Pi branch and the Windows fallback
branch in parallel.

---

### 10:37 AM — Discord — The core product behavior gets stated clearly

**Source:** Discord export  
**Messages around this time:**

- `R we going with ur earlier idea?`
- `So it will recognize falls and remind you stuff`

### What this means technically

This is the first compact functional definition of Lumi AI.

From a systems perspective, that sentence already implies at least three
subsystems:

1. fall/perception logic
2. identity or resident-state awareness
3. reminder or interaction logic

### Why this matters

The final repo looks broad because the product was broad from this exact moment,
not because the team lost focus later.

---

### 10:43 AM — Discord — Care experience expands beyond pure detection

**Source:** Discord export  
**Messages around this time:**

- discussion about adding music/games/entertainment

### What this means technically

The product scope is not just:

- detect emergency

It also includes:

- daily-use comfort interactions
- companionship-style assistance

This explains why later files include:

- caregiver app scaffolds
- Gemini prompts
- med/reminder language

instead of only emergency detection scripts.

---

### 11:17:19 AM — Git — `f5c4e7d` — Initial commit lands on `main`

**Commit:** `f5c4e7d`  
**Branch context:** `main`  
**Message:** `Initial commit`

### Technical event

The repository is created in usable form.

### What exists technically right after this

- almost no product logic
- no defined hardware subsystem
- no defined preview subsystem
- no defined backend/identity subsystem

### Technical significance

This is the zero point for the code timeline. Everything else in the repo is
same-day acceleration layered on top of this.

---

### 11:34 AM — Discord — FamiliarAI reference enters the conversation

**Source:** Discord export  
**Message:** FamiliarAI link shared

### What this means technically

By `11:34 AM`, the team is already referencing an existing face-recognition
style implementation as inspiration or comparison.

### Why this matters

This reference shows that recognition was not being invented from scratch in a
vacuum. The team was actively comparing against an existing architecture for:

- face detection
- face matching
- “known vs unknown” logic

This becomes important later when the Windows/Supabase path is built.

---

### 12:45:14 PM — Git — `3a3f618` — The first real Pi/Limelight scaffold lands

**Commit:** `3a3f618`  
**Branch context:** `main`  
**Message:** `Add Raspberry Pi Limelight viewer scaffold`

### Files introduced

- `pi/limelight_probe.py`
- `pi/limelight_video_viewer.py`
- `requirements.txt`
- `prompts/gemini_system_prompt.txt`
- `README.md`
- `codex.md`

### Technical event

This is the first moment the project becomes a real hardware/software build and
not just a concept.

### What the code is doing

- probing Limelight endpoints
- trying stream paths
- opening raw stream data in OpenCV

### Technical reading

The Pi path is still very direct and local:

- no browser serving yet
- no public preview yet
- no backend state
- no face/identity persistence

This is a hardware access proof phase.

### What is still missing after this event

- shareable preview
- public reachability
- Windows fallback
- Supabase identity
- integrated fall detection

---

### 12:45:28 PM — Git — `a4c9fa3` — Repo hygiene correction after the first scaffold

**Commit:** `a4c9fa3`  
**Branch context:** `main`  
**Message:** `Ignore Python cache files`

### Technical event

A compiled Python cache artifact is removed/ignored.

### Technical meaning

This is small, but it shows the pace of the first implementation pass:

- code was being run immediately
- generated artifacts were entering the repo
- cleanup followed right after

It is a typical same-day hackathon signal: the first objective was to make
things run, then clean up after.

---

### 1:07:07 PM — Git — `a220cf9` — Stream access becomes browser preview

**Commit:** `a220cf9`  
**Branch context:** `main`  
**Message:** `Add public Limelight web preview bridge`

### Files introduced or changed

- `pi/limelight_web_preview.py`
- `pi/limelight_video_viewer.py`

### Technical event

The project moves from:

- raw local stream opening

to:

- local browser preview via an HTTP bridge

### What changed in code

- a preview server exists now
- MJPEG is proxied to a web route
- a root page and stream endpoint become part of the runtime surface

### Technical meaning

This is the first move from “developer proof” to “demo surface.”

### What is still missing after this event

- no durable public route
- no cloud-friendly upstream solution
- no face identity pipeline

---

### 1:11:45 PM — Git — `63b6a42` — Cloud Run preparation appears

**Commit:** `63b6a42`  
**Branch context:** `main`, later the base for `raw-limelight-feed` and `openpose-pose-integration`  
**Message:** `Prepare Limelight preview for Cloud Run`

### Files introduced

- `Dockerfile`
- `.dockerignore`

### Technical event

The preview path is reshaped into something that can theoretically be deployed.

### What changed technically

- preview app becomes more container-compatible
- runtime starts respecting deployment-style port behavior

### Technical meaning

By `1:11 PM`, the problem has already shifted from:

- “can the Pi read the stream”

to:

- “can this be hosted or made available somewhere useful”

### Why this timestamp matters

This commit becomes a branch base. That means the code state at `1:11 PM`
captures the point before the repo splits into:

- the raw preview/tunnel line
- the OpenPose exploration line
- the later Windows-heavy recognition line

---

### 1:20 PM — Discord — First public stream URL is shared

**Source:** Discord export  
**Message:** `https://calm-crabs-relate.loca.lt/stream.mjpg`

### Technical event

A shareable public stream URL exists and is being passed around live.

### Technical meaning

The tunnel/public-preview problem is no longer abstract. The team has an actual
end-to-end path:

- local camera source
- local preview server
- tunnel
- publicly reachable URL

### What is still unresolved

- whether the tunnel is stable
- whether the source stays reachable
- whether this can be productionized or only demoed

---

### 1:27:25 PM — Git — `c9e0f2f` — Preview and tunnel get operational support

**Commit:** `c9e0f2f`  
**Branch context:** `main`  
**Message:** `Add managed services for Limelight preview tunnel`

### Files introduced

- `deploy/systemd/aegis-preview.service`
- `deploy/systemd/aegis-localtunnel.service`
- `scripts/install_user_services.sh`
- `scripts/localtunnel-watch.sh`

### Technical event

The preview/tunnel path gets turned into a more self-maintaining subsystem.

### What changed technically

- user services can keep the preview path alive
- tunnel management becomes scripted

### Technical meaning

At this point, the preview system is already being treated like an operational
dependency, not just a helper script.

### What this says about the day

The team had learned very quickly that a working preview was not enough. It had
to survive repeated launches and demo pressure.

---

### 1:48 PM and 1:56 PM — Discord — More public preview links are shared

**Source:** Discord export  
**Messages:**

- `https://puny-houses-rest.loca.lt/`
- same preview link re-shared a few minutes later

### Technical event

Public preview sharing is still actively being tested and circulated.

### Technical meaning

This suggests:

- the preview path was considered central enough to keep checking
- URL reachability/stability was still a live concern

This phase is still about:

- video visibility

not yet:

- identity correctness

---

### 2:50:58 PM — Git — `7aeebc1` — The sender/receiver architecture appears on `raw-limelight-feed`

**Commit:** `7aeebc1`  
**Branch context:** `origin/raw-limelight-feed`  
**Message:** `Add webcam face sender and ngrok service`

### Files introduced or changed

- `pi/face_capture_sender.py`
- `windows/face_receiver.py`
- `deploy/systemd/aegis-ngrok.service`
- `scripts/ngrok-watch.sh`
- `pi/limelight_web_preview.py`

### Technical event

The project no longer treats the Pi as only a preview device.

A new architectural split appears:

- Pi can capture or forward face-related data
- Windows can receive/process it

### Technical meaning

This is the first true distributed architecture moment in the repo.

### Why this matters

From here on, the project is not locked into “all intelligence runs on the Pi.”

### What remains unsolved after this event

- Supabase identity path is not yet mature
- live dashboard is not yet hardened
- duplicate/update semantics are still absent

---

### 2:52:27 PM — Git stash — `openpose-pose-integration` active experimentation

**Source:** git stash / branch evidence  
**Evidence:** `stash@{0}: On openpose-pose-integration: wip openpose overlay`

### Technical event

OpenPose work was happening live enough to produce a stash, even though it did
not land as a normal branch head commit.

### Technical meaning

This proves a parallel exploration was happening:

- preview/public path work was underway
- sender/receiver architecture had appeared
- and a stronger pose/perception route was still being explored

### Why this matters

The later fall-detection and pose work was not an afterthought. It was a real
same-day parallel effort.

---

### 3:46:09 PM — Git — `04927dd` — The Windows fallback becomes a real full-stack runtime

**Commit:** `04927dd`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Add Windows face matching and LumiAI launcher`

### Files introduced

- `windows/face_matching.py`
- `windows/supabase_known_faces.py`
- `windows/webcam_supabase_live.py`
- `windows/webcam_supabase_match.py`
- `windows/lumiai.ps1`
- `scripts/install_lumiai_command.ps1`

### Technical event

This is the biggest architecture pivot in the repo.

The project now has a real Windows-only fallback that can potentially handle:

- webcam capture
- face detection/embedding
- Supabase matching
- local browser preview
- launch ergonomics

### Technical meaning

At this exact time, the repo stops being primarily “Pi preview plus ideas” and
becomes “two competing runtime centers”:

- Pi/Limelight path
- Windows webcam path

### What remains unresolved after this event

- live view stability
- unknown naming conventions
- image transport semantics
- matched-face update path

---

### 3:48 PM — Discord — OpenPose shared explicitly

**Source:** Discord export  
**Message:** OpenPose GitHub link

### Technical event

The team explicitly shares OpenPose after the Windows fallback already exists.

### Technical meaning

This confirms that the project did not pivot away from perception exploration
when the Windows path appeared. Both were happening in parallel:

- fallback runtime hardening
- pose/fall/perception exploration

---

### 4:11:40 PM — Git — `8e963d5` — The Windows live runtime gets re-architected for usability

**Commit:** `8e963d5`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `fix(windows): resolve live view issues by adding missing dependencies and updating configuration`

### Technical event

The first Windows live runtime proved too weak or awkward in practice, so it
gets a substantial redesign.

### What the diff actually changes

- local IPv4 discovery
- JPEG helper functions
- `/images/<filename>` serving
- frame reuse across processing cycles
- stream cadence increased
- detection cadence separated with `--process-every-n`
- detection cost reduced with `--detect-scale`
- Gemini description + speaker prompt hooks

### Technical meaning

This is not a cosmetic fix. It is the moment the Windows runtime starts being
tuned for:

- lower latency
- better operator ergonomics
- easier LAN access from other devices

### What this reveals

The first Windows runtime existed, but it was not yet fit for repeated demo use.

---

### 4:12:05 PM — Git — `cf5dd81` — Unknown naming gets standardized

**Commit:** `cf5dd81`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `fix(windows): set default unknown person name to 'unidentified'`

### Technical event

The project tightens its identity semantics immediately after the larger runtime
fix.

### Technical meaning

This is a sign that:

- the fallback architecture existed
- but the data semantics still needed cleanup

It is small in code but important in meaning.

---

### 4:18:38 PM — Git — `3c07a54` — Direct Supabase insert testing becomes necessary

**Commit:** `3c07a54`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Add Supabase test face insert script`

### Technical event

The team creates a direct probe for backend correctness.

### Technical meaning

The system now has enough moving parts that a live app failure could mean:

- bad app logic
- bad key
- wrong row shape
- wrong table assumptions
- RLS rejection

This script exists to isolate those.

---

### 4:21 PM — Discord — Real med schedule arrives

**Source:** Discord export  
**Messages:** Amlodipine, Lisinopril, Metformin, Simvastatin schedule

### Technical event

Care-domain data is being integrated while the engineering stack is still being
debugged.

### Technical meaning

The room-assistant product scope stays alive throughout the implementation
chaos. The project did not collapse into only camera work.

---

### 4:22:17 PM — Git — `c3d7038` — Caregiver iOS/web shell lands on `main`

**Commit:** `c3d7038`  
**Branch context:** `main`  
**Message:** `Add SwiftUI iOS app and bootstrap Next.js onboarding web app`

### Technical event

The caregiver-facing app layer is built in parallel with the perception and
fallback runtime work.

### Technical meaning

This shows the repo developing on two tracks at once:

- product-facing shell
- runtime/perception/identity plumbing

### Why this matters

The hackathon story is not “first backend then frontend” or “first hardware then
app.” It is parallel construction because both were needed for the final story.

---

### 4:24–4:26 PM — Discord — Pitch framing gets refined while engineering continues

**Source:** Discord export  
**Message:** “Master hackathon pitch deck creator” style request

### Technical event

The team starts compressing the architecture into technical pitch language while
runtime fixes are still landing.

### Technical meaning

This creates an important constraint:

- the code has to keep evolving
- but the team also has to know how to explain it coherently in real time

---

### 4:31:29 PM — Git — `b4cff0d` — Image transport pivots toward base64

**Commit:** `b4cff0d`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Add base64 face upload flow and harden secret hygiene`

### Files introduced or changed

- `windows/face_receiver.py`
- `windows/send_first_face_base64.py`

### Technical event

The project changes how images move through the system.

### Technical meaning

The transport problem is now explicit. The team is moving away from relying only
on:

- local file paths
- or multipart-only assumptions

and toward:

- JSON + base64 payloads

### Why this matters

This is the start of the backend image-semantics story that continues through
multiple later fixes.

---

### 4:37:53 PM — Discord — Live technical self-assessment captures a real limitation

**Source:** Discord export  
**Message:** detailed technical summary

### Technical event

The stack is summarized live as:

- edge CV
- Raspberry Pi + Windows webcam path
- `face_recognition`
- Supabase `known_faces`
- MJPEG preview over Flask
- unknown auto-insert
- Gemini naming support

### Crucial technical note in that message

The summary explicitly says matched known faces were not yet getting their latest
image updated correctly.

### Why this matters

This gives a real-time technical checkpoint that later commits can be judged
against. It confirms that by `4:37 PM`, the update semantics were still weaker
for matched faces than for unknown insertions.

---

### 4:47:51 PM — Git — `eb9bc05` — Receiver becomes a visible local surface

**Commit:** `eb9bc05`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Add live local face receiver view`

### Technical event

The receiver gains a better local view and startup support.

### Technical meaning

This is a toolability/observability step:

- easier to inspect locally
- easier to restart
- easier to use in repeated tests

The project is maturing operationally, not just functionally.

---

### 5:01:02 PM — Git — `2337100` — Supabase embedding compatibility and browser-camera UX improve

**Commit:** `2337100`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `feat(windows): improve face matching and preview with browser-side camera and embedding normalization`

### Technical event

The team fixes two quiet but important issues:

1. Supabase embedding values can arrive in inconsistent formats
2. local preview UX is better if the browser owns the camera feed

### What the diff actually changes

- `normalize_embedding` in `supabase_known_faces.py`
- browser-camera path in `face_receiver.py`
- `/known-faces` payload route
- more robust image source inference

### Technical meaning

This is both:

- a data compatibility fix
- and a latency/usability fix

### What remains unresolved

- image storage semantics
- matched-face update correctness
- duplicate suppression

---

### 5:08:04 PM — Git — `dd5a198` — Base64 handling gets standardized enough to vendor

**Commit:** `dd5a198`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Add vendored base64 CLI and Python helper`

### Technical event

Base64 is no longer treated like a temporary workaround. It becomes a first-class
tool in the repo.

### Technical meaning

This commit says:

- image transport/storage is central now
- encoding behavior needs to be consistent enough to vendor tooling for it

---

### 5:08 PM — Discord — `guardiancare.zip` is shared

**Source:** Discord export  
**Artifact:** `guardiancare.zip`

### Technical event

Late-stage fall-detection work is handed off as an archive.

### Technical meaning

At almost the exact same time as the base64/image/backend work is intensifying,
fall-detection work is still arriving.

This is one of the strongest pieces of evidence that the project had multiple
serious technical centers right up to the end.

---

### 5:09:32 PM and 5:12:29 PM — Git — Documentation is being revised while core engineering is still active

**Commits:**

- `ffa3713` `Revise README for Lumi AI project`
- `f06b742` `Revise README for improved clarity and organization`

### Technical meaning

The team is simultaneously:

- still hardening the system
- and already refining how it will be described

That is standard hackathon behavior, but it matters for reading the later
commits: technical stabilization and narrative stabilization were happening in
parallel.

---

### 5:14:34 PM — Git — `78f28eb` — Supabase image records get a more explicit update model

**Commit:** `78f28eb`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `Use progers/base64 for image encoding; add Supabase image base64 insert/update; name new faces 'unidentified'`

### Technical event

Image handling in Supabase gets promoted from ad hoc behavior to an explicit API
surface inside the code.

### What the diff adds

- `insert_image_base64`
- `find_image_by_url`
- `update_image_by_id`
- `update_known_face_photo`

### Technical meaning

This is the first mature attempt to make the backend image lifecycle coherent.

### What is still unresolved

The project is still not fully clean on what `photo_url` means everywhere. That
semantic cleanup comes later.

---

### 5:21:31 PM — Git — `349ce49` — Existing matches start getting treated as update targets

**Commit:** `349ce49`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `feat(windows): sync faces to Supabase with raw base64 and update existing matches`

### Technical event

The system begins explicitly trying to update matched users, not just create
unknowns.

### Technical meaning

This is the correct direction after the `4:37 PM` Discord self-assessment.

### Important nuance

This commit introduces the right intent, but the later fixes show the behavior
still was not fully correct yet.

---

### 5:24:29 PM — Git — `39f6c42` — GuardianCare fall-detection lineage enters `main`

**Commit:** `39f6c42`  
**Branch context:** `main`  
**Message:** `Fall detection`

### Technical event

The earlier GuardianCare code is imported into the repo.

### What arrives technically

- `guardiancare/fall_detection.py`
- `guardiancare/face_recognition_module.py`
- `guardiancare/main.py`
- iOS and web shells inside `guardiancare/`

### Technical meaning

This is not cleanup. This is another major product lineage entering the main
history during the active implementation window.

### What this shows

By `5:24 PM`, Lumi AI’s technical history is definitely not linear. It now
contains:

- Pi preview path
- Windows fallback path
- GuardianCare integrated prototype path

all on the same day.

---

### 5:33:07 PM — Git — `ae0cf6c` — Direct sample-image upload proving continues

**Commit:** `ae0cf6c`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `feat: upload download.jpg and ensure unknown faces are registered as unidentified in Supabase`

### Technical event

The team adds more concrete validation scripts around image upload behavior.

### Technical meaning

The project still does not fully trust the live loop alone. It needs controlled
probe artifacts and scripts to prove that backend writes behave as expected.

---

### 5:36:10 PM — Git — `0238dc7` — Real-time event log and telemetry appear

**Commit:** `0238dc7`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `feat(dashboard): add real-time event log and telemetry status`

### Technical event

The app gains internal event logging and telemetry.

### Technical meaning

At this stage, the problem is no longer “we need more features.” It is:

- where exactly is the pipeline failing

This commit makes the app explain itself.

---

### 5:39:39 PM — Git — `436ab6b` — Duplicate suppression and logging get tightened

**Commit:** `436ab6b`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `feat(windows): enhance logging for encoding/uploads and tune sensitivity to prevent duplicates`

### Technical event

The team tunes thresholds and expands event logging to reduce duplicate face
handling.

### What the diff changes

- threshold lowered to `0.55`
- recent-face distance lowered to `0.20`
- recent-face window expanded to `90` seconds
- upload/detection logging becomes more explicit

### Technical meaning

This is an application-behavior tuning event, not just a coding cleanup event.

It shows that duplicate creation or repeated processing had become a live pain
point.

---

### 5:42:43 PM — Git — `9ced36a` — A real control-flow bug in uploads gets fixed

**Commit:** `9ced36a`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `fix(windows): ensure face uploads occur by decoupling encoding from initial embedding check and reducing cooldown`

### Technical event

The team fixes a real logic flaw in the live upload pipeline.

### What the diff does

- moves embedding gating deeper into the unknown-face path
- reduces save cooldown from `10s` to `5s`

### Technical meaning

Before this commit, a face could be detected but still fail to upload because
the control flow exited too early.

This is one of the clearest bug-fix moments in the whole repo.

---

### 5:44:40 PM — Git — `ad6a6f9` — More logging means the previous fix was not the end

**Commit:** `ad6a6f9`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `debug: add verbose logging and continue investigating supabase sync issues`

### Technical event

Verbose debugging is added right after the upload control-flow fix.

### Technical meaning

This confirms:

- upload correctness was improving
- but backend sync was still not stable enough to trust

---

### 5:46:13 PM — Git — `d6dd6f3` — Matched-face updates get explicit backend logic

**Commit:** `d6dd6f3`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `fix(windows): ensure face data is sent to Supabase on matches and rename old entries to unidentified`

### Technical event

Matched faces finally get explicit update behavior.

### What the diff does

- logs match detection
- attempts image update for matched users
- falls back to new image record creation if needed
- updates face-photo linkage afterwards

### Technical meaning

This is the clearest direct response to the earlier Discord note that matched
faces were weaker than unknowns in backend update behavior.

---

### 5:48:22 PM — Git — `e233891` — Windows/Supabase sync reaches a “stable” milestone

**Commit:** `e233891`  
**Branch context:** `windows-face-supabase-match`  
**Message:** `stable: working face sync to supabase with unidentified naming and base64 storage`

### Technical event

The branch explicitly declares stability for the face sync path.

### Technical meaning

By this point, the branch had already accumulated:

- base64 transport
- direct backend tests
- telemetry
- duplicate suppression tuning
- upload logic fixes
- matched-face update logic

This is the first point where the Windows fallback can reasonably be treated as
a converged runtime path.

---

### 5:49:29 PM — Git — `78f7a8a` — Gallery rendering is improved on the remote branch head

**Commit:** `78f7a8a`  
**Branch context:** `origin/windows-face-supabase-match`  
**Message:** `feat(dashboard): add recognized faces gallery with base64 decoding`

### Technical event

The dashboard/gallery begins decoding backend-stored image data for display.

### Technical meaning

The project moves from:

- “state is being written”

to:

- “state is being rendered meaningfully”

---

### 5:57:38 PM — Git — `9484893` — Final major hardening: dashboard semantics become more backend-correct

**Commit:** `9484893`  
**Branch context:** `origin/pi-limelight-orchestrator`  
**Message:** `Fix face upload errors and wire dashboard entirely to Supabase`

### Technical event

The day’s last major code hardening commit lands.

### What the diff actually changes

- `find_image_by_id` is added
- gallery logic stops assuming `photo_url` is always directly usable as a URL
- dashboard fetches real image content from the `images` table by id

### Technical meaning

This is the semantic cleanup commit for the backend truth model.

It fixes a structural mismatch between:

- face rows
- image rows
- gallery rendering assumptions

### Why this is such an important endpoint

This is the clearest final sign that the project is trying to end the day with:

- a dashboard that reflects Supabase truth
- not just local memory and optimistic assumptions

---

## 9:44 PM — Git — Merge phase begins on `main`

**Commits:**

- `5662334` Merge `pi-limelight-orchestrator` into `main`
- `aac1438` Merge `raw-limelight-feed` into `main`

### Technical event

The project stops treating the branches as temporary experiments and starts
preserving them in one history.

### Technical meaning

This is not just a repo-management detail. It is a technical decision:

- keep the working Pi preview line
- keep the working Windows/Supabase line
- do not lose either just because the final demo centered more on one than the
  other

---

## 9:51 PM onward — Documentation and artifact preservation phase

### 9:51 PM — `5034da5`

- README rewritten as hackathon narrative

### 10:17 PM — `11a2789`

- unpacked `guardiancare.zip` into `guardiancare_late/`

### 10:28 PM — `960f8ca`

- README aligned to Discord timeline and commit history

### 10:31 PM — `5adf24e`

- README gains detailed commit-by-commit engineering section

### 8:36 AM next morning — `3cd3788`

- README gains cross-branch timeline analysis

### 8:47 AM next morning — `f0446c7`

- technical retrospective added

### 8:57 AM next morning — `d7d43e4`

- this super detailed timeline file added

### Technical meaning

The project’s last phase is preservation:

- preserve branch history
- preserve late artifacts
- preserve the real technical story

---

## Final reading of the timeline

If you read the repo strictly by timestamped events, the project evolves in this
order:

1. the team chooses a hardware-differentiated elder-care assistant idea
2. the Pi/Limelight path proves raw stream access
3. the team turns stream access into a browser preview problem
4. the team turns browser preview into a public reachability problem
5. the sender/receiver split appears
6. the Windows fallback becomes a real alternate runtime
7. image transport shifts toward base64 because backend truth matters
8. telemetry appears because silent failures matter
9. matched-face update correctness becomes a central bug class
10. dashboard semantics are cleaned up against real Supabase data
11. fall-detection work continues in parallel and gets preserved at the end
12. the branches are merged instead of being thrown away

That is the most accurate chronological technical reading of Lumi AI based on:

- the commit timestamps
- the diff contents
- the branch graph
- and the Discord event timings together.
