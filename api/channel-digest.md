---
name: channel-digest
type: task
version: 3.0.4
collection: projects
description: Checks a project's communications channel for new messages, produces a digest summary, and extracts candidate action items and updates for human review.
stateful: true
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord"
    access_required: "Read channel history"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

The channel digest task reads a project's communications channel since the last check, summarizes the conversation, and extracts candidates for the review queue. Nothing from the channel is automatically promoted to action items, updates, or decisions — all extracted candidates require human review via manage-action-items.

This task is the bridge between informal team conversation and structured project tracking. It ensures that important signals in chat don't get lost, while respecting that most chat is casual and doesn't belong in the project record.

### Inputs

The member identifies a project with an active comms channel. The task reads all messages since the last digest.

### Outputs

- Activity log entry with the digest summary
- Candidates added to `{project}/state/review-queue.json`
- Updated `{project}/state/channel-cursor.json` with the new last-checked timestamp

### Cadence & Triggers

Depends on `channel_monitor_cadence` in collection setup:
- `per_session`: suggested at every session start for projects with active channels
- `daily`: suggested once per day
- `weekly`: suggested once per week
- `manual`: only when the member explicitly invokes it

The cadence is a suggestion surfaced at session-start, not an automated schedule. The member always chooses whether to run it.

---

## Workflow

### Step 1: Read Configuration and Identify Project

Read `collection-setup-responses.md` via `aifs_read` to get `channel_monitor_enabled`, `comms_platform`, `activity_log_enabled`, `action_items_enabled`.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` MCP tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `channel_monitor_enabled` is `false`: halt with appropriate message.

Identify the project. Verify it has an active comms channel (`comms_channel.enabled: true` and `comms_channel.status: active` in project.md — read via `aifs_read`).

If no active channel: surface "This project doesn't have an active {comms_platform} channel. Set one up via '@ai:edit-project'." Halt.

Read `{project}/state/channel-cursor.json` via `aifs_read` to get the last-checked timestamp. If the file doesn't exist, this is the first digest — note that to the member.

**On success:** Proceed to Step 2.

---

### Step 2: Read Channel History

Use the appropriate MCP connector for the platform (Slack, Teams, Discord) to read messages from the project's channel since the last-checked timestamp.

If the connector is not available: surface "I can't reach {comms_platform} right now. Try again later or check your connection." Halt.

If no new messages since last check: surface "No new messages in #{channel_name} since the last check on {last_checked_date}." Update the cursor timestamp and halt.

Collect all messages with their authors, timestamps, and content.

**On success:** Proceed to Step 3.

---

### Step 3: Produce Digest and Extract Candidates

Analyze the channel messages and produce:

1. **Digest summary** — a concise summary of what was discussed, organized by topic or thread. This is what goes into the activity log. It should be readable on its own — someone who wasn't in the channel should understand what happened.

2. **Candidate extraction** — scan for signals that suggest actionable content:
   - **Action item candidates**: messages where someone commits to doing something ("I'll handle the API integration"), assigns work ("Can you review this by Friday?"), or reports something that needs follow-up ("Found a bug in the auth flow").
   - **Update candidates**: messages that look like progress reports on existing work ("Finished the homepage mockups", "PR is up for the database migration"). Try to match these against existing action items by keyword.
   - **Decision candidates**: messages where a direction is set ("Let's go with option B", "PM approved the new timeline"). These would become decisions via project-decide.

For each candidate, record:
- The original message content (summarized, not verbatim — respect the conversational nature of chat)
- The author
- The timestamp
- The suggested type (action_item, update_to_existing, decision_candidate)
- For action items: suggested title and suggested owner
- For updates: the action item ID it appears to relate to (if any)

---

### Step 4: Present and Confirm

Present the digest to the member:

> **Channel Digest for #{channel_name}**
> Period: {last_checked} to {now}
> Messages: {count}
>
> **Summary:**
> {digest summary — organized by topic, 3-8 sentences typically}
>
> **Candidates for Review:** {count}
> {brief list of extracted candidates with types}
>
> I've added {N} candidates to the review queue. Process them now with '@ai:manage-action-items', or review them later.
>
> Record this digest?

Wait for confirmation.

On confirmation:

1. Append to `{project}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "channel_digest",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "channel_name": "{channel_name}",
     "period_start": "{last_checked ISO}",
     "period_end": "{now ISO}",
     "message_count": {N},
     "candidates_extracted": {N},
     "summary": "{digest summary}"
   }
   ```

2. Write candidates to `{project}/state/review-queue.json`. Append to existing candidates (don't overwrite — the queue may have unprocessed items from previous digests):
   ```json
   {
     "last_updated": "{today}",
     "candidates": [
       {
         "id": "{auto-generated}",
         "source": "channel_digest",
         "digest_date": "{today}",
         "channel_name": "{channel_name}",
         "original_author": "{message author}",
         "original_timestamp": "{message timestamp}",
         "content_summary": "{summarized message}",
         "suggested_type": "action_item | update_to_existing | decision_candidate",
         "suggested_title": "{for action items}",
         "suggested_owner": "{for action items}",
         "related_action_item": "{ID, for updates}",
         "status": "pending"
       }
     ]
   }
   ```

3. Update `{project}/state/channel-cursor.json`:
   ```json
   {
     "last_checked": "{now ISO 8601}",
     "last_digest_by": "{member_hash}",
     "messages_processed": {N}
   }
   ```

4. Offer: "Would you like to process the review queue now?"
   - If yes: hand off to the review queue processing flow in manage-action-items
   - If no: confirm "The candidates are saved for later review."

---

## Directives

### Behavior

The digest should be genuinely useful — not just a transcript. Summarize by topic, highlight what's important, and skip the noise. A good digest lets someone skip reading the channel entirely and still know what happened.

For candidate extraction, err on the side of capturing too many rather than too few. It's easier for the reviewer to dismiss a false positive than to catch something the digest missed. But don't extract obvious non-candidates — casual conversation, jokes, off-topic chat.

When summarizing messages for the digest and candidates, paraphrase rather than quote verbatim. The channel is a conversation; the digest is a record. They should read differently.

### Constraints

This task is the sole entry point for reading a project's communications channel. No other task, skill, or ad-hoc request should read channel messages directly. If a member asks to "read the channel," "check Slack for updates," "sync from the channel," or any variation — route through this task. This ensures the channel cursor is always used, messages are never re-processed, and all extracted content flows through the review queue.

Never auto-promote channel content to action items, updates, or decisions. Everything goes through the review queue.

Never store verbatim message content in the activity log or review queue. Always summarize/paraphrase. Channel conversations are informal and members should not feel that their casual chat is being recorded word-for-word.

Never run a digest on an archived project's channel.

The channel cursor must always advance forward. Never re-process messages that were already in a previous digest.

### Edge Cases

If channel-cursor.json doesn't exist: this is the first digest. Ask the member: "This is the first channel check for this project. How far back should I look? I can check the last day, last week, or all messages since the channel was created." Set the cursor based on their choice.

If review-queue.json doesn't exist: initialize it with an empty candidates array.

If the channel has a very large volume of messages (100+): summarize in broader strokes and extract only the highest-signal candidates. Note: "There were {N} messages — I've focused on the most actionable content. You may want to skim the channel directly for anything I missed."

If the MCP connector returns partial results or an error mid-read: process what was received, note the issue, and set the cursor to the last successfully read timestamp.
