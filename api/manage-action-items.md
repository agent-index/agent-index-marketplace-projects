---
name: manage-action-items
type: task
version: 3.0.4
collection: projects
description: Create, view, assign, complete, reassign, and chain action items. Process the review queue from channel digests.
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Post notification to project channel (only if comms_channel_enabled)"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

Action items are the universal work unit in a project. They track who needs to do what, by when, and what depends on what. This task is the primary interface for creating, viewing, and managing action items — including processing the review queue populated by channel digests.

Action items can be created here directly, or they arrive from other sources: promoted idea artifacts, decisions, update-project extractions, or channel digest candidates. Regardless of origin, all action items live in `{project}/action-items.json` and are managed through this task.

### Inputs

The member identifies a project and describes what they want to do: create an item, view items, update status, reassign, process the review queue, or manage dependencies.

### Outputs

- Updated `{project}/action-items.json`
- Activity log entries for significant changes
- Optional channel notifications

### Cadence & Triggers

On demand. Also surfaced at session-start if the member has open or newly unblocked action items.

---

## Workflow

### Step 1: Read Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get feature flags.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `action_items_enabled` is `false`: halt with appropriate message.

Identify the project (read `projects-manifest.json` via `aifs_read`). Read `{project}/action-items.json` via `aifs_read`.

**On success:** Proceed to Step 2.

---

### Step 2: Determine Operation

If the member specified an operation: proceed to it directly.

If general invocation: show a summary dashboard:

> **Action Items for '{project name}'**
>
> **Your Items:**
> {items owned by current member, grouped by status: open, in_progress, blocked}
>
> **All Open Items:** {count} open, {count} in progress, {count} blocked, {count} completed
>
> {if review queue has items}: **Review Queue:** {count} candidates from channel digest awaiting review
>
> What would you like to do?

---

### Step 3: Handle Operations

**Create action item:**
Collect:
- Title: "What needs to be done?"
- Owner: resolve against members registry. "Who owns this?"
- Description: "Any additional details or context?"
- Due date (optional): "Is there a deadline?"
- Dependencies (optional): "Is this blocked by or does it feed into any other items?" Present existing items for reference.
- Source (optional): if created in context of another operation, auto-link the source.

Write the item to action-items.json. Assign an auto-incrementing ID (format: `AI-{NNN}`). Log to activity log. Notify via channel if applicable.

**View items:**
Support multiple views:
- "My items" — items owned by current member
- "All items" — full list, optionally filtered by status
- "Blocked items" — items currently blocked, with what they're blocked by
- "Overdue items" — items past due date
- "Item {ID}" — detailed view of a single item including full update history

**Update status:**
Accept: `open` → `in_progress`, `in_progress` → `completed`, any → `blocked`, `blocked` → `in_progress`, any → `deferred`.

When marking `completed`: set `completed_date: {today}`. Append an update entry. Log to activity log.

After completing an item: check `feeds_into` for downstream items. For each downstream item that lists this item in its `blocked_by`: check if all blockers are now resolved. If so, update the downstream item's status to `open` (from `blocked`) and notify the owner: "{downstream title} is now unblocked — {owner name} can proceed."

When marking `blocked`: ask "What's blocking this?" Record the blocker description in an update entry. If the blocker is another action item, add it to `blocked_by`.

**Reassign:**
Ask for the new owner. Resolve against members registry. Update the item. Add an update entry noting the reassignment. Log to activity log. Notify the new owner via channel if applicable.

**Add dependency chain:**
For an existing item, set `blocked_by` (upstream dependencies) and/or `feeds_into` (downstream items). This establishes the production chain so that completing one item surfaces the next.

**Process review queue:**
Read `{project}/state/review-queue.json`. For each candidate:

Present it to the member with context:
> **Channel Candidate {N of total}:**
> Source: {comms_platform} — {date/time}
> Content: "{extracted message summary}"
> Suggested type: {action_item | update_to_existing | decision_candidate}
> {if action_item}: Suggested title: "{extracted title}", Suggested owner: "{extracted name}"
> {if update_to_existing}: Appears related to: {action item ID and title}
>
> Accept, edit, or dismiss?

For each candidate the member accepts:
- Action item candidates: create the action item (let member edit title, owner, etc. before creating)
- Update candidates: append the update to the referenced action item
- Decision candidates: note for the member to create via `@ai:project-decide`

For dismissed candidates: remove from the queue. No record needed.

After processing all candidates: write the updated (now shorter) review-queue.json.

---

## Directives

### Behavior

The action items list should be a trustworthy record of what needs to happen. Every item in it is either confirmed by a human or created by a human. This trust is the entire value proposition — don't undermine it by auto-creating items or being loose about what gets added.

When showing items, prioritize what's actionable: blocked items with recently resolved blockers, items approaching deadlines, items owned by the current member. Don't just dump a flat list.

For the review queue: present candidates one at a time, not as a batch. Let the member focus on each one. If the queue is long (10+), offer: "There are {N} candidates to review. Want to go through them all now, or just the most recent ones?"

### Constraints

Never create action items without explicit member confirmation.

Never auto-complete action items. Even if evidence suggests the work is done, the owner must confirm completion.

Never modify the review queue without the member processing it. Candidates don't age out or auto-dismiss.

Action item IDs are permanent. Completed or deferred items retain their IDs. IDs are never reused.

### Edge Cases

If action-items.json doesn't exist yet: initialize it:
```json
{
  "last_updated": "{today}",
  "next_id": 1,
  "items": []
}
```

If review-queue.json doesn't exist: there's nothing to process. Surface "No channel candidates to review."

If a member tries to complete an item they don't own: allow it but note "This item is owned by {owner name}. Marking it complete on their behalf." Log who actually marked it.

If completing an item unblocks multiple downstream items: notify about each one individually.

If the member wants to delete an action item: items are never deleted. Offer `deferred` status instead: "Action items aren't deleted — they're part of the project history. Would you like to defer it instead?"
