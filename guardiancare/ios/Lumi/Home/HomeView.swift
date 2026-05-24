import SwiftUI

struct HomeView: View {
    @EnvironmentObject var store: OnboardingStore

    @State private var showCallPicker: Bool = false
    @State private var showMessagePicker: Bool = false
    @State private var messageRecipient: FamilyMember? = nil
    @State private var showEmergencyAlert: Bool = false
    @State private var confirmEmergency: Bool = false

    private let recentEvents = Array(ActivityEvent.sample().prefix(3))

    private var residentName: String {
        store.state.resident.nickname?.nilIfEmpty
            ?? store.state.resident.name?.nilIfEmpty
            ?? "your loved one"
    }

    private var emergencyBody: String {
        "URGENT — please check in about \(residentName) right now. Sent from Lumi."
    }

    private var caregiverPhones: [String] {
        store.state.family.map(\.phone)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Hello")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                    Text("Lumi is watching over \(residentName)")
                        .font(.system(size: 24, weight: .medium))
                        .foregroundStyle(LumiColors.slate800)
                        .fixedSize(horizontal: false, vertical: true)
                }

                EmergencyAlertButton(disabled: caregiverPhones.isEmpty) {
                    confirmEmergency = true
                }

                StatusCard()

                VStack(alignment: .leading, spacing: 12) {
                    Text("Quick actions")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                    HStack(spacing: 12) {
                        QuickActionCard(icon: "phone.fill", title: "Call caregiver") {
                            if !store.state.family.isEmpty { showCallPicker = true }
                        }
                        QuickActionCard(icon: "message.fill", title: "Message caregiver") {
                            if !store.state.family.isEmpty { showMessagePicker = true }
                        }
                    }
                    if store.state.family.isEmpty {
                        Text("Add a caregiver in the Family tab to enable these.")
                            .font(.system(size: 12, weight: .light))
                            .foregroundStyle(LumiColors.slate600)
                    }
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("Last 24 hours")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                    if recentEvents.isEmpty {
                        EmptyActivityCard()
                    } else {
                        VStack(spacing: 8) {
                            ForEach(recentEvents) { event in
                                SmallEventRow(event: event)
                            }
                        }
                    }
                }
            }
            .padding(24)
        }
        .background(LumiColors.slate50.ignoresSafeArea())
        .confirmationDialog("Call caregiver",
                            isPresented: $showCallPicker,
                            titleVisibility: .visible) {
            ForEach(store.state.family) { member in
                Button(buttonLabel(for: member)) { callNumber(member.phone) }
            }
            Button("Cancel", role: .cancel) {}
        }
        .confirmationDialog("Message caregiver",
                            isPresented: $showMessagePicker,
                            titleVisibility: .visible) {
            ForEach(store.state.family) { member in
                Button(buttonLabel(for: member)) { messageRecipient = member }
            }
            Button("Cancel", role: .cancel) {}
        }
        .confirmationDialog(
            "Send emergency alert to all caregivers?",
            isPresented: $confirmEmergency,
            titleVisibility: .visible
        ) {
            Button("Send alert", role: .destructive) {
                showEmergencyAlert = true
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Opens Messages with all \(caregiverPhones.count) caregiver(s) pre-filled. You still need to tap Send.")
        }
        .sheet(item: $messageRecipient) { member in
            MessageSendSheet(phones: [member.phone]) {
                messageRecipient = nil
            }
        }
        .sheet(isPresented: $showEmergencyAlert) {
            MessageSendSheet(
                phones: caregiverPhones,
                bodyOverride: emergencyBody
            ) {
                showEmergencyAlert = false
            }
        }
    }

    private func buttonLabel(for member: FamilyMember) -> String {
        member.name?.nilIfEmpty ?? member.phone
    }

    private func callNumber(_ phone: String) {
        let cleaned = phone.filter { $0.isNumber || $0 == "+" }
        guard !cleaned.isEmpty, let url = URL(string: "tel:\(cleaned)") else { return }
        UIApplication.shared.open(url)
    }
}

private struct EmergencyAlertButton: View {
    let disabled: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 14) {
                Image(systemName: "bell.fill")
                    .font(.system(size: 22))
                VStack(alignment: .leading, spacing: 2) {
                    Text("Alert caregivers")
                        .font(.system(size: 17, weight: .semibold))
                    Text(disabled
                         ? "Add a caregiver first"
                         : "Notify everyone something is wrong")
                        .font(.system(size: 13, weight: .light))
                        .opacity(0.9)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.system(size: 13, weight: .semibold))
                    .opacity(0.85)
            }
            .foregroundStyle(.white)
            .padding(20)
            .frame(maxWidth: .infinity)
            .background(LumiColors.slate400)
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .opacity(disabled ? 0.5 : 1)
        }
        .buttonStyle(.plain)
        .disabled(disabled)
    }
}

private struct StatusCard: View {
    var body: some View {
        HStack(spacing: 12) {
            Circle().fill(.green).frame(width: 10, height: 10)
            VStack(alignment: .leading, spacing: 2) {
                Text("All systems normal")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                Text("Lumi is on and listening")
                    .font(.system(size: 14, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
            }
            Spacer()
        }
        .padding(16)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct QuickActionCard: View {
    let icon: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 22))
                    .foregroundStyle(LumiColors.slate400)
                Text(title)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(.white)
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(LumiColors.slate100, lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}

private struct SmallEventRow: View {
    let event: ActivityEvent

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(event.kind.category.accent.opacity(0.12))
                    .frame(width: 32, height: 32)
                Image(systemName: event.kind.icon)
                    .font(.system(size: 14))
                    .foregroundStyle(event.kind.category.accent)
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(event.title)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                    .lineLimit(1)
                Text(relative(event.timestamp))
                    .font(.system(size: 12, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
            }
            Spacer()
        }
        .padding(12)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func relative(_ date: Date) -> String {
        let fmt = RelativeDateTimeFormatter()
        fmt.unitsStyle = .short
        return fmt.localizedString(for: date, relativeTo: Date())
    }
}

private struct EmptyActivityCard: View {
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "moon.zzz")
                .font(.system(size: 28))
                .foregroundStyle(LumiColors.slate200)
            Text("Nothing to report")
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
}
