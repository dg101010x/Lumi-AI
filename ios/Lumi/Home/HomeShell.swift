import SwiftUI

struct HomeShell: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem { Label("Home", systemImage: "house.fill") }

            ActivityView()
                .tabItem { Label("Activity", systemImage: "clock.fill") }

            FamilyView()
                .tabItem { Label("Family", systemImage: "person.2.fill") }

            SettingsView()
                .tabItem { Label("Settings", systemImage: "gearshape.fill") }
        }
        .tint(LumiColors.slate400)
    }
}
