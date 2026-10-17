---
name: manage-action-items
type: task
version: 4.3.1
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

**Session-start prefix mention (4.3):** **alongside** the open-items surfacing above — not as a separate channel — if the member owns private projects whose in-use prefix is derived but unclaimed, mention the count once: "{N} of your private projects haven't claimed their action-item prefix." Private projects are invisible to an admin, so the bulk upgrade cannot reach them; this is how their owners find out.

This rides the session-start surfacing this task already declares; it introduces no new mechanism, and if that surfacing does not fire, nothing is lost — the claim guard above is the guarantee, and this only shortens the window. Once per session, never repeated, never blocking.

---

## Workflow

### Step 1: Read Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get feature flags.

**Tier resolution (4.0):** read local `member-index.json` (`member_hash`, `member_folder_id`); resolve the project via `/shared/projects-index/` or the member's own private projects → base path. Action items are project-record material (design decision 4): they live in the project's `action-items.json`, tier follows the project, NO per-item prompts, and every commons write is activity-attributed. `projects-manifest.json` is retired.

If `action_items_enabled` is `false`: halt with appropriate message.

Read `{base}/action-items.json`: `aifs_stat` it first and keep its `revision`, then `aifs_read` it. Every write back follows "Writing `action-items.json`" below (bug `20260921-8d20ea22-202128-c7e9`).

**Action-item ID prefix (4.3):** resolve the project's effective prefix in this order, and write nothing while resolving:

1. `action_item_prefix` from `project.md` frontmatter — the normal path once a project has claimed one.
2. Else the **in-use prefix**: the alphabetic stem of the highest-numbered existing item ID (`AC-040` → `AC`). This is how a project keeps issuing the IDs it already issues before anything has been claimed.
3. Else `AI` — reachable only when the project has **no items and no recorded prefix**.

4.2 resolved an absent prefix to the constant `AI`. That was wrong: projects in the wild already used their own conventions (`AC-`, `AW-`, `CI-`, bare integers), so the constant split live sequences. Step 2 replaces it. Full rules in `action-item-prefix-rules.md` at the collection root.

**Existing item IDs are never rewritten** — not to add a prefix, not to change one, not ever. A project whose items predate any convention keeps them exactly as they are.

**Org field config (4.2):** read `action-item-fields.json` **once here**, not inside any per-item loop. Read `/shared/projects-config/action-item-fields.json` first (gdrive: `id:{resource_ids.shared_root}/projects-config/action-item-fields.json`, path as the fallback; OneDrive: the path). If it isn't there, fall back to the old org-root path `/action-item-fields.json`: an org whose admin hasn't re-run projects setup since the move still has it there (findings 8, 66). Three cases, all non-fatal:

- **File absent** → no org fields are defined. Skip every field prompt. This is the expected state for an org that has upgraded but not configured anything.
- **`fields` is an empty array** → identical behaviour to absent. This is the shipped default.
- **File unparseable** (invalid JSON) → report it plainly ("Your org's action-item field config couldn't be read, so I'll skip those fields — worth telling your admin"), then continue with no fields. Never halt, and never write a partial item because a config was bad.
- **Individual definition invalid** → skip **that definition only**, and keep the valid ones. Discarding the whole config because one entry is wrong turns a typo in a field nobody uses into a silent loss of every field that works. Name the rejected key and the reason so the admin can fix it.

Validate each definition on read, rejecting any that:
  - has no `key`, or a `key` duplicating an earlier definition (first wins, later one rejected)
  - has a `type` outside `string`, `number`, `single-select`, `date`
  - is `single-select` with a missing or empty `options` array
  - declares `options` on a type other than `single-select`, or `unit` on a type other than `number`
  - has a **non-null** `default` that is not among its own `options` (`single-select`) or is not numeric (`number`). `default: null` means "no default" and is valid for **every** type — the guide's own `estimated_size` example uses it
  - has a `status` other than `active` or `deprecated`

These are the same constraints the admin guide states (`action-item-fields-guide.md`); validating them here is what makes the guide's promises true at runtime, since nothing validates the file at write time.

Hold the active field definitions (those with `status: active`) in session state. Deprecated fields are **not** offered at creation but are still displayed wherever an existing item holds a value for them.

**Assignment guard (private projects):** assigning an item to someone who is not on the roster (= has no grant) would create an item they can't see. Prompt: "{name} doesn't have access to this private project — add them as a member first (`@ai:edit-project`), assign to someone with access, or leave unassigned?" Never silently create unreachable assignments.

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
- **Org fields (4.2, only if any are active):** ask for each active field in config order. For a `single-select`, offer the `options` list and accept only a listed value — on a miss, restate the valid options rather than rejecting generically. For a `number`, accept a numeric value and echo it with the field's `unit` if one is defined. For a `date`, normalize to ISO `YYYY-MM-DD`. Every field is optional: "skip" leaves it unset, which reads as the field's default. Do not ask about deprecated fields.
- **Tags (4.2, optional):** "Any tags? " and, when the project has tags of its own, offer them as suggestions: "This project uses `mobile`, `q3` — reuse any of those, or add your own." Suggesting existing values is what keeps a tag vocabulary from fragmenting. **Normalize on write:** lowercase, spaces to hyphens, consecutive hyphens collapsed, leading and trailing hyphens removed. Show the normalized form when it differs from what the member typed. Item tags are independent — the item does **not** inherit the project's tags.

**Claim guard (4.3) — run before issuing the ID.** If the effective prefix came from resolution step 2 (derived, not recorded) **and** `/shared/prefix-registry/{PREFIX}.json` does not exist, offer to reserve it, in one line:

> *"This project's items use `{PREFIX}-`. I'll claim `{PREFIX}` for it so nobody else takes it — ok?"*

- **Accept** → claim via the two-write protocol (`action-item-prefix-rules.md` §5), with `owner_hash` set to the **project's owner** from its pointer — never the current member's, unless they are the owner. Then write `action_item_prefix` into `project.md` and the pointer. Then issue the ID.
- **Decline** → issue the ID and carry on. Record nothing, and offer again next time: a refusal usually means "not now", not "never", so persisting it would be wrong.
- **Already claimed by this project** → no offer; there is nothing to do.
- **Already claimed by a different project** → **do not block the member's work.** Issue the ID under the derived prefix — those IDs are already in circulation — and surface the conflict: two projects are using one prefix, neither can be renumbered, and a human has to decide.

Ambiguity is **presented, never guessed**: mixed stems within one project, bare-integer IDs with no stem at all, or an empty `items` array with `next_id > 1` (IDs were issued and removed, and may still be referenced elsewhere). Show what was found and let the member choose or skip; skipping takes the decline path.

This mirrors the assignment guard above — an inline check at the moment of action rather than a separate chore.

Write the item to action-items.json (revision-aware — "Writing `action-items.json`" below). **Assign the ID as `{PREFIX}-{NNN}`**, where `{PREFIX}` is the effective prefix resolved in Step 1 and `{NNN}` is `next_id` zero-padded to three digits, exactly as before. Increment `next_id`. Store org field values nested under a `fields` object and tags under `tags`:

```json
{ "id": "MOB-014", "title": "...", "owner": "...", "status": "open",
  "tags": ["mobile"],
  "fields": { "type": "bug", "estimated_size": 5 } }
```

A field whose `default` is `null` and which the member skipped is simply **unset**: display it as blank or omit it, never as the literal string "null". "Unset" and "set to nothing" are the same state here, and neither is a value.

Field values are nested rather than flattened onto the item so that an admin-defined key can never collide with a built-in one (`id`, `status`, `owner`, `priority`, `blocked_by`) — a collision there would be silent and unrecoverable. Omit `fields` entirely when nothing was set; omit `tags` when there are none. Log to activity log. Notify via channel if applicable.

**View items:**
Support multiple views:
- "My items" — items owned by current member
- "All items" — full list, optionally filtered by status
- "Blocked items" — items currently blocked, with what they're blocked by
- "Overdue items" — items past due date
- "Item {ID}" — detailed view of a single item including full update history, org field values (rendered with each field's label and, for numbers, its unit — "Size: 13 pts"), and tags
- **Filter by field or tag (within this project):** e.g. "show bugs" where a `single-select` field has that value, or "show items tagged mobile". Cross-project filtering is deliberately out of scope in 4.2 — this task resolves one project at a time.

**Update status:**
Accept: `open` → `in_progress`, `in_progress` → `completed`, any → `blocked`, `blocked` → `in_progress`, any → `deferred`.

When marking `completed`: set `completed_date: {today}`. Append an update entry. Log to activity log.

After completing an item: check `feeds_into` for downstream items. For each downstream item that lists this item in its `blocked_by`: check if all blockers are now resolved. If so, update the downstream item's status to `open` (from `blocked`) and notify the owner: "{downstream title} is now unblocked — {owner name} can proceed."

When marking `blocked`: ask "What's blocking this?" Record the blocker description in an update entry. If the blocker is another action item, add it to `blocked_by`.

**Edit fields or tags (4.2):**

Change an org field value or add/remove tags on an existing item. Validate exactly as at creation. Two rules worth stating because they are easy to get wrong:

- An item that has **no value** for a field is not "empty" — it reads as that field's **default**. Setting it explicitly to the default is a no-op and should not be written.
- A field deprecated after this item was created still shows its stored value and may be **cleared**, but is not offered as something to set.

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

### Writing `action-items.json` (revision-aware — bug `20260921-8d20ea22-202128-c7e9`)

`action-items.json` has several writers (this task, `update-project`, `project-decide`, `manage-ideas`, `share-idea`, `transition-project`) and every write replaces the whole file, so an unguarded read-modify-write silently drops whatever another member wrote in between. Every write of an existing `action-items.json`, in any projects task, follows this rule:

1. `aifs_stat` the file and keep its `revision`, then `aifs_read` it (stat first: if the file changes between the two, the guarded write below conflicts instead of overwriting).
2. Apply the change to that copy and write it with `"if_revision": "{revision}"`. Write the payload with `content_file` (a local temp file), not inline `content` — the file can be well over the ~128 KiB inline limit.
3. On `REVISION_CONFLICT`: stat + re-read the fresh file, re-apply the same change to the fresh copy once (re-resolve anything derived from the old copy — e.g. a new item's ID comes from the fresh `next_id`), and write again with the new `revision`.
4. A second `REVISION_CONFLICT` → stop. Write nothing more and tell the member: "Someone else is updating this project's action items right now, so I didn't save your change ({summary}). Try again in a moment." Never fall back to an unguarded write.

Creating the file for the first time (it doesn't exist yet) is a plain write; every later write is guarded.

### Constraints

Never create action items without explicit member confirmation.

Never auto-complete action items. Even if evidence suggests the work is done, the owner must confirm completion.

Never modify the review queue without the member processing it. Candidates don't age out or auto-dismiss.

Action item IDs are permanent. Completed or deferred items retain their IDs. IDs are never reused.

Never renumber an existing item, and never rewrite an item's ID because the project's prefix changed. Items keep the prefix they were issued under; `prefix_history` on the project exists so those IDs still resolve (`action-item-prefix-rules.md` §8).

Never write to existing items in order to add a newly-defined field. A field added by an admin today applies to yesterday's items by **read-time default resolution**, not by migration. Rewriting every item to insert a default is a mass full-file write for zero information gain, and it is the operation class that has already destroyed action-item and activity-log files in this org.

Never accept a `single-select` value outside the field's declared `options`, and never invent an option on the member's behalf. Extending the option list is an admin action on the config, not a side effect of item creation.

Never halt because the field config is missing, empty, or malformed. Fields are additive; their absence must never block the core job of recording work.

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

If an item holds a value for a field that is **no longer defined** in the config (the admin removed it outright instead of deprecating it): display it as an unrecognized field with its raw key and value rather than hiding it. Silently dropping data from view is worse than showing something ugly — and it tells the admin what deprecation would have preserved.

If an item's stored `single-select` value is no longer in the field's `options` (the admin narrowed the list): display the stored value, flag it as no longer valid, and offer to change it to a current option. Never auto-correct it.

If `next_id` disagrees with the highest existing item number: trust `next_id` and never reuse a number below it. A gap is harmless; a reused ID is a collision with something already referenced externally.

If a project's prefix was changed while it had zero items and the member now creates the first item: it is issued under the current prefix. `prefix_history` stays empty because nothing was ever issued under the old one.

If a member tries to complete an item they don't own: allow it but note "This item is owned by {owner name}. Marking it complete on their behalf." Log who actually marked it.

If completing an item unblocks multiple downstream items: notify about each one individually.

If the member wants to delete an action item: items are never deleted. Offer `deferred` status instead: "Action items aren't deleted — they're part of the project history. Would you like to defer it instead?"
