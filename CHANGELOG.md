# Projects Collection — Changelog

All notable changes to this collection will be documented here.

Format: [MAJOR.MINOR.PATCH] — YYYY-MM-DD

---

## [4.1.0] — 2026-06-28 — Release C.1.3: crossdriveread

### Fixed
- **`crossdriveread` — shared private projects/ideas are now openable cross-drive.** On OneDrive a bare `id:{folder_id}` anchor resolves against the reader's own drive and 404s for content held in the owner's personal drive. Pointer-writers (`share-idea`, `create-project`, `edit-project`) now capture the item's `drive_id` from `aifs_stat` and write `item_drive_id` into the discovery pointer; readers (`edit-project`, `update-project`, `project-pulse`, `manage-ideas`) open shared-with-me content via the cross-drive anchor `id:{item_drive_id}:{folder_id}/...` (bare-anchor fallback for older pointers). Requires onedrive adapter 2.3.0+; harmless on gdrive.

---

## [4.0.0] — 2026-06-06 — two-tier access model (MAJOR, breaking)

### Requires Admin Attention (read BEFORE provisioning)

**The upgrade ships ACL and setup-interview changes** (`collaborative-acls.json` is new;
`projects_default_visibility`/`ideas_default_visibility` replace `shared_projects_path`/
`ideas_require_private_stage`) — upgrade-collection Step 6.5 will flag provisioning. **ORDERING:
run `upgrade/3-to-4.md`'s admin half (project inventory → pointer-index build; gated-idea review;
`projects-manifest.json` retirement) BEFORE `@ai:install-collection projects` applies the
commons grants.** The inventory must touch ONLY real projects (directories with `project.md`) —
`/shared/projects/` also hosts org record spaces that are not projects.

### Why a MAJOR

The cross-collection access audit's final row: under least-privilege, members were reader-only on
`/shared`, so every 3.x project write (action items, updates, decisions, idea promotion, digests)
failed for non-admins. 4.0 fixes it with the org's two proven access models, plus the visibility
outcomes decided 2026-06-06 (design doc 10, all eight decisions).

### Changed

- **Projects are two-tier.** ORG-PUBLIC (default): `/shared/projects/{slug}/` commons, uniform
  `all@` writer (install-time grant), every write activity-attributed. PRIVATE: the owner's own
  My Drive, **invisible until shared** — no org-visible record exists; the roster IS the grant
  list (adding a member = an owner-approved collaborator grant, Accept-gated and verified; the
  first member ends invisibility). New **transition-project** moves projects between tiers
  (copy → pointer flip → stub; going-private re-grants the roster and stubs the commons original).
- **Ideas are private-and-invisible by default**, stored at `id:{member_folder_id}/ideas/…`
  (4.0 — previously the local workspace; remote member space is what makes selective sharing
  possible). **share-idea reworked into three moves**: share with people (per-person grants +
  pointer-on-first-share), promote into the project (relocation + tier adoption — the 3.x flow),
  unshare (revoked pointer). Legacy local ideas get a one-time move offer on first touch.
- **Artifacts inherit structurally** — they live inside their parent item's folder; no per-item
  permissions. Widening overrides (publishing an artifact beyond its parent's audience) require
  an explicit warning + a hygiene pointer that never names the private parent; narrowing
  relocates into the owner's space + grants.
- **Action items, decisions, status reports, digests are project-record material** — tier follows
  the project, no per-item prompts; private-project action items can only be assigned to people
  with access (prompt-to-add-member guard).
- **Discovery via `/shared/projects-index/`** (pointer per discoverable item);
  `projects-manifest.json` retired. Archive/unarchive update pointer status; never-shared private
  projects may be permanently deleted by their owner (clean vanish); ever-shared items keep a
  permanent name-record.
- All 13 capabilities reworked or rewritten to 4.0.0; projects-tutorial rewritten for the model.

### Added

- `collaborative-acls.json` — `all@` writer on `/shared/projects/` and `/shared/projects-index/`.
- `upgrade/3-to-4.md` — REQUIRED MAJOR migration (admin inventory + gated-idea review with
  role-divergence detection + manifest retirement + provisioning order; member half optional).
- `transition-project` task (+ setup + manifest + routing triggers).

### Requirements

- agent-index-core **3.9.0+**, gdrive adapter **2.5.0+**, permission-helper-go **0.4.1+**.
- 3.x line: `eol_date` set 90 days from this release (2026-09-04) per EOL policy.

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
