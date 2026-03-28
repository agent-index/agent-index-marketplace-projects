# Projects Collection

A foundational project management collection for agent-index. Provides a shared project registry where org members can create, manage, and archive projects with structured ownership, team membership, and role assignments.

## What's Included

- **create-project** — Create a new project with scope, ownership, member list, and roles
- **edit-project** — Update any field of an active project
- **archive-project** — Mark a project as no longer relevant (preserves all data)
- **unarchive-project** — Restore an archived project to active status

## Project Data Location

All project data is stored on the org's remote filesystem (accessed via `aifs_*` MCP tools) at the path configured during collection setup (default: `/shared/projects/`). This is shared org-level data — not stored in individual member workspaces.

## Project Structure

Each project gets its own directory:

```
/shared/projects/{project-slug}/
  project.md          ← scope, ownership, members, roles
  /assets/            ← any files relevant to the project
  /state/             ← project state (current-state.md)
  /artifacts/         ← agent-index generated outputs
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

## Version History

See CHANGELOG.md.
