# Projects Collection

Full project lifecycle management for agent-index. Create projects with structured briefs, track ideas from private exploration to actionable artifacts, manage action items with dependency chains, record decisions, monitor comms channels, and generate status reports for stakeholders.

## What's Included

### Project Lifecycle

- **create-project** — Create a new project with a structured brief, ownership, member list, roles, milestones, and optional comms channel
- **edit-project** — Update any field of an active project, add members, create or archive channels
- **archive-project** — Mark a project as no longer relevant (preserves all data, optionally archives the comms channel)
- **unarchive-project** — Restore an archived project to active status
- **transition-project** — Move a project between visibility tiers: private → org-public (the org gains custody) or org-public → private (copied to the owner's space; an archived stub remains in the commons)

### Ideas

- **create-idea** — Capture a private idea in your own member space for early-stage thinking — invisible to everyone until you share or promote it
- **share-idea** — Promote a private idea to the project's shared space with collaborator assignments
- **manage-ideas** — View, edit, and manage ideas across projects; promote approved artifacts to project scope

### Project Tracking

- **update-project** — Record incremental project updates with activity log integration
- **manage-action-items** — Track action items with dependencies, assignments, and status workflows; issue project-prefixed IDs, set org-defined fields, and apply tags
- **project-decide** — Record project decisions with rationale, context, and spawned action items

### Monitoring and Reporting

- **channel-digest** — Summarize project channel conversations and extract candidate action items and decisions via a review queue
- **project-pulse** — Status report generation for stakeholders and conversational project Q&A

### Onboarding

- **projects-tutorial** — Guided tour of the projects collection for new members

## Action Item IDs, Fields, and Tags (4.2)

**IDs are project-prefixed.** Action items are numbered `{PREFIX}-{NNN}` — `MOB-014`, `PAY-003`. The prefix is chosen when the project is created (suggested from the project name, confirmed or overridden by the creator) and is **unique across the org**, so an ID identifies one item anywhere it appears: a branch name, a Slack message, a pull request. It can be changed until the project issues its first action item, then it locks — by that point the ID is referenced outside agent-index and renaming it would invalidate those references. A project that already has action items keeps the prefix it is already using, resolved from its own items — nothing is renamed or renumbered, ever, including IDs that predate any convention. The first new item on such a project offers to reserve its prefix; `upgrade/4-2-to-4-3.md` does the same in bulk for an admin. Rules: [`action-item-prefix-rules.md`](action-item-prefix-rules.md).

**Fields are defined by your org admin.** An admin can add, extend and deprecate action-item fields at any time — a type, an effort estimate, a compliance flag — in `action-item-fields.json`. Fields are shared by every project, so a value means the same thing everywhere. **The collection ships none**: after upgrading, nothing changes until an admin defines one. Adding a field never rewrites existing items — items without a value read as the field's default. Admin guide: [`action-item-fields-guide.md`](action-item-fields-guide.md).

**Tags are free-form and belong to members.** Any member can tag a project or an action item, with no admin setup. Tags are normalized on write and existing project tags are suggested at item creation, so a shared vocabulary builds rather than fragmenting. Project tags and item tags are independent — no inheritance.

**Scope, stated plainly:** field and tag queries resolve **one project at a time**. `project-pulse` reports a project's open bug count or total effort per assignee; there is no org-wide rollup across projects in 4.2.

## Project Data Location

All project data is stored on the org's remote filesystem (accessed via `aifs_*` tools) at the path configured during collection setup (default: `/shared/projects/`). This is shared org-level data — not stored in individual member workspaces. Private projects and private ideas live in their owner's own member space on the remote filesystem (not the local workspace, which changed in 4.0) and are invisible to the org until shared or promoted.

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

Discovery (4.0): one pointer file per discoverable item at `/shared/projects-index/` — org-public projects always; private projects and ideas only once shared (invisible until then; they live in their owners' own My Drives). The 3.x `projects-manifest.json` is retired.

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

4.4.1

## Version History

See CHANGELOG.md.
