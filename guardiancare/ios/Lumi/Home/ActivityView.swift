import SwiftUI

struct ActivityView: View {
    private let events = ActivityEvent.sample()

    private var grouped: [(ActivityCategory, [ActivityEvent])] {
        let groups = Dictionary(grouping: events, by: { $0.kind.category })
        return ActivityCategory.allCases.compactMap { cat in
            guard let evs = groups[cat], !evs.isEmpty else { return nil }
            return (cat, evs.sorted(by: { $0.timestamp > $1.timestamp }))
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("Activity")
                    .font(.system(size: 24, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)

                if events.isEmpty {
                    emptyState
                } else {
                    ForEach(grouped, id: \.0) { category, events in
                        CategorySection(category: category, events: events)
                    }
                }
            }
            .padding(24)
        }
        .background(LumiColors.slate50.ignoresSafeArea())
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "clock.badge.questionmark")
                .font(.system(size: 48))
                .foregroundStyle(LumiColors.slate200)
            Text("No activity yet")
                .font(.system(size: 18, weight: .medium))
                .foregroundStyle(LumiColors.slate800)
            Text("Calls, alerts, and conversations with Lumi will appear here.")
                .font(.system(size: 14, weight: .light))
                .foregroundStyle(LumiColors.slate600)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 80)
    }
}

private struct CategorySection: View {
    let category: ActivityCategory
    let events: [ActivityEvent]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Text(category.rawValue.uppercased())
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(LumiColors.slate600)
                Text("\(events.count)")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(LumiColors.slate600)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(LumiColors.slate100)
                    .clipShape(Capsule())
                Spacer()
            }

            VStack(spacing: 8) {
                ForEach(events) { event in
                    EventCard(event: event)
                }
            }
        }
    }
}

private struct EventCard: View {
    let event: ActivityEvent

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            ZStack {
                Circle()
                    .fill(event.kind.category.accent.opacity(0.12))
                    .frame(width: 40, height: 40)
                Image(systemName: event.kind.icon)
                    .font(.system(size: 18))
                    .foregroundStyle(event.kind.category.accent)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(event.title)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(LumiColors.slate800)
                    .fixedSize(horizontal: false, vertical: true)
                if let detail = event.detail {
                    Text(detail)
                        .font(.system(size: 13, weight: .light))
                        .foregroundStyle(LumiColors.slate600)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text(relative(event.timestamp))
                    .font(.system(size: 12, weight: .light))
                    .foregroundStyle(LumiColors.slate600)
                    .padding(.top, 2)
            }

            Spacer(minLength: 0)

            if let url = event.imageURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        RoundedRectangle(cornerRadius: 8).fill(LumiColors.slate100)
                    case .success(let image):
                        image.resizable().scaledToFill()
                    case .failure:
                        RoundedRectangle(cornerRadius: 8).fill(LumiColors.slate100)
                    @unknown default:
                        RoundedRectangle(cornerRadius: 8).fill(LumiColors.slate100)
                    }
                }
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            }
        }
        .padding(14)
        .background(.white)
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(LumiColors.slate100, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func relative(_ date: Date) -> String {
        let fmt = RelativeDateTimeFormatter()
        fmt.unitsStyle = .short
        return fmt.localizedString(for: date, relativeTo: Date())
    }
}
