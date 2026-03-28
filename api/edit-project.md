---
name: edit-project
type: task
version: 2.0.0
collection: projects
description: Edits an existing active project — updating brief, milestones, ownership, member list, roles, comms channel, or any other project fields.
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

- `{shared_projects_path}/{project-slug}/project.md` — updated in place
- `{shared_projects_path}/projects-manifest.json` — updated if name, owner, or channel status changed

### Cadence & Triggers

On demand, whenever a project record needs to change.

---

## Workflow

### Step 1: Read Org Configuration and Identify Project

Read `collection-setup-responses.md` to get `shared_projects_path`, `roles_config`, and all feature flags (`brief_enabled`, `brief_sections`, `milestones_enabled`, `comms_channel_enabled`, `comms_platform`, `comms_channel_naming_template`).

If the member named a project in their invocation: use that name. Generate the slug and check whether `{shared_projects_path}/{slug}/project.md` exists.

If the member did not name a project: ask "Which project would you like to edit?"

Read `projects-manifest.json`. If the member's input doesn't exactly match a known slug, find the closest match by name. If multiple close matches exist, present them and ask the member to confirm which one.

If the identified project has `status: archived`:

**On archived:** Surface: "'{name}' is archived and cannot be edited. Would you like to unarchive it first? Say '@ai:unarchive-project' or 'unarchive {name}'." Halt.

If the project cannot be found:

**On not found:** Surface: "I couldn't find a project matching '{input}'. Say '@ai:list-projects' to see all projects, or check the name and try again." Halt.

**On success:** Read the full `project.md` for the identified project. Proceed to Step 2.

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

Multiple changes in a single session are supported. Collect all changes before writing.

**On success:** Proceed to the relevant step(s) for each change requested.

---

### Step 3: Collect Changes

Handle each type of change as follows:

**Name change:**
Ask for the new name. Generate the new slug. Check for collisions with existing projects (excluding the current project). Warn the member: "Changing the project name will also change its directory from `{old-slug}` to `{new-slug}`. Any links or references to the old path will need to be updated." Require explicit confirmation of the rename consequence before accepting.

**Owner change:**
Ask for the new owner's name. Resolve their identity against the members registry using the same process defined in `create-project.md` Step 3: search `/members/members-registry.json` by `display_name`, confirm if one match is found, disambiguate if multiple, and note if unregistered.

**Project Manager change:**
Ask for the new PM's name. Resolve identity the same way as owner changes.

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

**Member changes:**
- *Add member:* Ask for a name and role. Role must be from current roles list. Resolve their identity against the members registry using the same process as owner changes: search by `display_name`, confirm if one match, disambiguate if multiple, note if unregistered.
- *Remove member:* Ask which member to remove. Confirm before marking for removal.
- *Change member role:* Ask which member and what their new role should be.
- *Link unregistered member:* If a project has members recorded with `member_hash: null` (added before they joined the org), and the member is now in the registry, offer to link their full identity. Search the registry by display name, confirm the match, and update the entry with their `member_hash` and `email`.
- Multiple member changes can be collected in sequence.

**Comms channel changes** (only if `comms_channel_enabled` is `true`):
- *Create channel (if project doesn't have one):* Generate the channel name from the naming template. Confirm or customize the name. Record for creation during write step.
- *Rename channel:* Not supported directly — channel renaming depends on platform capabilities. Surface: "Channel renaming varies by platform. You may need to rename the channel directly in {comms_platform}. I can update the project record to reflect the new name if you've already renamed it."
- *Archive channel (without archiving the project):* Prompt to confirm. Record for archival during write step.
- If new members are being added in this edit session and the project has an active channel, note that they will be invited to the channel as part of the write step.

**On success for all collected changes:** Proceed to Step 4.

---

### Step 4: Confirm and Write

Present a clear summary of all proposed changes as a diff — what the current value is and what it will become:

> **Proposed Changes to '{name}'**
> {for each changed field}:
> {field}: "{old value}" → "{new value}"
> {if new members added and channel exists}: New members will be invited to #{channel_name}
>
> Ready to apply these changes?

Wait for explicit confirmation.

On confirmation:

1. If the project name changed: rename the project directory from `{old-slug}` to `{new-slug}`.

2. Write the updated `project.md` with all changes applied. Update `last_updated` to today's date.

3. If name, owner, or channel status changed: update the corresponding entry in `projects-manifest.json`. Update `last_updated` on the manifest.

4. If comms channel operations are pending:
   - *Channel creation:* Use the platform's MCP connector to create the channel. Set topic/description. Invite all registered members. If the connector is unavailable, set `comms_channel.status: pending` and note: "Channel creation is pending — I can't reach {comms_platform} right now. Try again later."
   - *Channel archival:* Use the platform's MCP connector to archive the channel. If the connector is unavailable, note: "I couldn't archive the channel on {comms_platform}. You may need to do this manually."
   - *Member invitations (for newly added members):* Invite any newly added registered members to the existing channel. Unregistered members cannot be invited — note them. If the connector is unavailable, note who needs to be manually invited.

5. Confirm to member:
   > "'{name}' has been updated."
   > {if renamed}: "The project directory is now at `{shared_projects_path}/{new-slug}/`."
   > {if channel created}: "Channel #{channel_name} has been created on {comms_platform}."
   > {if members invited}: "{N} new members have been invited to #{channel_name}."

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

`projects-manifest.json` is read, parsed, updated in memory, and serialized — never written as a string substitution.

### Constraints

Never edit an archived project. The archived check in Step 1 is mandatory.

Never allow `status` to be changed via this task. Status transitions are handled exclusively by `archive-project` and `unarchive-project`.

Never allow the roles list to be emptied. Minimum one role must remain at all times.

Never allow a role to be removed if it is the only role and members are assigned to it — there must be at least one valid role for members to hold.

A slug rename renames the physical directory. This is a significant operation — the warning in Step 3 about path references is mandatory, not optional.

For `org-mandated` roles configuration, roles edits are fully blocked. Do not present roles as an editable field in this mode.

Comms channel operations are always best-effort. A failure to create, archive, or invite must never block the project edit. Log the failure in the project record and note it to the member.

### Edge Cases

If the member tries to set owner or PM to an empty value: surface "A project must have an owner. Who should be the owner?" Do not allow blank owner or PM fields.

If the member tries to add a member with a role that doesn't exist in the current roles list: surface the conflict and ask whether they want to add the new role first or choose from existing roles.

If `projects-manifest.json` is missing or unparseable: proceed with writing `project.md` but surface a warning: "The projects manifest couldn't be updated — it may be missing or corrupted. Your project record was saved, but the manifest may be out of sync. Contact your org admin to repair the manifest."

If the member makes a change and then says "actually, never mind" before Step 4 confirmation: discard all collected changes and confirm: "No changes were made to '{name}'."

If the member tries to edit brief sections but `brief_enabled` is `false` in the org config: surface "The structured project brief isn't enabled for your org. You can edit the scope narrative instead." If the project was created before the brief was enabled and has a scope narrative instead of a brief, treat the scope narrative as the `description` section.

If the project has milestones from before `milestones_enabled` was turned off in the org config: the milestones remain in the record and can still be viewed, but the member is informed: "Milestones are no longer enabled for new projects in your org, but this project's existing milestones are preserved. Contact your org admin if you'd like milestones re-enabled."

If the member wants to create a channel but the project predates the comms channel feature: proceed normally — the channel fields are added to the project record during the write.
