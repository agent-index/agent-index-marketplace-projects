# Projects Collection — Changelog

All notable changes to this collection will be documented here.

Format: [MAJOR.MINOR.PATCH] — YYYY-MM-DD

---

## [3.0.6] — 2026-05-02

### Added

- **Trigger phrases for three previously trigger-less capabilities** — `unarchive-project` ("reopen project," "unarchive project"), `share-idea` ("share an idea," "publish my idea"), `manage-ideas` ("show my ideas," "manage ideas," "idea list"). Seven new natural-language phrases total, bringing the trigger-coverage of the projects collection in line with the rest of the v3.0.5+ trigger-bearing capabilities.

### Changed

- **`collection.json` `api` array reformatted** from compact one-line-per-entry form to multi-line object form. Improves readability when reviewing or editing trigger blocks; no functional change.
- **All API-member manifests bumped** to `collection_version: 3.0.6`. (Reconciles bookkeeping drift from the 3.0.5 release where manifests weren't synced.)
- **`ROADMAP.md`** Current-version and Last-updated lines bumped to 3.0.6 / 2026-05-02.
- **`setup/collection-setup.md`** frontmatter `version` bumped to 3.0.6 to match the collection.

### Fixed

- **`agent_index_min_version` regression corrected** — was downgraded to 2.0.0 in the 3.0.6 working-tree edit, restored to 3.0.0 (the actual minimum that projects depends on; reverting to 2.0.0 would let the collection install on agent-index versions that can't run it).

### Notes

This release was assembled from a working-tree state that had drifted on dev_source: a previous edit pass had bumped `collection.json` to 3.0.6 with new trigger phrases and a JSON reformat, but never wrote a CHANGELOG entry, never synced the manifests, and accidentally regressed `agent_index_min_version`. The cleanup landed all the bookkeeping that should have accompanied the original edit, surfaced and corrected the min-version regression, and shipped 3.0.6 as the canonical "everything synced" release. The new developer 1.2.2 preflight checks (manifest `collection_version` sync) caught the manifest drift; the existing Step 4 CHANGELOG-entry check caught the missing entry; the existing `agent_index_min_version`-vs-frontmatter check did not catch the regression because the value is collection-level not per-capability — file separately as a preflight enhancement idea.

---

## [3.0.5] — 2026-04-19

### Added
- **Natural language trigger phrases in `collection.json`.** API entries now include trigger arrays that map conversational phrases to capabilities, powering the routing layer introduced in agent-index-core 3.0.5. Members can say things like "what's on my plate" or "project pulse" instead of using `@ai:` alias syntax. Triggers are customizable per-member via `routing.json`.

---

## [3.0.4] — 2026-04-05

### Added
- Slack app prerequisite guidance in collection setup — when the org admin selects Slack as their comms platform, the setup interview now explains that a Slack app with the required OAuth scopes must exist before members can generate their user tokens

---

## [3.0.3] — 2026-04-01

### Fixed
- Ad-hoc "read the channel and update the project" requests bypassed the `channel-digest` task, reading the entire channel history without using the cursor — wasting context on already-processed messages and skipping the review queue
- Added channel source check to `update-project` Step 1: if the member's update source is a comms channel, hand off to `channel-digest` instead of reading the channel directly
- Added sole-entry-point constraint to `channel-digest` Directives: no other task or ad-hoc request should read channel messages outside of this task

---

## [3.0.2] — 2026-04-01

### Fixed
- 7 task files (archive-project, edit-project, update-project, unarchive-project, create-idea, channel-digest, manage-action-items) were missing explicit `aifs_read` / `aifs_*` tool references — agents defaulted to local file reads and reported "no projects found" even when remote data existed
- Added **Tool selection** block and explicit `via aifs_read` qualifiers to all affected files, matching the pattern already used in newer tasks (manage-ideas, project-decide, project-pulse, share-idea)

---

## [3.0.1] — 2026-03-31

### Changed
- All tasks and setup files now attempt automatic re-authentication on auth failures instead of prompting users to say `@ai:member-bootstrap`

---

## [3.0.0] — 2026-03-25

### Changed
- `agent_index_min_version` bumped to `2.0.0` — requires agent-index-core v2.0.0 with remote filesystem support
- All `@ai:fs-setup` references updated to `@ai:member-bootstrap`
- Shared project data operations (`/shared/projects/`) now reference `aifs_*` MCP tools for remote filesystem access
- `members-registry.json` reads updated to use `aifs_read` with corrected path (`/members-registry.json`)
- `collection-setup-responses.md` reads updated to use `aifs_read`
- Setup file parameter descriptions updated: "filesystem path" → "remote filesystem path"
- README updated to reference remote filesystem model
- `produces_shared_artifacts: true` tasks now declare `reads_from`/`writes_to` paths under `/shared/projects/`

### Added
- `create-idea` — create private ideas in member workspace for later sharing
- `share-idea` — promote private ideas to project shared space with collaborator assignments
- `manage-ideas` — view, edit, and manage ideas with artifact promotion
- `update-project` — incremental project updates with activity log integration
- `manage-action-items` — track action items with dependencies and status workflows
- `project-decide` — record project decisions with rationale and spawned action items
- `channel-digest` — summarize project channel conversations and extract candidate items
- `project-pulse` — status report generation and conversational project Q&A
- `projects-tutorial` — guided tour of the projects collection
- Project brief with configurable sections (description, goals, success criteria, constraints, dependencies, stakeholders, risks)
- Project milestones with target dates and status tracking
- Communications channel integration (Slack, Teams, Discord)
- Activity logging (append-only `activity-log.jsonl`)
- Channel monitoring with configurable cadence

---

## [1.0.0] — 2026-03-17

### Added
- Initial release
- `create-project` task — create new projects with scope, ownership, member list, and roles
- `edit-project` task — edit any field of an active project
- `archive-project` task — archive an active project
- `unarchive-project` task — restore an archived project to active status
- `collection-setup.md` — org admin configuration for shared projects path and roles mode
- `projects-manifest.json` initialization at collection setup
- Three roles configuration modes: `org-mandated`, `org-suggested`, `project-defined`
