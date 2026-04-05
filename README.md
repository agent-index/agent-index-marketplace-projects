# Projects Collection

Full project lifecycle management for agent-index. Create projects with structured briefs, track ideas from private exploration to actionable artifacts, manage action items with dependency chains, record decisions, monitor comms channels, and generate status reports for stakeholders.

## What's Included

### Project Lifecycle

- **create-project** — Create a new project with a structured brief, ownership, member list, roles, milestones, and optional comms channel
- **edit-project** — Update any field of an active project, add members, create or archive channels
- **archive-project** — Mark a project as no longer relevant (preserves all data, optionally archives the comms channel)
- **unarchive-project** — Restore an archived project to active status

### Ideas

- **create-idea** — Capture a private idea in your local workspace for early-stage thinking
- **share-idea** — Promote a private idea to the project's shared space with collaborator assignments
- **manage-ideas** — View, edit, and manage ideas across projects; promote approved artifacts to project scope

### Project Tracking

- **update-project** — Record incremental project updates with activity log integration
- **manage-action-items** — Track action items with dependencies, assignments, and status workflows
- **project-decide** — Record project decisions with rationale, context, and spawned action items

### Monitoring and Reporting

- **channel-digest** — Summarize project channel conversations and extract candidate action items and decisions via a review queue
- **project-pulse** — Status report generation for stakeholders and conversational project Q&A

### Onboarding

- **projects-tutorial** — Guided tour of the projects collection for new members

## Project Data Location

All project data is stored on the org's remote filesystem (accessed via `aifs_*` MCP tools) at the path configured during collection setup (default: `/shared/projects/`). This is shared org-level data — not stored in individual member workspaces. Ideas start private in the member's local workspace and are promoted to shared space when shared.

## Project Structure

Each project gets its own directory:

```
/shared/projects/{project-slug}/
  project.md          ← brief, ownership, members, roles, milestones
  /ideas/             ← shared ideas promoted from member workspaces
  /assets/            ← any files relevant to the project
  /state/             ← project state (current-state.md, activity-log.jsonl)
  /artifacts/         ← agent-index generated outputs (pulse reports, etc.)
```

A manifest at `/shared/projects/projects-manifest.json` provides a lightweight index of all projects and their status.

## Project Lifecycle

```
(created) → active → archived
                ↑        ↓
           unarchive ←───┘
```

Projects have two statuses: `active` and `archived`. There is no intermediate "complete" state — a project that is done but may be relevant later stays active; a project that is no longer relevant gets archived.

## Roles Configuration

During collection setup, org admins choose one of three modes:

| Mode | Behavior |
|---|---|
| `org-mandated` | Org defines roles; all projects use exactly that list |
| `org-suggested` | Org defines a starting list; project creators can modify per project |
| `project-defined` | No org default; each project defines its own roles |

## Communications Channel Integration

When enabled during collection setup, project creation can optionally create a dedicated channel on Slack, Teams, or Discord. Team members are invited automatically. Channels are created using each member's own user token (not a shared bot), so channels appear as created by the actual person. Channel monitoring via `channel-digest` extracts action items, updates, and decisions from ongoing conversations.

## Version

3.0.4

## Version History

See CHANGELOG.md.
