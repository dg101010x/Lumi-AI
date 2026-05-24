import SwiftUI

struct LumiButton: View {
    enum Variant { case primary, outline, ghost }

    let title: String
    var variant: Variant = .primary
    var fullWidth: Bool = false
    var isEnabled: Bool = true
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .padding(.horizontal, 20)
                .padding(.vertical, 14)
                .frame(maxWidth: fullWidth ? .infinity : nil)
                .background(backgroundColor)
                .foregroundStyle(foregroundColor)
                .overlay(borderOverlay)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .opacity(isEnabled ? 1 : 0.5)
        }
        .buttonStyle(.plain)
        .disabled(!isEnabled)
    }

    private var backgroundColor: Color {
        switch variant {
        case .primary: return LumiColors.slate400
        case .outline: return .white
        case .ghost:   return .clear
        }
    }

    private var foregroundColor: Color {
        switch variant {
        case .primary: return .white
        case .outline: return LumiColors.slate800
        case .ghost:   return LumiColors.slate600
        }
    }

    @ViewBuilder
    private var borderOverlay: some View {
        if variant == .outline {
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(LumiColors.slate200, lineWidth: 1)
        }
    }
}
