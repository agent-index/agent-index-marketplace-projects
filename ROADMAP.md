# Projects Collection — Roadmap

Current version: 4.2.0
Last updated: 2026-07-28

---

## Current State

The collection covers the full project lifecycle — structured briefs, ideas, action items with dependencies, formal decision records, comms-channel integration and digests, and stakeholder status reports — on top of the org's **two-tier access model** (4.0).

**4.0 — two-tier access (breaking).** Projects are org-public by default and live in the org commons; private projects live in the owner's own member space and are *invisible* until shared or made public. Ideas are private-first and invisible by default. Artifacts inherit their parent's access structurally. Action items, decisions, reports and digests are project-record material — they follow the project's tier with no per-item prompts. Discovery runs on the pointer index `/shared/projects-index/`; `projects-manifest.json` is retired.

**4.1 — `crossdriveread`.** Pointers carry `item_drive_id` so a shared private project or idea opens correctly from another member's drive (OneDrive parity; harmless on gdrive).

**4.2 — action-item identity and description.** Action item IDs are project-prefixed and org-unique (`MOB-014`), suggested at creation, confirmed by the creator, and locked once the project issues its first item. Org admins can define, extend and deprecate action-item fields at any time via `action-item-fields.json` — **the collection ships none**, so nothing changes for an org until its admin defines one. Members can tag both projects and action items. Two reference documents at the collection root are authoritative: `action-item-prefix-rules.md` and `action-item-fields-guide.md`.

### Known Limitations

- **No cross-project view of action items.** Every task resolves a single project. "All my open items" or "every open bug in the org" requires reading each project in turn, which is slow enough to be impractical at org scale. This is the most-requested gap and is **deferred deliberately**, not overlooked — see Deferred below.
- **Structured writes go through a general-purpose file write.** Capabilities compose JSON and JSONL records and write whole files. Two data-loss incidents have resulted (an unsupported `append` flag silently replacing an activity log; a JSON-escaping error truncating an action-items file). Both were recovered from backend version history. Deferred, and tracked.
- **Field values are queryable within a project only.** `project-pulse` reports per-project counts and totals. There is no org-wide aggregation, so a field defined expecting an org-level dashboard will not deliver one yet (4.2).
- **Tags are deliberately unstructured.** Nothing prevents an item carrying two tags that ought to be mutually exclusive. A dimension that needs exactly one value should be an admin-defined `single-select` field instead.
- **Prefix uniqueness depends on the registry being provisioned.** `/shared/prefix-registry/` must exist before prefixes can be claimed; the prefix flow halts rather than proceeding without reservation, since silently skipping it is how colliding prefixes get in.
- **Channel digest relies on MCP connector availability.** If the Slack/Teams/Discord connector is unavailable, the run is marked pending. There is no retry or queue — the member runs it again later.
- **Milestone tracking is passive.** Milestones are stored and surfaced when deadlines approach, but nothing escalates a missed one.
- **Idea promotion is one-way.** A promoted artifact does not reference the idea it came from, though the idea records that promotion happened.
- **Activity log grows unbounded.** `activity-log.jsonl` is append-only with no rotation or archival.

### Known Bugs

- **Private comms channels are not discoverable.** When a project's channel is private, the Slack lookup fails because `conversations.list` defaults to public channels only. Notifications to private project channels therefore fail. Tracked as an idea in the Projects Collection project.

---

## Deferred (decided, not forgotten)

Recorded here so the absence reads as a decision rather than an oversight.

- **Cross-project action-item query.** A dedicated capability that fans reads across projects in one process and returns a filtered list, replacing per-project sequential reads. Prerequisite for org-wide field rollups ("every open bug") and for effort totals per person across projects. The precedent to follow is `/shared/projects-index/` — a materialized index — rather than adding a content search: the backend's search matches filenames only.
- **Dedicated deterministic write operations.** Intention-revealing operations (append an activity entry; upsert an action item) that own their serialization, plus guardrails on the general write path — reject unknown arguments, validate structure before commit, flag large negative size deltas. This is the fix for the data-loss class above.
- **Task lookup by ID.** Resolving an action item's title from `(project, ID)` without an agent session — needed by release-notes tooling that parses IDs out of git branch names, and the same read path a read-only web view would use. Unblocked by 4.2's org-unique IDs.
- **Team-scoped project filtering.** A member-built companion collection already does this by filtering projects to a defined team. Whether it belongs in this collection, stays a companion, or goes to the marketplace is open. Project-level tags (4.2) are the filter dimension it wants.

---

## Wishlist

### Next — Quality of Life

- **Cross-project dashboard.** A unified view of the member's projects: upcoming milestones, open action items assigned to them, recent activity. Blocked on the cross-project query above — the dashboard is the consumer, not the mechanism.
- **Milestone notifications.** Active reminders when a milestone's target date is approaching (7 days, 1 day) or has passed.
- **Activity log rotation.** Archive entries older than a configurable threshold to a dated archive file. Note the ordering constraint: rotation rewrites an append-only file, so it should follow the dedicated write operations rather than precede them.

### Later — Deeper Integration

- **Capability provider migration.** Replace the direct Slack/Teams/Discord platform branching with the capability provider model (communications capability type). This would let channel operations work through any registered communications provider.
- **Idea linking.** When an artifact is promoted from an idea, embed a reference in the promoted artifact back to the idea record, creating a bidirectional trail.
- **Action item delegation via comms.** When an action item is assigned, optionally send a notification to the assignee via the project's comms channel.

### Structural (would break)

- **Project templates.** Pre-defined project structures (brief sections, default milestones, standard roles) that can be selected at creation time. Requires a new org-level configuration surface.
- **Multi-project dependencies.** Track dependencies between projects, not just between action items within a single project.

---

## Design Notes

- The collection deliberately treats ideas as a private-first workflow, and since 4.0 private ideas are *invisible* rather than merely private: they live in the owner's own member space with no org-visible record of any kind until the owner shares or promotes them. (Before 4.0 they sat in the member's local workspace.) The reasoning is that premature visibility changes what people are willing to write down.

- Action item IDs are treated as identifiers, not metadata (4.2). A prefix is chosen once and locked once the project issues an item, and existing items are never renumbered. The constraint follows from where IDs end up: branch names, pull requests, Slack messages, release notes — places agent-index does not control and cannot update. A multi-prefix scheme was considered and rejected for the same reason; dimensions that people would encode into a prefix belong in fields or tags.

- Adding an org field never rewrites existing items (4.2). An item with no value reads as the field's default, resolved at read time. The alternative — a migration pass inserting defaults across every project's action-items file — is a mass write for no new information, in exactly the operation class that has already caused data loss here.

- Channel digest is the sole entry point for reading comms channel messages. This was a v3.0.3 fix — ad-hoc requests to "read the channel" were bypassing the cursor and review queue, wasting context and skipping human validation. All channel message reading must go through channel-digest.

- Project pulse is designed for stakeholder consumption, not team coordination. It produces a curated status summary, not a raw dump of activity. The distinction matters for what gets included and how it's framed.
