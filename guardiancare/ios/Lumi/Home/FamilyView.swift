import SwiftUI

struct FamilyView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Family")
                    .font(.system(size: 24, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                Text("These caregivers are notified when something needs attention.")
                    .font(.system(size: 14, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
                    .padding(.bottom, 4)
                CaregiverListEditor()
            }
            .padding(24)
        }
        .background(LumiColors.slate50.ignoresSafeArea())
    }
}
