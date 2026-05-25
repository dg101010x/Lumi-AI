# Lumi AI

Lumi AI is our full hackathon build log for **Synthesis Hacks**, the in-person
high school hackathon held on **May 23, 2026** at **Google Humboldt in
Sunnyvale, California**. The event gave teams a single day to build, submit,
and demo live. This repo is not a cleaned-up product repo. It is the merged
record of what we actually built, what broke, what we pivoted away from, and
what we preserved near the end so none of the work got lost.

At the highest level, Lumi AI was our attempt to build a room-based care
assistant for elderly residents. The idea was that a camera and AI system in
the room could notice when something important happened, like a fall or an
unfamiliar person showing up, and could also help with day-to-day care tasks
like reminders, room awareness, and caregiver updates. We wanted it to feel
like something between a safety monitor and a lightweight care companion, not
just a single-purpose computer vision demo.

What made the project hard is that it was really several systems at once. One
part of it was perception: getting video from the Raspberry Pi, Limelight, or a
Windows webcam and turning that into something useful. Another part was
identity: figuring out whether a face matched someone we already knew or if it
should become a new record. Another part was product experience: making the
system visible in a browser, giving it app/dashboard surfaces, and shaping it
into something we could explain in a pitch. Because we were building all of
that in one hackathon day, the repo shows the real path we took: starting with
hardware, building live preview links, creating a Windows fallback when the Pi
path was too risky, wiring face and image data into Supabase, and pulling in
late fall-detection work near the end.

So this repo is best read as the engineering story of how Lumi AI came
together. It includes the original hardware path, the fallback runtime that
kept the demo alive, the database and recognition plumbing, the app shells, and
the late artifacts that show where the project was still heading when the
hackathon clock ran out.

Hackathon page:

- [Synthesis Hacks on Devpost](https://synthesishacks.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Recently+ended)

## Devpost visuals

These are the images from our Devpost submission that show the main shape of
the project. They are useful because they capture both sides of Lumi AI: the
caregiver app experience and the hardware setup that we were trying to make
work during the event.

### Caregiver home screen

This screen shows the main caregiver view: the resident status, a quick way to
alert caregivers, today's medications, and fast contact actions.

![Lumi AI caregiver home screen](assets/devpost/ios-home.png)

### Activity and unknown-person flow

This screen shows the activity feed, including unknown-person detection,
recently seen people, and the flow where the system asks the user to identify a
new face instead of silently guessing.

![Lumi AI activity screen](assets/devpost/ios-activity.png)

### Family and caregiver contacts

This screen shows the caregiver contact list and the family-notification side
of the app, which was a big part of the project story from the start.

![Lumi AI family screen](assets/devpost/ios-family.png)

### Resident settings and alert preferences

This screen shows the resident profile, medical context, and the emergency SMS
and push-notification settings that tied the app back to the care workflow.

![Lumi AI settings screen](assets/devpost/ios-settings.png)

### Limelight hardware photo

This photo shows the Limelight hardware setup we were using as part of the
original in-room sensing path before we had to rely more heavily on fallback
software paths.

![Lumi AI Limelight hardware](assets/devpost/limelight-hardware.jpeg)

This repo includes:

- the caregiver-facing app scaffolds
- Raspberry Pi + Limelight streaming work
- Windows webcam + Supabase face recognition work
- live browser preview paths
- older GuardianCare prototype code
- a late-stage fall-detection bundle that was shared right before the end

The README below is written from the actual repo history, the actual code that landed, and the team Discord export from the day of the event.

## What tools we could use

The hackathon rules were permissive. We could use:

- any language
- any framework
- any library
- any API
- AI tools, as long as outside-generated code/content was cited in the final submission

That freedom is why the stack ended up mixed instead of pure:

- Python for camera, preview, and face pipelines
- SwiftUI for the iPhone caregiver app scaffold
- Next.js for the onboarding/dashboard web scaffold
- Supabase for face data and image records
- Gemini / Google AI ideas for naming and room intelligence
- Raspberry Pi + Limelight for the original in-room hardware path
- Windows webcam tooling for the fallback path
- Google Cloud workshop guidance for Cloud Run / service deployment ideas

## Our constraints and guidelines

These were the real constraints that shaped the build:

- everything had to be built during the event window
- the demo had to work live, not just in theory
- hardware had to be worth the risk if we used it
- if a path was too fragile, we had to pivot fast without losing earlier work
- network reachability mattered almost as much as the model/code itself
- any cloud path had to be lightweight enough to wire up under hackathon pressure

The practical constraints that emerged during the day were harsher:

- Raspberry Pi installs were slower and more fragile than Windows
- camera URLs often worked only on the local network
- public streaming was harder than local streaming
- Supabase RLS and schema details took real debugging time
- camera device indexes were not stable
- one working fallback was better than one elegant but fragile architecture

## Themes and tracks

Synthesis Hacks was open-ended. It was not a hackathon with one strict required theme. The team could build broadly, but the judging lenses still mattered:

- Grand Prize
- Best Technical Implementation
- Most Creative Concept
- Best First Hackathon
- Best UI/UX Design
- Audience Favorite

Our own Discord from the morning shows that we were actively deciding how to fit the event:

- **10:26 AM**: the team was already talking about “tracks” and idea fit
- **10:34 AM**: one message explicitly asked, `can we not do the canvas idea?`
- **10:34 AM**: the reply was `Clunky school interface`
- **10:34 AM**: another reply was `no hardware component`
- **10:35 AM**: the team noted `there's barely anyone with hardware`
- **10:36 AM**: someone asked if hardware was even required
- **10:36 AM**: the answer was `no`
- **10:36 AM**: the immediate follow-up was `but its how we win`

That ended up being the real track logic for Lumi AI:

- build something AI-heavy
- make it obviously useful
- keep a hardware angle because it differentiated the demo
- still preserve a software-only fallback in case hardware slowed us down too much

## Our brainstorming

The idea did not start as “just face recognition.”

The morning chat shows the product direction sharpening very early:

- **10:37 AM**: `R we going with ur earlier idea?`
- **10:37 AM**: `So it will recognize falls and remind you stuff`
- **10:43 AM**: there was even discussion about adding entertainment/music as part of the resident experience

That is basically Lumi AI in one sentence:

> a room assistant for elder care that can notice falls, recognize people, remind residents about meds, and keep caregivers in the loop

The full PRD direction behind the build was bigger than what the final code path achieved. The intended product included:

- fall detection
- voice interaction
- medication reminders
- caregiver notifications
- face recognition / room awareness
- a caregiver dashboard

The repo looks broad because the idea was broad first, and then the implementation narrowed under time pressure.

## Problems we ran into +

These were the real technical and product problems we hit, based on the commit history and the code itself.

### 1. We split into multiple valid product paths

Very early, the repo stopped being a single clean line of work. We had:

- caregiver app scaffold work
- Raspberry Pi + Limelight stream work
- Windows webcam + Supabase recognition work
- older GuardianCare prototype code
- late GuardianCare fall-detection handoff work

That made git history messy, but it was an honest reflection of how the team was building.

Looking at the full branch graph, the split was not just cosmetic. We had:

- `raw-limelight-feed` carrying the Pi preview/tunnel work
- `windows-face-supabase-match` carrying the recognition/demo-survival path
- `pi-limelight-orchestrator` carrying the later Windows/Supabase hardening
- `openpose-pose-integration` representing a real exploration path that never
  became the primary production route

That means one of the real problems was merge debt itself:

- features were proven in parallel instead of in one clean line
- some branches were experiments, some were fallbacks, and some were the path
  that actually became demoable
- merging all of it later without losing context became part of the project

### 2. Local video was easy enough. Public video was not.

We could get the Limelight preview working locally much earlier than we could make it demo-shareable.

The Discord export shows this phase in real time:

- **1:20 PM**: `https://calm-crabs-relate.loca.lt/stream.mjpg`
- **1:48 PM**: `https://puny-houses-rest.loca.lt/`
- **1:56 PM**: that same preview link was being passed around again

That lines up exactly with the Pi/web-preview commits:

- `3a3f618` Add Raspberry Pi Limelight viewer scaffold
- `a220cf9` Add public Limelight web preview bridge
- `63b6a42` Prepare Limelight preview for Cloud Run
- `c9e0f2f` Add managed services for Limelight preview tunnel

The problem was not “can we display frames.” The problem was:

- can we expose them outside the room
- can the upstream stream stay reachable
- can a cloud service see a LAN-only camera source

### 3. Cloud deployment was less of a blocker than upstream reachability

Cloud Run preparation landed, but the real blocker was that the actual camera feed often lived behind:

- `limelight.local`
- local IPs
- tunnel URLs that were temporary by nature

So the architecture lesson was:

> cloud hosting the preview page is easy compared to making the live camera source reachable from the cloud in the first place

### 4. The Pi path cost more time than expected

The original vision put the Pi in the center, but the Pi path was expensive in hackathon time:

- ARM installs were slower
- `face_recognition` / `dlib` was much heavier there
- hardware/network debugging was slower than local Windows debugging
- public stream routing from the Pi added another layer of fragility

The full branch history shows that the Pi path never really died, but it did
stop being the only center of the project. It turned into:

- one branch for raw stream access
- one branch for preview/public-hosting attempts
- then a handoff/orchestrator branch once the Windows face pipeline became the
  more reliable demo route

That is why Windows stopped being just a backup and became a first-class demo path.

### 5. The Windows live stack had repeated real bugs, not just “setup issues”

The Windows branch history shows specific code problems:

- `8e963d5` fixed live view failures by adding missing dependencies and updating configuration
- `cf5dd81` standardized the default unknown label to `unidentified`
- `9ced36a` fixed missed uploads by decoupling face encoding from the initial embedding gate and reducing cooldown
- `d6dd6f3` fixed the case where matched faces were not being sent back to Supabase reliably
- `9484893` fixed a broken image update path by storing an image row id instead of trying to use a broken photo URL lookup

So the “face stack” problem was not abstract. The code was repeatedly being hardened against:

- frames being seen but not uploaded
- known matches not updating properly
- broken image references
- live preview dependencies not all being present
- naming/state inconsistencies for unknowns

### 6. Supabase auth and schema cost real time

We had multiple phases where:

- reads worked
- inserts failed
- RLS blocked writes
- publishable keys were not enough
- service-role access was required to fully validate the flow

That drove commits such as:

- `3c07a54` Add Supabase test face insert script
- `b4cff0d` Add base64 face upload flow and harden secret hygiene
- `349ce49` sync faces to Supabase with raw base64 and update existing matches
- `e233891` stable: working face sync to Supabase with unidentified naming and base64 storage
- `78f7a8a` add recognized faces gallery with base64 decoding
- `9484893` wire dashboard entirely to Supabase

### 7. We still kept looking for stronger pose/fall paths late in the day

The Discord export shows:

- **11:34 AM**: FamiliarAI link shared
- **3:48 PM**: OpenPose repo shared
- **5:08 PM**: `guardiancare.zip` shared

That tells the story clearly:

- we were looking at multiple recognition/perception baselines
- we were still escalating the fall/perception path late into the event
- we did not want that last work to disappear just because it arrived near the end

The branch graph reinforces this too. There was no single final fall-detection
implementation during the event. Instead, there were multiple overlapping
attempts:

- the original Lumi AI camera + reminder idea
- the FamiliarAI-style face path
- the OpenPose exploration path
- the earlier GuardianCare prototype
- the late `guardiancare.zip` handoff

That overlap was messy, but it was also a realistic hackathon pattern: the team
kept chasing the most demoable perception path instead of pretending the first
technical choice had to be permanent.

## Our product steps and each step what we did to get there

The real build order across the branches was:

1. define the caregiver product
2. prove Pi and Limelight video access
3. make the feed visible in a browser and try to share it
4. build a Windows fallback when the Pi path became too risky
5. make recognition and Supabase sync actually work
6. keep fall-detection work alive in parallel
7. merge and preserve everything at the end

### Step 1: We defined the product

We started with the product story, not the final hardware stack. Lumi AI was
meant to be a caregiver-facing elder-care assistant with room awareness, fall
detection, reminders, and recognition. This step shows up in the early app
shells and pitch framing.

### Step 2: We proved the Pi camera path

We got the Raspberry Pi and Limelight path working enough to probe the camera,
open the stream, and preview it locally. This gave us a real hardware base
instead of only an idea.

### Step 3: We tried to make the feed shareable

After local preview worked, we turned it into a browser preview and then tried
to make it reachable for a live demo. That led to tunnel links, deployment
prep, and the realization that public reachability was its own problem.

### Step 4: We built the Windows fallback

This was the biggest pivot. We made Windows capable of doing webcam capture,
live preview, face detection, Supabase lookup, and unknown-face creation on one
machine. After that, the Pi path became one subsystem and the Windows path
became the fastest place to debug.

### Step 5: We made recognition and Supabase real

We moved from “there is a webcam page” to “the system can match a known face or
create a new one.” This is where the project became stateful: face rows, image
rows, backend updates, and gallery/dashboard state all had to work together.

### Step 6: We spent a lot of time hardening the live loop

Late in the day, most of the work was repeated fixes instead of new features.
We kept tightening lag, duplicate detections, duplicate uploads, image-path
handling, matched-face updates, and logging until the fallback path felt
believable enough for a demo.

### Step 7: We kept the fall-detection path alive

Even while the face and backend loop was getting most of the debug effort, the
fall-detection story stayed active through the morning product framing, the
OpenPose exploration, the earlier GuardianCare code, and the late
`guardiancare.zip` handoff.

### Step 8: We preserved the real build

At the end, the job was not just to keep building. It was to make sure the real
history survived. That is why `main` now holds the Pi preview work, the Windows
recognition path, the app scaffolds, the earlier GuardianCare code, and the
late fall-detection bundle together.

## Commit-by-commit engineering timeline

This is the closest thing to the actual engineering diary. It is based on the
code diffs, not just the commit titles.

### `f5c4e7d` Initial commit

- The repo started almost empty.
- At this point there was no real hardware path, no app path, and no backend
  logic yet.
- This commit matters mostly because everything after it was built under the
  pressure of one day.

### `3a3f618` Add Raspberry Pi Limelight viewer scaffold

- This was the first real technical base.
- It added:
  - `pi/limelight_probe.py`
  - `pi/limelight_video_viewer.py`
  - `requirements.txt`
  - the early Gemini prompt file
- The code here was focused on discovery and direct access:
  - probing endpoints
  - trying common Limelight stream paths
  - opening the raw stream with OpenCV
- What was still missing:
  - no browser preview
  - no public sharing path
  - no receiver path
  - no stable deployment story
- The next commit that meaningfully extended this was `a220cf9`.

### `a4c9fa3` Ignore Python cache files

- This fixed a repo hygiene mistake from the scaffold phase.
- A compiled `__pycache__` artifact had been committed.
- It did not change functionality, but it shows how quickly the first Pi work
  was moving: files were being generated and committed before the repo
  conventions were fully settled.

### `a220cf9` Add public Limelight web preview bridge

- This was the first major leap from “dev tool” to “demo tool.”
- It added `pi/limelight_web_preview.py` and expanded the viewer path.
- The code change was important:
  - instead of only opening the stream locally in OpenCV
  - it now proxied the MJPEG feed through a local HTTP server
  - and exposed `/`, `/stream.mjpg`, and health-style preview endpoints
- What this solved:
  - a browser could now view the feed
  - the stream no longer depended on an OpenCV desktop window to be useful
- What was still broken:
  - this was still a local-network solution
  - there was no proper public path
- The next commit tried to solve that operational gap.

### `63b6a42` Prepare Limelight preview for Cloud Run

- This commit did not fix camera logic. It fixed deployment shape.
- It added:
  - `Dockerfile`
  - `.dockerignore`
  - `PORT`-aware behavior in the preview app
- In code terms, this was the difference between:
  - “works as a local Python script”
  - and “can at least be containerized and hosted”
- What it revealed:
  - the preview server itself was not the hard part
  - the hard part was that Cloud Run still could not see LAN-only upstream
    sources like `limelight.local`
- That is why the next commit turned toward keepalive services and tunneling.

### `c9e0f2f` Add managed services for Limelight preview tunnel

- This added the operational Pi glue:
  - systemd user services
  - localtunnel watcher
  - preview keepalive scripts
- The problem being solved here was not code correctness.
- The problem was that even a working preview is useless if:
  - it dies between demos
  - it must be restarted manually
  - or the tunnel is too fragile to keep up
- This commit made the preview path more survivable, but it still did not solve
  perception or identity.

### `7aeebc1` Add webcam face sender and ngrok service

- This is where the project started stepping beyond “stream a camera.”
- It added:
  - `pi/face_capture_sender.py`
  - `windows/face_receiver.py`
  - `requirements-face.txt`
  - `requirements-windows.txt`
  - ngrok service support
- The architecture change here was major:
  - the Pi could now send face data outward
  - a Windows machine could receive it
  - the repo started splitting into sender/receiver responsibilities
- What was still missing:
  - robust matching
  - Supabase-backed identity
  - a usable local dashboard on Windows
- The next big commit built that out.

### `04927dd` Add Windows face matching and LumiAI launcher

- This was the first real “software-only fallback can run the whole demo”
  commit.
- It added:
  - `windows/face_matching.py`
  - `windows/supabase_known_faces.py`
  - `windows/webcam_supabase_live.py`
  - `windows/webcam_supabase_match.py`
  - `windows/lumiai.ps1`
  - Windows requirements files
- The code change was architectural:
  - direct webcam access on Windows
  - local matching against Supabase
  - a local preview path
  - a launcher to keep the demo usable from one command
- What was still wrong right after this:
  - the live view path was not yet stable
  - unknown naming was inconsistent
  - image/update semantics were still immature
- That is exactly what the next series of commits fixed.

### `8e963d5` fix(windows): resolve live view issues by adding missing dependencies and updating configuration

- This is the first big “debugging the working fallback” commit.
- The code diff shows several concrete improvements:
  - local IPv4 discovery
  - explicit JPEG byte helpers
  - a lower-latency stream loop
  - `/images/<filename>` serving
  - frame skipping with `--process-every-n`
  - downscaled detection with `--detect-scale`
  - lower stream sleep from `0.1` to `0.03`
  - optional Gemini face description + Windows speaker prompt
- In plain English, this fixed:
  - laggy local preview
  - preview pages that were too heavy to feel live
  - saved images that were not reachable from other laptops on the LAN
- It also introduced a more serious performance pattern:
  - reuse the last processed detections between recognition passes instead of
    forcing full recognition every frame
- What still needed cleanup immediately after this:
  - unknown names were still not standardized
  - upload logic was still missing some cases

### `cf5dd81` fix(windows): set default unknown person name to `unidentified`

- Small diff, important semantic cleanup.
- Before this, unknowns could be named in inconsistent ways.
- After this, the unknown-person fallback had one stable label.
- That mattered because the next Supabase sync commits were trying to make the
  insert/update path easier to reason about.

### `3c07a54` Add Supabase test face insert script

- This commit exists because configuration guessing was no longer enough.
- The script was added to test:
  - whether a face row could actually be inserted
  - whether the current key worked
  - whether the table schema accepted the payload shape
- This commit does not make the app smarter.
- It makes the team faster at separating:
  - app bugs
  - from Supabase auth/RLS problems

### `c3d7038` Add SwiftUI iOS app and bootstrap Next.js onboarding web app

- This commit did not come from the same linear implementation thread as the
  Windows fixes.
- It added the product shell:
  - iOS caregiver app
  - Next.js onboarding flow
- It mattered because the repo was not just a camera project. It preserved the
  family/caregiver product surface while the recognition stack was still being
  debugged elsewhere.

### `b4cff0d` Add base64 face upload flow and harden secret hygiene

- This was a key transport change.
- Before this, the image flow was more file/URI-centric.
- After this, the receiver could accept `/upload-base64`, and the helper
  `windows/send_first_face_base64.py` could push a detected face directly as a
  base64 JSON payload.
- In code terms, this solved:
  - easier browser/client uploads
  - easier first-face testing without multipart file juggling
  - less dependence on local file paths when moving image data around
- It also started setting the repo up for safer secret handling.

### `eb9bc05` Add live local face receiver view

- This commit turned the receiver into something visible, not just an endpoint.
- It added:
  - a richer root page
  - camera state
  - a startup script
- This solved the “the backend might be running but we cannot quickly tell”
  problem.
- It made local validation faster and reduced guesswork during repeated runs.

### `2337100` feat(windows): improve face matching and preview with browser-side camera and embedding normalization

- This commit fixed two subtle but important issues.
- First, `supabase_known_faces.py` gained embedding normalization logic so that
  embeddings loaded from Supabase could be parsed even if they came back as JSON
  strings rather than already-materialized Python lists.
- Second, `face_receiver.py` gained a browser-camera front end instead of
  depending only on server-side camera capture.
- What this solved:
  - fewer broken loads when Supabase returned embeddings in inconsistent shapes
  - lower-latency local viewing by letting the browser own the camera preview
  - a better `/known-faces` JSON/data path for the dashboard
- This is one of the clearest “previous commit worked, but was still awkward or
  brittle” improvements.

### `dd5a198` Add vendored base64 CLI and Python helper

- This commit was about deterministic encoding behavior.
- Instead of relying only on whichever encoder happened to be available, the
  repo gained:
  - `scripts/base64_helper.py`
  - vendored `vendor/progers-base64/cli.js`
- That set up the next commit, where image storage leaned harder into raw
  base64 flows.

### `78f28eb` Use progers/base64 for image encoding; add Supabase image base64 insert/update; name new faces `unidentified`

- This changed the Supabase image strategy directly.
- The code diff shows:
  - new `insert_image_base64`
  - `find_image_by_url`
  - `update_image_by_id`
  - `update_known_face_photo`
  - helper functions to encode/decode raw bytes
- It also changed unknown-face creation to use `person_name="unidentified"`.
- What this solved:
  - image records could be inserted and updated without relying only on local
    file URIs
  - matched faces finally had a path toward image updates in Supabase
- What it still did awkwardly:
  - it sometimes pushed raw base64 into places that later had to be cleaned up
  - photo reference semantics were still not fully stable

### `349ce49` feat(windows): sync faces to Supabase with raw base64 and update existing matches

- This was the first serious attempt to make matched faces update, not just
  newly created unknowns.
- It pushed the live Windows pipeline toward:
  - raw base64 images
  - updating existing matches
  - not just inserting unknowns forever
- This commit mattered because the later Discord summary at **4:37 PM** still
  correctly observed that matched-user image updating was not fully correct yet.
- In other words, this commit introduced the right intention, but the following
  commits had to make it reliable.

### `39f6c42` Fall detection

- This brought in the earlier GuardianCare branch.
- Technically it is huge, but the key point is not just size. It added a
  parallel implementation of the Lumi AI idea:
  - fall detection
  - face recognition
  - iOS app
  - web app
  - Supabase client
- The repo became broader here, but also more historically honest.

### `ae0cf6c` feat: upload `download.jpg` and ensure unknown faces are registered as `unidentified` in Supabase

- This was another direct Supabase validation commit.
- It added scripts that could push a known sample image and prove whether the
  insert flow actually worked.
- This is the kind of commit that only appears when the team is debugging the
  backend with real payloads instead of theory.

### `0238dc7` feat(dashboard): add real-time event log and telemetry status

- This commit improved observability.
- The code added:
  - event log support
  - telemetry state
  - richer dashboard status
- This solved a real hackathon problem:
  - when uploads or detections failed, the team needed to see where in the
    pipeline it died
- It turned the app into something closer to a live debugging console.

### `436ab6b` feat(windows): enhance logging for encoding/uploads and tune sensitivity to prevent duplicates

- This commit used the new telemetry to attack duplicate and sensitivity issues.
- The diff shows:
  - server-side event buffers
  - upload/detection event logging
  - a lower matching threshold from `0.6` to `0.55`
  - tighter recent-face distance from `0.25` to `0.20`
  - a longer repeat window from `45` to `90` seconds
- That combination says exactly what was going wrong:
  - duplicates were too easy to produce
  - the app needed better introspection to see why

### `9ced36a` fix(windows): ensure face uploads occur by decoupling encoding from initial embedding check and reducing cooldown

- This is one of the most concrete bug-fix commits in the repo.
- Before this patch, the upload loop could skip too early if the embedding check
  short-circuited, so the face crop never got encoded and sent.
- The diff literally moves the embedding check so unknown upload encoding still
  happens in the right branch.
- It also cuts `save-cooldown` from `10.0` seconds to `5.0`.
- So the real issue was:
  - faces were visible
  - but uploads were sometimes not happening at all

### `ad6a6f9` debug: add verbose logging and continue investigating Supabase sync issues

- This commit is the clearest proof that sync still was not stable after
  `9ced36a`.
- It added more logging, which means the prior fix helped but did not fully
  explain all failures.
- This is exactly the kind of small debug commit that marks a real live-fire
  investigation.

### `d6dd6f3` fix(windows): ensure face data is sent to Supabase on matches and rename old entries to unidentified

- This fixed the next bug after unknown uploads:
  - matched users were not being updated reliably
- The diff shows:
  - event log entries when a match is found
  - explicit matched-face update attempts
  - fallback image insertion if the old reference is missing
  - updating the known face’s stored photo after a new image record
- This is exactly the code-path that the earlier 4:37 PM Discord summary said
  was still weak.

### `e233891` stable: working face sync to Supabase with unidentified naming and base64 storage

- This commit is the first one that calls the Windows sync path “stable,” and
  that lines up with the sequence before it.
- By here, the project had already:
  - changed image transport
  - improved observability
  - fixed missed uploads
  - fixed matched-face updates
- So “stable” here reads as earned, not aspirational.

### `78f7a8a` feat(dashboard): add recognized faces gallery with base64 decoding

- Once the sync path mostly worked, the next issue was presentation.
- This commit made the dashboard/gallery decode and show recognized faces from
  stored base64 image data.
- In other words, it solved:
  - “the face data may be in Supabase”
  - but “the dashboard still does not render it in a useful way”

### `9484893` Fix face upload errors and wire dashboard entirely to Supabase

- This is the cleanup/final-hardening commit for the Windows face pipeline.
- The most important code change here was conceptual:
  - instead of treating `photo_url` as a brittle URL lookup target
  - it started treating it as an image row id when appropriate
- `supabase_known_faces.py` gained `find_image_by_id`.
- `webcam_supabase_live.py` changed `/known-faces` so the gallery fetched the
  actual image row by id and rendered real base64 content from Supabase.
- What this solved:
  - broken gallery rendering
  - incorrect assumptions about `photo_url`
  - mixed local/Supabase state in the dashboard
- This is the commit that most clearly moved the dashboard from “mostly local
  and patched together” to “really backed by Supabase.”

### `5034da5`, `11a2789`, and `960f8ca`

- These were the documentation and preservation phase.
- `5034da5` rewrote the README as a hackathon narrative.
- `11a2789` unpacked the late GuardianCare fall-detection bundle into
  `guardiancare_late/`.
- `960f8ca` rewrote the README again using the Discord timeline and actual repo
  history.
- These commits matter because the final repo goal was not just “ship code.”
  It was “preserve the actual journey and all the useful branches of work.”

## What is in the repo now

### Current caregiver / app scaffolds

- `ios/`
- `web/`

### Raspberry Pi / Limelight path

- `pi/limelight_probe.py`
- `pi/limelight_video_viewer.py`
- `pi/limelight_web_preview.py`
- `deploy/systemd/`

### Windows face / Supabase / live preview path

- `windows/face_receiver.py`
- `windows/face_matching.py`
- `windows/supabase_known_faces.py`
- `windows/webcam_supabase_match.py`
- `windows/webcam_supabase_live.py`
- `windows/lumiai.ps1`

### Earlier and later preserved fall-detection work

- `guardiancare/`
- `guardiancare_late/`

## Why main looks like a monorepo

Because it is the merged result of the real hackathon sprint.

We did not do one perfect architecture from start to finish. We:

1. defined the caregiver product
2. tried the Pi / Limelight path
3. fought public streaming and reachability
4. built a Windows fallback that could still demo the core idea
5. fought Supabase auth and image/update correctness
6. preserved the older and later fall-detection work instead of throwing it away

That is why `main` contains multiple valid paths. It is not accidental sprawl. It is the record of the actual journey.

## Final summary

Lumi AI ended up being less of a “single polished product” and more of a successful hackathon survival pattern:

- hardware where it was compelling
- software fallback where it was reliable
- local preview when public streaming was fragile
- Supabase as the identity backbone
- caregiver-facing product framing carried all the way through
- fall detection preserved both in earlier prototype code and in a late shared bundle

That combination is what this repo documents.
