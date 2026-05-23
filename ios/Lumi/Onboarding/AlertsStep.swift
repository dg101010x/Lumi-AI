import SwiftUI

struct AlertsStep: View {
    @EnvironmentObject var store: OnboardingStore
    let onBack: () -> Void

    @State private var emergencySms: Bool = true
    @State private var emergencyPush: Bool = true
    @State private var medsReminders: Bool = true
    @State private var quietHoursStart: Date = Self.defaultStart
    @State private var quietHoursEnd: Date = Self.defaultEnd
    @State private var quietHoursEnabled: Bool = false

    @State private var isSaving: Bool = false
    @State private var errorMessage: String?

    var body: some View {
        StepLayout(
            step: 4,
            total: 4,
            title: "How should we reach you?",
            subtitle: "Emergencies always go out. Everything else is up to you.",
            nextLabel: isSaving ? "Saving…" : "Finish setup",
            canProceed: !isSaving,
            onNext: handleNext,
            onBack: onBack
        ) {
            VStack(spacing: 12) {
                LumiToggleRow(
                    title: "Emergency SMS",
                    description: "Text every caregiver immediately on a fall or distress event",
                    isOn: $emergencySms
                )
                LumiToggleRow(
                    title: "Emergency push notifications",
                    description: "Same as above, but to the Lumi app",
                    isOn: $emergencyPush
                )
                LumiToggleRow(
                    title: "Medication reminders",
                    description: "A gentle nudge if a scheduled dose is missed",
                    isOn: $medsReminders
                )
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("Quiet hours")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundStyle(LumiColors.slate600)
                Text("Non-emergency alerts are held until quiet hours end.")
                    .font(.system(size: 14, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
                    .padding(.bottom, 4)

                HStack(spacing: 12) {
                    FieldLabel(title: "Start") {
                        timePicker(selection: $quietHoursStart)
                    }
                    FieldLabel(title: "End") {
                        timePicker(selection: $quietHoursEnd)
                    }
                }
            }
            .padding(.top, 24)

            if let errorMessage {
                Text(errorMessage)
                    .font(.system(size: 13))
                    .foregroundStyle(.red)
                    .padding(.top, 12)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .onAppear {
            emergencySms = store.state.alerts.emergencySms
            emergencyPush = store.state.alerts.emergencyPush
            medsReminders = store.state.alerts.medsReminders
            if let start = store.state.alerts.quietHoursStart,
               let parsed = Self.timeFormatter.date(from: start) {
                quietHoursStart = parsed
                quietHoursEnabled = true
            }
            if let end = store.state.alerts.quietHoursEnd,
               let parsed = Self.timeFormatter.date(from: end) {
                quietHoursEnd = parsed
                quietHoursEnabled = true
            }
        }
    }

    private func timePicker(selection: Binding<Date>) -> some View {
        DatePicker("", selection: selection, displayedComponents: .hourAndMinute)
            .labelsHidden()
            .datePickerStyle(.compact)
            .tint(LumiColors.slate400)
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.white)
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(LumiColors.slate100, lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .onChange(of: selection.wrappedValue) { _, _ in quietHoursEnabled = true }
    }

    private func handleNext() {
        Task { await saveAndComplete() }
    }

    @MainActor
    private func saveAndComplete() async {
        store.state.alerts = AlertPrefs(
            emergencySms: emergencySms,
            emergencyPush: emergencyPush,
            medsReminders: medsReminders,
            quietHoursStart: quietHoursEnabled ? Self.timeFormatter.string(from: quietHoursStart) : nil,
            quietHoursEnd: quietHoursEnabled ? Self.timeFormatter.string(from: quietHoursEnd) : nil
        )

        errorMessage = nil
        isSaving = true
        defer { isSaving = false }

        do {
            try await OnboardingRepository().saveAll(store.state)
            store.complete()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    static let timeFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f
    }()

    static var defaultStart: Date {
        var c = DateComponents()
        c.hour = 22
        c.minute = 0
        return Calendar.current.date(from: c) ?? Date()
    }

    static var defaultEnd: Date {
        var c = DateComponents()
        c.hour = 7
        c.minute = 0
        return Calendar.current.date(from: c) ?? Date()
    }
}
