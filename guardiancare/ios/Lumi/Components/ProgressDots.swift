import SwiftUI

struct ProgressDots: View {
    let current: Int
    let total: Int

    var body: some View {
        HStack(spacing: 6) {
            ForEach(0..<total, id: \.self) { i in
                let idx = i + 1
                let filled = idx <= current
                let isCurrent = idx == current
                Capsule()
                    .fill(filled ? LumiColors.slate400 : LumiColors.slate100)
                    .frame(width: isCurrent ? 24 : 6, height: 6)
                    .animation(.easeInOut(duration: 0.2), value: current)
            }
        }
        .accessibilityLabel("Step \(current) of \(total)")
    }
}
