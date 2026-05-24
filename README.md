# Lumi AI

Lumi AI is our full hackathon build log for **Synthesis Hacks**, the in-person
high school hackathon held on **May 23, 2026** at **Google Humboldt in
Sunnyvale, California**. The event gave teams a single day to build, submit,
and demo live. This repo is not a cleaned-up product repo. It is the merged
record of what we actually built, what broke, what we pivoted away from, and
what we preserved near the end so none of the work got lost.

Hackathon page:

- [Synthesis Hacks on Devpost](https://synthesishacks.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Recently+ended)

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

## Our product steps and each step what we did to get there

### Step 1: We defined the product story first

The product idea came before the stable hardware implementation.

What we wanted:

- a caregiver-facing system
- elder-care room awareness
- falls + reminders + recognition
- an AI layer that could help interpret and label events

Early repo commits that show that product shell:

- `f5c4e7d` Initial commit
- `c3d7038` Add SwiftUI iOS app and bootstrap Next.js onboarding web app
- `ffa3713` and `f06b742` README revisions around the Lumi AI story

What we built in this step:

- `ios/` SwiftUI caregiver app scaffold
- `web/` onboarding / dashboard scaffold

This was the “what judges and caregivers should understand” layer.

### Step 2: We proved raw room-camera access on the Pi

Before AI, we needed one basic proof:

> can the Pi actually see and surface the Limelight feed

What we built:

- `pi/limelight_probe.py`
- `pi/limelight_video_viewer.py`
- `pi/limelight_web_preview.py`

The related commits:

- `3a3f618` Add Raspberry Pi Limelight viewer scaffold
- `a220cf9` Add public Limelight web preview bridge
- `63b6a42` Prepare Limelight preview for Cloud Run
- `c9e0f2f` Add managed services for Limelight preview tunnel

What that step accomplished:

- raw stream access
- local preview
- early public-preview experiments
- a practical Pi-side foundation instead of only a diagram

### Step 3: We turned “preview” into a demo problem, not just a dev problem

Once the video existed locally, the next issue was:

> can anyone else actually see it during a demo

That is when tunnel URLs started being shared and reused in Discord, and when deployment prep appeared in the repo.

What we learned here:

- local success is not demo success
- temporary preview links are fragile
- Cloud Run can host a service, but it cannot magically see a local camera that the internet cannot reach

### Step 4: We built a software-only fallback because the Pi path was too risky to be our only bet

This was the most important technical pivot of the day.

Instead of treating Windows as a side experiment, we made it capable of doing the whole recognition/demo loop on one machine:

- webcam capture
- live preview
- face detection/embedding
- Supabase lookup
- unknown-face creation
- local dashboard/browser preview

That work landed through:

- `04927dd` Add Windows face matching and LumiAI launcher
- `8e963d5` live-view repair
- `eb9bc05` Add live local face receiver view
- `2337100` improve face matching and preview with browser-side camera and embedding normalization

This was not the cleanest architecture. It was the best hackathon architecture once time became the main constraint.

### Step 5: We made the identity path real instead of fake

This step moved us from “a webcam page exists” to “the system actually recognizes or creates people.”

What we added:

- `windows/face_receiver.py`
- `windows/face_matching.py`
- `windows/supabase_known_faces.py`
- `windows/webcam_supabase_match.py`
- `windows/webcam_supabase_live.py`
- `windows/lumiai.ps1`

And the commits show the hardening sequence clearly:

- standardize unknown naming
- test inserts directly against Supabase
- switch image handling to base64
- fix cases where uploads did not fire
- fix cases where matched users did not update properly
- move the dashboard/gallery to Supabase-backed state instead of mixed local state

By the end of this step, the project had a working path for:

- live local face view
- matching against `known_faces`
- creating new rows when needed
- serving a local preview for demo use

### Step 6: We fed in real product data late in the day

The Discord export shows product details continuing to arrive deep into the sprint:

- **4:21 PM**: medication schedule shared
  - Amlodipine - 1 pill - 9AM
  - Lisinopril - 1 pill - 9PM
  - Metformin - 1 pill - 1PM
  - Simvastatin - 1 pill - 9PM

That matters because Lumi AI was never just “camera tech.” The goal stayed tied to the elder-care workflow all the way through the end.

### Step 7: We tightened the pitch while still building

The Discord export shows that by **4:26 PM** the team was already refining the
50-word technical pitch language, and by **4:37 PM** there was a detailed
technical summary tying together:

- edge CV
- Raspberry Pi
- Windows webcam pipeline
- `face_recognition`
- Supabase `known_faces`
- Flask MJPEG preview
- unknown face insertion
- Gemini-assisted naming prompts

That same 4:37 PM technical note also correctly called out a real code limitation:

> matched known faces were not yet updating their most recent image path the way unknown faces were

That limitation later lines up with the fixes that landed in `d6dd6f3` and `9484893`.

### Step 8: We preserved the older GuardianCare prototype instead of deleting it

The commit:

- `39f6c42` Fall detection

brought in the earlier GuardianCare code. That commit matters because it preserved another branch of the same core idea:

- fall detection
- face recognition
- iOS scaffold
- web scaffold
- Supabase-connected code

It made `main` larger, but it kept a real product ancestor in the repo instead of losing it.

### Step 9: We preserved the late fall-detection handoff too

Near the end of the day, another artifact arrived:

- **5:08 PM**: `guardiancare.zip`

We unpacked and kept it as:

- `guardiancare_late/`

That bundle contains:

- `fall_detection.py`
- `main.py`
- `face_recognition_module.py`
- `config.py`
- `supabase_client.py`
- same-day registration images

This bundle is real late-stage fall work, not just a leftover archive. The code
uses a MediaPipe pose-based fall path with torso-angle and hip-drop logic,
which makes it relevant to the original Lumi AI concept instead of being random
extra files.

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
