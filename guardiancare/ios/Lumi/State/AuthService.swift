import Foundation
import FirebaseAuth

struct AuthUser: Equatable {
    let id: String
    let email: String?
}

@MainActor
final class AuthService: ObservableObject {
    @Published private(set) var currentUser: AuthUser?

    var isSignedIn: Bool { currentUser != nil }

    init() {
        // Firebase keeps the session in the keychain, so re-hydrate on launch.
        if let user = Auth.auth().currentUser {
            currentUser = AuthUser(id: user.uid, email: user.email)
        }
        Auth.auth().addStateDidChangeListener { [weak self] _, user in
            Task { @MainActor in
                self?.currentUser = user.map { AuthUser(id: $0.uid, email: $0.email) }
            }
        }
    }

    func signIn(email: String, password: String) async throws {
        _ = try await Auth.auth().signIn(withEmail: email, password: password)
    }

    func signUp(email: String, password: String) async throws {
        _ = try await Auth.auth().createUser(withEmail: email, password: password)
    }

    func signInWithGoogle() async throws {
        throw NSError(
            domain: "AuthService",
            code: -1,
            userInfo: [NSLocalizedDescriptionKey:
                "Enable Google in Firebase Console (Authentication → Sign-in method), then redownload GoogleService-Info.plist."]
        )
    }

    func signOut() {
        try? Auth.auth().signOut()
    }
}
