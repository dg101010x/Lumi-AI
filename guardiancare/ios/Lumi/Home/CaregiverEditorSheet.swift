import SwiftUI

struct CaregiverEditorSheet: View {
    let initialMember: FamilyMember?
    let onSave: (FamilyMember) -> Void
    var onDelete: (() -> Void)? = nil

    @Environment(\.dismiss) private var dismiss
    @State private var name: String
    @State private var phone: String
    @State private var relationship: String

    init(initialMember: FamilyMember?,
         onSave: @escaping (FamilyMember) -> Void,
         onDelete: (() -> Void)? = nil) {
        self.initialMember = initialMember
        self.onSave = onSave
        self.onDelete = onDelete
        _name = State(initialValue: initialMember?.name ?? "")
        _phone = State(initialValue: initialMember?.phone ?? "")
        _relationship = State(initialValue: initialMember?.relationship ?? "")
    }

    private var canSave: Bool { !phone.trimmed.isEmpty }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    FieldLabel(title: "Name") {
                        LumiTextField(
                            placeholder: "Sarah Chen",
                            text: $name,
                            textContentType: .name,
                            autocapitalization: .words
                        )
                    }
                    FieldLabel(title: "Phone") {
                        LumiTextField(
                            placeholder: "(555) 555-0123",
                            text: $phone,
                            keyboard: .phonePad,
                            textContentType: .telephoneNumber,
                            autocapitalization: .never
                        )
                    }
                    FieldLabel(title: "Relationship") {
                        LumiTextField(
                            placeholder: "Daughter",
                            text: $relationship,
                            autocapitalization: .words
                        )
                    }

                    LumiButton(title: "Save", fullWidth: true, isEnabled: canSave) {
                        let member = FamilyMember(
                            id: initialMember?.id ?? UUID(),
                            name: name.trimmed.nilIfEmpty,
                            phone: phone.trimmed,
                            relationship: relationship.trimmed.nilIfEmpty
                        )
                        onSave(member)
                        dismiss()
                    }
                    .padding(.top, 8)

                    if let onDelete {
                        LumiButton(title: "Remove caregiver", variant: .ghost, fullWidth: true) {
                            onDelete()
                            dismiss()
                        }
                    }
                }
                .padding(24)
            }
            .background(LumiColors.slate50.ignoresSafeArea())
            .navigationTitle(initialMember == nil ? "Add caregiver" : "Edit caregiver")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}
