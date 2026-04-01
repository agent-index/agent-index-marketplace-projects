---
name: archive-project
type: task
version: 2.0.0
collection: projects
description: Archives an active project, marking it as no longer relevant and making it read-only. Optionally archives the project's comms channel. Archived projects remain in the shared registry but cannot be edited.
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Channel archival (only if comms_channel_enabled and project has a channel)"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

Archiving a project signals that it is no longer relevant to active org work. The project record and all its data remain intact in the shared projects directory — nothing is deleted. The project is marked `archived` in both its own record and the projects manifest, which removes it from active project views and makes it read-only.

Archiving is the only way to transition a project from `active` to `archived`. This separation from `edit-project` is intentional — archiving is a meaningful lifecycle event, not just a field change.

Any member with write access can archive any active project.

### Inputs

The member identifies which project to archive and optionally provides an archive reason or note.

### Outputs

- `{shared_projects_path}/{project-slug}/project.md` — status updated to `archived`, archive note added
- `{shared_projects_path}/projects-manifest.json` — project entry status updated to `archived`

---

## Workflow

### Step 1: Read Org Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get `shared_projects_path`.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If the member named a project in their invocation: use that name. If not: ask "Which project would you like to archive?"

Read `projects-manifest.json` via `aifs_read` and find the matching project. If the project is already `archived`:

**On already archived:** Surface: "'{name}' is already archived. If you want to bring it back, say '@ai:unarchive-project' or 'unarchive {name}'." Halt.

If the project cannot be found:

**On not found:** Surface: "I couldn't find a project matching '{input}'. Say '@ai:list-projects' to see all projects." Halt.

Read the full `project.md` for the identified project via `aifs_read`.

**On success:** Proceed to Step 2.

---

### Step 2: Collect Archive Note (Optional)

Ask: "Would you like to add a note about why this project is being archived? This is optional but can be useful context for the future."

Accept any string or skip. This becomes the `archive_note` field in `project.md`.

**On success:** Proceed to Step 3.

---

### Step 3: Comms Channel Handling

Read `collection-setup-responses.md` via `aifs_read` to get `comms_channel_enabled` and `comms_channel_archive_on_project_archive`.

Check the project's `comms_channel` field in `project.md`. If the project has an active channel (`comms_channel.enabled: true` and `comms_channel.status: active`):

**If `comms_channel_archive_on_project_archive` is `prompt`:**
Ask: "This project has a {comms_platform} channel `#{channel_name}`. Would you like to archive the channel as well?"
Record the member's choice.

**If `comms_channel_archive_on_project_archive` is `automatic`:**
Inform the member: "The project's {comms_platform} channel `#{channel_name}` will also be archived."
Record for automatic archival.

**If `comms_channel_archive_on_project_archive` is `none`:**
Do not mention the channel. It will be left as-is.

If the project has no active channel, or `comms_channel_enabled` is `false`: skip this step.

**On success:** Proceed to Step 4.

---

### Step 4: Confirm

Present a clear confirmation prompt:

> **Archive '{name}'?**
> Owner: {owner}
> Project Manager: {project_manager}
> {if archive_note provided}: Archive note: "{archive_note}"
> {if channel will be archived}: Channel `#{channel_name}` will also be archived on {comms_platform}.
>
> Archiving will mark this project as no longer active. The project record and all its files will be preserved but the project will be read-only. This can be reversed with 'unarchive project'.
>
> Confirm?

Wait for explicit confirmation. Do not write anything before confirmation.

---

### Step 5: Write

On confirmation:

1. Update `project.md`:
   - Set `status: archived`
   - Add `archived_date: {today YYYY-MM-DD}`
   - Add `archive_note: {note}` (empty string if none provided)
   - Update `last_updated: {today YYYY-MM-DD}`

2. Update `projects-manifest.json`:
   - Set `status: archived` on the project entry
   - Update `last_updated` on the manifest

3. If channel archival was confirmed or automatic:
   - Use the platform's MCP connector to archive the channel.
   - If successful: update `comms_channel.status: archived` in `project.md`. Confirm: "Channel `#{channel_name}` has been archived on {comms_platform}."
   - If the connector is unavailable: note: "I couldn't archive the channel on {comms_platform} — you may need to do this manually." Leave `comms_channel.status: active` in the project record.

4. Confirm to member:
   > "'{name}' has been archived. Its files are preserved at `{shared_projects_path}/{slug}/`. To reactivate it, say '@ai:unarchive-project' or 'unarchive {name}'."

**On any write failure:** Surface the specific file that failed. Report the current state of each file clearly so the member can assess whether the project is in a consistent state.

---

## Directives

### Behavior

Keep this task focused and efficient. Archiving is a simple lifecycle operation — the confirmation in Step 3 is the heart of it. Do not over-explain or add friction beyond the confirmation.

The optional archive note is worth prompting for — future members (or the same member months later) will appreciate context about why a project was archived. But do not require it.

### Constraints

Never archive a project that is already archived.

Never delete any project files or directories. Archiving is a status change only — all data is preserved.

Never change any field other than `status`, `archived_date`, `archive_note`, `comms_channel.status`, and `last_updated`. Archiving does not touch scope, members, roles, brief, milestones, or any other project data.

Comms channel archival is always best-effort. A failure to archive the channel must never block or roll back the project archive operation.

Do not write before the Step 4 confirmation.

### Edge Cases

If `project.md` can be read but `projects-manifest.json` cannot be written: write the status change to `project.md` anyway, then surface a warning: "The project record was archived, but the projects manifest couldn't be updated. The project may still appear as active in project listings until the manifest is repaired. Contact your org admin."

If the member confirms archiving and then immediately says "wait, undo that": read the current state of the file. If the write has already occurred, surface: "The archive has been applied. To reverse it, say '@ai:unarchive-project' or 'unarchive {name}'." Do not attempt to reverse a completed write silently.
