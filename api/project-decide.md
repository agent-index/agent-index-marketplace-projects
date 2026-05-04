---
name: project-decide
type: task
version: 3.0.4
collection: projects
description: Records an official project decision with rationale, source ideas, and spawned action items. Decisions are the authoritative record of why the team is doing something.
stateful: false
produces_artifacts: false
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Post notification to project channel (only if comms_channel_enabled)"
    contact: "org admin"
reads_from: /shared/projects/*/
writes_to: /shared/projects/*/decisions/
---

## About This Task

A decision is the authoritative record of "we're doing this, and here's why." Decisions are distinct from action items — a decision captures the *why*, action items capture the *what*. A stakeholder asking "why did we go with this approach?" reads the decision record. A team member asking "what do I need to do?" reads their action items.

Decisions are stored as individual files in `{project}/decisions/` — one file per decision, named by date and topic. This makes them individually addressable, browsable by new team members, and stable references for action items.

### Inputs

The member describes: what was decided, who made the decision (the decider — typically the project owner or PM), the rationale, which ideas or discussions led to this decision, and what action items should be spawned from it.

### Outputs

- `{project}/decisions/{YYYY-MM-DD}-{slug}.md` — the decision record
- Activity log entry
- New action items (if any)
- Optional channel notification

### Cadence & Triggers

On demand, whenever a project direction is set, an approach is chosen, or a significant choice is made. Also suggested by manage-ideas when an idea is approved and the member wants to formalize the reasoning.

---

## Workflow

### Step 1: Read Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get feature flags.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `activity_log_enabled` is `false`: surface "Decision recording requires activity logging to be enabled. Contact your org admin." Halt.

Identify the project. Verify it's active (read project data via `aifs_read`).

**On success:** Proceed to Step 2.

---

### Step 2: Collect Decision Details

Ask: "What was decided?"

Accept a clear statement of the decision. If the member gives a long narrative, help them distill it: "Let me capture the core decision as: '{distilled statement}'. Does that capture it?"

Ask: "Who made this decision?" Default to the project owner or PM if the member says "I did" or "we did." Resolve against the members registry.

Ask: "What's the rationale? Why this approach over alternatives?"

Accept any depth of explanation. This is important context for the future — encourage thoroughness: "This is the part future team members will read when they want to understand why. Worth capturing any trade-offs or alternatives you considered."

Ask: "Is this related to any project ideas?" If ideas are enabled, list shared ideas for the project. The member can link one or more, or none.

**On success:** Proceed to Step 3.

---

### Step 3: Spawn Action Items (Optional)

Ask: "Does this decision create any new action items? For example: 'Sarah needs to implement the approved design' or 'Engineering team needs to estimate the new approach.'"

If yes: collect action items using the same flow as manage-action-items — title, owner, description, due date for each.

If no: proceed without spawning items.

**On success:** Proceed to Step 4.

---

### Step 4: Confirm and Write

Present the decision record:

> **Decision for '{project name}'**
> Decision: {decision statement}
> Decided by: {decider display_name}
> Rationale: {rationale summary}
> {if linked ideas}: Related ideas: {idea titles}
> {if action items}: Action items spawned: {count}
> {for each: title — owner}
>
> Record this decision?

Wait for confirmation.

On confirmation:

1. Generate the decision slug from the decision statement (short, descriptive). Write `{project}/decisions/{today}-{slug}.md`:

   ```markdown
   ---
   title: {decision statement}
   slug: {slug}
   decided_by:
     display_name: {decider display_name}
     member_hash: {decider member_hash or null}
     email: {decider email or null}
   date: {today YYYY-MM-DD}
   related_ideas:
     - {idea slug(s) or empty array}
   spawned_action_items:
     - {action item ID(s) or empty array}
   ---

   ## Decision

   {decision statement}

   ## Rationale

   {full rationale text}

   ## Context

   {any additional context, trade-offs considered, alternatives rejected}
   ```

2. If action items were collected: create each in `{project}/action-items.json` with `source: { "type": "decision", "decision": "{slug}" }`.

3. Append to `{project}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "decision",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "decision_slug": "{slug}",
     "decided_by": "{decider display_name}",
     "summary": "Decision: {decision statement}",
     "action_items_spawned": ["{IDs}"]
   }
   ```

4. If comms channel is active: post notification: "📋 Decision recorded: '{decision statement}' — decided by {decider}. {if action items: '{N} action items created.'}"

5. Confirm: "Decision recorded for '{project name}'. You can find it at `{decisions path}`."

---

## Directives

### Behavior

Decisions should feel weighty but not burdensome. The rationale is the most valuable part — push gently for it. A decision without rationale is a decree; a decision with rationale is institutional knowledge.

If the member is recording a decision that came out of a meeting or discussion, help them capture the key points without requiring a transcript. "What were the main alternatives considered?" and "What tipped the balance toward this choice?" are good prompts.

### Constraints

Never record a decision without explicit confirmation.

Never modify or delete an existing decision. Decisions are permanent records. If a decision is reversed, record a new decision that supersedes the old one and reference it.

The decisions directory is append-only. Each decision is a separate file, never overwritten.

### Edge Cases

If the decisions directory doesn't exist: create `{project}/decisions/` on first use.

If the slug collides with an existing decision (same topic on the same day): append a sequence number (e.g., `2026-03-21-homepage-direction-2`).

If the member wants to revise a previous decision: create a new decision that references the old one. "This supersedes the decision on {date}: '{old decision title}'." Add `supersedes: {old slug}` to the frontmatter.

If the decider is not a project member: accept it. Decisions can be made by stakeholders, executives, or others outside the immediate project team.
