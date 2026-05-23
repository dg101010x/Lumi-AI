import SwiftUI

private let allConditions = [
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

struct EditResidentSheet: View {
    @EnvironmentObject var store: OnboardingStore
    @Environment(\.dismiss) private var dismiss

    @State private var name: String
    @State private var nickname: String
    @State private var dob: Date
    @State private var hasDob: Bool
    @State private var mobility: Mobility?
    @State private var conditions: Set<String>
    @State private var isSaving: Bool = false
    @State private var errorMessage: String?

    init(resident: Resident, health: Health) {
        _name = State(initialValue: resident.name ?? "")
        _nickname = State(initialValue: resident.nickname ?? "")
        if let dobStr = resident.dob, let d = Self.dateFormatter.date(from: dobStr) {
            _dob = State(initialValue: d)
            _hasDob = State(initialValue: true)
        } else {
            _dob = State(initialValue: Date())
            _hasDob = State(initialValue: false)
        }
        _mobility = State(initialValue: health.mobility)
        _conditions = State(initialValue: Set(health.conditions))
    }

    private var canSave: Bool { !name.trimmed.isEmpty && !isSaving }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    FieldLabel(title: "Full name") {
                        LumiTextField(
                            placeholder: "Margaret Chen",
                            text: $name,
                            textContentType: .name,
                            autocapitalization: .words
                        )
                    }
                    FieldLabel(title: "Nickname") {
                        LumiTextField(
                            placeholder: "Maggie",
                            text: $nickname,
                            autocapitalization: .words
                        )
                    }
                    FieldLabel(title: "Date of birth") {
                        DatePicker("", selection: $dob, displayedComponents: .date)
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
                    FieldLabel(title: "Mobility") {
                        VStack(spacing: 8) {
                            ForEach(Mobility.allCases, id: \.self) { m in
                                mobilityRow(m)
                            }
                        }
                    }
                    FieldLabel(title: "Conditions") {
                        FlowLayout(spacing: 8) {
                            ForEach(allConditions, id: \.self) { c in
                                LumiChip(label: c, selected: conditions.contains(c)) {
                                    if conditions.contains(c) {
                                        conditions.remove(c)
                                    } else {
                                        conditions.insert(c)
                                    }
                                }
                            }
                        }
                    }

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.system(size: 13))
                            .foregroundStyle(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }

                    LumiButton(
                        title: isSaving ? "Saving…" : "Save",
                        fullWidth: true,
                        isEnabled: canSave,
                        action: { Task { await save() } }
                    )
                    .padding(.top, 4)
                }
                .padding(24)
            }
            .background(LumiColors.slate50.ignoresSafeArea())
            .navigationTitle("Edit resident")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }

    private func mobilityRow(_ m: Mobility) -> some View {
        let selected = mobility == m
        return Button { mobility = m } label: {
            HStack {
                Text(label(for: m))
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                Spacer()
                if selected {
                    Image(systemName: "checkmark")
                        .foregroundStyle(LumiColors.slate400)
                }
            }
            .padding(16)
            .background(.white)
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(selected ? LumiColors.slate400 : LumiColors.slate100,
                            lineWidth: selected ? 2 : 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private func label(for m: Mobility) -> String {
        switch m {
        case .independent: return "Independent"
        case .walker:      return "Uses a walker or cane"
        case .wheelchair:  return "Uses a wheelchair"
        case .bed:         return "Mostly bed-bound"
        }
    }

    @MainActor
    private func save() async {
        isSaving = true
        errorMessage = nil
        defer { isSaving = false }

        let updatedResident = Resident(
            name: name.trimmed.nilIfEmpty,
            nickname: nickname.trimmed.nilIfEmpty,
            dob: hasDob ? Self.dateFormatter.string(from: dob) : nil,
            photoUrl: store.state.resident.photoUrl,
            room: store.state.resident.room
        )
        let updatedHealth = Health(
            conditions: allConditions.filter { conditions.contains($0) },
            mobility: mobility
        )

        do {
            try await OnboardingRepository().updateResident(updatedResident, health: updatedHealth)
            store.state.resident = updatedResident
            store.state.health = updatedHealth
            dismiss()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f
    }()
}
