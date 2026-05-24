import Foundation

extension String {
    var trimmed: String {
        trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var nilIfEmpty: String? {
        isEmpty ? nil : self
    }
}

extension Optional where Wrapped == String {
    var nilIfEmpty: String? {
        switch self {
        case .some(let value) where !value.isEmpty: return value
        default: return nil
        }
    }
}
