import Foundation
import Supabase
import FirebaseAuth

enum SupabaseService {
    static let client: SupabaseClient = {
        SupabaseClient(
            supabaseURL: SupabaseConfig.url,
            supabaseKey: SupabaseConfig.publishableKey,
            options: SupabaseClientOptions(
                // Every PostgREST request will carry the current Firebase ID token,
                // which Supabase verifies via the third-party Firebase auth integration.
                // RLS policies read auth.jwt() ->> 'sub' to get the Firebase UID.
                auth: SupabaseClientOptions.AuthOptions(
                    accessToken: {
                        try await Auth.auth().currentUser?.getIDToken()
                    }
                )
            )
        )
    }()
}
