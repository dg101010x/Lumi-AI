import SwiftUI

struct FieldLabel<Content: View>: View {
    let title: String
    var hint: String? = nil
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(LumiColors.slate600)
            content()
            if let hint {
                Text(hint)
                    .font(.system(size: 12, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.bottom, 16)
    }
}
