---
name: manage-ideas
type: task
version: 3.0.0
collection: projects
description: View, edit, and manage ideas — add artifacts, create response ideas, add collaborators, and promote artifacts to the project with actionable assignments.
stateful: false
produces_artifacts: true
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Post notification to project channel (only if comms_channel_enabled)"
    contact: "org admin"
reads_from: /shared/projects/*/ideas/
writes_to: /shared/projects/*/ideas/
---

## About This Task

Manage-ideas is the ongoing workspace for all idea-related activity. Members use it to view ideas they've created or been invited to collaborate on, add artifacts and references, create response ideas (variations or alternatives), add new collaborators, and — most importantly — promote specific artifacts from an idea to the project's official artifact space with actionable assignments.

This task handles both private ideas (in the member's workspace) and shared ideas (in the project space) that the member authored or is a collaborator on.

### Inputs

The member can: view their ideas, edit an idea, add artifacts, add references, create a response idea, add collaborators, or promote artifacts.

### Outputs

Depends on the operation. May update idea.md, create files in artifacts/, update action-items.json, append to the activity log, and write promoted artifacts to the project's artifact space.

### Cadence & Triggers

On demand, whenever a member wants to work with project ideas.

---

## Workflow

### Step 1: Read Configuration and Determine Context

Read `collection-setup-responses.md` via `aifs_read` to get feature flags.

**Tool selection:** Operations on the member's private workspace (`/members/{member_hash}/ideas/`) use native Read/Write tools. Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `ideas_enabled` is `false`: halt with appropriate message.

Determine what the member wants to do. If they specified in their invocation (e.g., "add a mockup to my homepage idea"), go directly to the relevant operation. If they invoked generally ("manage ideas" or "@ai:manage-ideas"), proceed to Step 2.

---

### Step 2: Show Ideas Dashboard

Gather the member's ideas from two sources:

1. **Private ideas:** Read from `/members/{member_hash}/ideas/` across all projects (or a specific project if the member narrowed scope).
2. **Shared ideas they're involved in:** Read from each active project's `/ideas/` directory. Include ideas where the member is the author or a collaborator.

Present a dashboard:

> **Your Ideas**
> {if private ideas exist}:
> **Private Drafts:**
> - {title} (project: {project name}) — {status}, {artifact count} artifacts
>
> {if shared ideas exist}:
> **Shared Ideas:**
> - {title} (project: {project name}) — by {author}, {collaborator count} collaborators
>   {if member is a collaborator}: Your assignment: "{assignment}"
>
> What would you like to do?

---

### Step 3: Handle Operations

**Edit idea (description, title):**
Read the current idea.md. Present the content. Accept updates. Write the updated file. If the idea is shared, log to the activity log.

**Add artifacts:**
Accept files provided in the session. Copy to the idea's `/artifacts/` directory. Update `last_updated` in idea.md. If shared, log to the activity log.

**Add references:**
Collect links with labels and optional platform types. Add to the `references` array in idea.md. If shared, log to the activity log.

**Add collaborators (shared ideas only):**
Resolve each person against the members registry. Collect their assignment. Add to the `collaborators` array. Create an action item for each (if action_items_enabled). Post channel notification (if applicable). Log to activity log.

**Create response idea:**
A response idea is a new idea that references the current idea as its parent. It follows the same creation flow as create-idea but with `parent_idea` set to the current idea's slug. Response ideas are always created in the shared project space (since they're responding to a shared idea). The parent idea's record is not modified — the relationship is tracked via the child's `parent_idea` field.

Ask: "What's the title for your response idea?" Then collect description, artifacts, references as in create-idea. Write to `{project}/ideas/{response-slug}/idea.md` with `parent_idea: {parent-slug}`. Log to activity log.

**Promote artifacts:**
This is the critical operation that moves work from exploration to action. The member selects one or more artifacts from a shared idea and promotes them to the project's official artifact space.

For each artifact being promoted:
1. Ask: "Who is this for?" — resolve against the members registry.
2. Ask: "What should they do with it? For example: 'Implement this design' or 'Review and sign off'." — this becomes the actionable assignment.
3. Ask: "Is there a deadline?"
4. Copy the artifact to `{shared_projects_path}/{project-slug}/artifacts/{today YYYY-MM-DD}/{artifact-filename}`.
5. Record the promotion in the idea's `promoted_artifacts` array:
   ```yaml
   - artifact_name: "{filename}"
     promoted_date: "{today}"
     promoted_to: "{destination path}"
     assigned_to:
       display_name: "..."
       member_hash: "..."
       email: "..."
     assignment: "{what they should do}"
   ```
6. If `action_items_enabled`: create an action item for the assignee with the assignment description, linked to the promoted artifact as its source.
7. Log to the activity log:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "artifact_promoted",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "idea_slug": "{idea-slug}",
     "idea_title": "{idea title}",
     "artifact_name": "{filename}",
     "assigned_to": "{assignee display_name}",
     "assignment": "{assignment text}",
     "summary": "Promoted '{filename}' from idea '{title}' — assigned to {assignee} for: {assignment}"
   }
   ```
8. Post channel notification (if applicable): "📎 {author} promoted '{artifact name}' from idea '{idea title}' → assigned to {assignee}: '{assignment}'"

**Mark idea as approved:**
The idea author (or project owner/PM) can mark a shared idea as `approved`. This signals that the concept is accepted — it does not automatically promote any artifacts. Set `status: approved` in idea.md. Log to activity log. This often precedes or accompanies artifact promotion but is a separate act.

**Mark idea as superseded:**
If a newer idea replaces this one, mark it `superseded`. Optionally reference the superseding idea. Set `status: superseded` and `superseded_by: {slug}` in idea.md. Log to activity log.

---

## Directives

### Behavior

When a member is a collaborator viewing an idea, foreground their assignment: "Your assignment on this idea is: '{assignment}'. Would you like to add your work, or do something else?"

For artifact promotion, take time to get the assignment right. This is the moment where exploration becomes commitment. The assignment text should be clear enough that the assignee can act on it without needing additional context. If the member's assignment is vague, gently prompt: "Can you be more specific? The assignee will see this as their action item."

When showing the ideas dashboard, sort by: ideas with pending assignments for the current member first, then recently updated, then oldest.

### Constraints

Only the idea author can promote artifacts, mark as approved, or mark as superseded. Collaborators can add artifacts, add references, and create response ideas.

Never promote artifacts from a private idea. The idea must be shared first.

Never auto-approve an idea. Approval is always an explicit member action.

Never modify the content of a promoted artifact after promotion. The promoted copy is a snapshot. If the artifact needs to change, promote a new version.

### Edge Cases

If a collaborator tries to promote an artifact: surface "Only the idea author can promote artifacts. Let {author name} know this is ready for promotion."

If the project's artifacts directory for today doesn't exist: create `{project}/artifacts/{today YYYY-MM-DD}/`.

If the project's action-items.json doesn't exist: initialize it.

If a promoted artifact filename collides with an existing file in the target directory: append a version number (e.g., `homepage-layout-v2.png`).

If a member has no ideas across any project: surface "You don't have any ideas yet. Create one with '@ai:create-idea'."
