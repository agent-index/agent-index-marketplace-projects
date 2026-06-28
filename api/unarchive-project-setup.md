---
name: unarchive-project-setup
type: setup
version: 3.0.4
collection: projects
description: Setup interview for the unarchive-project task
target: unarchive-project
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup takes about one minute. It connects your unarchive-project task to your org's shared project directory.

---

## Pre-Setup Checks

- `collection-setup-responses.md` is readable → if not: "The Projects collection hasn't been fully configured by your org admin yet. Contact them to complete collection setup before you can install this task."
- The commons `/shared/projects/` is readable → if not: auth-retry guidance, then '@ai:member-bootstrap'.

---

## Parameters

### Org-Mandated Parameters [org-mandated]

**projects_default_visibility** [org-mandated]
- Description: Which tier is pre-selected at project creation (org_public_first | ask | private_first); the commons is the fixed `/shared/projects/`; private projects live in members' own My Drives
- Value source: injected from collection org-setup-responses
- Member visibility: read-only

---

## Setup Completion

1. Write all collected parameter values to `setup-responses.md`
2. Write the installed instance to `/members/{member-id}/tasks/unarchive-project/`
3. Write `manifest.json`
4. Register entry in `member-index.json` with alias `@ai:unarchive-project`
5. Confirm to member: "unarchive-project is installed. Say '@ai:unarchive-project' or 'unarchive project {name}' to restore any archived project."

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
