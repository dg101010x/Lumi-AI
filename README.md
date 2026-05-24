# Lumi AI

**Caregiving shouldn't feel like a second job.**

Lumi AI is a care companion app for families keeping an eye on aging parents or loved ones who need a little extra support. It connects family members, simplifies coordination, and surfaces the moments that actually matter — without burying everyone in noise.

---

## The Problem

Most families cobble together a mix of group texts, phone tag, and gut instinct to manage caregiving from a distance. It works until it doesn't. Lumi exists for the moments when it doesn't.

---

## What It Does

- **Onboarding in 4 steps** — set up your family, add your loved one's info, share health context, and configure alerts. Takes about two minutes.
- **Caregiver alerts** — one tap from the home dashboard notifies the right people immediately
- **Per-caregiver calling & messaging** — reach any family member directly, right from the app
- **Activity feed** — grouped by alerts, visitors, meals & medication, and daily activity so nothing gets buried
- **Editable settings** — update caregiver or resident info anytime, changes sync instantly

---

## Tech Stack

| Layer | Technology |
|---|---|
| iOS | SwiftUI |
| Auth | Firebase Auth (email/password) |
| Data | Supabase Postgres |
| Web | Next.js (onboarding scaffold) |

---

## Repo Structure

```
.
├── ios/
│   ├── Lumi.xcodeproj/
│   └── Lumi/
│       ├── Auth/
│       ├── Components/
│       ├── Home/
│       ├── Models/
│       ├── Onboarding/
│       ├── Services/
│       ├── State/
│       ├── Supabase/
│       ├── Theme/
│       ├── Utilities/
│       └── LumiApp.swift
├── web/
├── README.md
└── prd.md
```

---

## Running It Locally

You'll need Xcode, a Firebase project, and a Supabase project.

1. Clone the repo
2. Open `ios/Lumi.xcodeproj` in Xcode
3. Drop in your `GoogleService-Info.plist` for Firebase
4. Add your Supabase credentials locally
5. Build and run

---

## Demo Path

1. Complete onboarding (Family → Resident → Health → Alerts)
2. Land on the home dashboard
3. Trigger the caregiver alert flow
4. Browse the activity feed categories
5. Edit a caregiver or resident from settings
