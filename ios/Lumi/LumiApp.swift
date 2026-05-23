import SwiftUI
import FirebaseCore

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        FirebaseApp.configure()
        return true
    }
}

@main
struct LumiApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    @StateObject private var store = OnboardingStore()
    @StateObject private var auth = AuthService()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .environmentObject(auth)
        }
    }
}

struct RootView: View {
    @EnvironmentObject var auth: AuthService
    @EnvironmentObject var store: OnboardingStore

    var body: some View {
        Group {
            if !auth.isSignedIn {
                SignInView()
            } else if store.isComplete {
                HomeShell()
            } else {
                OnboardingFlow()
            }
        }
        .task(id: auth.currentUser?.id) {
            guard auth.currentUser != nil else { return }
            await store.hydrateFromBackend()
        }
    }
}
