import SwiftUI

struct StepLayout<Content: View>: View {
    let step: Int
    let total: Int
    let title: String
    var subtitle: String? = nil
    var nextLabel: String = "Continue"
    var canProceed: Bool = true
    var showBack: Bool = true
    let onNext: () -> Void
    var onBack: (() -> Void)? = nil
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(spacing: 0) {
            header

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Text(title)
                        .font(.system(size: 24, weight: .medium))
                        .foregroundStyle(LumiColors.slate800)
                        .fixedSize(horizontal: false, vertical: true)
                    if let subtitle {
                        Text(subtitle)
                            .font(.system(size: 16, weight: .light))
                            .foregroundStyle(LumiColors.slate600)
                            .padding(.top, 8)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    VStack(alignment: .leading, spacing: 0) {
                        content()
                    }
                    .padding(.top, 32)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 24)
                .padding(.top, 32)
                .padding(.bottom, 24)
            }

            footer
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LumiColors.slate50.ignoresSafeArea())
    }

    private var header: some View {
        HStack {
            if showBack {
                Button(action: { onBack?() }) {
                    Text("← Back")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                }
                .buttonStyle(.plain)
                .frame(width: 60, alignment: .leading)
            } else {
                Color.clear.frame(width: 60, height: 20)
            }
            Spacer()
            ProgressDots(current: step, total: total)
            Spacer()
            Color.clear.frame(width: 60, height: 20)
        }
        .padding(.horizontal, 24)
        .padding(.top, 12)
        .padding(.bottom, 8)
    }

    private var footer: some View {
        VStack(spacing: 0) {
            Rectangle()
                .fill(LumiColors.slate100)
                .frame(height: 1)
            LumiButton(title: nextLabel, fullWidth: true, isEnabled: canProceed, action: onNext)
                .padding(.horizontal, 24)
                .padding(.vertical, 16)
        }
        .background(.white)
    }
}
