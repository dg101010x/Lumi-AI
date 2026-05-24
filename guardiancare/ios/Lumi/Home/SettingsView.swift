import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var store: OnboardingStore
    @EnvironmentObject var auth: AuthService

    @State private var showEditResident: Bool = false
    @State private var alertSaveError: String?

    private let repository = OnboardingRepository()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Settings")
                    .font(.system(size: 24, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)

                sectionTitle("Resident")
                VStack(alignment: .leading, spacing: 12) {
                    InfoCard(rows: [
                        ("Name", store.state.resident.name?.nilIfEmpty ?? "—"),
                        ("Nickname", store.state.resident.nickname?.nilIfEmpty ?? "—"),
                        ("Date of birth", store.state.resident.dob?.nilIfEmpty ?? "—"),
                        ("Mobility", store.state.health.mobility?.rawValue.capitalized ?? "—"),
                        ("Conditions", store.state.health.conditions.isEmpty
                            ? "—" : store.state.health.conditions.joined(separator: ", ")),
                    ])
                    LumiButton(title: "Edit resident", variant: .outline, fullWidth: true) {
                        showEditResident = true
                    }
                }

                sectionTitle("Alerts")
                VStack(spacing: 12) {
                    LumiToggleRow(
                        title: "Emergency SMS",
                        description: "Text every caregiver immediately on a fall or distress event",
                        isOn: alertsBinding(\.emergencySms)
                    )
                    LumiToggleRow(
                        title: "Emergency push",
                        description: "Same as above, but to the Lumi app",
                        isOn: alertsBinding(\.emergencyPush)
                    )
                    LumiToggleRow(
                        title: "Medication reminders",
                        description: "A gentle nudge if a scheduled dose is missed",
                        isOn: alertsBinding(\.medsReminders)
                    )
                    if let alertSaveError {
                        Text(alertSaveError)
                            .font(.system(size: 13))
                            .foregroundStyle(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                sectionTitle("Caregivers")
                CaregiverListEditor()

                sectionTitle("Account")
                if let email = auth.currentUser?.email {
                    InfoCard(rows: [("Signed in as", email)])
                }
                LumiButton(title: "Sign out", variant: .outline, fullWidth: true, action: auth.signOut)
                    .padding(.top, 4)
            }
            .padding(24)
        }
        .background(LumiColors.slate50.ignoresSafeArea())
        .sheet(isPresented: $showEditResident) {
            EditResidentSheet(resident: store.state.resident, health: store.state.health)
        }
    }

    private func sectionTitle(_ title: String) -> some View {
        Text(title)
            .font(.system(size: 12, weight: .medium))
            .textCase(.uppercase)
            .foregroundStyle(LumiColors.slate600)
            .padding(.top, 8)
    }

    /// Binding that writes to `store.state.alerts` AND fires a Supabase upsert.
    private func alertsBinding(_ keyPath: WritableKeyPath<AlertPrefs, Bool>) -> Binding<Bool> {
        Binding(
            get: { store.state.alerts[keyPath: keyPath] },
            set: { newValue in
                store.state.alerts[keyPath: keyPath] = newValue
                let snapshot = store.state.alerts
                Task {
                    do {
                        try await repository.updateAlertPreferences(snapshot)
                        await MainActor.run { alertSaveError = nil }
                    } catch {
                        await MainActor.run { alertSaveError = error.localizedDescription }
                    }
                }
            }
        )
    }
}

private struct InfoCard: View {
    let rows: [(String, String)]
    var body: some View {
        VStack(spacing: 0) {
            ForEach(Array(rows.enumerated()), id: \.offset) { idx, row in
                HStack {
                    Text(row.0)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                    Spacer()
                    Text(row.1)
                        .font(.system(size: 14))
                        .foregroundStyle(LumiColors.slate800)
                        .multilineTextAlignment(.trailing)
                }
                .padding(16)
                if idx < rows.count - 1 {
                    Rectangle().fill(LumiColors.slate100).frame(height: 1)
                }
            }
        }
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}
