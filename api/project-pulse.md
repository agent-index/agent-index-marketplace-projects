---
name: project-pulse
type: task
version: 3.0.4
collection: projects
description: Status report generation and conversational Q&A about a project. Synthesizes activity logs, action items, decisions, milestones, ideas, and the project brief into coherent views for stakeholders and managers.
stateful: false
produces_artifacts: true
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies: []
reads_from: /shared/projects/*/
writes_to: /shared/projects/*/artifacts/
---

## About This Task

Project pulse is the stakeholder-facing synthesis layer. It reads everything the project tracking system has captured — activity log, action items, decisions, milestones, ideas, and the project brief — and produces coherent views of project health and progress.

It operates in two modes: **report mode** (generates a written status report) and **conversational mode** (the member talks to Claude about the project as if Claude were the project manager who knows every detail).

The quality of pulse output depends entirely on how well the underlying tracking data has been maintained. Pulse doesn't generate new information — it synthesizes what's already captured.

### Inputs

The member identifies a project and either asks for a report or asks questions about the project.

### Outputs

Report mode:
- `{project}/artifacts/status-reports/{YYYY-MM-DD}-status-report.md` — the generated report
- Activity log entry recording the report generation

Conversational mode:
- No files written (unless the member asks to save something)

### Cadence & Triggers

On demand, whenever a stakeholder or manager wants a project update. Can be run by any member — not limited to the project owner or PM.

---

## Workflow

### Step 1: Read Configuration and Load Project Context

Read `collection-setup-responses.md` via `aifs_read` to get feature flags, especially `project_pulse_enabled` and `project_pulse_report_sections`.

**Tool selection:** Operations on the shared projects path (`{shared_projects_path}`) use `aifs_*` tools (e.g., `aifs_read`, `aifs_write`, `aifs_exists`).

If `project_pulse_enabled` is `false`: halt with appropriate message.

Identify the project. Read the full project context (via `aifs_read`):
- `project.md` — brief, milestones, members, channel info
- `action-items.json` — all items with their full update histories
- `activity/activity-log.jsonl` — recent entries (last 30 days by default, adjustable)
- `decisions/` — all decision files
- `ideas/` — all shared ideas with their statuses
- `state/current-state.md` — latest state summary

This is a heavy read. Load everything needed before interacting with the member.

**On success:** Proceed to Step 2.

---

### Step 2: Determine Mode

If the member asked for a report ("give me a status report", "generate a project update"): proceed to Report Mode (Step 3).

If the member asked a specific question ("who's working on the API?", "are we on track for the April milestone?", "what decisions have been made this week?"): proceed to Conversational Mode (Step 4).

If the member invoked generally ("project pulse for X"): ask "Would you like a status report, or do you have specific questions about the project?"

---

### Step 3: Report Mode

Generate a status report using the sections configured in `project_pulse_report_sections`. For each accepted section:

**executive_summary:**
One paragraph capturing: overall project health (on track / at risk / off track), the most important recent development, and the most pressing upcoming item. This should be readable in 15 seconds.

**recent_activity:**
Key events from the activity log since the last report (or last 7 days if no previous report). Organized chronologically. Focus on: updates, decisions, idea promotions, milestone changes. Skip routine channel digests unless they surfaced important candidates.

**action_items_summary:**
Structured overview:
- Completed since last report: {count and titles}
- Currently in progress: {count, titles, and owners}
- Blocked: {count, what's blocking each, and who can unblock}
- Open (not yet started): {count and titles}
- Overdue: {count, how overdue, and owners}

**decisions_made:**
List decisions recorded since the last report with their dates, deciders, and one-line summaries. Link to the full decision records.

**milestones_status:**
For each milestone: name, target date, current status, and whether it's on track. Highlight any milestones that are approaching (within 2 weeks), at risk, or missed.

**risks_and_blockers:**
Synthesize from: blocked action items, risks noted in the project brief, overdue milestones, and any concerning patterns in the activity log (e.g., no updates for 5+ days on critical items).

**ideas_in_progress:**
List shared ideas with their statuses, collaborator counts, and any recently promoted artifacts.

Present the report to the member:

> **Status Report for '{project name}' — {today}**
> {report content}
>
> Save this report?

If yes: write to `{project}/artifacts/status-reports/{today}-status-report.md`. Log to activity log.

---

### Step 4: Conversational Mode

In conversational mode, Claude acts as the project's informed representative. The member asks questions; Claude answers from the loaded project context.

Answer precisely. Use specific dates, names, action item IDs, and decision references. Don't generalize when the data has specifics.

Examples of questions Claude should handle well:

- "What's the status of the homepage redesign?" → Check ideas, action items, and recent activity for anything related to homepage. Synthesize a coherent answer.
- "Who's blocked right now?" → Read action items with `blocked` status. Report each with what's blocking them.
- "What decisions have been made this week?" → Read decisions directory, filter by date, summarize each.
- "Is the April 15th milestone at risk?" → Check the milestone, look at action items that feed into it, assess progress.
- "What has Sarah been working on?" → Search action items, updates, and activity log for entries by or assigned to Sarah.
- "What's left to do?" → Summarize open and in-progress action items, unresolved ideas, upcoming milestones.
- "Give me the timeline of what's happened." → Walk through the activity log chronologically, narrating the project story.
- "Why did we choose this approach for the database?" → Search decisions for database-related entries, present the rationale.

Stay in conversational mode until the member moves on to another topic or ends the session. Multiple questions in sequence are expected.

If the member asks a question the data can't answer: say so. "I don't have that information in the project record. It may not have been captured as an update or decision." Don't fabricate.

---

## Directives

### Behavior

In report mode: be comprehensive but concise. A status report that takes 10 minutes to read has failed. Aim for 2-3 minutes reading time for the full report. Use the executive summary to give the 15-second version.

In conversational mode: be specific, precise, and direct. Stakeholders asking project questions want answers, not caveats. If the data says Sarah completed the API work on March 19, say that — don't hedge with "it appears that."

When the data reveals problems (blocked items, overdue milestones, no recent activity), surface them clearly. Don't soften bad news in a way that obscures it. "The API integration has been blocked for 6 days waiting on Sarah's review" is more useful than "there may be some delays in the API area."

### Constraints

Never fabricate information. If the activity log, action items, and decisions don't contain the answer, say so.

Never share information from one member's private ideas in a pulse response. Only shared ideas are visible to pulse.

Status reports are snapshots, not living documents. Once written, they are not updated. The next report is a new file.

### Edge Cases

If the project has no activity log entries: the report will be sparse. Note: "This project doesn't have activity tracking data yet. The report is based on the project brief and milestones only."

If the project has no action items: skip that section in the report. In conversational mode, note: "Action items aren't being tracked for this project."

If the status-reports directory doesn't exist: create `{project}/artifacts/status-reports/` on first use.

If a report for today already exists: append a sequence number (e.g., `2026-03-21-status-report-2.md`).

If the member asks to compare to a previous report: read the most recent previous report and highlight what changed. This is a powerful use case — "What's different since last week's report?"
