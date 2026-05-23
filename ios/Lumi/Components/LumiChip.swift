import SwiftUI

struct LumiChip: View {
    let label: String
    let selected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(label)
                .font(.system(size: 14))
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(selected ? LumiColors.slate400 : .white)
                .foregroundStyle(selected ? .white : LumiColors.slate600)
                .overlay(
                    Capsule().stroke(selected ? LumiColors.slate400 : LumiColors.slate100, lineWidth: 1)
                )
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}
