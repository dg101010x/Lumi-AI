# Lumi iOS

Native SwiftUI port of the Lumi onboarding flow that lives in `../web`.

## Requirements
- Xcode 16+
- iOS 17+ deployment target

## Run
Open `Lumi.xcodeproj` in Xcode and hit ⌘R. Any iPhone simulator works (portrait only).

The project uses Xcode 16's *synchronized folder* mechanism — Swift files added under `Lumi/` are picked up automatically with no pbxproj edits needed.

## Structure
- `Lumi/LumiApp.swift` — `@main` entry; switches between `OnboardingFlow` and `CompletedView`
- `Lumi/Theme/LumiColors.swift` — palette ported from `web/app/globals.css`
- `Lumi/Models/OnboardingModels.swift` — `Codable` types mirroring `web/lib/types.ts`
- `Lumi/State/OnboardingStore.swift` — `@MainActor ObservableObject`; persists to `UserDefaults` under `lumi.onboarding` (matches the web `localStorage` key)
- `Lumi/Components/` — `LumiButton`, `LumiTextField`/`LumiTextEditor`, `LumiChip`, `LumiToggleRow`, `ProgressDots`, `FieldLabel`, `StepLayout`, `FlowLayout`
- `Lumi/Onboarding/OnboardingFlow.swift` — six-step state machine
- `Lumi/Onboarding/{Welcome,Resident,Health,Likes,Family,Alerts}Step.swift` — one per route in `web/app/onboarding/*`

## Parity notes
- Validation matches the web: welcome requires name + phone, resident requires name, health requires mobility, other steps are optional.
- Date strings use `yyyy-MM-dd`; time strings use `HH:mm`, same as the HTML `date`/`time` inputs.
- Quiet hours only persist if the user actually touched the pickers.
