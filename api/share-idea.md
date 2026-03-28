---
name: share-idea
type: task
version: 3.0.0
collection: projects
description: Promotes a private idea to the project's shared space and invites collaborators with specific assignments.
stateful: false
produces_artifacts: false
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Post notification to project channel (only if comms_channel_enabled and project has a channel)"
    contact: "org admin"
reads_from: /shared/projects/*/ideas/
writes_to: /shared/projects/*/ideas/
---

## About This Task

Sharing an idea is the intentional act of moving it from private exploration to collaborative visibility. The idea is copied from the member's private workspace to the project's shared idea space, collaborators are invited with specific assignments, and the act is recorded in the project activity log.

The original private copy remains in the member's workspace as a reference. The shared copy becomes the active version that collaborators interact with.

### Inputs

The member identifies which private idea to share, and optionally provides collaborators with assignments.

### Outputs

- `{shared_projects_path}/{project-slug}/ideas/{idea-slug}/` — the shared idea directory (copied from private)
- Activity log entry recording the share
- Action items created for each collaborator (if action items are enabled)
- Optional channel notification

### Cadence & Triggers

On demand, when a member decides their private idea is ready for collaboration.

---

## Workflow

### Step 1: Read Org Configuration and Identify Idea

Read `collection-setup-responses.md` via `aifs_read` to get `shared_projects_path`, `ideas_enabled`, `action_items_enabled`, `activity_log_enabled`, `comms_channel_enabled`.

**Tool selection:** Operations on the member's private workspace (`/members/{member_hash}/ideas/`) use native Read/Write tools. Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `ideas_enabled` is `false`: halt with appropriate message.

If the member named an idea in their invocation: find it in `/members/{member_hash}/ideas/`. If the member named a project too, narrow the search.

If the member did not name an idea: list their private ideas across all projects (or for a specific project if specified). Present the list and ask which one to share.

If the idea is not found: surface "I couldn't find a private idea matching '{input}'. Say '@ai:manage-ideas' to see your ideas." Halt.

If the idea's status is already `shared` or `approved`: surface "This idea has already been shared. You can manage it via '@ai:manage-ideas'." Halt.

Read the full `idea.md` for the identified idea. Identify the project it belongs to.

**On success:** Proceed to Step 2.

---

### Step 2: Review Before Sharing

Present the idea summary to the member:

> **Share this idea?**
> Title: {title}
> Project: {project name}
> Description: {first few sentences}
> Artifacts: {count}
> References: {count}
>
> This will make it visible to the project team.

Ask: "Would you like to make any changes before sharing, or is it ready?"

If the member wants changes: let them update the description, add/remove artifacts, or add/remove references. Apply changes to the private copy first.

**On success:** Proceed to Step 3.

---

### Step 3: Invite Collaborators

Ask: "Would you like to invite collaborators? Each collaborator gets a specific assignment — what you want them to do with this idea."

If yes, collect collaborators one at a time:
- Ask: "Who would you like to invite?"
- Resolve against the members registry (same process as create-project Step 3).
- Ask: "What's their assignment? For example: 'Explore layout options and create mockups' or 'Review technical feasibility and estimate effort'."
- Accept any non-empty string as the assignment.
- Continue until the member says they're done.

If no: proceed with no collaborators. The idea is shared but not actively assigned to anyone.

**On success:** Proceed to Step 4.

---

### Step 4: Confirm and Write

Present a final summary:

> **Sharing '{title}' to project '{project name}'**
> {if collaborators}: Collaborators:
> {for each: display_name — "{assignment}"}
>
> Confirm?

Wait for confirmation.

On confirmation:

1. Create the shared idea directory at `{shared_projects_path}/{project-slug}/ideas/{idea-slug}/`. Copy all files from the private idea (idea.md, artifacts, references).

2. Update the shared `idea.md`:
   - Set `status: shared`
   - Set `last_updated` to today
   - Populate `collaborators` array with each collaborator's structured person object plus their assignment and `added_date`

3. Update the private `idea.md`:
   - Set `status: shared`
   - Add `shared_path: {path to shared copy}` for cross-reference
   - Set `last_updated` to today

4. If `activity_log_enabled`: append to `{project}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "idea_shared",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "idea_slug": "{idea-slug}",
     "idea_title": "{title}",
     "collaborators": [{"name": "...", "assignment": "..."}],
     "summary": "Shared idea '{title}' with {N} collaborators"
   }
   ```

5. If `action_items_enabled` and collaborators were added: for each collaborator, create an action item in `{project}/action-items.json`:
   ```json
   {
     "id": "{auto-generated}",
     "title": "Collaborate on idea: {idea title}",
     "description": "{collaborator assignment}",
     "owner": { "display_name": "...", "member_hash": "...", "email": "..." },
     "status": "open",
     "created": "{today}",
     "due_date": null,
     "source": { "type": "idea_collaboration", "idea": "{idea-slug}" },
     "blocked_by": [],
     "feeds_into": [],
     "updates": []
   }
   ```

6. If `comms_channel_enabled` and the project has an active channel: post a notification to the channel: "💡 {author display_name} shared a new idea: '{title}'. {if collaborators: '{collaborator names} have been invited to collaborate.'}"

7. Confirm to member:
   > "Idea '{title}' is now shared in project '{project name}'."
   > {if collaborators}: "{N} collaborators have been invited with their assignments."
   > "Manage it anytime with '@ai:manage-ideas'."

---

## Directives

### Behavior

Sharing an idea is a significant moment — the member is choosing to expose their thinking. Keep the tone encouraging and the process smooth. Don't add friction beyond the necessary confirmation.

Collaborator assignments should be specific and actionable. If a member gives a vague assignment ("look at this"), gently prompt for more clarity: "Can you be more specific about what you'd like them to do? For example, 'review and suggest improvements' or 'create alternative mockups'."

### Constraints

Never share an idea that is already shared or approved.

Never modify the private copy's content during the share — only update its status and cross-reference. The private copy remains a snapshot of what was shared.

Never auto-promote artifacts or create decisions from a shared idea. Sharing makes an idea visible; promotion to project artifacts is a separate, explicit act via manage-ideas.

### Edge Cases

If the project's ideas directory doesn't exist yet: create it.

If the project's action-items.json doesn't exist yet: initialize it with an empty items array.

If a collaborator is unregistered (member_hash is null): they cannot receive an action item or channel notification. Note this to the member: "{name} isn't in the org registry, so they won't receive an automatic notification. You'll need to let them know directly."

If the idea slug collides with an existing shared idea in the project: append a number (e.g., `homepage-design-2`) and inform the member.
