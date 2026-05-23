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
