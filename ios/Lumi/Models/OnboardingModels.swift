import Foundation

enum Mobility: String, Codable, CaseIterable {
    case independent
    case walker
    case wheelchair
    case bed
}

struct Caregiver: Codable, Equatable {
    var name: String?
    var email: String?
    var phone: String?
}

struct Resident: Codable, Equatable {
    var name: String?
    var nickname: String?
    var dob: String?
    var photoUrl: String?
    var room: String?
}

struct Health: Codable, Equatable {
    var conditions: [String] = []
    var mobility: Mobility?
}

struct Likes: Codable, Equatable {
    var music: String?
    var food: String?
    var hobbies: String?
    var family: String?
}

struct FamilyMember: Codable, Equatable, Identifiable {
    var id: UUID = UUID()
    var name: String?
    var phone: String
    var relationship: String?

    enum CodingKeys: String, CodingKey {
        case name, phone, relationship
    }
}

struct AlertPrefs: Codable, Equatable {
    var emergencySms: Bool = true
    var emergencyPush: Bool = true
    var medsReminders: Bool = true
    var quietHoursStart: String?
    var quietHoursEnd: String?
}

struct OnboardingState: Codable, Equatable {
    var caregiver: Caregiver = Caregiver()
    var resident: Resident = Resident()
    var health: Health = Health()
    var likes: Likes = Likes()
    var family: [FamilyMember] = []
    var alerts: AlertPrefs = AlertPrefs()
    var completedAt: String?
}
