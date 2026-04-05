# Projects Collection — Roadmap

Current version: 3.0.4
Last updated: 2026-04-05

---

## Current State

v3.0 is a major expansion from the original CRUD-only project management collection. It now covers the full project lifecycle: structured briefs, ideas (private-to-shared promotion), action items with dependencies, formal decision recording, comms channel integration (Slack, Teams, Discord), channel monitoring with digest extraction, and stakeholder status reports via project pulse. A guided tutorial helps new members onboard.

### Known Limitations

- **Channel digest relies on MCP connector availability.** If the Slack (or Teams/Discord) MCP connector is unavailable, channel digest silently marks the run as pending. There's no retry or queuing mechanism — the member has to run it again later.
- **No cross-project views.** Each task operates on a single project at a time. There's no "dashboard" view showing action items, milestones, or pulse across all projects a member is involved in.
- **Milestone tracking is passive.** Milestones are stored and surfaced by session-start tasks when deadlines approach, but there's no active notification or escalation when a milestone is missed.
- **Idea promotion is one-way.** Once an idea's artifact is promoted to the project, there's no link back to the original idea's development history. The idea record tracks that promotion happened, but the promoted artifact doesn't reference its origin.
- **Activity log grows unbounded.** The `activity-log.jsonl` file is append-only with no archival or rotation. For very active projects over long periods, this file could become large.

### Known Bugs

None currently tracked.

---

## Wishlist

### v3.1 — Quality of Life

- **Cross-project dashboard.** A skill that reads all projects the member is involved in and surfaces a unified view: upcoming milestones, open action items assigned to them, recent activity across projects.
- **Milestone notifications.** Active reminders when a milestone's target date is approaching (7 days, 1 day) or has passed.
- **Activity log rotation.** Archive activity log entries older than a configurable threshold to a dated archive file, keeping the active log manageable.

### v3.2 — Deeper Integration

- **Capability provider migration.** Replace the direct Slack/Teams/Discord platform branching with the capability provider model (communications capability type). This would let channel operations work through any registered communications provider.
- **Idea linking.** When an artifact is promoted from an idea, embed a reference in the promoted artifact back to the idea record, creating a bidirectional trail.
- **Action item delegation via comms.** When an action item is assigned, optionally send a notification to the assignee via the project's comms channel.

### v4.0 — Structural Changes (breaking)

- **Project templates.** Pre-defined project structures (brief sections, default milestones, standard roles) that can be selected at creation time. Requires a new org-level configuration surface.
- **Multi-project dependencies.** Track dependencies between projects, not just between action items within a single project.

---

## Design Notes

- The collection deliberately treats ideas as a private-first workflow. Ideas start in the member's local workspace and require an explicit share action to move to the project's shared space. This prevents half-formed thinking from cluttering the project record.

- Channel digest is the sole entry point for reading comms channel messages. This was a v3.0.3 fix — ad-hoc requests to "read the channel" were bypassing the cursor and review queue, wasting context and skipping human validation. All channel message reading must go through channel-digest.

- Project pulse is designed for stakeholder consumption, not team coordination. It produces a curated status summary, not a raw dump of activity. The distinction matters for what gets included and how it's framed.
