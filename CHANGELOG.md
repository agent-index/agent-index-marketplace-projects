# Projects Collection — Changelog

All notable changes to this collection will be documented here.

Format: [MAJOR.MINOR.PATCH] — YYYY-MM-DD

---

## [3.0.1] — 2026-03-31

### Changed
- All tasks and setup files now attempt automatic re-authentication on auth failures instead of prompting users to say `@ai:member-bootstrap`

---

## [3.0.0] — 2026-03-25

### Changed
- `agent_index_min_version` bumped to `2.0.0` — requires agent-index-core v2.0.0 with MCP server support
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
