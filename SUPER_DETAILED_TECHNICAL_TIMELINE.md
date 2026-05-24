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

This file is a strict chronological event log. It is not grouped by topic
first. Each entry starts with the event time and then explains what technically
happened, what code changed, what branch carried that work, and why that moment
mattered. The timeline is built from exact git commit timestamps, the merged
branch graph, diff contents, and the downloaded Discord export.

Branch names matter in this timeline, so here is the short key up front.
`main` starts as the product shell and later becomes the merge-and-preservation
branch. `raw-limelight-feed` is the Pi stream, preview, and tunnel branch.
`windows-face-supabase-match` is the Windows webcam, face recognition, and
Supabase branch. `pi-limelight-orchestrator` ends up carrying the latest
dashboard and Supabase hardening despite its Pi-heavy name. `openpose-pose-
integration` is an exploration branch with stash evidence rather than a fully
landed line of work.

## Saturday, May 23, 2026

### 10:26 AM — Discord — Track and idea positioning starts

The first meaningful event in the exported chat is not code, it is team
positioning. Messages like `about these tracks` and `and any ideas they might
have` show that before implementation really started, the team was already
optimizing for the hackathon environment rather than only for abstract product
fit. That matters technically because the later repo structure only makes sense
if you understand that the system had to be both real and stage-worthy. The
team was not just asking “what can we build,” but “what technical shape gives us
the best chance to stand out.”

### 10:34 AM — Discord — The earlier non-hardware direction gets rejected

The next key event is the rejection of the earlier `canvas idea`, with follow-up
messages calling it a `Clunky school interface` and pointing out it had `no
hardware component`. This is the first real architecture decision of the day
even though it appears only in chat. Once that decision is made, the project is
effectively committed to camera IO, edge-device uncertainty, networking
problems, and the possibility of a much messier implementation path. A purely
software dashboard project would not have created the later split between Pi
preview work, Windows fallback work, and preserved fall-detection prototypes.

### 10:35–10:36 AM — Discord — Hardware becomes a differentiation strategy

The hardware question gets made explicit right after that. The team notes that
`there's barely anyone with hardware`, asks whether hardware is even required,
gets the answer `no`, and then immediately reframes that as `but its how we
win`. Technically, this is one of the most important moments of the day because
it creates the central design tension that never goes away: hardware is wanted
for differentiation, but because it is optional, the team must keep a fallback
in reserve in case the hardware path becomes too fragile. That exact tension is
what later produces the Pi path and the Windows fallback path in parallel rather
than one neat implementation line.

### 10:37 AM — Discord — The core product behavior gets stated clearly

At `10:37 AM`, the project gets its first compact functional definition in chat:
`So it will recognize falls and remind you stuff`. That sentence is technically
more important than it looks. It already implies at least three subsystems:
perception for falls or room-state changes, identity or resident-awareness for
knowing who the person is, and reminder or interaction logic for follow-up
behavior. The later breadth of the repo is not accidental sprawl; it is a
direct consequence of this early product sentence being broader than a single
computer-vision demo.

### 10:43 AM — Discord — Care experience expands beyond pure detection

Very shortly after that, the conversation includes the idea of adding
entertainment, music, or comfort-oriented behavior. That means the product scope
was never just “detect an emergency.” Even before the first substantial commit,
Lumi AI was being framed as a room assistant, not merely a sensor. This is why
the repo later contains caregiver-facing app shells, Gemini prompt work, med
schedule context, and room-intelligence language rather than only bare detection
code.

### 11:17:19 AM — Git — `f5c4e7d` — Initial commit lands on `main`

The first git event is the initial commit on `main`. Technically, almost nothing
exists yet beyond the repo skeleton, but this timestamp matters because it marks
the start of same-day code acceleration. There is still no real hardware path,
no preview stack, no backend identity path, and no fall-detection runtime. That
absence is important because the later branch complexity developed within only a
few hours from this starting point.

### 11:34 AM — Discord — FamiliarAI reference enters the conversation

By `11:34 AM`, the team is already passing around a FamiliarAI reference. That
means recognition was not being invented in a vacuum. The team was actively
looking at another architecture for face detection, matching, and known-versus-
unknown handling. This matters later when the Windows/Supabase path appears,
because it shows that the repo’s face logic sits inside a wider comparison space
of possible recognition patterns, not just a one-off implementation choice.

### 12:45:14 PM — Git — `3a3f618` — The first real Pi/Limelight scaffold lands on `main`

The first serious implementation commit arrives at `12:45:14 PM` with
`3a3f618`, which adds `pi/limelight_probe.py`, `pi/limelight_video_viewer.py`,
`requirements.txt`, the early Gemini prompt file, and the first project notes.
Technically, this is still a direct hardware-proof phase. The code is trying to
discover the Limelight, probe candidate endpoints, and open the raw stream in
OpenCV. There is no browser preview yet, no public shareability, no Supabase
identity model, and no integrated fall-detection runtime. The team is still
proving that the room camera path exists at all.

### 12:45:28 PM — Git — `a4c9fa3` — Repo hygiene correction after the first scaffold

Only seconds later, `a4c9fa3` cleans up a committed Python cache artifact. This
is minor functionally, but it tells you something about the pace of the day.
The first implementation pass was run immediately, generated local artifacts,
and then got cleaned up after. It is a small but honest signal that the first
priority was to make the Pi work, not to keep the repo perfectly curated from
the first minute.

### 1:07:07 PM — Git — `a220cf9` — Raw stream access becomes browser preview

At `1:07 PM`, `a220cf9` adds `pi/limelight_web_preview.py` and expands the
viewer path so the project moves from opening a raw stream locally to serving a
browser-visible preview through an HTTP bridge. This is the first moment the
code stops being only a developer-side camera tool and starts becoming a demo
surface. The root page, MJPEG proxy path, and preview-serving logic mean the
system can now be shown through a browser instead of only through an OpenCV
window on the dev machine. What is still not solved is durability and
reachability: the preview is local, not yet a robust public demo endpoint.

### 1:11:45 PM — Git — `63b6a42` — Cloud Run preparation appears

Just a few minutes later, `63b6a42` adds `Dockerfile` and `.dockerignore` and
reshapes the preview path into something that can theoretically be deployed. The
important technical shift here is not model logic but deployment shape. The
problem has already moved from “can the Pi read the stream” to “can this be
hosted somewhere useful.” This commit later becomes the base for both
`raw-limelight-feed` and `openpose-pose-integration`, so it is effectively the
branch split point where the code has a preview server but has not yet decided
whether the next big fight will be public reachability, stronger perception, or
fallback runtime strategy.

### 1:20 PM — Discord — First public stream URL is shared

At `1:20 PM`, the Discord export shows `https://calm-crabs-relate.loca.lt/stream.mjpg`
being shared. That means the public-preview problem is no longer theoretical.
There is now a real tunnel-backed path from the local camera source to a public
URL. Technically, this is huge because it shows the system has crossed a full
stack boundary: local source, local preview server, tunnel, public endpoint.
But it also exposes a new category of fragility. Once the preview is public,
the team now has to care about tunnel stability, source reachability, and
whether a cloud-hosted or tunneled path is reliable enough to use in front of
judges.

### 1:27:25 PM — Git — `c9e0f2f` — Preview and tunnel get operational support

By `1:27 PM`, `c9e0f2f` adds systemd services and watcher scripts for the
preview and localtunnel stack. This is an operationalization event, not a
computer-vision event. A working preview existed, but that was already not
enough; it had to stay alive, restart correctly, and behave like a service
rather than a fragile one-shot script. This commit reveals that the preview
problem had become a subsystem in its own right.

### 1:48 PM and 1:56 PM — Discord — More public preview links are shared

The Discord export shows `https://puny-houses-rest.loca.lt/` being shared at
`1:48 PM` and then repeated at `1:56 PM`. The repetition matters. It suggests
that public preview reachability was still being actively checked and circulated
as a live dependency. At this point in the day, the project is still centered
more on “can people see the video at all” than on “does the identity stack tell
the truth.”

### 2:50:58 PM — Git — `7aeebc1` — The sender/receiver architecture appears on `origin/raw-limelight-feed`

At `2:50:58 PM`, `7aeebc1` lands on `origin/raw-limelight-feed` and changes the
architecture meaningfully. It adds `pi/face_capture_sender.py`,
`windows/face_receiver.py`, ngrok service support, and related scripts. The Pi
is no longer only a preview device. It can now capture or forward face-related
data while another machine can receive and process it. This is the first truly
distributed architecture moment in the repo. The team is no longer assuming all
useful intelligence must live on the Pi itself.

### 2:52:27 PM — Git stash — `openpose-pose-integration` is an active experiment

Only about two minutes later, the stash entry on `openpose-pose-integration`
shows `wip openpose overlay`. Even though it did not land as a normal branch
head commit, this is critical evidence. By mid-afternoon, preview work,
sender/receiver splitting, and stronger pose/perception exploration were all
happening at once. OpenPose was not a hypothetical idea remembered later. It
was an active same-day technical exploration path.

### 3:46:09 PM — Git — `04927dd` — The Windows fallback becomes a real full-stack runtime

At `3:46 PM`, `04927dd` lands on `windows-face-supabase-match` and is the
biggest architecture pivot in the entire repo. It adds the main Windows face
matching, Supabase, live preview, and launcher files: `windows/face_matching.py`,
`windows/supabase_known_faces.py`, `windows/webcam_supabase_live.py`,
`windows/webcam_supabase_match.py`, `windows/lumiai.ps1`, and the install
scripts around them. From this point on, the repo stops being primarily “Pi
preview plus ideas” and becomes “two competing runtime centers”: the Pi /
Limelight path and a Windows webcam path that can potentially carry the whole
demo on one machine. The unresolved problems at this exact moment are live-view
stability, unknown naming semantics, image transport semantics, and matched-face
update behavior.

### 3:48 PM — Discord — OpenPose gets shared explicitly after the Windows fallback already exists

The OpenPose GitHub link is shared in Discord at `3:48 PM`, after the Windows
fallback branch already exists. That timing matters. It proves the team did not
stop looking for stronger perception routes just because a workable fallback had
appeared. The day is now truly running two loops in parallel: demo survivability
through the Windows path and deeper perception exploration through OpenPose and
other pose/fall ideas.

### 4:11:40 PM — Git — `8e963d5` — The Windows live runtime gets re-architected for usability

At `4:11:40 PM`, `8e963d5` lands and substantially redesigns the live Windows
runtime. The diff is not a tiny fix. It adds LAN IP discovery, JPEG helper
logic, `/images/<filename>` serving, detection reuse across frames, `--process-
every-n`, `--detect-scale`, a faster streaming cadence, and hooks for Gemini
description plus Windows speech. Technically, this is the moment the Windows
runtime stops being merely “possible” and starts being tuned for lower latency,
better operator ergonomics, and easier LAN viewing from other devices. It tells
us the earlier Windows live view worked, but it was too laggy or awkward to
trust as-is.

### 4:12:05 PM — Git — `cf5dd81` — Unknown naming gets standardized

Only seconds later, `cf5dd81` standardizes the default unknown person name to
`unidentified`. This is a small diff but an important semantic event. It shows
that once the live Windows path existed, the project immediately ran into data-
model cleanliness issues. The runtime was there, but the identity layer was not
yet semantically stable.

### 4:18:38 PM — Git — `3c07a54` — Direct Supabase insert testing becomes necessary

At `4:18 PM`, `3c07a54` adds a dedicated Supabase insert test script. That means
backend correctness had become uncertain enough that the team needed a direct
probe. The live app no longer provided enough confidence by itself. A failure
could now mean bad logic, bad auth, wrong row shape, wrong table assumption, or
RLS rejection. This script exists to separate those causes.

### 4:21 PM — Discord — Real medication data arrives while the runtime is still being debugged

The med schedule appears in Discord at `4:21 PM`. Technically, this matters
because it proves the product scope had not collapsed into just camera and
backend debugging. Even as runtime fixes were landing, the team was still
feeding in actual elder-care product data. Lumi AI remained a care assistant
idea, not only a CV pipeline.

### 4:22:17 PM — Git — `c3d7038` — Caregiver iOS/web shell lands on `main`

At `4:22 PM`, `c3d7038` lands on `main` and adds the SwiftUI iOS app scaffold
and the Next.js onboarding web app. This is technically important because it
shows the repo developing on two tracks at once. While one branch was hardening
runtime, identity, and sync, `main` was receiving the product-facing shell that
would make the system explainable and demoable as a caregiver product.

### 4:24–4:26 PM — Discord — Pitch framing gets refined while engineering continues

Around `4:24–4:26 PM`, the Discord export shows pitch-language work kicking in.
This means technical compression was now a live requirement: the team needed to
keep changing the system while also being able to describe it confidently. That
constraint matters because some of the late commits are not just engineering
stabilization; they are also about making the architecture coherent enough to be
spoken aloud.

### 4:31:29 PM — Git — `b4cff0d` — Image transport pivots toward base64

At `4:31 PM`, `b4cff0d` lands and changes the image transport story in a serious
way. The receiver gains `/upload-base64`, and the helper
`windows/send_first_face_base64.py` appears. This is the moment the system
starts moving away from relying only on local file paths or multipart-only
assumptions and begins using JSON plus base64 payloads for image movement. That
shift becomes one of the main backend themes of the rest of the day.

### 4:37:53 PM — Discord — Live technical self-assessment captures a real limitation

At `4:37 PM`, the Discord export contains the most valuable technical checkpoint
of the day. The stack is summarized live as edge CV on Raspberry Pi plus Windows
webcam, `face_recognition`, Supabase `known_faces`, MJPEG over Flask, unknown
auto-insert, and Gemini naming support. But the message also points out a real
limitation at that exact moment: matched known faces were not yet getting their
latest image updated the way unknown faces were. That observation becomes a
perfect anchor for reading the next sequence of commits.

### 4:47:51 PM — Git — `eb9bc05` — Receiver becomes a more visible local surface

At `4:47 PM`, `eb9bc05` improves the local face receiver view and adds startup
support. This is a toolability event. The receiver is becoming something the
team can inspect, restart, and operate more easily in repeated test cycles. The
project is maturing operationally, not just functionally.

### 5:01:02 PM — Git — `2337100` — Supabase embedding compatibility and browser-camera UX improve

At `5:01 PM`, `2337100` lands and fixes two subtle but important issues. First,
`supabase_known_faces.py` gains embedding normalization so embeddings loaded from
Supabase can be interpreted correctly even if they arrive in inconsistent
formats. Second, `face_receiver.py` gains a browser-camera path so the browser
can own local camera preview. This commit is both a data-compatibility fix and
a latency/usability improvement, and it shows the team was now refining the
Windows path at the level of quiet correctness problems rather than only broad
architecture.

### 5:08:04 PM — Git — `dd5a198` — Base64 handling gets standardized enough to vendor

At `5:08 PM`, `dd5a198` adds vendored base64 tooling and a Python helper. This
is an important signal that base64 is no longer being treated like a temporary
hack. Image transport and storage have become central enough to standardize the
encoding layer itself.

### 5:08 PM — Discord — `guardiancare.zip` is shared

At almost exactly the same time, the Discord export shows `guardiancare.zip`
being shared. This is the late-stage fall-detection handoff. Technically, it is
one of the strongest proofs that the project still had multiple serious centers
right up to the end. While the Windows/Supabase branch was intensifying around
image semantics and backend truth, late fall-detection work was still being
delivered into the team’s flow.

### 5:09:32 PM and 5:12:29 PM — Git — Documentation revisions happen while deep engineering is still active

The README revisions at `5:09 PM` and `5:12 PM` show the team simultaneously
hardening the system and clarifying how to talk about it. This is a hackathon
reality signal: narrative stabilization and engineering stabilization were
happening in parallel, not sequentially.

### 5:14:34 PM — Git — `78f28eb` — Supabase image records get a more explicit update model

At `5:14 PM`, `78f28eb` adds explicit image-table operations such as
`insert_image_base64`, `find_image_by_url`, `update_image_by_id`, and
`update_known_face_photo`. This is the first mature attempt to make backend
image lifecycle behavior coherent. It is also where unknown-face naming is
tightened further around `unidentified`. The important nuance is that even after
this commit, the project was still not fully clean on what `photo_url` meant in
every context. That semantic issue survives into the later hardening commits.

### 5:21:31 PM — Git — `349ce49` — Existing matches start being treated as update targets

At `5:21 PM`, `349ce49` explicitly pushes the system toward updating matched
users instead of only inserting unknowns forever. This is the correct technical
direction after the `4:37 PM` Discord self-assessment. But it is not yet the
final answer, because the later commits prove the matched-face update behavior
still was not completely correct.

### 5:24:29 PM — Git — `39f6c42` — GuardianCare fall-detection lineage enters `main`

At `5:24 PM`, `39f6c42` imports the earlier GuardianCare code into `main`. That
brings in `guardiancare/fall_detection.py`, `guardiancare/face_recognition_module.py`,
`guardiancare/main.py`, and associated iOS/web shells. This is not cleanup. It
is another major product lineage entering the repo during the active
implementation window. By this moment, Lumi AI’s technical history is
definitively not linear. It contains the Pi preview path, the Windows fallback
path, and the GuardianCare integrated prototype path all on the same day.

### 5:33:07 PM — Git — `ae0cf6c` — Direct sample-image upload proving continues

At `5:33 PM`, `ae0cf6c` adds scripts around uploading a sample image and
ensuring unknowns register correctly in Supabase. This is another proof that the
team did not fully trust the live loop by itself. Controlled artifacts and
direct scripts were still necessary to verify backend writes.

### 5:36:10 PM — Git — `0238dc7` — Real-time event log and telemetry appear

At `5:36 PM`, `0238dc7` adds a real-time event log and telemetry status to the
Windows dashboard path. Technically, this means the problem had changed from “we
need more features” to “we need the app to explain where it is failing.” This
is a serious maturity step in the runtime because it gives the team internal
visibility into a multi-stage pipeline.

### 5:39:39 PM — Git — `436ab6b` — Duplicate suppression and logging get tightened

At `5:39 PM`, `436ab6b` tunes thresholds and recent-face parameters to reduce
duplicates while also expanding event logging. The matching threshold drops, the
recent-distance threshold tightens, and the recent window expands. This says
something precise about the system’s behavior at this time: duplicate face
creation or repeated processing had become a live pain point, and the team was
tuning application behavior rather than only fixing syntax or auth.

### 5:42:43 PM — Git — `9ced36a` — A real control-flow bug in uploads gets fixed

At `5:42 PM`, `9ced36a` fixes one of the clearest actual logic flaws in the
repo. Before this commit, a face could be detected but still fail to upload
because control flow exited too early before the crop was encoded and sent. The
diff moves the embedding gate deeper into the unknown-face branch and reduces
cooldown. This is a true pipeline bug fix, not just a configuration tweak.

### 5:44:40 PM — Git — `ad6a6f9` — More logging means the previous fix was not enough

At `5:44 PM`, `ad6a6f9` adds verbose logging immediately after the upload
control-flow fix. That timing is important. It proves the previous fix helped,
but Supabase sync still was not stable enough to trust. The team was still
actively diagnosing rather than declaring victory.

### 5:46:13 PM — Git — `d6dd6f3` — Matched-face updates get explicit backend logic

At `5:46 PM`, `d6dd6f3` finally adds explicit matched-face update behavior:
logging matches, attempting image updates for matched users, falling back to new
image records when necessary, and updating face-photo linkage afterwards. This
is the clearest direct answer to the earlier Discord note that matched users
were weaker than unknown insertions in backend update behavior.

### 5:48:22 PM — Git — `e233891` — Windows/Supabase sync reaches a “stable” milestone

At `5:48 PM`, the branch declares itself stable with `e233891`. That statement
is credible only because of the sequence immediately before it: base64
transport, direct backend tests, telemetry, duplicate suppression tuning,
upload-control-flow repair, and matched-face update logic are all already in
place. This is the first point where the Windows fallback can honestly be read
as a converged runtime path rather than only an emergency backup.

### 5:49:29 PM — Git — `78f7a8a` — Gallery rendering is improved on the remote branch head

At `5:49 PM`, `78f7a8a` improves gallery rendering by decoding backend-stored
base64 image data for display. The project is now moving from merely writing
state to rendering state meaningfully.

### 5:57:38 PM — Git — `9484893` — Final major hardening: dashboard semantics become more backend-correct

At `5:57 PM`, `9484893` lands on `origin/pi-limelight-orchestrator` even though
its content is really the final major Windows/Supabase dashboard hardening. The
diff adds `find_image_by_id`, stops assuming `photo_url` is always directly
usable as a URL, and fetches actual image content from the `images` table by id
for dashboard rendering. This is the semantic cleanup endpoint of the day. It
fixes a structural mismatch between face rows, image rows, and gallery
assumptions. It is also a good example of branch naming no longer matching
subsystem ownership cleanly; by this point, the engineering work had outrun the
branch taxonomy.

### 9:44 PM — Git — Merge phase begins on `main`

At `9:44 PM`, `main` starts absorbing the active branches through merge commits.
This is not only a repo-management step. It is a technical preservation
decision. The project is choosing not to throw away either the Pi preview line
or the Windows/Supabase line simply because the demo centered more on one than
the other.

### 9:51 PM onward — Git — Documentation and artifact preservation become the final engineering task

From `9:51 PM` onward, the remaining work is preservation: rewriting the README,
unpacking `guardiancare.zip` into `guardiancare_late/`, aligning the docs to the
Discord timeline and commit history, and later adding technical writeups. By
this phase, the hackathon implementation day is effectively over. The
engineering task becomes making sure the real technical story, branch meaning,
and late artifact work do not get lost.

## Final reading of the day

Read strictly as an event log, the day evolves like this. The team first picks
an elder-care assistant idea and explicitly chooses hardware as a differentiator.
The Pi/Limelight path then proves raw room-camera access. That quickly turns
into a browser preview problem, and then into a public reachability problem. The
sender/receiver split appears, and then the Windows fallback becomes a real
alternate runtime because the Pi path is too risky to be the only demo center.
Once that fallback exists, the technical battle shifts toward backend truth:
image transport becomes a base64 problem, telemetry becomes necessary, duplicate
suppression gets tuned, matched-face update correctness becomes a central bug
class, and dashboard semantics are finally cleaned up against real Supabase
state. In parallel, fall-detection work never disappears; it survives both in
the earlier GuardianCare import and the late `guardiancare.zip` handoff. The
end of the night is not about new subsystems. It is about preserving all of
those lines honestly instead of pretending the project ever had only one clean
implementation path.
