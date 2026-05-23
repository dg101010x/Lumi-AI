import SwiftUI

enum OnboardingStep: Int, CaseIterable {
    case family, resident, health, alerts

    var next: OnboardingStep? { OnboardingStep(rawValue: rawValue + 1) }
    var previous: OnboardingStep? { OnboardingStep(rawValue: rawValue - 1) }
}

struct OnboardingFlow: View {
    @State private var step: OnboardingStep = .family

    var body: some View {
        ZStack {
            switch step {
            case .family:
                FamilyStep(onNext: advance)
            case .resident:
                ResidentStep(onNext: advance, onBack: back)
            case .health:
                HealthStep(onNext: advance, onBack: back)
            case .alerts:
                AlertsStep(onBack: back)
            }
        }
    }

    private func advance() {
        if let next = step.next {
            withAnimation(.easeInOut(duration: 0.2)) { step = next }
        }
    }

    private func back() {
        if let prev = step.previous {
            withAnimation(.easeInOut(duration: 0.2)) { step = prev }
        }
    }
}
