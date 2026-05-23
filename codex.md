# AegisAI Repo Notes

## Active branch
- `windows-face-supabase-match`

## Scope for this branch
- Windows receiver for Pi face uploads.
- Supabase-backed face matching against `known_faces`.
- Pi sender based on `face_recognition`.
- Windows-only webcam stack with no Raspberry Pi dependency.

## Immediate goal
Support two face paths:
- Pi sender -> Windows receiver -> Supabase matching
- Windows webcam -> local matching against Supabase with no Pi

## Demo priorities
1. Windows receiver loads known face embeddings from Supabase.
2. Pi sender uploads face embeddings and annotated frames.
3. Matching works against the real project schema, not the FamiliarAI demo schema.
4. Windows-only local webcam path works when the camera is plugged into this PC.

## Current repo state
- Raw Limelight preview path already exists on another branch lineage.
- This branch adds a face sender/receiver path and real Supabase matching.

## User ownership note
- User asked for the Windows side plus matching from Supabase project `gmmpltgvtonpnrfckrvy.supabase.co`.
- Actual public face table discovered by live probing is `known_faces`.

## Current blocker
- The previously used Supabase publishable key shown in `README.md` no longer authorizes REST writes. A direct `POST` test on 2026-05-23 returned `401 Unauthorized`.
- Added `scripts/insert_test_face_to_supabase.ps1` to generate a simple face PNG, encode it as a base64 data URL, and insert a test row once a valid key is supplied through `SUPABASE_PUBLISHABLE_KEY` or `-ApiKey`.

## Localhost receiver status
- `windows/face_receiver.py` now serves a simple root page at `/` and health JSON at `/healthz`.
- The receiver also accepts JSON base64 uploads at `/upload-base64` in addition to multipart `/upload`.
- `windows/send_first_face_base64.py` captures the first detected webcam face, base64-encodes the crop, and posts it to `/upload-base64`.

## Supabase schema and auth facts
- `known_faces` accepts rows with `embedding`, `person_name`, `label`, and `photo_url`.
- `images` accepts rows with `image_name` and `image_url`.
- The publishable key can read enough for the receiver to start, but direct REST writes to `known_faces` fail under RLS.
- A service-role key was provided on 2026-05-23 and successfully used for verified inserts into both `known_faces` and `public.images`.
- Do not store the raw service-role key in repo files; keep it in environment variables or local untracked secrets only.

## Verified inserts on 2026-05-23
- Inserted base64 `data:image/png;base64,...` rows into `known_faces` with random test names and verified they could be read back.
- Inserted base64 `data:image/png;base64,...` rows into `public.images` using `image_name` and `image_url`, and verified those rows could be read back.
