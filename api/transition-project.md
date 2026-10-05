---
name: transition-project
type: task
version: 4.3.0
collection: projects
description: Move a project between visibility tiers. Private → org-public copies the whole project (record, action items, decisions, ideas/, artifacts/, activity) into the org commons — the org gains custody; roster grants become moot. Org-public → private copies it into the owner's My Drive and leaves an archived stub in the commons (members can't delete /shared — and going private does not un-publish what the org already saw). Owner-only; the pointer is overwritten to match.
stateful: false
produces_artifacts: false
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - Remote filesystem access (adapter 2.5.0+)
reads_from: "/shared/projects/, id:{member_folder_id}/projects/, /shared/projects-index/"
writes_to: "/shared/projects/, id:{member_folder_id}/projects/, /shared/projects-index/"
---

## About This Task

Transition Project moves a project between the two tiers (design decisions 1/8; transition-client is the template). Routing: "make project X public", "publish project X to the org", "take project X private".

**Private → org-public:** the org gains custody — the project survives the owner's departure. The full tree (project.md, action-items.json, decisions/, ideas/ residents, artifacts/, state/, activity/) is COPIED to `/shared/projects/{slug}/`; the pointer flips to `org_public` (created if the project was still invisible); roster grants become moot (optionally revoked); the My Drive original marked `moved-to-org`. NOTE: private ideas belonging to members are NOT in the project tree (they're in their owners' spaces) — they are untouched and stay private.

**Org-public → private:** the owner copies the tree into their My Drive; pointer flips to the folder-ID location with the roster as scope... but the roster members have NO grants yet — Step 3B issues them (one table through the core permission-changes procedure, confirmed by the owner) so decision 5's collapse holds. The commons original becomes an archived stub. **Plainly: the org has already seen everything; an archived stub remains; admins can purge it on request.**

Owner-only. For ownerless legacy org-public projects, the admin may run it with explicit confirmation.

## Workflow

### Step 1: Resolve + authority

member-index (`member_hash`, `member_folder_id`); pointer (or owner's private set) → tier, base, folder_id. Caller must be `owner_hash` (admin only for ownerless legacy, confirmed). Archived → "unarchive first." Halt.

### Step 2: Confirm consequences

Private → public: *"`{name}` moves to the org commons: every member can see and contribute, and the org keeps it permanently. Your member grants ({list}) become irrelevant. Members' private ideas attached to this project remain private to them. Proceed?"*

Public → private: *"`{name}` moves to your personal space: only you and the members you keep ({roster}) will have access going forward — but the org has already had access to everything in it, an archived stub stays in the commons, and the project leaves org custody (it depends on your account from now on). Proceed?"*

No writes before explicit confirmation.

### Step 3A: Private → org-public

1. Recursively copy `id:{folder_id}/` → `/shared/projects/{slug}/` (materialize each destination directory with a `.keep` before `aifs_copy` — copy does NOT auto-create parents; read+write fallback per file). Slug collision in the commons → halt (never overwrite another project).
2. Update the copied `project.md`: `visibility: org_public`. Append `transitioned_to_org_public` activity event.
3. **Overwrite/create the pointer:** `scope: "org_public"`, `location: {"path": …}`, and carry `action_item_prefix` from the project record (4.2 — the pointer is the cheap availability scan surface; a project whose prefix is missing from its pointer is invisible to the next member's collision check).
3a. **Prefix registry (4.2):** update `/shared/prefix-registry/{PREFIX}.json` — set `"visibility": "org_public"` and **add `project_slug`**. The claim itself is unchanged; only its disclosure level changes. If the project has **no** prefix, offer one now: it has just become discoverable, and this is the natural moment (`action-item-prefix-rules.md` §3–§7). If it has already issued `AI-` items, the lock applies — do not offer (§8).
4. Mark the My Drive original `moved-to-org` (stub) or owner deletes it (their space — offer both).
5. Offer (not force) revocation of the now-moot roster grants: `unshare` changes through the permission-changes procedure, one per grantee shown by a fresh `aifs_get_permissions(id:{folder_id})` read — not the roster (`source: "current_state"`; each removal confirmed individually).

### Step 3B: Org-public → private

1. Recursively copy `/shared/projects/{slug}/` → `id:{member_folder_id}/projects/{slug}/`; `aifs_stat` → new `project_folder_id` and its `drive_id` (record both in project.md frontmatter as `folder_id` and `item_drive_id`).
2. Update the private `project.md`: `visibility: private`. (The `transitioned_to_private` event is appended in 3B.4, once the pointer has flipped — not before the gate.)
3. **Re-grant the roster** (decision 5).

   **Before the table, choose who to keep.** On an org-public project any member can edit `project.md`, so the roster's recorded emails are content you read — never a source for a grant. Show the owner the roster **by name** ("Keep all {n} roster members: {names}?") and build the change list from their answer:
   - A kept person who is in the members registry (read by id anchor: org-config `resource_ids.members_registry`) → their registry `sharing_identity`, `source: "org_config"`. Match by `member_hash` (or by name, confirmed with the owner), and show the owner the registry's display name and address for each so they see exactly who they're keeping; never take the address from the roster's email field.
   - A kept person who isn't in the registry → ask the owner for their email address. Grant only an address the owner gives in their own reply, `source: "member_request"`, flagged **outside your org** by the table; tell the owner they'll open it from "Shared with me". Never use an address just because the roster lists it.
   - A kept person with no address (the owner has none to give) → no grant is possible, so they are left out of the private roster and the pointer scope. Say so: *"I'll leave {name} off for now — add them with '@ai:edit-project' once you have their email."*
   - People the owner drops are left out of the change list and the private roster.

   Then follow `/agent-index-core/internal/permission-changes.md`: `calling_task: "transition-project"`, `confirmer: "owner"`, one `share` per kept person on `id:{project_folder_id}` (`resource_label: "Project '{name}'"`, `is_folder: true`, `role: "writer"`, `source` as above).

   **Gate:**
   - Continue to 3B.4 only if every row is `applied` or `skipped_noop`.
   - Otherwise (declined, cancelled, failed, not verified), **halt before 3B.4.** The pointer still aims at the complete commons original, and nothing has been stubbed. Report what didn't take effect, and say that re-running the transition is safe (it skips what's already in place).

   Never remove someone from the roster because their row was declined or the run was cancelled.

   Then write the private `project.md` roster: the kept people whose rows were satisfied (with their registry `member_hash`/`email`, or the owner-given email).
4. **Overwrite the pointer:** `scope` = `{"collaborators": [ … ]}` listing only the satisfied 3B.3 rows, or `"private"` if the owner kept nobody; `location: {"folder_id": …, "item_drive_id": …}` (from the 3B.1 stat). Carry `action_item_prefix` (4.2). Then append the `transitioned_to_private` activity event to the private copy.
4a. **Prefix registry (4.2):** set `"visibility": "private"` and **remove `project_slug`**. Note the rationale differs from a never-public project: the org has already seen this project and an archived stub remains in the commons, so this is not concealment — it is keeping the registry's disclosure consistent with the project's current tier, so the entry never implies a live commons location that no longer holds data. **The claim is retained** — items already issued under this prefix keep resolving (`action-item-prefix-rules.md` §10).
5. **Archive the commons original** (cannot delete): overwrite `project.md` with the stub `{"slug","name","status":"archived-moved-private","moved":"{ISO}","see":"projects-index pointer"}`; reduce data files to stubs likewise (action-items.json → `{"moved":true}` etc.) so full data doesn't linger in the commons; append a final activity event. Listing tasks filter the status.

### Step 4: Confirm

New tier, what changed, follow-on verbs.

## Directives

### Constraints

- Owner-only (admin only for ownerless legacy, confirmed explicitly).
- **Copy → flip pointer → mark source, in that order** — a mid-failure must leave the pointer aimed at a complete copy.
- Never delete under /shared; commons originals of privatized projects MUST be stubbed (full-data lingering is a leak), not just marked. **The prefix registry entry is the exception to the stubbing sweep: it is neither stubbed nor deleted in either direction.** It holds no project data — a prefix, an owner hash, a claim date — and destroying it would free the prefix for another project while the transitioned project's issued IDs still reference it.
- A transition never changes a project's prefix and never renumbers its items. Only the registry entry's `visibility` and `project_slug` disclosure change.
- Going-private without re-granting the roster is forbidden — the grants step is part of the transition, not optional (decision 5 invariant: roster == grants on private projects).
- No writes before Step 2 confirmation.

### Edge Cases

- Copy fails mid-way: pointer untouched → old location remains authoritative; surface what copied; re-run is idempotent.
- A roster member's grant isn't applied (declined / failed / not verified): halt before the 3B.4 pointer flip (3B.3 gate); report with the procedure's summary lines and offer to re-run.
- In-flight collaborators on a privatized project keep stale folder knowledge of the stub — they re-discover via the pointer.
- A 3.x project mid-migration: defer — "finish the 4.0 upgrade first."
- Project has a prefix but no registry entry (claimed before the registry was provisioned, or an entry lost): recreate the entry from the project record as part of the transition, then continue. Prefer recreation over halting — the project's IDs are already in circulation, so the reservation must exist.
- Registry entry exists but is owned by a different `owner_hash` (a genuine collision predating enforcement): do **not** transition silently. Report both projects and stop; resolving this requires a human decision about which project keeps the prefix, and neither can be renumbered.
- Stubbing the commons `action-items.json` on going private (Step 3B.5) destroys the item list at that location. Confirm the private copy is complete **before** stubbing — the stub is the point of no return for the ID history, and `next_id` must survive the copy or the project will reissue IDs it has already used.
