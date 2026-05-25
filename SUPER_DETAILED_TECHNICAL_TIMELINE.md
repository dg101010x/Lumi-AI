# Lumi AI Super Detailed Technical Timeline

Lumi AI was our hackathon build for elder care. The core idea was that the
system would watch a room, recognize people, notice falls or other important
events, remind people about things like medication, and keep a caregiver-facing
record of what was happening. What actually happened during the hackathon was
that we built that idea in pieces under time pressure. We started with the room
camera and preview path, then split into sender and receiver pieces, then built
the Windows fallback, then spent a huge part of the day getting face syncing,
image handling, and Supabase updates to behave correctly, while fall-detection
work kept arriving in parallel.

## Saturday, May 23, 2026

### 10:26 AM

We started by talking about the shape of the hackathon and what kind of build
would actually stand out. We were not coding yet. We were deciding whether we
were making something that felt like a real system or just a polished software
demo. The problem at that point was that we did not have a locked direction
yet.

### 10:34 AM

We dropped the earlier canvas-style idea because it felt clunky and did not
have a hardware component. The problem at that point was that our earlier idea
did not feel strong enough for the event, so we changed direction before the
main build even really started.

### 10:35 AM to 10:36 AM

We decided hardware was not required, but hardware was probably how we would
win attention. The problem at that point was that using hardware made the build
harder, but we still chose it because it gave the project more presence.

### 10:37 AM

We finally said the product in one sentence: it would recognize falls and
remind you about things. The problem at that point was that the idea was now
bigger than a single feature. We had committed ourselves to perception, care
logic, and some kind of data or identity layer all at once.

### 10:43 AM

We were already talking about comfort and room-assistant behavior, like music
or other supportive actions. The problem at that point was scope. The product
was already expanding beyond just emergency detection.

### 11:17:19 AM

We made the initial repo commit and basically started from zero inside the
repository. The problem at that point was that none of the real system pieces
existed yet. There was no Pi runtime, no preview path, no face pipeline, no
backend sync path, and no integrated fall-detection flow.

### 11:34 AM

We pulled in FamiliarAI as a reference for face detection and recognition. The
problem at that point was that we needed a concrete pattern for how to think
about known faces, unknown faces, and matching behavior instead of inventing
everything blindly.

### 12:45:14 PM

We got the first real Raspberry Pi and Limelight scaffold into the repo. We
added the Pi probe script, the raw Limelight viewer, the requirements file, the
first prompt file, and project notes. The problem at that point was basic
camera proof. We were still trying to prove that we could discover the
Limelight, hit its endpoints, and see the stream at all.

### 12:45:28 PM

We cleaned up Python cache files right after the first Pi pass. The problem at
that point was minor repo mess from just getting the first code to run.

### 1:07:07 PM

We turned the raw Limelight stream into a browser preview by adding the web
preview bridge with a root page and MJPEG endpoint. The problem at that point
was that an OpenCV-only window was not enough for a demo. We needed the feed in
a browser so it was easier to see and share.

### 1:11:45 PM

We prepared that preview path for Cloud Run by adding deployment files like the
Dockerfile and `.dockerignore`. The problem at that point was that local-only
preview was not enough anymore. We were already thinking about how to host or
share it.

### 1:20 PM

We got the first public stream link working through a tunnel. The problem at
that point was that once the feed was public, reliability became the next
issue. It was no longer just about “can we see the feed locally.” It became
“will this still work when someone else opens it.”

### 1:27:25 PM

We added managed services and watcher behavior around the preview and tunnel so
the public path would behave more like a real service. The problem at that
point was that the preview could work once and still not be good enough if it
did not stay up.

### 1:48 PM and 1:56 PM

We were still sharing and rechecking public preview links. The problem at that
point was that public shareability was still fragile enough that we kept having
to test whether the feed was actually reachable.

### 2:50:58 PM

We split the system into a sender and a receiver. We added the Pi face sender,
the Windows receiver, and the tunnel-related support around that flow. The
problem at that point was that one machine alone was not giving us the control
we wanted, so we changed the architecture and started moving data between
systems instead of trying to do everything in one place.

### 2:52:27 PM

We were also experimenting with OpenPose around the same time. The problem at
that point was that we still wanted a stronger pose or fall-detection path,
even while the preview and sender/receiver work was already happening.

### 3:46:09 PM

We built the real Windows fallback. We added the Windows face matching flow,
Supabase path, local live preview path, and launcher behavior. The problem at
that point was risk. The Pi path alone was too fragile to be our only demo
runtime, so we made a Windows path that could carry more of the system if
needed.

### 3:48 PM

We were still talking about OpenPose and stronger perception even after the
Windows fallback existed. The problem at that point was that the product still
needed a convincing perception story, not just a stable runtime.

### 4:11:40 PM

We redesigned the Windows live runtime to make it usable in practice. We added
LAN IP discovery, JPEG helper logic, image serving over HTTP, reused detections
between frames, added frame-skipping controls like `process-every-n`, added
`detect-scale`, and wired in the Gemini description and speaker hooks. The
problem at that point was live usability. The system existed, but it was too
laggy and too rough to feel good.

### 4:12:05 PM

We standardized the default unknown label to `unidentified`. The problem at
that point was messy naming behavior once the live path started creating or
showing unknown people.

### 4:18:38 PM

We added a direct Supabase test insert script. The problem at that point was
that when something failed, we could not tell if it was the app logic, the
backend schema, the auth, or RLS. We needed a direct backend test path.

### 4:21 PM

We got the medication schedule information while the runtime was still being
debugged. The problem at that point was that the care-assistant product layer
was still growing while the infrastructure underneath it was not fully stable.

### 4:22:17 PM

We added the SwiftUI iOS app scaffold and the Next.js onboarding web app. The
problem at that point was that the product needed user-facing surfaces too, not
just perception and backend code, so we were building those in parallel.

### 4:24 PM to 4:26 PM

We were already compressing the build into pitch language while still coding.
The problem at that point was that the system had to be explainable at the same
time that it was still changing.

### 4:31:29 PM

We changed the image upload path to base64 by adding `/upload-base64` and the
helper that captures the first detected face and sends it in that form. The
problem at that point was that local file assumptions were getting in the way
of reliable transport and backend writes.

### 4:37 PM

We had a strong enough technical summary to explain the stack clearly, but we
also knew one major problem: matched known faces were not updating correctly
the way new unknown faces were. That problem drove the next series of backend
fixes.

### 4:47:51 PM

We improved the local face receiver view and added startup support. The problem
at that point was operational friction. We needed the receiver to be easier to
watch, restart, and test repeatedly.

### 5:01:02 PM

We improved face matching and preview behavior by normalizing embeddings from
Supabase and giving the browser a better local camera path. The problem at that
point was quiet compatibility and correctness issues in the Windows path, not
big architecture problems.

### 5:08:04 PM

We vendored the base64 tooling because it had become a core part of the image
path. The problem at that point was that the image transport layer was no
longer optional glue code. It was central infrastructure.

### 5:08 PM

We received `guardiancare.zip`, which was late-stage fall-detection work. The
problem at that point was that major fall-related code was still arriving while
the main live face and backend flow was still being fixed.

### 5:09:32 PM and 5:12:29 PM

We revised the README while the system was still changing. The problem at that
point was that the story and the implementation were moving at the same time,
so documentation and code were both active work.

### 5:14:34 PM

We made image-table handling more explicit and tightened unknown-face naming
again around `unidentified`. The problem at that point was that face rows and
image rows were not being handled cleanly enough yet.

### 5:21:31 PM

We changed the backend flow so matched people were treated as update targets,
not just new unknown people as inserts. The problem at that point was the one
we had already identified earlier: known faces were lagging behind unknowns in
the backend state.

### 5:24:29 PM

We pulled the earlier GuardianCare fall-detection lineage into `main`. The
problem at that point was that the project no longer had one clean line of
work. We were now carrying multiple real implementation lines at once.

### 5:33:07 PM

We kept using direct sample-image scripts to force backend behavior and make
sure unknowns registered correctly. The problem at that point was that we still
did not fully trust the live loop by itself.

### 5:36:10 PM

We added a real-time event log and telemetry status to the Windows path. The
problem at that point was visibility. We needed the app to explain what it was
doing while it was running so we could debug it faster.

### 5:39:39 PM

We tuned logging and sensitivity to reduce duplicate detections and duplicate
uploads. The problem at that point was repeated creation and repeated
processing, not missing features.

### 5:42:43 PM

We fixed a real upload control-flow bug by moving the embedding gate deeper into
the unknown-face branch and reducing cooldown. The problem at that point was
that a face could be detected and still never get uploaded because the code was
exiting too early.

### 5:44:40 PM

We added more verbose logging because the sync issues were still not fully
solved. The problem at that point was that the previous fix helped, but we
still did not trust the end-to-end upload behavior enough.

### 5:46:13 PM

We finally gave matched faces explicit backend update behavior, including image
record updates and linkage updates. The problem at that point was the exact one
we had been chasing since the mid-afternoon summary: matched users were not
updating correctly.

### 5:48:22 PM

We reached the first point where the Windows and Supabase path felt stable. The
problem at that point was less about one obvious missing fix and more about
whether the whole chain finally behaved consistently enough to trust.

### 5:49:29 PM

We improved the recognized-faces gallery so it could decode and show backend
image data correctly. The problem at that point was that backend state existed,
but it was not being shown clearly enough in the UI.

### 5:57:38 PM

We did the last big cleanup of dashboard and image semantics by stopping the
code from assuming `photo_url` was always directly usable, adding
`find_image_by_id`, and wiring the dashboard to the `images` table more
properly. The problem at that point was structural mismatch between face rows,
image rows, and what the dashboard expected.

### 9:44 PM

We started merging the active branches into `main`. The problem at that point
was preservation. We had multiple real working lines of effort and did not want
to lose any of them.

### 9:51 PM onward

We shifted into preservation mode. We rewrote the README, unpacked
`guardiancare.zip` into `guardiancare_late/`, aligned the docs with the code
history, and added the technical writeups. The problem at that point was making
sure the final repo actually reflected what we built instead of pretending the
day had been cleaner than it really was.
