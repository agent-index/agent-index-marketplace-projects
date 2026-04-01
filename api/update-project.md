---
name: update-project
type: task
version: 3.0.0
collection: projects
description: The primary input mechanism for project updates — share progress, report blockers, update action items, and log what's happening. Lightweight and conversational.
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
reads_from: null
writes_to: null
---

## About This Task

Update-project is the daily touchpoint for project work. A member opens a session, says "update project X," and shares what they've been working on, what's done, what's blocked. Claude records everything to the activity log, updates any relevant action item statuses, and can create new action items on the fly.

This task is designed to be fast and conversational — not a form to fill out. The member talks naturally about their work; Claude structures and records it.

### Inputs

The member identifies a project and shares updates in natural language. Updates can include: progress on work, completed items, blockers encountered, new tasks discovered, questions or concerns, or general status notes.

### Outputs

- Activity log entry in `{project}/activity/activity-log.jsonl`
- Updated action items in `{project}/action-items.json` (if applicable)
- Updated `{project}/state/current-state.md`

### Cadence & Triggers

On demand, whenever a member has something to report. Designed for frequent, lightweight use — even a one-sentence update is valuable.

---

## Workflow

### Step 1: Read Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get `shared_projects_path`, `activity_log_enabled`, `action_items_enabled`.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If the member named a project: find it in `projects-manifest.json` via `aifs_read`. If not: ask "Which project are you updating?"

Read the project's `current-state.md` via `aifs_read` to understand the current context.

If `action_items_enabled`: read `action-items.json` via `aifs_read` and identify items assigned to the current member.

**Channel source check:** If the member's request indicates the update source is a communications channel (e.g., "read the Slack channel and update the project," "check the channel for updates," "sync from Slack"), do not read the channel directly. Instead, hand off to `channel-digest`. That task manages the channel cursor, extracts candidates properly, and writes to the review queue. After channel-digest completes, return here to apply any confirmed updates to the project files. Never read a project's comms channel outside of the channel-digest workflow — even for ad-hoc requests.

**On success:** Proceed to Step 2.

---

### Step 2: Show Context and Collect Update

If the member has open action items on this project, briefly surface them: "You have {N} open action items on this project: {brief list}."

Then ask: "What's your update?"

Let the member speak naturally. They might say:
- "Finished the API integration, PR is up for review"
- "Blocked on the design approval — waiting for Sarah"
- "Started working on the database migration, should be done by Thursday"
- "Found a new issue with the auth flow — we need to handle token refresh"

Accept the full update as provided. Do not interrupt to structure it.

**On success:** Proceed to Step 3.

---

### Step 3: Parse and Categorize

Analyze the member's update and extract:

1. **Progress notes** — what was done, what's in progress
2. **Completed action items** — if the update references finishing something that matches an open action item, flag it
3. **New blockers** — anything the member is waiting on or stuck on
4. **New action items** — things the member mentioned that need to be done (by them or someone else)
5. **Status changes** — any action items whose status should change based on the update

Present the parsed breakdown to the member:

> **Here's what I captured:**
> Progress: {summary}
> {if completed items detected}: Completed: {action item title(s)} — mark as done?
> {if blockers detected}: Blockers: {summary} — {if matching action item: mark as blocked?}
> {if new action items detected}: New action items I noticed: {list} — want me to create these?
>
> Does this look right? Anything to add or change?

Wait for the member to confirm, adjust, or add more.

---

### Step 4: Write

On confirmation:

1. If `activity_log_enabled`: append to `{project}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "update",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "summary": "{parsed progress summary}",
     "details": {
       "progress": "{progress notes}",
       "blockers": ["{blocker descriptions}"],
       "completed_items": ["{action item IDs}"],
       "new_items_created": ["{action item IDs}"]
     }
   }
   ```

2. If `action_items_enabled` and the member confirmed action item changes:
   - Mark completed items as `completed` with `completed_date: {today}` and append an update entry
   - Mark blocked items as `blocked` with a note about the blocker
   - Create new action items with owners, descriptions, and source referencing this update
   - For any newly unblocked downstream items (items that were `blocked_by` a now-completed item): update their status and note: "{action item title} is now unblocked — {owner} can proceed."

3. Update `{project}/state/current-state.md`:
   - Update the `Last Updated` timestamp
   - Increment `Session Count`
   - Update the `Status` one-liner based on the latest state
   - Update `Last Session Summary` with a concise account of this update
   - Update `Open Items` to reflect any changes

4. Confirm to member:
   > "Update recorded for '{project name}'."
   > {if action items completed}: "Marked {N} action items as done."
   > {if new action items created}: "Created {N} new action items."
   > {if items unblocked}: "{item title} is now unblocked for {owner}."

---

## Directives

### Behavior

This task should feel like talking to a colleague, not filling out a status form. Accept whatever the member says in whatever order. Don't ask them to categorize their own update — that's Claude's job.

Be proactive about connecting updates to existing action items. If the member says "finished the API work," look for an open action item about API work and offer to close it. But never auto-close — always confirm.

When suggesting new action items extracted from the update, be conservative. Only suggest items that are clearly actionable. "We should think about..." is not an action item. "Need to handle token refresh" is.

Keep the whole interaction under 2-3 minutes for a typical update. This task succeeds by being fast enough that people actually use it.

### Constraints

Never create action items without member confirmation. Extracted candidates are always suggestions.

Never modify the activity log retroactively. It is append-only.

Never log the full conversational transcript. The activity log captures structured summaries, not raw conversation.

### Edge Cases

If the project has no activity log yet (predates tracking features): create `{project}/activity/activity-log.jsonl` on first use.

If the project has no action-items.json yet: initialize it on first use.

If the member's update doesn't reference any specific action items and has no extractable new items: that's fine. Record the progress note to the activity log and update current-state.md. Not every update needs to touch action items.

If the member updates multiple projects in one session: handle each project separately with its own confirmation cycle.

If the member says "nothing to report": don't force an update. Acknowledge and move on.
