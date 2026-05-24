# Lumi AI

Lumi AI is an AI care companion that helps families monitor, support, and respond when a loved one may need attention.

## Overview

Lumi AI is built as a caregiving product with a native iOS app and a companion web onboarding experience. The current repository includes a SwiftUI iOS app, Firebase Authentication for identity, and Supabase for application data and state management.

## Features

- 4-step onboarding flow covering Family, Resident, Health, and Alerts
- Email/password authentication with Firebase Auth
- Supabase-backed app data with authenticated access control
- Home dashboard with a prominent “Alert caregivers” action
- Per-caregiver calling and messaging support
- Activity feed grouped by alerts, visitors, meals & medication, and daily activity
- Editable caregiver and resident settings with live write-through updates

## Tech Stack

- **iOS:** SwiftUI
- **Authentication:** Firebase Auth
- **Backend/Data:** Supabase Postgres
- **Web:** Next.js onboarding scaffold

## Repository Structure

```text
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

## Getting Started

### Prerequisites

- Xcode
- A Firebase project
- A Supabase project

### Setup

1. Clone the repository.
2. Open `ios/Lumi.xcodeproj` in Xcode.
3. Add your local `GoogleService-Info.plist` file for Firebase configuration.
4. Configure Supabase credentials locally.
5. Build and run the iOS app.

## Demo Flow

A good demo path is:

1. Complete onboarding
2. Enter the home dashboard
3. Trigger the caregiver alert flow
4. Show the activity feed categories
5. Edit caregiver or resident settings

## Why it matters

Caring for loved ones from a distance is stressful. Lumi AI is designed to make caregiving more proactive, connected, and actionable through alerts, communication tools, and a structured family dashboard.

## Current Status

This repository already contains the core app structure, onboarding flow, caregiver communication actions, and settings management. The next improvements are polishing the README further with screenshots, a short architecture diagram, and a demo video link.

## Security Note

Do not commit production secrets or live config files to the public repository. Keep Firebase and backend credentials in local-only configuration or secure environment management.
