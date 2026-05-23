import SwiftUI

private struct CaregiverRow: Identifiable, Equatable {
    let id = UUID()
    var name: String = ""
    var phone: String = ""
    var relationship: String = ""
}

struct FamilyStep: View {
    @EnvironmentObject var store: OnboardingStore
    let onNext: () -> Void
    var onBack: (() -> Void)? = nil

    @State private var rows: [CaregiverRow] = [CaregiverRow(), CaregiverRow()]

    var body: some View {
        StepLayout(
            step: 1,
            total: 4,
            title: "Add family caregivers",
            subtitle: "They'll get a text the moment something needs attention.",
            canProceed: true,
            showBack: onBack != nil,
            onNext: handleNext,
            onBack: onBack
        ) {
            VStack(spacing: 16) {
                ForEach(Array(rows.enumerated()), id: \.element.id) { index, _ in
                    rowCard(index: index)
                }
            }
        }
        .onAppear {
            if !store.state.family.isEmpty {
                let restored = store.state.family.map { member in
                    CaregiverRow(
                        name: member.name ?? "",
                        phone: member.phone,
                        relationship: member.relationship ?? ""
                    )
                }
                rows = restored.count >= 2 ? restored : restored + Array(repeating: CaregiverRow(), count: 2 - restored.count)
            }
        }
    }

    private func rowCard(index: Int) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("Caregiver \(index + 1)")
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(LumiColors.slate600)
                .padding(.bottom, 12)

            FieldLabel(title: "Name") {
                LumiTextField(
                    placeholder: "Sarah Chen",
                    text: $rows[index].name,
                    textContentType: .name,
                    autocapitalization: .words
                )
            }

            FieldLabel(title: "Phone") {
                LumiTextField(
                    placeholder: "(555) 555-0123",
                    text: $rows[index].phone,
                    keyboard: .phonePad,
                    textContentType: .telephoneNumber,
                    autocapitalization: .never
                )
            }

            FieldLabel(title: "Relationship") {
                LumiTextField(
                    placeholder: "Daughter",
                    text: $rows[index].relationship,
                    autocapitalization: .words
                )
            }
        }
        .padding(16)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func handleNext() {
        let cleaned: [FamilyMember] = rows
            .filter { !$0.phone.trimmed.isEmpty }
            .map { row in
                FamilyMember(
                    name: row.name.trimmed.nilIfEmpty,
                    phone: row.phone.trimmed,
                    relationship: row.relationship.trimmed.nilIfEmpty
                )
            }
        store.state.family = cleaned
        onNext()
    }
}
