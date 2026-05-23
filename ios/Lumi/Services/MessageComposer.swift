import SwiftUI
import MessageUI

/// SwiftUI wrapper around `MFMessageComposeViewController`.
/// Opens iOS Messages pre-filled. User taps Send themselves (Apple doesn't allow
/// silent SMS from third-party apps).
struct MessageComposer: UIViewControllerRepresentable {
    let recipients: [String]
    let body: String
    let onComplete: (MessageComposeResult) -> Void

    static var canSend: Bool { MFMessageComposeViewController.canSendText() }

    func makeUIViewController(context: Context) -> MFMessageComposeViewController {
        let vc = MFMessageComposeViewController()
        vc.recipients = recipients
        vc.body = body
        vc.messageComposeDelegate = context.coordinator
        return vc
    }

    func updateUIViewController(_ uiViewController: MFMessageComposeViewController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(onComplete: onComplete) }

    final class Coordinator: NSObject, MFMessageComposeViewControllerDelegate {
        let onComplete: (MessageComposeResult) -> Void
        init(onComplete: @escaping (MessageComposeResult) -> Void) { self.onComplete = onComplete }

        func messageComposeViewController(_ controller: MFMessageComposeViewController,
                                          didFinishWith result: MessageComposeResult) {
            onComplete(result)
        }
    }
}

/// Presented when a "send message" action is triggered. Handles both the
/// single-recipient test message and the multi-recipient emergency alert.
struct MessageSendSheet: View {
    @EnvironmentObject var store: OnboardingStore
    let phones: [String]
    var bodyOverride: String? = nil
    let onDismiss: () -> Void

    private var messageBody: String {
        if let bodyOverride { return bodyOverride }
        let name = store.state.resident.nickname?.nilIfEmpty
            ?? store.state.resident.name?.nilIfEmpty
            ?? "your loved one"
        return "Lumi here — this is a test alert about \(name). Reply OK if you got this."
    }

    var body: some View {
        if MessageComposer.canSend {
            MessageComposer(
                recipients: phones,
                body: messageBody,
                onComplete: { _ in onDismiss() }
            )
            .ignoresSafeArea()
        } else {
            simulatorFallback
        }
    }

    private var simulatorFallback: some View {
        ZStack {
            LumiColors.slate50.ignoresSafeArea()
            VStack(spacing: 16) {
                Image(systemName: "iphone.slash")
                    .font(.system(size: 48))
                    .foregroundStyle(LumiColors.slate200)
                Text("Messages isn't available here")
                    .font(.system(size: 18, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                Text("The iOS simulator can't send SMS or iMessage. Run Lumi on a real iPhone to message \(recipientsLabel).")
                    .font(.system(size: 14, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
                LumiButton(title: "OK", action: onDismiss)
                    .padding(.top, 8)
            }
            .padding(24)
        }
    }

    private var recipientsLabel: String {
        switch phones.count {
        case 0: return "your caregivers"
        case 1: return phones[0]
        default: return "\(phones.count) caregivers"
        }
    }
}
