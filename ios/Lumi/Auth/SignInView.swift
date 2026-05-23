import SwiftUI

struct SignInView: View {
    @EnvironmentObject var auth: AuthService

    enum Mode { case signIn, signUp }
    @State private var mode: Mode = .signIn
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isWorking: Bool = false
    @State private var errorMessage: String?

    private var canSubmit: Bool {
        !email.trimmed.isEmpty && !password.isEmpty && !isWorking
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                logo.padding(.top, 64)

                VStack(spacing: 8) {
                    Text(mode == .signIn ? "Welcome back" : "Create your account")
                        .font(.system(size: 28, weight: .medium))
                        .foregroundStyle(LumiColors.slate800)
                    Text(mode == .signIn ? "Sign in to continue." : "Just an email and password.")
                        .font(.system(size: 16, weight: .light))
                        .foregroundStyle(LumiColors.slate600)
                }
                .multilineTextAlignment(.center)
                .padding(.bottom, 8)

                VStack(spacing: 12) {
                    LumiTextField(
                        placeholder: "you@example.com",
                        text: $email,
                        keyboard: .emailAddress,
                        textContentType: .emailAddress,
                        autocapitalization: .never
                    )
                    LumiSecureField(
                        placeholder: "Password",
                        text: $password,
                        textContentType: mode == .signUp ? .newPassword : .password
                    )
                    if let errorMessage {
                        Text(errorMessage)
                            .font(.system(size: 13))
                            .foregroundStyle(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                LumiButton(
                    title: primaryButtonTitle,
                    fullWidth: true,
                    isEnabled: canSubmit,
                    action: { Task { await runEmailPassword() } }
                )

                dividerWithOr

                LumiButton(
                    title: "Continue with Google",
                    variant: .outline,
                    fullWidth: true,
                    isEnabled: !isWorking,
                    action: { Task { await runGoogle() } }
                )

                Button(action: toggleMode) {
                    Text(mode == .signIn ? "Don't have an account? Sign up" : "Already have an account? Sign in")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(LumiColors.slate600)
                }
                .buttonStyle(.plain)
                .padding(.top, 8)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 32)
            .frame(maxWidth: .infinity)
        }
        .background(LumiColors.slate50.ignoresSafeArea())
    }

    private var logo: some View {
        ZStack {
            Circle().fill(LumiColors.slate100).frame(width: 80, height: 80)
            Text("L")
                .font(.system(size: 32, weight: .medium))
                .foregroundStyle(LumiColors.slate600)
        }
    }

    private var dividerWithOr: some View {
        HStack(spacing: 12) {
            Rectangle().fill(LumiColors.slate100).frame(height: 1)
            Text("or")
                .font(.system(size: 13))
                .foregroundStyle(LumiColors.slate600)
            Rectangle().fill(LumiColors.slate100).frame(height: 1)
        }
    }

    private var primaryButtonTitle: String {
        if isWorking {
            return mode == .signIn ? "Signing in…" : "Creating account…"
        }
        return mode == .signIn ? "Sign in" : "Sign up"
    }

    private func toggleMode() {
        withAnimation(.easeInOut(duration: 0.15)) {
            mode = mode == .signIn ? .signUp : .signIn
            errorMessage = nil
        }
    }

    @MainActor
    private func runEmailPassword() async {
        errorMessage = nil
        isWorking = true
        defer { isWorking = false }
        do {
            if mode == .signIn {
                try await auth.signIn(email: email.trimmed, password: password)
            } else {
                try await auth.signUp(email: email.trimmed, password: password)
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    @MainActor
    private func runGoogle() async {
        errorMessage = nil
        isWorking = true
        defer { isWorking = false }
        do {
            try await auth.signInWithGoogle()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
