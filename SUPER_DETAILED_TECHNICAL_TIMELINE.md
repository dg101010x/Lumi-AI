# Lumi AI Super Detailed Technical Timeline

Lumi AI was our hackathon attempt to build an elder-care room assistant that
could do three things at once. First, it needed to watch the room well enough
to notice events like falls, presence, and changes in activity. Second, it
needed to keep track of people and state, so the system could recognize known
faces, create new ones, and eventually connect what it saw to a caregiver-facing
record. Third, it needed to feel like a real product instead of a disconnected
demo script, which meant live preview, caregiver UI, reminder logic, and a
story we could explain on stage. The tension in the whole codebase comes from
trying to build those three layers under a one-day hackathon clock: perception,
backend truth, and demo survivability.

This file is a strict chronological event log. It is written like our own
technical journal of the day, not like an outside analysis. Each section starts
with a time and then explains what we were doing, what changed in code, and how
the system evolved at that moment.

## Saturday, May 23, 2026

### 10:26 AM — We started by thinking about the hackathon shape, not just the code

Before we had meaningful code, we were already talking about tracks, ideas, and
what kind of build would stand out. We were not deciding between random project
ideas. We were deciding what kind of technical shape would feel strong in a
hackathon setting. That mattered later because it pushed us toward something
that had to be visibly real, not just conceptually polished.

### 10:34 AM — We dropped the earlier non-hardware direction

We decided not to do the earlier canvas-style interface idea because it felt too
clunky and did not have a hardware component. That was the first real
engineering decision of the day even though it happened in chat before the main
commits. Once we made that choice, we were committing ourselves to camera input,
device setup, networking issues, and a much harder implementation path.

### 10:35–10:36 AM — We decided hardware was optional, but it was how we would stand out

We talked through whether hardware was even required and realized it was not,
but we still wanted it because it gave the project presence. That created the
main tension that shaped the rest of the repo: we wanted the wow factor of
hardware, but we also had to protect ourselves in case the hardware path became
too fragile. That is the reason the repo later splits into the Pi/Limelight
path and the Windows fallback path instead of staying clean and linear.

### 10:37 AM — We finally said the product in one sentence

This was the moment we said what Lumi AI actually was: it would recognize falls
and remind you about things. That one sentence already contained the three
technical layers that later spread across the repo: perception, identity, and
care logic. The repo ended up broad because the idea itself was broad from the
start.

### 10:43 AM — We widened it from emergency detection into care and comfort

We were already talking about adding music or entertainment-type behavior, which
meant the product was not just an emergency detector. We were thinking about it
as a room assistant for elder care. That is why the repo later includes app
shells, prompts, reminder language, and caregiver-facing flows instead of only
fall-detection code.

### 11:17:19 AM — We created the repo and effectively started from zero

The initial commit is small, but it marks the beginning of the real build day.
At this point there was no hardware runtime, no preview stack, no backend face
path, and no fall-detection implementation in the repo yet. Everything that
made the project complicated came after this.

### 11:34 AM — We pulled in FamiliarAI as a recognition reference point

By late morning, we were already looking at FamiliarAI. That gave us a concrete
reference for face detection, matching, and handling known versus unknown
people. This mattered later because the Windows/Supabase face path was not
appearing out of nowhere; it was forming in dialogue with an existing pattern we
were studying.

### 12:45:14 PM — We got the first real Pi/Limelight scaffold into the repo

This was the first major code step. We added the Pi probe script, the raw
Limelight viewer, the requirements file, the first Gemini prompt, and the first
project notes. At this point we were still in pure proof mode. We were trying
to discover the Limelight, hit the right endpoints, and open the stream. We had
not yet built the browser preview, the public-shareability layer, the Supabase
identity flow, or the integrated fall-detection runtime. We were simply trying
to prove that the room camera path was real.

### 12:45:28 PM — We cleaned up the first Pi pass immediately after running it

We had already generated Python cache artifacts while getting the first Pi code
running, so we cleaned that up right away. It is small, but it reflects the
actual pace of the day: make it run first, then make the repo cleaner.

### 1:07:07 PM — We turned raw stream access into a browser preview

Once the raw Limelight path worked, we moved quickly from an OpenCV window to a
browser preview. We added the web preview bridge so the stream could be served
through HTTP and shown in a root page and MJPEG endpoint. This was the first
time the code started feeling like a demo surface instead of only a local dev
tool. At this point, though, the preview was still local. People could see it
in a browser, but that did not yet mean it was easy to share or stable enough
for a public demo.

### 1:11:45 PM — We started shaping the preview path for deployment

Just a few minutes later, we added the Dockerfile and `.dockerignore` and began
preparing the preview for Cloud Run. The important shift here was not perception
logic. It was deployment logic. By this point the question had already changed
from “can the Pi read the stream” to “can we host this somewhere useful.” This
commit became the base for later branch splits, which is why it sits at such an
important point in the repo history.

### 1:20 PM — We got the first public stream link working

By `1:20 PM`, we had a tunnel-backed stream URL we could send around. That was a
big milestone because the problem stopped being only local camera access. We now
had a full path from the camera to a public endpoint. At the same time, that
success exposed the next problem immediately: once the preview was public, we
had to worry about tunnel stability, upstream reachability, and whether this
kind of path would survive a live demo.

### 1:27:25 PM — We made the preview and tunnel path behave more like a service

Once we had a public link at all, we started wrapping the preview and tunnel in
services and watcher scripts. A working preview was already not enough. It had
to stay up, restart correctly, and feel reliable enough that we could build
other things on top of it. This is when preview and tunnel handling became its
own subsystem instead of just a helper script.

### 1:48 PM and 1:56 PM — We were still checking and re-sharing public preview links

We shared another public preview link and then sent it again a few minutes
later. That captures the feel of this phase well. We were still actively
checking whether people could reach the video at all. At this point in the day,
the project was still more about making the feed visible than about whether the
identity layer was already correct.

### 2:50:58 PM — We split the system into a sender and a receiver

This was one of the most important architecture shifts of the day. We added the
Pi face sender, the Windows receiver, and ngrok-related support. From this
moment on, the Pi was not just a preview device anymore. It could capture or
forward face-related data while another machine could receive and process it.
That changed the project from one edge-device experiment into a distributed
system.

### 2:52:27 PM — We were also actively experimenting with OpenPose

Around the same time, we had active OpenPose overlay work sitting in the
OpenPose branch stash. That matters because it means we were not moving in a
single straight line. While preview, tunneling, and sender/receiver work were
happening, we were also still exploring a stronger pose-based perception path.

### 3:46:09 PM — We built the real Windows fallback

This was the biggest architecture pivot in the repo. We added the main Windows
face matching, Supabase, live preview, and launcher files. From this point on,
the repo stopped being mainly “Pi preview plus ideas” and became two real
runtime centers: the Pi/Limelight path and a Windows webcam path that could
potentially carry the whole demo on one machine. It was powerful, but it was
not yet stable. We still had problems with live view quality, naming semantics,
image transport, and how matched faces should update.

### 3:48 PM — We were still pushing the pose/fall side even after the Windows fallback existed

We explicitly shared OpenPose after the Windows fallback was already real. That
shows the team had not abandoned deeper perception work just because we found a
more reliable runtime center. We were now doing two things in parallel: making
the demo survivable and still chasing a stronger perception path.

### 4:11:40 PM — We redesigned the Windows live runtime so it would actually feel usable

This was not a small patch. We added LAN IP discovery, JPEG helper logic,
served saved images over HTTP, reused detections across frames, split preview
cadence from processing cadence, and introduced processing controls like
`process-every-n` and `detect-scale`. We also wired in the Gemini description
and Windows speaker hooks. This was the moment the Windows live path stopped
being just barely possible and started being tuned for latency, clarity, and
operator usability.

### 4:12:05 PM — We standardized unknown naming

Right after the larger runtime redesign, we cleaned up the default unknown
person name to `unidentified`. That sounds small, but it mattered because once
the live Windows path existed, the next problems were already moving from
runtime existence into data-model cleanliness.

### 4:18:38 PM — We added direct Supabase test tooling because the live app was no longer enough

By this point, a failure could mean bad logic, bad auth, wrong schema
assumptions, or RLS issues. So we added a direct Supabase insert test script to
separate those problems. This was the moment we stopped trusting the live app as
the only way to understand the backend.

### 4:21 PM — We were still feeding in real care data while the runtime was being debugged

The medication schedule arrived while we were still fixing runtime and backend
problems. That matters because it shows Lumi AI never collapsed into only a
camera project. The care-assistant product layer was still active at the same
time as the engineering scramble.

### 4:22:17 PM — We built the caregiver-facing shell in parallel

While the runtime and backend were being hardened elsewhere, we added the
SwiftUI iOS scaffold and the Next.js onboarding web app on `main`. That meant
the repo was growing on two tracks at once: product-facing surfaces and
perception/backend plumbing.

### 4:24–4:26 PM — We started compressing the build into pitch language while still coding

At this point we were already refining how to explain the system for the pitch
while still changing it. That mattered because the architecture had to become
not just functional, but explainable under pressure.

### 4:31:29 PM — We changed image transport to base64 because local-file assumptions were getting in the way

This was a major backend shift. We added `/upload-base64` and the helper that
captures the first detected face and sends it as base64. From here on, image
movement in the system was less about local file paths and more about raw
payload transport that we could push through the backend more reliably.

### 4:37:53 PM — We had a working technical story, but we also knew exactly what was still wrong

By `4:37 PM`, we could already summarize the stack clearly: Raspberry Pi and
Windows webcam paths, `face_recognition`, Supabase `known_faces`, MJPEG over
Flask, unknown auto-insert, and Gemini naming support. But we also knew the big
gap at that exact moment: matched known faces were not being updated the way
unknown faces were. That is what the next series of commits starts fixing.

### 4:47:51 PM — We made the receiver easier to inspect and operate

We improved the local face receiver view and added startup support so the
receiver was easier to watch, restart, and reuse in repeated test cycles. This
was operational hardening more than feature expansion.

### 5:01:02 PM — We fixed quiet compatibility problems in the Windows path

This commit fixed two important issues that were easy to miss but mattered a
lot. We normalized embeddings coming back from Supabase so they would parse
correctly even when the data shape was inconsistent, and we improved local
preview by giving the browser its own camera path. This was the moment the
Windows path started getting refined at the level of quiet correctness instead
of only broad architecture.

### 5:08:04 PM — We standardized the base64 layer because it had become core infrastructure

By this point base64 handling was central enough that we vendored tooling for
it. That says a lot about where the project had moved. Image transport was no
longer a small helper concern. It was part of the core backend path.

### 5:08 PM — We received the late GuardianCare fall-detection bundle while everything else was still moving

At almost the same time as the base64/backend work, `guardiancare.zip` was
shared. That was the late fall-detection handoff. It shows how the day really
felt: we were still hardening the Windows/Supabase path while late perception
and fall-detection work was still arriving.

### 5:09:32 PM and 5:12:29 PM — We were revising the README while still fixing the system

The README revisions show that we were tightening the narrative while the core
engineering work was still active. We were not doing engineering first and story
later. Both were happening together.

### 5:14:34 PM — We made backend image updates explicit instead of implied

This was the first strong attempt to make the image lifecycle in Supabase
coherent. We added explicit image-table operations and tightened unknown-face
naming further around `unidentified`. The system was getting more deliberate
about how face rows and image rows were connected, even though the semantics
were still not fully clean yet.

### 5:21:31 PM — We started treating matched people as update targets, not just unknowns as inserts

This was the right move after the earlier realization that matched people were
lagging behind unknowns in the backend flow. We pushed the system toward
updating known people instead of only inserting new ones, but it still was not
the final clean solution yet.

### 5:24:29 PM — We pulled the earlier GuardianCare fall-detection lineage into `main`

This brought in the earlier GuardianCare code with its fall detection, face
recognition, `main.py`, and associated app shells. It was not cleanup. It was
another major technical line entering the repo during the same active build
window. By this point the project clearly had multiple legitimate lineages at
the same time.

### 5:33:07 PM — We kept using direct sample-image scripts to prove backend behavior

We added more scripts around uploading a sample image and making sure unknowns
registered correctly. That tells the story clearly: we still did not fully
trust the live loop alone, so we kept building direct probes for the backend.

### 5:36:10 PM — We made the app explain itself

We added a real-time event log and telemetry status to the Windows dashboard
path. That was a major maturity step because the problem had shifted from
wanting more features to needing the runtime to show us where it was failing.

### 5:39:39 PM — We tuned the live behavior to cut down duplicate detections and duplicate uploads

We adjusted thresholds and recent-face timing while expanding event logging.
That tells us exactly what was hurting at this point: duplicate creation and
repeated processing had become a real live problem, and we were tuning behavior
instead of just fixing syntax or auth.

### 5:42:43 PM — We fixed a real upload control-flow bug

Before this commit, a face could be detected but still fail to upload because
the flow exited too early before the crop was encoded and sent. We moved the
embedding gate deeper into the unknown-face branch and reduced cooldown. This
was one of the clearest true pipeline bug fixes in the repo.

### 5:44:40 PM — We added more logging because the previous upload fix was not the end

Right after fixing the upload control flow, we added more verbose logging. That
shows the previous fix helped, but sync still was not stable enough to trust. We
were still actively investigating.

### 5:46:13 PM — We finally gave matched faces explicit backend update behavior

This was the clearest answer to the earlier problem we had already named out
loud. We added explicit matched-face update logic, including image updates,
fallback creation of image records when needed, and linkage updates afterwards.
This was when the known-person path started catching up with the unknown-person
path.

### 5:48:22 PM — We reached the first point where the Windows/Supabase path felt stable

By this point we had base64 transport, direct backend tests, telemetry,
duplicate suppression tuning, upload control-flow repair, and matched-face
update logic all in place. That is why this was the first moment the Windows
fallback could really be treated as a converged runtime path rather than only an
emergency backup.

### 5:49:29 PM — We improved gallery rendering so backend state was actually visible

We improved the gallery by decoding backend-stored base64 image data for
display. This was the step where the system moved from simply writing state into
the backend to actually showing that state meaningfully.

### 5:57:38 PM — We did the final major cleanup of dashboard and image semantics

This was the last big hardening pass of the day. We stopped assuming `photo_url`
was always directly usable as a URL, added `find_image_by_id`, and fetched
actual image content from the `images` table by id for dashboard rendering. This
fixed a structural mismatch between face rows, image rows, and gallery
assumptions. It also showed how messy the branch structure had become, because
the final major Windows/Supabase dashboard cleanup was sitting on a branch with
a Pi-heavy name.

### 9:44 PM — We started merging the active branches into `main`

At this point we stopped treating the branches as temporary experiments and
started preserving them together. This was not just repo housekeeping. It was a
decision to keep both the Pi preview line and the Windows/Supabase line instead
of pretending one of them never mattered.

### 9:51 PM onward — We shifted into preservation mode

From here on, the work became about preserving what we had really built. We
rewrote the README, unpacked `guardiancare.zip` into `guardiancare_late/`,
aligned the docs to the timeline and commit history, and then added the
technical writeups. The hackathon implementation day was effectively over by
then. The final engineering task was making sure the real story and the late
artifacts did not disappear.

## Final reading of the day

Read straight through, the day went like this. We chose an elder-care assistant
idea and decided hardware would help us stand out. We proved the Pi/Limelight
camera path first, then turned that into a browser preview, then tried to make
that preview shareable. As soon as we did that, reachability and durability
became their own problem. We then split the architecture so the Pi could send
data outward and a receiver could process it. After that, we built a true
Windows fallback because the Pi path was too risky to be the only center of the
demo. Once the Windows path existed, the fight moved into backend truth:
transporting images cleanly, syncing with Supabase, suppressing duplicates,
updating matched faces correctly, and making the dashboard render real backend
state. At the same time, fall-detection work kept coming in through both the
earlier GuardianCare import and the late `guardiancare.zip` handoff. By the end
of the night, the challenge was no longer inventing another subsystem. It was
making sure all the real lines of work we had built were preserved honestly in
one repo.
