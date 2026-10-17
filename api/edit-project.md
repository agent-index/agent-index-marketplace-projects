---
name: edit-project
type: task
version: 4.4.3
collection: projects
description: Edits an existing active project — brief, milestones, ownership, member list, roles, comms channel. Tier-resolved (4.0) — on org-public projects the roster is metadata; on PRIVATE projects membership IS the grant list (adding a member applies a collaborator grant through the core permission-changes procedure, confirmed by the owner and verified; the first member ends the project's invisibility).
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Channel creation, archival, member invitation (only if comms_channel_enabled)"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

Projects change. Scope evolves, team members join and leave, ownership transfers, roles get redefined, milestones shift, and channels need updating. The edit-project task handles all modifications to an existing project record — from small corrections to substantial restructuring.

Any member with write access to the shared projects directory can edit any active project. Edits are reflected immediately in the project record and, where applicable, in the projects manifest.

Archived projects cannot be edited. Use `unarchive-project` first if a project needs to be brought back to active status before editing.

### Inputs

The member identifies which project to edit and describes what they want to change. Changes can be targeted ("add Sarah Kim as a Contributor") or broad ("update the project brief").

### Outputs

- `{base}/project.md` — updated in place (base tier-resolved; private-tier membership changes also touch grants + the pointer)
- `/shared/projects-index/{owner_hash}-{slug}.json` — overwritten if name, status, or (private tier) membership scope changed; created when a private project gains its first member

### Cadence & Triggers

On demand, whenever a project record needs to change.

---

## Workflow

### Step 1: Read Org Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` for `roles_config` and all feature flags (`brief_enabled`, `brief_sections`, `milestones_enabled`, `comms_channel_enabled`, `comms_platform`, `comms_channel_naming_template`). Read local `member-index.json` for `member_hash` + `member_folder_id`.

**Tier resolution (4.0):** (read the index as `id:{resource_ids.shared_root}/projects-index/` when the path doesn't resolve — `resource_ids` from org-config, read as `id:{org_config_id}`; open an org-public project by its pointer's `location.folder_id` when present — projects 4.4.1, `publicptrid`) resolve the named project via the pointer index `/shared/projects-index/` (org-public + shared-private projects) and the member's own private projects (`id:{member_folder_id}/projects/`). Tier → base path: org-public = `location.path`; private = the cross-drive anchor `id:{item_drive_id}:{folder_id}/` when the pointer carries `item_drive_id` (a shared-private project lives on the owner's drive — C.1.3 `crossdriveread`), falling back to the bare `id:{folder_id}/` for older pointers and for the member's OWN private projects (own-drive, where the bare anchor resolves correctly). On gdrive the bare anchor already reaches shared items, so the qualified form is OneDrive parity and harmless there. `projects-manifest.json` is retired.

**Write authority is tier-mechanical:** org-public = any member (edits activity-attributed); private = owner and collaborators. **Membership changes on a PRIVATE project are owner-only** (they are Drive grants — collected in Step 3, applied in Step 4.0).

If the member did not name a project: ask, listing what they can see (their own + pointers).

If the identified project has `status: archived`:

**On archived:** Surface: "'{name}' is archived and cannot be edited. Would you like to unarchive it first? Say '@ai:unarchive-project' or 'unarchive {name}'." Halt.

If the project cannot be found:

**On not found:** Surface: "I couldn't find a project matching '{input}'. Say '@ai:list-projects' to see all projects, or check the name and try again." Halt.

**On success:** Read the full `project.md` for the identified project via `aifs_read`. Proceed to Step 2.

---

### Step 2: Determine What to Edit

If the member specified what they want to change in their invocation: proceed directly to the relevant step.

If the member invoked generally ("edit project Rebrand 2026"): present the current project record in a readable summary and ask: "What would you like to change?"

Fields available to edit:
- Project name (and slug — see constraints)
- Owner
- Project Manager
- Project brief (if `brief_enabled`) or scope narrative (if not)
- Milestones (if `milestones_enabled`)
- Roles list (subject to `roles_config`)
- Members (add, remove, change role, link unregistered)
- Comms channel (if `comms_channel_enabled`)
- Action-item ID prefix (if `action_items_enabled` — **only while the project has issued no action items**; see Step 3)
- Project tags

Multiple changes in a single session are supported. Collect all changes before writing.

**On success:** Proceed to the relevant step(s) for each change requested.

---

### Step 3: Collect Changes

Handle each type of change as follows:

**Action-item ID prefix change (new in 4.2):**

All rules live in `action-item-prefix-rules.md` at the collection root. Follow that file rather than restating it.

First read `{base}/action-items.json` and check whether `items` is non-empty.

*If the project has already issued action items* — **refuse the change** (rules §8):

> *"I can't change the prefix now. This project has already issued {count} action item(s) starting at `{PREFIX}-001`, and those IDs are referenced outside agent-index — in branch names, Slack, documents. Renaming the prefix would make every one of those references wrong, and renumbering existing items isn't an option either. The prefix is locked to `{PREFIX}`."*

This is a refusal **with the reason stated**, never a silent no-op and never a "are you sure?" that can be clicked through. If the member pushes back, explain that `prefix_history` exists precisely so old IDs keep resolving, but that splitting a project's ID space is a worse outcome than an imperfect prefix.

*If the project has issued no action items* — the change is allowed:

1. If the project currently has **no** prefix: derive a candidate (§3) and offer it. This is the path by which every project created before 4.2 adopts a prefix.
2. Validate the member's choice (§4) and check availability (§5).
3. **Claim the new prefix using the full two-write protocol (§5) and confirm it succeeded before releasing the old one** (§8) — `aifs_write`, keep the revision, then the guarded `if_revision` write. A read-back alone is not sufficient and a failure between claim and release must never leave the project holding no claim.
4. Release the old claim only after the new one is confirmed. Leave `prefix_history` empty — nothing was ever issued under the old prefix, so there is nothing to resolve.

*If the project has no prefix and the member declines one:* leave it `null`. The project continues to read as `AI` (§9). Do not re-prompt on every subsequent edit.

**Project tags change (new in 4.2):**

Add or remove free-form labels on the project. **Normalize on write** — lowercase, spaces to hyphens, consecutive hyphens collapsed, leading and trailing hyphens removed. Show the normalized form back to the member when it differs from what they typed, so the stored value is never a surprise.

Project tags are not inherited by the project's action items; item tags are managed in `manage-action-items`.

**Name change:**
Ask for the new name. Generate the new slug. Check for collisions with existing projects (excluding the current project). Warn the member: "Changing the project name will also change its directory from `{old-slug}` to `{new-slug}`. Any links or references to the old path will need to be updated." Require explicit confirmation of the rename consequence before accepting.

**Resolving a person (used by owner, PM and member changes):** read the members registry **by id anchor** — org-config `resource_ids.members_registry` → `aifs_read("id:{members_registry_id}")` (org-config itself is read by `id:{org_config_id}` from local `agent-index.json`). OneDrive (local `agent-index.json` `remote_filesystem.backend`): read `/org-config.json` and `/members-registry.json` by path instead — a bare `id:` resolves against your own drive there (core `runtime-reference.md` § "Addressing: Owned Content and Sharing", finding 63). On gdrive, never read it by a root path such as `/members-registry.json`: a member who isn't a Drive member of the org root gets `FILE_NOT_FOUND` there even though the file exists. Search by `display_name` (case-insensitive partial match), confirm if one match is found, disambiguate if multiple. What happens when there is no match depends on the field and the tier (below).

**Owner change:**
- **Org-public project:** ownership is record metadata. Ask for the new owner's name and resolve it as above; if there's no match, record them by name as unregistered.
- **Private project:** **block the change.** A private project lives in the owner's own drive, so its ownership can't move from here. Say: *"'{name}' is private, so it lives in your own drive and I can't hand ownership to someone else from here. Two options: make it org-public first with '@ai:transition-project' (then the owner is just a record field you can change), or {new owner} creates their own project and you add them as a member here in the meantime."* Collect no owner change; carry on with any other edits.

**Project Manager change:**
Ask for the new PM's name. Resolve it as above (no match → recorded by name as unregistered). The PM field is record metadata on both tiers; on a private project it grants nothing, so a PM who also needs access is added as a member.

**Project brief changes** (only if `brief_enabled` is `true`):
Present the current brief sections with their content (or note which are empty). Ask what the member wants to change. Supported operations:
- *Edit a section:* Present the current content and ask for the replacement. Accept a full replacement or instructions to modify (e.g., "add a note about the Q3 deadline to constraints").
- *Fill in a skipped section:* If a section was skipped during creation (shows as `*Not yet defined.*`), the member can now provide content.
- *Clear a section:* Set a section back to `*Not yet defined.*`.
- Multiple section edits can be collected in sequence.

**Scope narrative change** (only if `brief_enabled` is `false`):
Present the current scope narrative. Ask: "Would you like to replace this entirely, or add to it?" Accept either a full replacement or an addition to append.

**Milestones changes** (only if `milestones_enabled` is `true`):
Present the current milestones with their names, target dates, and statuses. Supported operations:
- *Add milestone:* Collect name and target date. Status defaults to `pending`.
- *Edit milestone:* Change name, target date, or status of an existing milestone.
- *Remove milestone:* Delete a milestone from the list. Confirm before removing.
- *Update milestone status:* Mark a milestone as `completed`, `missed`, or `deferred`. If marking as `completed`, record `completed_date: {today}`.
- Multiple milestone changes can be collected in sequence.

**Roles change** (subject to `roles_config`):
- If `org-mandated`: surface "Your org's roles are fixed and cannot be changed here. Contact your org admin if the org roles list needs updating." Do not allow roles edits.
- If `org-suggested` or `project-defined`: present current roles. Accept additions, removals, or renaming. Enforce minimum of one role at all times.
- If removing a role that is currently assigned to one or more members: warn "The role '{role}' is currently assigned to {N} member(s). Removing it will leave those members without a role. Would you like to reassign them before removing the role, or remove the role and leave those members unassigned?"

**Member changes (4.0 — the roster collapse, design decision 5):**

- *Add member (both tiers):* Ask for a name and role. Role must be from current roles list. Resolve the person as above.
- *Remove member:* Ask which member to remove. Confirm before marking for removal.
- *Change member role:* Ask which member and what their new role should be.
- *Link unregistered member:* If a project has members recorded with `member_hash: null` (added before they joined the org), and the member is now in the registry, offer to link their full identity. Search the registry by display name and confirm the match.
- Multiple member changes can be collected in sequence.

- **On an ORG-PUBLIC project:** the roster is attribution/assignment metadata only — access is uniform for the whole org. Add/remove/change-role/link edits the roster in project.md, nothing else. No grants exist or are needed. A name with no registry match can be roster-listed as unlinked (`member_hash: null`, `email: null`) — on this tier that grants and withholds nothing.
- **On a PRIVATE project:** the roster IS the grant list. **In this step you only collect** — no grant, removal, roster entry or pointer change happens here. Access changes are applied in Step 4, after the member confirms the diff (Step 4.0).
  - *Add member* → one `share` row (`writer`, collaborator) on `id:{project_folder_id}`.
  - *Remove member* → one `unshare` row (`source: "current_state"`), confirmed individually by the procedure.
  - *Link unregistered member* → a legacy unlinked entry has no access, so linking is an *Add member* for their registry `sharing_identity`. The entry's `member_hash`/`email` are written only if that row is satisfied.
  - *Change member role* → roster metadata only (every collaborator is `writer`); no access change.
  - **Recipients.**
    - A registered member → their `sharing_identity` (email on gdrive, UPN on onedrive).
    - A name with no registry match → **ask the owner for their email address. Never guess.** If they don't have one, the person is **not** added — don't roster-list them unlinked on a private project, because the roster would claim access they don't have. Say: *"I'll need {name}'s email address to give them access. Add them again once you have it."*
    - An address outside the registry (one the owner gives) is allowed. The procedure's table flags it **outside your org**; it's the owner's call. Tell the owner the person opens the project from their storage app's "Shared with me", because agent-index discovery pointers are for org members.

**Comms channel changes** (only if `comms_channel_enabled` is `true`):
- *Create channel (if project doesn't have one):* Generate the channel name from the naming template. Confirm or customize the name. Record for creation during write step.
- *Rename channel:* Not supported directly — channel renaming depends on platform capabilities. Surface: "Channel renaming varies by platform. You may need to rename the channel directly in {comms_platform}. I can update the project record to reflect the new name if you've already renamed it."
- *Archive channel (without archiving the project):* Prompt to confirm. Record for archival during write step.
- If new members are being added in this edit session and the project has an active channel, note that they will be invited to the channel as part of the write step (on a private project, only those whose access is confirmed and verified in Step 4.0).

**On success for all collected changes:** Proceed to Step 4.

---

### Step 4: Confirm and Write

Present a clear summary of all proposed changes as a diff — what the current value is and what it will become:

> **Proposed Changes to '{name}'**
> {for each changed field}:
> {field}: "{old value}" → "{new value}"
> {if new members added and channel exists}: New members will be invited to #{channel_name}
> {private tier, if membership changes}: Access changes: give {names} collaborator access / remove {names}' access — I'll show you the exact permission table to confirm next, and nothing changes until you confirm it.
>
> Ready to apply these changes?

Wait for explicit confirmation. Nothing has been changed yet — not even access — so declining here (or "never mind") discards everything: "No changes were made to '{name}'."

On confirmation:

0. **Private-tier access changes (only if membership adds, removals or links were collected on a PRIVATE project) — before anything is written.** Follow `/agent-index-core/internal/permission-changes.md` with one table for this edit:
   - `calling_task: "edit-project"`, `purpose: "Update who can access project '{name}'"`, `confirmer: "owner"` (only the owner reaches this step — Step 1).
   - One `share` per added or linked member: `resource: "id:{project_folder_id}"` (bare ID from project.md `folder_id`), `resource_label: "Project '{name}'"`, `is_folder: true`, `recipient` = their `sharing_identity` or the email the owner gave, `role: "writer"`, `source: "member_request"`.
   - One `unshare` per removed member on the same resource, `source: "current_state"`.

   The procedure shows its own table and takes its own confirmation; the diff confirmation above does not count for it. If the owner's reply cancels the table, every access row is declined and nothing about membership changes. Before writing anything else, ask once: *"Apply your other changes without the access changes?"* — a clear yes continues with the non-membership edits only; anything else ends with "No changes were made to '{name}'."

   When the procedure returns, compute the membership result:
   - **Adds / links:** a roster entry is written (or an unlinked entry gets its `member_hash` and `email`) **only** for rows `applied` or `skipped_noop`. Every other row is pending: the person is not on the roster.
   - **Removals:** never take "who still has access" from the list you meant to remove. Re-read `aifs_get_permissions({path: "id:{project_folder_id}", include_inherited: true})`. Drop a roster entry only when that re-read shows the person no longer has access; anyone still shown keeps their entry (a declined or failed removal leaves them in).
   - **Pointer scope** (used in 4.3) = the roster entries whose `sharing_identity`/email appears with access in that fresh re-read.

1. If the project name changed: rename the project directory from `{old-slug}` to `{new-slug}`.

1.5. **If the action-item prefix changed:** claim the new prefix via the two-write protocol (`action-item-prefix-rules.md` §5 — write, then guarded `if_revision` write), **then** release the old claim by deleting `/shared/prefix-registry/{OLD}.json`. Never the reverse order — a failure after releasing and before claiming leaves the project with no reservation, and another project can take the prefix it still has recorded. If the claim fails, abandon the prefix change and report it; apply the rest of the member's edits normally.

2. Write the updated `project.md` with all changes applied. Update `last_updated` to today's date. If the prefix changed, write the new `action_item_prefix`; if tags changed, write the normalized `tags` list. On a private project the `members` list is the Step 4.0 result — never the list as collected.

3. **Pointer** at `/shared/projects-index/{owner_hash}-{slug}.json`:
   - **A pointer exists** (org-public, or a private project that has had members) and name, owner, status, action-item prefix or (private tier) membership changed: overwrite it to match. On a private project `scope` is `{"collaborators": [ … ]}` from the Step 4.0 scope; if nobody remains, `"private"` (owner-only). The pointer is never deleted (title residue accepted).
   - **No pointer yet** (a private project that has never had a member) and the Step 4.0 scope is non-empty: **create** it now — the first-ever member ends the project's invisibility (title and owner become org-visible; data stays gated to the grantees):
     ```json
     {
       "type": "project", "name": "{name}", "slug": "{slug}",
       "owner": "{owner display_name}", "owner_hash": "{owner_hash}",
       "status": "active", "scope": {"collaborators": ["{sharing_identity or email}", "…"]},
       "action_item_prefix": "{PREFIX, or null}",
       "location": {"folder_id": "{project_folder_id}", "item_drive_id": "{item_drive_id}"},
       "created": "{project created date}", "last_updated": "{ISO}", "owner_departed": false
     }
     ```
   - `location` always carries **`item_drive_id`** alongside `folder_id` on a private project (from project.md frontmatter, written by create-project; if absent on a pre-C.1.3 project, `aifs_stat` the project folder once and record both its `id` and `drive_id`) so a grantee can open it cross-drive (C.1.3 `crossdriveread`) — a bare `id:{folder_id}` would 404 against the recipient's own drive.
   - No pointer and an empty scope (nothing satisfied): write no pointer — the project stays invisible.
4. If comms channel operations are pending:
   - *Channel creation:* Use the platform's MCP connector to create the channel. Set topic/description. Invite all registered members. If the connector is unavailable, set `comms_channel.status: pending` and note: "Channel creation is pending — I can't reach {comms_platform} right now. Try again later."
   - *Channel archival:* Use the platform's MCP connector to archive the channel. If the connector is unavailable, note: "I couldn't archive the channel on {comms_platform}. You may need to do this manually."
   - *Member invitations (for newly added members):* Invite any newly added registered members to the existing channel. On a private project, invite **only** members whose Step 4.0 row was `applied` or `skipped_noop` — a pending member is not on the project. Unregistered members cannot be invited — note them. If the connector is unavailable, note who needs to be manually invited.

5. Confirm to member:
   > "'{name}' has been updated."
   > {if renamed}: "The project directory is now at `{base}/{new-slug}/`."
   > {if channel created}: "Channel #{channel_name} has been created on {comms_platform}."
   > {if members invited}: "{N} new members have been invited to #{channel_name}." ({N} counts only members actually invited — on a private project, only satisfied rows.)
   > {private tier, if access changed}: the procedure's `summary_lines`, then for each satisfied add "{name} can now open and edit the project." and, for an outside-registry address, "{name} is outside your org — they'll find it under 'Shared with me' in their storage app."
   > {private tier, if any row is pending}: "{name}'s access didn't take effect ({reason}), so they're not on the project yet. Say 'add {name} to {project}' to try again." / "{name} still has access ({removal declined or failed}), so they're still on the roster."
   > {private tier, if the pointer was created}: "'{name}' is now listed in the org's project index (title and owner only); its contents stay limited to its members."

**Entry from create-project (private tier).** When `create-project` hands off its `pending_members`, start at Step 4.0 with them as *Add member* rows (every one already has a registry `sharing_identity` or an email the owner gave). Do not re-run Steps 2–3 or the "Ready to apply?" diff — the owner confirmed the project in create-project Step 9; the permission table is the confirmation that matters here. Then Step 4.2 (roster entries for satisfied rows only), 4.3 (pointer — created if any row is satisfied), 4.4 (channel invitations for satisfied rows only) and the 4.5 confirmation, including any pending people.

**On any write failure:** Surface the specific file that failed. Do not leave the project in a partially-updated state — if the directory rename succeeded but `project.md` write failed, report both the success and the failure clearly so the member can assess the state.

---

## Directives

### Behavior

Read the full current `project.md` before any interaction. Always operate from the actual current state of the file, never from assumed or remembered state.

For targeted edits (member named a specific change in their invocation), go directly to collecting that change. Do not present the full project record unless the member asks to see it or the change requires context.

For broad edits (member said "edit project X" with no specifics), present the project summary and let the member direct what to change. Do not preemptively present every editable field — wait for the member to identify what needs updating.

Collect all changes in a single session before writing. If a member wants to make three changes, collect all three, present a combined diff in Step 4, and write once.

When showing the project summary, include enabled features. If the project has a brief, show which sections are filled and which are empty. If it has milestones, show them with their statuses. If it has a channel, show the channel name and status.

### Output Standards

`project.md` is always written with complete YAML frontmatter. No field is ever omitted, even if unchanged. The `last_updated` field is always set to today's date on any write.

Pointer files are read, parsed, updated in memory, and serialized — never written as a string substitution; overwrite-only, never deleted.

Prefix registry entries (`/shared/prefix-registry/{PREFIX}.json`) are a **different object with different rules** — they are not pointers. A registry entry is deleted in exactly one case: releasing a superseded prefix after the replacement claim is confirmed (`action-item-prefix-rules.md` §10). It is never deleted on archive, on transition, or on project deletion.

### Constraints

Never edit an archived project. The archived check in Step 1 is mandatory.

On a private project, never grant or remove access before the Step 4 diff is confirmed, never call `aifs_share`/`aifs_unshare`/`aifs_transfer_ownership` outside the core permission-changes procedure, and never write a roster entry, pointer scope, channel invitation or "can now access" message for a row that isn't `applied` or `skipped_noop`. Never change the owner of a private project here (Step 3 blocks it).

Never allow `status` to be changed via this task. Status transitions are handled exclusively by `archive-project` and `unarchive-project`.

Never change the action-item prefix of a project that has issued at least one action item. Read `action-items.json` and check it directly rather than taking the member's word for it. **"Issued" means a non-empty `items` array OR `next_id` greater than 1** — items can be deferred out or deleted by hand, and those IDs may still be referenced outside agent-index, so the array alone is not evidence. If the file cannot be read, fail closed and refuse. This check is mandatory and the refusal states the reason. (`action-item-prefix-rules.md` §8 is the authority; this restates only the trigger, not the rules.)

Never release an old prefix claim before the replacement claim's guarded `if_revision` write has succeeded. Claim-then-release, never release-then-claim.

Never renumber existing action items for any reason.

Never allow the roles list to be emptied. Minimum one role must remain at all times.

Never allow a role to be removed if it is the only role and members are assigned to it — there must be at least one valid role for members to hold.

A slug rename renames the physical directory. This is a significant operation — the warning in Step 3 about path references is mandatory, not optional.

For `org-mandated` roles configuration, roles edits are fully blocked. Do not present roles as an editable field in this mode.

Comms channel operations are always best-effort. A failure to create, archive, or invite must never block the project edit. Log the failure in the project record and note it to the member.

### Edge Cases

If `action-items.json` is missing or unreadable when evaluating a prefix change: treat the project as **having issued items** and refuse the change. Failing closed is correct here — wrongly refusing costs the member a prefix they wanted, while wrongly allowing mints IDs that collide with items you couldn't see.

If `action-items.json` exists with an empty `items` array but `next_id` is greater than 1: items were issued and later deleted, so those IDs may still be referenced externally. Refuse the change and say so — the empty array is not evidence that nothing was ever issued.

If the new prefix is claimed successfully but the subsequent `project.md` write fails: the project now holds a claim it does not reference. Report it explicitly, keep the old prefix in the record, and note the orphaned claim so it can be cleaned up — do not silently release the new claim, because a retry will want it.

If the project has no prefix and no pointer (invisible private project): the prefix can still be claimed. The registry entry omits `project_slug` and sets `"visibility": "private"` (rules §5) — the claim is global even though the project is not discoverable.

If the member tries to set owner or PM to an empty value: surface "A project must have an owner. Who should be the owner?" Do not allow blank owner or PM fields.

If the member tries to add a member with a role that doesn't exist in the current roles list: surface the conflict and ask whether they want to add the new role first or choose from existing roles.

If the discovery pointer is missing or unparseable (`/shared/projects-index/{owner_hash}-{slug}.json`): proceed with writing `project.md` but surface a warning: "Your project record was saved, but its discovery entry couldn't be updated, so other members may see stale details until it's repaired." Recreate the pointer from the project record where possible — it is derived data, not a source of truth. (This edge case referenced `projects-manifest.json` until 4.2; that file was retired in 4.0.)

If the member makes a change and then says "actually, never mind" before Step 4 confirmation: discard all collected changes and confirm: "No changes were made to '{name}'."

If the member tries to edit brief sections but `brief_enabled` is `false` in the org config: surface "The structured project brief isn't enabled for your org. You can edit the scope narrative instead." If the project was created before the brief was enabled and has a scope narrative instead of a brief, treat the scope narrative as the `description` section.

If the project has milestones from before `milestones_enabled` was turned off in the org config: the milestones remain in the record and can still be viewed, but the member is informed: "Milestones are no longer enabled for new projects in your org, but this project's existing milestones are preserved. Contact your org admin if you'd like milestones re-enabled."

If the member wants to create a channel but the project predates the comms channel feature: proceed normally — the channel fields are added to the project record during the write.
