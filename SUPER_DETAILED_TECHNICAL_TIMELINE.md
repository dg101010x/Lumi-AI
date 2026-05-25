# Lumi AI Super Detailed Technical Timeline

Lumi AI was our elder-care hackathon project. The idea was simple to explain
but hard to build in one day: use a camera and AI to watch a room, recognize
people, notice important events like falls, remember what happened, and support
care tasks like reminders. During the hackathon, we did not build it in one
straight line. We first tried to prove the camera and preview path, then we
made it shareable, then we split the system between devices, then we built a
Windows fallback, and then we spent a long stretch fixing how faces, images,
and Supabase data were actually syncing.

## Saturday, May 23, 2026

### 10:26 AM — Choosing the project direction

We started by talking about what kind of hackathon project would actually stand
out and feel real. At this point we were still choosing the direction, not
writing code. Problem: we did not have a locked idea yet, so everything was
still open.

### 10:34 AM — Dropping the first idea

We dropped the earlier canvas-style idea because it felt clunky and did not
have a hardware side to it. That was the first real decision that pushed us
toward the final project. Problem: our first idea did not feel strong enough
for the event.

### 10:35 AM to 10:36 AM — Choosing the hardware path

We decided that hardware was not required, but it would make the project feel
more real and more memorable, so we chose that harder path anyway. Problem:
hardware would make the build more fragile and more work, but we still wanted
it because it gave us a better demo.

### 10:37 AM — Defining Lumi AI

We said the product idea clearly for the first time: it would recognize falls
and remind you about things. That sentence basically set the rest of the day,
because now we needed room perception, reminders, and some way to track people
and events. Problem: the idea was already broad, so the scope got large very
fast.

### 10:43 AM — Expanding into care features

We were already talking about comfort features too, like supportive room
assistant behavior instead of only emergency detection. This is when the idea
started feeling more like a care companion than just a fall sensor. Problem:
the product scope was already growing before the main build even started.

### 11:17:19 AM — Starting the repo

We made the first repo commit and really started the project in code. At this
point the repo did not have the real system yet. There was no Pi runtime, no
browser preview, no face pipeline, no backend sync, and no fall-detection flow
working together. Problem: we were starting almost from zero.

### 11:34 AM — Pulling in a face-recognition reference

We brought in FamiliarAI as a reference for how to think about face detection,
matching, known faces, and unknown faces. This gave us a practical model to
copy ideas from instead of inventing the whole recognition flow from scratch.
Problem: we needed a clear recognition pattern before building our own.

### 12:45:14 PM — Building the first Pi and Limelight scaffold

We got the first Raspberry Pi and Limelight scaffold into the repo. We added
the Pi probe script, the raw Limelight viewer, the requirements file, the first
prompt file, and project notes. This was still pure proof-of-life work. We were
just trying to confirm that the Pi could discover the Limelight and read the
feed. Problem: we still did not know for sure that the camera path worked at
all.

### 12:45:28 PM — Cleaning the first Pi pass

We cleaned up Python cache files right after that first Pi pass. It was a small
step, but it showed the pace of the day: get it running first, then clean up
the repo after. Problem: the first working pass already left small repo mess.

### 1:07:07 PM — Turning the feed into a browser preview

We turned the raw Limelight stream into a browser preview by adding the web
preview bridge with a root page and an MJPEG endpoint. This was important
because a local OpenCV window was not enough for a demo or for easy testing.
Problem: we needed something easier to view and easier to share than a local
Python window.

### 1:11:45 PM — Preparing the preview for hosting

We started preparing that preview path for deployment by adding things like the
Dockerfile and `.dockerignore`. This was the point where we were already
thinking beyond local testing and toward hosting. Problem: a local-only preview
was useful, but it was not enough if other people could not reach it.

### 1:20 PM — Getting the first public stream link

We got the first public stream link working through a tunnel. That was a real
milestone because the feed was no longer trapped on one machine. Problem: as
soon as the stream became public, reliability became the new issue, because now
it had to keep working for other people too.

### 1:27:25 PM — Making the preview act like a service

We added managed services and watcher behavior around the preview and tunnel so
the stream would behave more like a real service and not just a one-off local
script. Problem: getting the feed public once was not enough if it could not
stay up.

### 1:48 PM and 1:56 PM — Rechecking public access

We were still sharing and rechecking public preview links during this part of
the day, which shows how active the stream-sharing problem still was. Problem:
public access was still fragile enough that we kept having to verify whether
the link was actually reachable.

### 2:50:58 PM — Splitting the system into sender and receiver

We split the system into a sender and a receiver. We added the Pi face sender,
the Windows receiver, and support around that path. This changed the project
from one-machine testing into a system where one device could capture data and
another could process it. Problem: one machine alone was not giving us enough
control or flexibility.

### 2:52:27 PM — Exploring OpenPose in parallel

We were also experimenting with OpenPose at the same time. That means we were
not moving in one clean line. While we were still fixing preview and
sender/receiver behavior, we were also exploring a stronger pose-based
perception path. Problem: we still wanted a better fall-detection story while
the main runtime was still being built.

### 3:46:09 PM — Building the Windows fallback

We built the real Windows fallback. We added the Windows face matching path,
Supabase support, the local live preview, and launcher behavior. This was one
of the biggest changes of the day because it meant the project no longer
depended only on the Pi path. Problem: the Pi path felt too risky to be the
only thing carrying the demo.

### 3:48 PM — Keeping the perception path alive

We were still talking about OpenPose and stronger perception even after the
Windows fallback existed. That shows we had not abandoned the perception side
just because we found a more stable runtime path. Problem: we still needed the
system to feel smart, not just stable.

### 4:11:40 PM — Redesigning the live Windows runtime

We redesigned the Windows live runtime so it would actually feel usable. We
added LAN IP discovery, JPEG helper logic, HTTP image serving, detection reuse
between frames, frame-skipping controls like `process-every-n`, `detect-scale`,
and the Gemini description plus speaker hooks. This was the part where the
Windows path stopped being just possible and started being practical. Problem:
the live system existed, but it was too laggy and rough to feel good.

### 4:12:05 PM — Cleaning up unknown-face naming

We cleaned up the default unknown-face label and changed it to
`unidentified`. This was a small change, but it mattered because the live app
was now creating and showing unknown people. Problem: the naming behavior was
messy and not clean enough for the UI or data flow.

### 4:18:38 PM — Adding direct Supabase tests

We added a direct Supabase test insert script so we could test the backend
without guessing whether a failure came from the app or the database layer.
Problem: when something broke, we could not tell if it was app logic, schema,
auth, or RLS.

### 4:21 PM — Adding real care data

We got the medication schedule while the runtime was still being debugged. This
shows the care-assistant side of the project was still growing in parallel with
the lower-level engineering work. Problem: product features were still being
added while the underlying system was not fully stable.

### 4:22:17 PM — Building the app surfaces

We added the SwiftUI iOS app scaffold and the Next.js onboarding web app. That
meant the repo was growing in two directions at once: user-facing surfaces and
backend/perception plumbing. Problem: we needed product-facing interfaces too,
not just camera and backend code.

### 4:24 PM to 4:26 PM — Tightening the pitch while coding

We were already tightening the pitch and how we would explain the system, even
while the build was still changing underneath us. Problem: we needed the
project to be explainable before it was even fully settled.

### 4:31:29 PM — Switching image upload to base64

We changed image upload to a base64 path by adding `/upload-base64` and the
helper that captures the first detected face and sends it that way. This was a
big backend change because it moved us away from weak local-file assumptions.
Problem: the original image transport path was not reliable enough for syncing
and backend writes.

### 4:37 PM — Seeing the matched-face bug clearly

By this point we could clearly explain the technical stack, but we also knew
the biggest live bug we still had: matched known faces were not updating the
same way new unknown faces were. Problem: the backend path handled new faces
better than already-known ones.

### 4:47:51 PM — Making the receiver easier to run

We improved the local face receiver view and added startup support. This made
the receiver easier to inspect, restart, and test over and over. Problem: the
receiver path still had too much friction for repeated live testing.

### 5:01:02 PM — Fixing quieter matching issues

We improved face matching and preview behavior by normalizing embeddings coming
back from Supabase and giving the browser a better local camera path. These
were quieter fixes, but they mattered because the Windows path was now failing
in more subtle ways instead of only obvious ones. Problem: compatibility and
correctness issues were still hurting the live path.

### 5:08:04 PM — Treating base64 as core infrastructure

We vendored the base64 tooling because the image path depended on it heavily by
this point. That shows how important image transport had become to the whole
system. Problem: base64 handling was no longer just a helper detail, it was now
part of the core pipeline.

### 5:08 PM — Receiving the late fall-detection bundle

We received `guardiancare.zip`, which was late-stage fall-detection work. This
meant a major perception artifact was still arriving while the face and backend
path was still being fixed. Problem: important fall-detection code was showing
up late, while the main live system was still unstable.

### 5:09:32 PM and 5:12:29 PM — Updating the story while building

We revised the README while code was still changing. That shows the story and
the implementation were moving at the same time. Problem: documentation could
not wait until the end because the pitch story also needed work.

### 5:14:34 PM — Tightening image and face row handling

We made image-table handling more explicit and tightened unknown-face naming
again around `unidentified`. This was another step toward making the face rows
and image rows behave more cleanly together. Problem: image and face data were
still not connected in a clean enough way.

### 5:21:31 PM — Updating matched people instead of only creating new ones

We changed the backend flow so matched people were treated as update targets,
not just new unknown people as inserts. This was a direct response to the bug
we had already identified earlier. Problem: known faces were falling behind
unknown faces in the backend state.

### 5:24:29 PM — Pulling in the earlier fall-detection line

We pulled the earlier GuardianCare fall-detection lineage into `main`. At this
point the repo clearly had multiple real technical lines in it at once. Problem:
the project no longer had one clean implementation path, so preserving all the
real work became part of the job.

### 5:33:07 PM — Forcing backend tests with sample images

We kept using direct sample-image scripts to force backend behavior and make
sure unknown faces registered correctly. This shows we still did not trust the
live loop by itself. Problem: the live app alone was not enough to prove the
backend was behaving correctly.

### 5:36:10 PM — Adding telemetry to the live app

We added a real-time event log and telemetry status to the Windows path. This
made the app tell us what it was doing while it was running instead of leaving
us to guess. Problem: we needed better visibility into the system while live
debugging it.

### 5:39:39 PM — Reducing duplicate detections and uploads

We tuned logging and sensitivity to reduce duplicate detections and duplicate
uploads. This part of the work was about making the live loop calmer and less
wasteful. Problem: repeated detection and repeated creation were causing noisy
behavior.

### 5:42:43 PM — Fixing the upload control-flow bug

We fixed a real upload control-flow bug by moving the embedding gate deeper into
the unknown-face branch and reducing cooldown. Before this, a face could be
detected and still never get uploaded because the code could exit too early.
Problem: the upload path was being skipped even when detection worked.

### 5:44:40 PM — Adding more logging to chase sync issues

We added more verbose logging because the sync issues still were not fully
settled. That meant the previous fix helped, but it was not the end of the
problem. Problem: we still did not trust the end-to-end sync enough.

### 5:46:13 PM — Fixing matched-face updates in Supabase

We finally gave matched faces explicit backend update behavior, including image
updates and linkage updates. This was the real fix for the bug we had been
chasing since the mid-afternoon summary. Problem: matched users were still not
updating correctly in Supabase.

### 5:48:22 PM — Reaching the first stable Windows path

We reached the first point where the Windows and Supabase path felt stable as a
whole. By now we had base64 transport, direct backend tests, better logging,
duplicate suppression, upload fixes, and matched-face updates all working
together better. Problem: the remaining issue was no longer one obvious bug, it
was whether the whole chain could be trusted consistently.

### 5:49:29 PM — Making backend images visible in the gallery

We improved the recognized-faces gallery so it could decode and show backend
image data correctly. This mattered because it turned backend state into
something we could actually see in the UI. Problem: even when the backend had
data, the UI still was not showing it clearly enough.

### 5:57:38 PM — Cleaning up dashboard image semantics

We did the last big cleanup of dashboard and image semantics by stopping the
code from assuming `photo_url` was always directly usable, adding
`find_image_by_id`, and wiring the dashboard to the `images` table more
properly. Problem: the face rows, image rows, and dashboard assumptions still
did not line up cleanly.

### 9:44 PM — Merging the active branches

We started merging the active branches into `main`. By then, the goal was no
longer just to keep building. It was also to make sure we did not lose any of
the real work from the different paths. Problem: we had multiple working lines
of effort and needed to preserve them together.

### 9:51 PM onward — Shifting into preservation mode

We shifted into preservation mode. We rewrote the README, unpacked
`guardiancare.zip` into `guardiancare_late/`, aligned the docs with the code
history, and added the technical writeups. Problem: we needed the final repo to
honestly show what we built and what actually happened, instead of pretending
the day had been cleaner than it really was.
