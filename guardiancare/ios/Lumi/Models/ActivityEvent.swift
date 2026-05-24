import Foundation
import SwiftUI

struct ActivityEvent: Identifiable, Equatable {
    let id: UUID
    let kind: Kind
    let title: String
    let detail: String?
    let timestamp: Date
    let imageURL: URL?

    init(
        id: UUID = UUID(),
        kind: Kind,
        title: String,
        detail: String? = nil,
        timestamp: Date,
        imageURL: URL? = nil
    ) {
        self.id = id
        self.kind = kind
        self.title = title
        self.detail = detail
        self.timestamp = timestamp
        self.imageURL = imageURL
    }

    enum Kind: String, Codable, Equatable {
        case meal
        case medication
        case fall
        case distress
        case visitor
        case unknownVisitor
        case mood
        case sleep
        case walking

        var icon: String {
            switch self {
            case .meal:           return "fork.knife"
            case .medication:     return "pill.fill"
            case .fall:           return "figure.fall"
            case .distress:       return "exclamationmark.bubble.fill"
            case .visitor:        return "person.crop.circle.badge.checkmark"
            case .unknownVisitor: return "person.crop.circle.badge.questionmark"
            case .mood:           return "face.smiling.fill"
            case .sleep:          return "bed.double.fill"
            case .walking:        return "figure.walk"
            }
        }

        var category: ActivityCategory {
            switch self {
            case .fall, .distress:          return .alerts
            case .visitor, .unknownVisitor: return .visitors
            case .meal, .medication:        return .health
            case .mood, .sleep, .walking:   return .daily
            }
        }
    }
}

enum ActivityCategory: String, CaseIterable, Identifiable, Hashable {
    case alerts   = "Alerts"
    case visitors = "Visitors"
    case health   = "Meals & medication"
    case daily    = "Daily activity"

    var id: String { rawValue }

    var accent: Color {
        switch self {
        case .alerts:   return Color(red: 0.83, green: 0.18, blue: 0.18)
        case .visitors: return LumiColors.slate400
        case .health:   return Color(red: 0.20, green: 0.60, blue: 0.30)
        case .daily:    return LumiColors.slate400
        }
    }
}

extension ActivityEvent {
    /// Sample feed — wire to a Supabase `events` table later.
    static func sample(now: Date = Date()) -> [ActivityEvent] {
        func ago(_ minutes: Int) -> Date {
            now.addingTimeInterval(TimeInterval(-minutes * 60))
        }
        return [
            ActivityEvent(kind: .fall,
                          title: "Possible fall detected",
                          detail: "In the living room",
                          timestamp: ago(2)),
            ActivityEvent(kind: .unknownVisitor,
                          title: "Unknown person at the door",
                          detail: "Front entrance",
                          timestamp: ago(14)),
            ActivityEvent(kind: .visitor,
                          title: "Sarah arrived",
                          detail: "Recognized from photos",
                          timestamp: ago(60)),
            ActivityEvent(kind: .meal,
                          title: "Margaret ate breakfast",
                          detail: "Oatmeal and tea",
                          timestamp: ago(75)),
            ActivityEvent(kind: .medication,
                          title: "Took medication",
                          detail: "Lisinopril 10 mg",
                          timestamp: ago(180)),
            ActivityEvent(kind: .walking,
                          title: "Walked to the kitchen",
                          timestamp: ago(230)),
            ActivityEvent(kind: .mood,
                          title: "Margaret seemed cheerful",
                          timestamp: ago(300)),
            ActivityEvent(kind: .sleep,
                          title: "Woke up",
                          detail: "After about 7 hours of sleep",
                          timestamp: ago(420)),
            ActivityEvent(kind: .sleep,
                          title: "Went to bed",
                          timestamp: ago(840)),
        ]
    }
}
