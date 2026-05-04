---
name: update-project-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the update-project task
target: update-project
target_type: task
upgrade_compatible: true
---

## Setup Overview
Primary input mechanism for project updates — share progress and report blockers to your team.

---

## Pre-Setup Checks
- Collection setup completed. At least one project exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify project access.
2. Register entry in `member-index.json` with alias `@ai:update-project`
3. Confirm to member: "update-project is ready. Use '@ai:update-project' to share progress and report blockers."

---

## Upgrade Behavior

### Preserved Responses
N/A.

### Reset on Upgrade
N/A.

### Requires Member Attention
None.

### Migration Notes
- v3.0 → future versions: migration notes will be added here as new versions are published.
