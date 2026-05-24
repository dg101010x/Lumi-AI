import SwiftUI

private let commonConditions = [
    "Dementia",
    "Alzheimer's",
    "Parkinson's",
    "Diabetes",
    "Heart condition",
    "High blood pressure",
    "Arthritis",
    "Stroke history",
    "Vision impairment",
    "Hearing impairment",
]

private struct MobilityOption {
    let value: Mobility
    let label: String
    let description: String
}

private let mobilityOptions: [MobilityOption] = [
    .init(value: .independent, label: "Independent", description: "Walks without aid"),
    .init(value: .walker, label: "Uses a walker or cane", description: "Walks with support"),
    .init(value: .wheelchair, label: "Uses a wheelchair", description: "Mostly seated"),
    .init(value: .bed, label: "Mostly bed-bound", description: "Limited movement"),
]

struct HealthStep: View {
    @EnvironmentObject var store: OnboardingStore
    let onNext: () -> Void
    let onBack: () -> Void

    @State private var conditions: Set<String> = []
    @State private var mobility: Mobility? = nil

    private var canProceed: Bool { mobility != nil }

    var body: some View {
        StepLayout(
            step: 3,
            total: 4,
            title: "Health and mobility",
            subtitle: "Helps Lumi know what to watch for and how to respond.",
            canProceed: canProceed,
            onNext: handleNext,
            onBack: onBack
        ) {
            FieldLabel(title: "Any conditions? Select all that apply.") {
                FlowLayout(spacing: 8) {
                    ForEach(commonConditions, id: \.self) { condition in
                        LumiChip(label: condition, selected: conditions.contains(condition)) {
                            toggle(condition)
                        }
                    }
                }
            }

            FieldLabel(title: "Mobility") {
                VStack(spacing: 8) {
                    ForEach(mobilityOptions, id: \.value) { opt in
                        MobilityRow(option: opt, selected: mobility == opt.value) {
                            mobility = opt.value
                        }
                    }
                }
            }
        }
        .onAppear {
            conditions = Set(store.state.health.conditions)
            mobility = store.state.health.mobility
        }
    }

    private func toggle(_ condition: String) {
        if conditions.contains(condition) {
            conditions.remove(condition)
        } else {
            conditions.insert(condition)
        }
    }

    private func handleNext() {
        store.state.health = Health(
            conditions: commonConditions.filter { conditions.contains($0) },
            mobility: mobility
        )
        onNext()
    }
}

private struct MobilityRow: View {
    let option: MobilityOption
    let selected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 4) {
                Text(option.label)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                Text(option.description)
                    .font(.system(size: 14, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(16)
            .background(.white)
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(selected ? LumiColors.slate400 : LumiColors.slate100, lineWidth: selected ? 2 : 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}
