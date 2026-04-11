---
name: unarchive-project
type: task
version: 3.0.4
collection: projects
description: Restores an archived project to active status, making it editable again and returning it to active project views. Optionally restores the project's comms channel.
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Channel unarchival (only if project has an archived channel)"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

Unarchiving reverses an archive operation — it restores a project to `active` status and makes it editable again. The project's full history, scope, member list, and all files are preserved through the archive and restoration cycle. Nothing was deleted during archiving and nothing changes structurally during unarchiving.

Unarchiving is the only way to transition a project from `archived` back to `active`. Any member with write access can unarchive any archived project.

### Inputs

The member identifies which archived project to restore.

### Outputs

- `{shared_projects_path}/{project-slug}/project.md` — status updated to `active`, archive fields cleared
- `{shared_projects_path}/projects-manifest.json` — project entry status updated to `active`

---

## Workflow

### Step 1: Read Org Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get `shared_projects_path`.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If the member named a project in their invocation: use that name. If not: ask "Which archived project would you like to restore?"

Read `projects-manifest.json` via `aifs_read` and find the matching project. If the project is already `active`:

**On already active:** Surface: "'{name}' is already active — there's nothing to unarchive. To edit it, say '@ai:edit-project' or 'edit project {name}'." Halt.

If the project cannot be found in the manifest at all:

**On not found:** Surface: "I couldn't find a project matching '{input}'. To see archived projects, say '@ai:list-projects' or 'list archived projects'." Halt.

Read the full `project.md` for the identified project via `aifs_read`.

**On success:** Proceed to Step 2.

---

### Step 2: Present Project Summary and Comms Channel Handling

Present a summary of the archived project so the member can confirm they have the right one.

Check the project's `comms_channel` field. If the project has a channel with `comms_channel.status: archived`:
- Ask: "This project had a {comms_platform} channel `#{channel_name}` that was archived. Would you like to restore the channel as well?"
- Record the member's choice.

If the project has no channel, or the channel status is not `archived`: skip the channel question.

Present the confirmation:

> **Restore '{name}'?**
> Owner: {owner}
> Project Manager: {project_manager}
> Archived: {archived_date}
> {if archive_note is non-empty}: Archive note: "{archive_note}"
> {if channel will be restored}: Channel `#{channel_name}` will also be restored on {comms_platform}.
>
> Restoring this project will make it active and editable again.
>
> Confirm?

Wait for explicit confirmation. Do not write anything before confirmation.

---

### Step 3: Write

On confirmation:

1. Update `project.md`:
   - Set `status: active`
   - Remove `archived_date` field
   - Remove `archive_note` field
   - Update `last_updated: {today YYYY-MM-DD}`

2. Update `projects-manifest.json`:
   - Set `status: active` on the project entry
   - Update `last_updated` on the manifest

3. If channel restoration was confirmed:
   - Use the platform's MCP connector to unarchive the channel.
   - If successful: update `comms_channel.status: active` in `project.md`. Confirm: "Channel `#{channel_name}` has been restored on {comms_platform}."
   - If the connector is unavailable: note: "I couldn't restore the channel on {comms_platform} — you may need to do this manually." Leave `comms_channel.status: archived` in the project record.

4. Confirm to member:
   > "'{name}' has been restored to active status. You can now edit it with '@ai:edit-project' or 'edit project {name}'."

**On any write failure:** Surface the specific file that failed. Report the current state clearly so the member can assess whether the project is in a consistent state.

---

## Directives

### Behavior

Mirror the simplicity of `archive-project`. This is a focused lifecycle operation — identify the project, confirm, write.

Showing the archive note (if present) in the Step 2 confirmation is important. It gives the member context for why the project was archived, which may be relevant to their decision to restore it.

### Constraints

Never unarchive a project that is already active.

Never modify any project data other than `status`, `archived_date`, `archive_note`, `comms_channel.status`, and `last_updated`. Unarchiving does not touch scope, members, roles, brief, milestones, or any other project content.

Comms channel restoration is always best-effort. A failure to restore the channel must never block or roll back the project unarchive operation.

Do not write before the Step 2 confirmation.

### Edge Cases

If `project.md` can be read but `projects-manifest.json` cannot be written: write the status change to `project.md` anyway, then surface a warning: "The project record was restored, but the projects manifest couldn't be updated. The project may still appear as archived in project listings until the manifest is repaired. Contact your org admin."

If `archived_date` or `archive_note` fields are absent from the `project.md` of an archived project (e.g., the project was manually edited or archived through a non-standard path): proceed with the unarchive normally. Set `status: active` and `last_updated`. Do not fail because expected archive fields are missing.

If the member wants to update the project immediately after unarchiving: confirm the unarchive completion, then surface: "Would you like to make any edits now? Say '@ai:edit-project' or describe what you'd like to change."
