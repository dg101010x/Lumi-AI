import Foundation
import FirebaseAuth
import Supabase

enum RepositoryError: LocalizedError {
    case notSignedIn

    var errorDescription: String? {
        switch self {
        case .notSignedIn: return "You're not signed in."
        }
    }
}

struct OnboardingRepository {
    private var client: SupabaseClient { SupabaseService.client }

    /// Pull the full onboarding state for the current user back out of Supabase.
    /// Returns nil if there's no resident row yet (i.e. user hasn't onboarded).
    func fetchOnboardingState() async throws -> OnboardingState? {
        guard let user = Auth.auth().currentUser else { return nil }
        let uid = user.uid

        let residents: [ResidentRow] = try await client
            .from("residents")
            .select()
            .eq("owner_id", value: uid)
            .limit(1)
            .execute()
            .value

        guard let resident = residents.first, let residentId = resident.id else {
            return nil
        }

        let family: [FamilyMemberRow] = try await client
            .from("family_members")
            .select()
            .eq("resident_id", value: residentId)
            .execute()
            .value

        let alerts: [AlertPreferencesRow] = try await client
            .from("alert_preferences")
            .select()
            .eq("profile_id", value: uid)
            .limit(1)
            .execute()
            .value

        var state = OnboardingState()
        state.resident = Resident(
            name: resident.name,
            nickname: resident.nickname,
            dob: resident.dob,
            photoUrl: resident.photoPath,
            room: nil
        )
        state.health = Health(
            conditions: resident.conditions,
            mobility: resident.mobility.flatMap { Mobility(rawValue: $0) }
        )
        state.family = family.map {
            FamilyMember(name: $0.name, phone: $0.phone, relationship: $0.relationship)
        }
        if let a = alerts.first {
            state.alerts = AlertPrefs(
                emergencySms: a.emergencySms,
                emergencyPush: a.emergencyPush,
                medsReminders: a.medsReminders,
                quietHoursStart: a.quietHoursStart,
                quietHoursEnd: a.quietHoursEnd
            )
        }
        state.completedAt = resident.onboardingCompletedAt
        return state
    }

    // MARK: - Post-onboarding edits

    func updateAlertPreferences(_ prefs: AlertPrefs) async throws {
        guard let user = Auth.auth().currentUser else { throw RepositoryError.notSignedIn }
        let row = AlertPreferencesRow(
            profileId: user.uid,
            emergencySms: prefs.emergencySms,
            emergencyPush: prefs.emergencyPush,
            medsReminders: prefs.medsReminders,
            quietHoursStart: prefs.quietHoursStart,
            quietHoursEnd: prefs.quietHoursEnd
        )
        try await client
            .from("alert_preferences")
            .upsert(row, onConflict: "profile_id")
            .execute()
    }

    func updateResident(_ resident: Resident, health: Health) async throws {
        guard let user = Auth.auth().currentUser else { throw RepositoryError.notSignedIn }
        let row = ResidentUpdateRow(
            name: resident.name?.trimmed.nilIfEmpty ?? "",
            nickname: resident.nickname?.nilIfEmpty,
            dob: resident.dob?.nilIfEmpty,
            photoPath: resident.photoUrl?.nilIfEmpty,
            mobility: health.mobility?.rawValue,
            conditions: health.conditions
        )
        try await client
            .from("residents")
            .update(row)
            .eq("owner_id", value: user.uid)
            .execute()
    }

    /// Replace-all strategy: delete the resident's family rows and re-insert.
    /// Fine at this scale (a handful of caregivers); avoids tracking server IDs locally.
    func saveFamilyList(_ members: [FamilyMember]) async throws {
        guard let user = Auth.auth().currentUser else { throw RepositoryError.notSignedIn }
        let residents: [ResidentRow] = try await client
            .from("residents")
            .select()
            .eq("owner_id", value: user.uid)
            .limit(1)
            .execute()
            .value
        guard let residentId = residents.first?.id else { return }

        try await client
            .from("family_members")
            .delete()
            .eq("resident_id", value: residentId)
            .execute()

        let rows = members.map { m in
            FamilyMemberRow(
                id: nil,
                residentId: residentId,
                name: m.name?.nilIfEmpty,
                phone: m.phone,
                relationship: m.relationship?.nilIfEmpty
            )
        }
        if !rows.isEmpty {
            try await client
                .from("family_members")
                .insert(rows)
                .execute()
        }
    }

    // MARK: - Onboarding (one-shot commit)

    /// Writes the entire onboarding state to Supabase in dependency order.
    /// Called from the final step ("Finish setup"), so callers can rely on `state` being complete.
    func saveAll(_ state: OnboardingState) async throws {
        guard let user = Auth.auth().currentUser else { throw RepositoryError.notSignedIn }
        let uid = user.uid

        // 1) profile (FK target for the rest)
        let profile = ProfileRow(
            id: uid,
            email: user.email,
            phone: state.caregiver.phone?.nilIfEmpty
        )
        try await client
            .from("profiles")
            .upsert(profile, onConflict: "id")
            .execute()

        // 2) resident — one per profile, so upsert manually
        let existing: [ResidentRow] = try await client
            .from("residents")
            .select()
            .eq("owner_id", value: uid)
            .limit(1)
            .execute()
            .value

        let residentRow = ResidentRow(
            id: existing.first?.id,
            ownerId: uid,
            name: state.resident.name?.trimmed.nilIfEmpty ?? "",
            nickname: state.resident.nickname?.nilIfEmpty,
            dob: state.resident.dob?.nilIfEmpty,
            photoPath: state.resident.photoUrl?.nilIfEmpty,
            mobility: state.health.mobility?.rawValue,
            conditions: state.health.conditions,
            onboardingCompletedAt: ISO8601DateFormatter().string(from: Date())
        )

        let savedResident: ResidentRow
        if existing.first != nil {
            savedResident = try await client
                .from("residents")
                .update(residentRow)
                .eq("owner_id", value: uid)
                .select()
                .single()
                .execute()
                .value
        } else {
            savedResident = try await client
                .from("residents")
                .insert(residentRow)
                .select()
                .single()
                .execute()
                .value
        }

        // 3) family_members — replace strategy (delete + insert)
        guard let residentId = savedResident.id else { return }
        try await client
            .from("family_members")
            .delete()
            .eq("resident_id", value: residentId)
            .execute()

        let memberRows = state.family.map { member in
            FamilyMemberRow(
                id: nil,
                residentId: residentId,
                name: member.name?.nilIfEmpty,
                phone: member.phone,
                relationship: member.relationship?.nilIfEmpty
            )
        }
        if !memberRows.isEmpty {
            try await client
                .from("family_members")
                .insert(memberRows)
                .execute()
        }

        // 4) alert preferences
        let alertRow = AlertPreferencesRow(
            profileId: uid,
            emergencySms: state.alerts.emergencySms,
            emergencyPush: state.alerts.emergencyPush,
            medsReminders: state.alerts.medsReminders,
            quietHoursStart: state.alerts.quietHoursStart,
            quietHoursEnd: state.alerts.quietHoursEnd
        )
        try await client
            .from("alert_preferences")
            .upsert(alertRow, onConflict: "profile_id")
            .execute()
    }
}
