---
name: archive-project-setup
type: setup
version: 1.0.0
collection: projects
description: Setup interview for the archive-project task
target: archive-project
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup takes about one minute. It connects your archive-project task to your org's shared project directory.

---

## Pre-Setup Checks

- `collection-setup-responses.md` is readable → if not: "The Projects collection hasn't been fully configured by your org admin yet. Contact them to complete collection setup before you can install this task."
- `shared_projects_path` from collection setup exists and is readable → if not: check `aifs_auth_status()` and attempt automatic re-authentication if `authenticated: false`. If re-auth succeeds, retry. If not: "The shared projects directory doesn't appear to be accessible. I tried to restore your connection but wasn't able to. Try '@ai:member-bootstrap' to troubleshoot."

---

## Parameters

### Org-Mandated Parameters [org-mandated]

**shared_projects_path** [org-mandated]
- Description: The remote filesystem path where all project data is stored (accessed via `aifs_*` MCP tools)
- Value source: injected from collection org-setup-responses
- Member visibility: read-only

---

## Setup Completion

1. Write all collected parameter values to `setup-responses.md`
2. Write the installed instance to `/members/{member-id}/tasks/archive-project/`
3. Write `manifest.json`
4. Register entry in `member-index.json` with alias `@ai:archive-project`
5. Confirm to member: "archive-project is installed. Say '@ai:archive-project' or 'archive project {name}' to archive any active project."

---

## Upgrade Behavior

### Preserved Responses
All responses are injected from collection setup — preserved automatically when the collection upgrades.

### Reset on Upgrade
None.

### Requires Member Attention
Any new org-level parameters introduced in a collection upgrade will be surfaced.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
