import Foundation

struct ProfileRow: Codable {
    let id: String
    let email: String?
    let phone: String?
}

struct ResidentRow: Codable {
    let id: String?
    let ownerId: String
    let name: String
    let nickname: String?
    let dob: String?
    let photoPath: String?
    let mobility: String?
    let conditions: [String]
    let onboardingCompletedAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case ownerId = "owner_id"
        case name
        case nickname
        case dob
        case photoPath = "photo_path"
        case mobility
        case conditions
        case onboardingCompletedAt = "onboarding_completed_at"
    }
}

struct FamilyMemberRow: Codable {
    let id: String?
    let residentId: String
    let name: String?
    let phone: String
    let relationship: String?

    enum CodingKeys: String, CodingKey {
        case id
        case residentId = "resident_id"
        case name
        case phone
        case relationship
    }
}

/// Payload for updating an existing resident — omits id/owner_id/onboarding_completed_at
/// so PostgREST doesn't overwrite the completion timestamp on edits.
struct ResidentUpdateRow: Codable {
    let name: String
    let nickname: String?
    let dob: String?
    let photoPath: String?
    let mobility: String?
    let conditions: [String]

    enum CodingKeys: String, CodingKey {
        case name, nickname, dob
        case photoPath = "photo_path"
        case mobility, conditions
    }
}

struct AlertPreferencesRow: Codable {
    let profileId: String
    let emergencySms: Bool
    let emergencyPush: Bool
    let medsReminders: Bool
    let quietHoursStart: String?
    let quietHoursEnd: String?

    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case emergencySms = "emergency_sms"
        case emergencyPush = "emergency_push"
        case medsReminders = "meds_reminders"
        case quietHoursStart = "quiet_hours_start"
        case quietHoursEnd = "quiet_hours_end"
    }
}
