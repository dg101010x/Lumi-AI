import SwiftUI

struct ResidentStep: View {
    @EnvironmentObject var store: OnboardingStore
    let onNext: () -> Void
    let onBack: () -> Void

    @State private var name: String = ""
    @State private var nickname: String = ""
    @State private var dob: Date = Date()
    @State private var hasDob: Bool = false

    private var canProceed: Bool { !name.trimmed.isEmpty }

    var body: some View {
        StepLayout(
            step: 2,
            total: 4,
            title: "Who is Lumi watching over?",
            subtitle: "Tell us a little about your loved one.",
            canProceed: canProceed,
            onNext: handleNext,
            onBack: onBack
        ) {
            FieldLabel(title: "Full name") {
                LumiTextField(
                    placeholder: "Margaret Chen",
                    text: $name,
                    textContentType: .name,
                    autocapitalization: .words
                )
            }

            FieldLabel(title: "What do they like to be called?", hint: "Lumi uses this in conversation") {
                LumiTextField(
                    placeholder: "Maggie",
                    text: $nickname,
                    autocapitalization: .words
                )
            }

            FieldLabel(title: "Date of birth") {
                DatePicker("Date of birth", selection: $dob, displayedComponents: .date)
                    .labelsHidden()
                    .datePickerStyle(.compact)
                    .tint(LumiColors.slate400)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.white)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(LumiColors.slate100, lineWidth: 1)
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    .onChange(of: dob) { _, _ in hasDob = true }
            }
        }
        .onAppear {
            name = store.state.resident.name ?? ""
            nickname = store.state.resident.nickname ?? ""
            if let dobStr = store.state.resident.dob,
               let parsed = Self.dateFormatter.date(from: dobStr) {
                dob = parsed
                hasDob = true
            }
        }
    }

    private func handleNext() {
        store.state.resident = Resident(
            name: name.trimmed.nilIfEmpty,
            nickname: nickname.trimmed.nilIfEmpty,
            dob: hasDob ? Self.dateFormatter.string(from: dob) : nil,
            photoUrl: store.state.resident.photoUrl,
            room: store.state.resident.room
        )
        onNext()
    }

    static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f
    }()
}
