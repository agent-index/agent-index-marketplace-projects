---
name: manage-ideas-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the manage-ideas task
target: manage-ideas
target_type: task
upgrade_compatible: true
---

## Setup Overview
Enables viewing, editing, and management of ideas — including adding artifacts, creating response ideas, and collaborating with team members.

---

## Pre-Setup Checks
- Collection setup completed.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify shared projects directory access.
2. Register entry in `member-index.json` with alias `@ai:manage-ideas`
3. Confirm to member: "manage-ideas is ready. Use '@ai:manage-ideas' to view and manage ideas across your projects."

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
