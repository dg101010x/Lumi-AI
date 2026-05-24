import SwiftUI

/// Shared list + add/edit/remove flow. Used in both Settings and the Family tab.
struct CaregiverListEditor: View {
    @EnvironmentObject var store: OnboardingStore
    @State private var editingMember: FamilyMember? = nil
    @State private var addingCaregiver: Bool = false
    @State private var messagingMember: FamilyMember? = nil
    @State private var errorMessage: String?

    private let repository = OnboardingRepository()

    var body: some View {
        VStack(spacing: 12) {
            if store.state.family.isEmpty {
                emptyCard
            } else {
                ForEach(store.state.family) { member in
                    CaregiverRowView(
                        member: member,
                        onEdit: { editingMember = member },
                        onMessage: { messagingMember = member }
                    )
                }
            }

            LumiButton(title: "+ Add caregiver", variant: .outline, fullWidth: true) {
                addingCaregiver = true
            }

            if let errorMessage {
                Text(errorMessage)
                    .font(.system(size: 13))
                    .foregroundStyle(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .sheet(isPresented: $addingCaregiver) {
            CaregiverEditorSheet(initialMember: nil) { newMember in
                store.state.family.append(newMember)
                syncFamily()
            }
        }
        .sheet(item: $editingMember) { member in
            CaregiverEditorSheet(
                initialMember: member,
                onSave: { updated in
                    if let idx = store.state.family.firstIndex(where: { $0.id == member.id }) {
                        store.state.family[idx] = updated
                    }
                    syncFamily()
                },
                onDelete: {
                    store.state.family.removeAll(where: { $0.id == member.id })
                    syncFamily()
                }
            )
        }
        .sheet(item: $messagingMember) { member in
            MessageSendSheet(phones: [member.phone]) {
                messagingMember = nil
            }
        }
    }

    private var emptyCard: some View {
        VStack(spacing: 8) {
            Image(systemName: "person.2")
                .font(.system(size: 32))
                .foregroundStyle(LumiColors.slate200)
            Text("No caregivers yet")
                .font(.system(size: 14, weight: .light))
                .foregroundStyle(LumiColors.slate600)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 32)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func syncFamily() {
        let snapshot = store.state.family
        Task {
            do {
                try await repository.saveFamilyList(snapshot)
                await MainActor.run { errorMessage = nil }
            } catch {
                await MainActor.run { errorMessage = error.localizedDescription }
            }
        }
    }
}

struct CaregiverRowView: View {
    let member: FamilyMember
    let onEdit: () -> Void
    let onMessage: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(action: onEdit) {
                HStack(spacing: 16) {
                    ZStack {
                        Circle().fill(LumiColors.slate100).frame(width: 48, height: 48)
                        Text(initials)
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(LumiColors.slate600)
                    }
                    VStack(alignment: .leading, spacing: 4) {
                        Text(member.name?.nilIfEmpty ?? "Unnamed")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(LumiColors.slate800)
                        Text(subtitle)
                            .font(.system(size: 13, weight: .light))
                            .foregroundStyle(LumiColors.slate600)
                    }
                    Spacer()
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            Button(action: onMessage) {
                Image(systemName: "message.fill")
                    .font(.system(size: 16))
                    .foregroundStyle(LumiColors.slate400)
                    .frame(width: 40, height: 40)
                    .background(LumiColors.slate100)
                    .clipShape(Circle())
            }
            .buttonStyle(.plain)
        }
        .padding(16)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var initials: String {
        let parts = (member.name ?? "").split(separator: " ").prefix(2)
        let init1 = parts.compactMap { $0.first.map(String.init) }.joined()
        return init1.isEmpty ? "?" : init1.uppercased()
    }

    private var subtitle: String {
        [member.relationship?.nilIfEmpty, member.phone.nilIfEmpty]
            .compactMap { $0 }
            .joined(separator: " · ")
    }
}
