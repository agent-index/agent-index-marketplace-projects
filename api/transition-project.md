---
name: transition-project
type: task
version: 4.0.0
collection: projects
description: Move a project between visibility tiers. Private → org-public copies the whole project (record, action items, decisions, ideas/, artifacts/, activity) into the org commons — the org gains custody; roster grants become moot. Org-public → private copies it into the owner's My Drive and leaves an archived stub in the commons (members can't delete /shared — and going private does not un-publish what the org already saw). Owner-only; the pointer is overwritten to match.
stateful: false
produces_artifacts: false
produces_shared_artifacts: true
dependencies:
  skills:
    - permission-change-helper
  tasks: []
external_dependencies:
  - Remote filesystem access (adapter 2.5.0+)
  - permission-change-helper binary 0.4.1+ (only when revoking moot grants during a go-public)
reads_from: "/shared/projects/, id:{member_folder_id}/projects/, /shared/projects-index/"
writes_to: "/shared/projects/, id:{member_folder_id}/projects/, /shared/projects-index/"
---

## About This Task

Transition Project moves a project between the two tiers (design decisions 1/8; transition-client is the template). Routing: "make project X public", "publish project X to the org", "take project X private".

**Private → org-public:** the org gains custody — the project survives the owner's departure. The full tree (project.md, action-items.json, decisions/, ideas/ residents, artifacts/, state/, activity/) is COPIED to `/shared/projects/{slug}/`; the pointer flips to `org_public` (created if the project was still invisible); roster grants become moot (optionally revoked); the My Drive original marked `moved-to-org`. NOTE: private ideas belonging to members are NOT in the project tree (they're in their owners' spaces) — they are untouched and stay private.

**Org-public → private:** the owner copies the tree into their My Drive; pointer flips to the folder-ID location with the roster as scope... but the roster members have NO grants yet — Step 3B issues them (one batch spec, owner Accepts) so decision 5's collapse holds. The commons original becomes an archived stub. **Plainly: the org has already seen everything; an archived stub remains; admins can purge it on request.**

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
3. **Overwrite/create the pointer:** `scope: "org_public"`, `location: {"path": …}`.
4. Mark the My Drive original `moved-to-org` (stub) or owner deletes it (their space — offer both).
5. Offer (not force) revocation of the now-moot roster grants (ONE unshare spec, owner Accepts, hard gate).

### Step 3B: Org-public → private

1. Recursively copy `/shared/projects/{slug}/` → `id:{member_folder_id}/projects/{slug}/`; `aifs_stat` → new `project_folder_id` (record in project.md frontmatter).
2. Update the private `project.md`: `visibility: private`. Append `transitioned_to_private` event.
3. **Re-grant the roster** (decision 5): ONE spec, a `writer` grant per registered roster member on `id:{project_folder_id}`; owner Accepts; HARD GATE. Members the owner drops at this step are removed from the roster. Unregistered roster entries: noted, no grant possible.
4. **Overwrite the pointer:** `scope` = roster object (`{"collaborators": […]}`) or `"private"` if the owner kept nobody; `location: {"folder_id": …}`.
5. **Archive the commons original** (cannot delete): overwrite `project.md` with the stub `{"slug","name","status":"archived-moved-private","moved":"{ISO}","see":"projects-index pointer"}`; reduce data files to stubs likewise (action-items.json → `{"moved":true}` etc.) so full data doesn't linger in the commons; append a final activity event. Listing tasks filter the status.

### Step 4: Confirm

New tier, what changed, follow-on verbs.

## Directives

### Constraints

- Owner-only (admin only for ownerless legacy, confirmed explicitly).
- **Copy → flip pointer → mark source, in that order** — a mid-failure must leave the pointer aimed at a complete copy.
- Never delete under /shared; commons originals of privatized projects MUST be stubbed (full-data lingering is a leak), not just marked.
- Going-private without re-granting the roster is forbidden — the grants step is part of the transition, not optional (decision 5 invariant: roster == grants on private projects).
- No writes before Step 2 confirmation.

### Edge Cases

- Copy fails mid-way: pointer untouched → old location remains authoritative; surface what copied; re-run is idempotent.
- Roster member grant fails (INVALID_RECIPIENT etc.): `partial_failure` handling — roster keeps only verified members; report the rest.
- In-flight collaborators on a privatized project keep stale folder knowledge of the stub — they re-discover via the pointer.
- A 3.x project mid-migration: defer — "finish the 4.0 upgrade first."
