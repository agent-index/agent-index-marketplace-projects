# Projects Collection — Changelog

All notable changes to this collection will be documented here.

Format: [MAJOR.MINOR.PATCH] — YYYY-MM-DD

---

## [4.3.0] — <RELEASE_DATE> — a project keeps the IDs it already issues

### Corrects a 4.2.0 statement

The 4.2.0 entry below says existing projects "keep issuing `AI-` IDs and are not renamed."
**The second half was true; the first half was false**, and it is retracted here rather than quietly
dropped. 4.2 resolved an absent prefix to the constant `AI`, on the assumption that projects
predating the feature had been issuing `AI-001`-style IDs — because `AI-` was hardcoded in 4.1. In
practice projects were already using their own conventions (`AC-`, `AW-`, `CI-`, bare integers),
since members had been hand-rolling prefixes, which is what motivated the feature. On 4.2 a project
on `AC-040` would issue `AI-041` next, and the prefix lock made that split permanent.

Nothing was ever renamed or renumbered — that half held.

### Fixed

- **A project now keeps issuing the IDs it already issues.** The effective prefix resolves as:
  recorded `action_item_prefix` → else the prefix in use, derived from the highest existing item ID
  → else `AI`, which is now reachable only for a project with no items at all. The 4.2 constant is
  removed.
- **Prefixes already in use can be reserved.** They held no registry claim, so another project could
  be told one was free and mint colliding IDs. `manage-action-items` now offers to claim a derived
  prefix at the point of use, and `upgrade/4-2-to-4-3.md` offers the same in bulk for an admin.
  Claims carry the **project owner's** hash; an admin reconciling a project does not become its owner.
- `default: null` on an action-item field is valid on **every** type and means "no default". The 4.2
  validation rule rejected any non-numeric default, which rejected the admin guide's own
  `estimated_size` example.
- `edit-project` now matches the prefix rules on what "issued" means — a non-empty `items` array
  **or** `next_id > 1`, failing closed if the file can't be read. 4.2's text contradicted the rules
  reference it told the reader to follow.
- The lost-race message is scripted verbatim. `REVISION_CONFLICT` is never shown to a member.
- The registry README no longer claims entries are "never deleted" — there is exactly one case where
  one is removed. Both the setup template and any README already provisioned under 4.2 are corrected.
- `create-project` no longer restates a derivation example that had drifted from the normative table.
- `setup/collection-setup.md` version was stale at 3.0.6 across three releases; now tracks the collection.

### Added

- `upgrade/4-2-to-4-3.md` — admin bulk reconciliation. Presents each visible project's in-use prefix
  for accept / override / skip; nothing is guessed. Conflicts are reported and skipped rather than
  aborting the pass. Re-runnable, and once an org is reconciled the re-run **is** the
  duplicate-issuance audit.
- A one-time session-start mention of private projects with an unclaimed prefix — the bulk upgrade
  cannot see private projects by design, so this is how their owners find out.

### Notes

- **Nothing existing is rewritten.** Item IDs are never renumbered to add or change a prefix. Items
  that predate any convention stay out of compliance permanently, by design.
- The upgrade is **recommended, not required**: everything it does also happens per-project the next
  time a member adds an action item.

---

## [4.2.0] — 2026-07-28 — action-item identity and description

### Requires Admin Attention (read BEFORE provisioning)

Two new provisioned objects: **`/shared/prefix-registry/`** (a directory; members write their own
prefix claims, so `collaborative-acls.json` gains an all-members writer grant) and
**`action-item-fields.json`** (an empty scaffold at the org root, admin-writable). Re-run
`@ai:install-collection projects` so Step 5.5 provisions both.

**Nothing changes for your org until you act.** No field definitions ship — the config is an empty
list, so members see no field prompts. Existing projects keep issuing `AI-` IDs and are not
renamed, renumbered, or rewritten. If `/shared/prefix-registry/` is missing, the prefix flow halts
with a provisioning message rather than issuing unreserved prefixes; if `action-item-fields.json`
is missing or empty, fields are simply absent and everything else works.

### Added

- **Per-project action-item ID prefixes.** Action items are numbered `{PREFIX}-{NNN}` (`MOB-014`).
  `create-project` derives a candidate from the project name, checks availability, and requires
  explicit confirmation; the member may override. Prefixes are **unique across the org**, reserved
  one-file-per-prefix in `/shared/prefix-registry/` via a two-write claim protocol: write the record,
  then write it again passing `if_revision`. The guarded second write is what establishes the claim —
  a same-path write overwrites rather than creating a sibling, so without it a losing claimant would
  silently destroy the winner's record and both projects would mint colliding IDs. Interleaving two
  claimants elects exactly one winner, and the loser is told rather than discovering the collision
  later. `AI` is reserved and unclaimable — it is the implicit prefix for every pre-4.2 project.
  Rules: `action-item-prefix-rules.md`.
- **Org-defined action-item fields.** Admins add, extend and deprecate fields at any time in
  `action-item-fields.json` — types `string`, `number`, `single-select`, `date`. Values are stored
  nested under `fields` on each item so an admin-chosen key can never collide with a built-in.
  `manage-action-items` prompts and validates; `project-pulse` renders values with labels and units
  and produces per-project breakdowns (counts per option, totals overall and per assignee).
  Adding a field **never rewrites existing items** — a missing value resolves to the field's default
  at read time. Guide: `action-item-fields-guide.md`.
- **Tags on projects and action items.** Free-form, member-owned, normalized on write (lowercase,
  hyphenated). Existing project tags are suggested when tagging an item. Project and item tags are
  independent namespaces — no inheritance.
- **`transition-project` keeps the registry consistent with tier.** Going public adds `project_slug`
  to the registry entry and carries the prefix into the pointer; going private removes the slug and
  **retains the claim**. A project that becomes discoverable without a prefix is offered one.

### Changed

- Discovery pointers carry `action_item_prefix` so availability checks are a cheap index scan.
- `project.md` frontmatter gains `action_item_prefix`, `prefix_history`, and `tags`.
- `edit-project` can set a prefix on a project that has none — which is how pre-4.2 projects adopt
  one — and **refuses to change it once the project has issued any action item**, stating why.
  Existing IDs are never renumbered.
- README documents `transition-project`, which shipped in 4.0.0 but was never added to the
  capability list, and no longer describes private ideas as living in the member's *local*
  workspace (untrue since 4.0).
- ROADMAP rewritten; it had stated "Current version: 3.0.6" since 2026-05-02. Now carries a
  **Deferred (decided, not forgotten)** section naming the cross-project query, dedicated write
  operations, task lookup by ID, and team-scoped filtering.

### Fixed

- **`create-idea` built paths from a setup parameter removed in 4.0.** Two edge cases substituted
  `{shared_projects_path}` when creating a project's `ideas/` or `activity/` directory on first use.
  That parameter was removed in 4.0 (the commons is the fixed `/shared/projects/`), so the
  substitution yielded a broken path. Both now use the tier-resolved project base. Found by
  preflight during the 4.2 release, not by a member report — it had shipped since 4.0.0.
- **`create-idea` described private ideas as living at `/members/{member_hash}/ideas/`.** The leading
  slash reads as the deprecated remote member space, and 4.0 moved private ideas into the owner's own
  drive. The constraint and edge case now name `id:{member_folder_id}/ideas/...`.

### Notes

- **Scope, stated plainly:** field and tag queries resolve **one project at a time**. There is no
  org-wide rollup in 4.2 — "every open bug in the org" is not answerable yet, and needs the deferred
  cross-project query capability.
- The prefix lock is a one-way door by design. An ID leaves agent-index's control the moment it
  appears in a branch name, pull request, or document; renaming a prefix would invalidate those
  references and renumbering would invalidate the rest.

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
