import Combine
import Foundation

@MainActor
final class OnboardingStore: ObservableObject {
    @Published var state: OnboardingState
    private let storageKey = "lumi.onboarding"
    private var saveCancellable: AnyCancellable?

    var isComplete: Bool { state.completedAt != nil }

    init() {
        if let data = UserDefaults.standard.data(forKey: "lumi.onboarding"),
           let decoded = try? JSONDecoder().decode(OnboardingState.self, from: data) {
            self.state = decoded
        } else {
            self.state = OnboardingState()
        }

        saveCancellable = $state
            .dropFirst()
            .removeDuplicates()
            .debounce(for: .milliseconds(150), scheduler: DispatchQueue.main)
            .sink { [weak self] newState in
                guard let self else { return }
                if let data = try? JSONEncoder().encode(newState) {
                    UserDefaults.standard.set(data, forKey: self.storageKey)
                }
            }
    }

    func reset() {
        state = OnboardingState()
        UserDefaults.standard.removeObject(forKey: storageKey)
    }

    func hydrateFromBackend() async {
        if let snapshot = try? await OnboardingRepository().fetchOnboardingState() {
            state = snapshot
        }
    }

    func complete() {
        let formatter = ISO8601DateFormatter()
        state.completedAt = formatter.string(from: Date())
    }
}
