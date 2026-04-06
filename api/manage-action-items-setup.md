---
name: manage-action-items-setup
type: setup
version: 3.0.0
collection: projects
description: Setup for the manage-action-items task
target: manage-action-items
target_type: task
upgrade_compatible: true
---

## Setup Overview
Enables creation, viewing, assignment, completion, reassignment, and chaining of action items across projects.

---

## Pre-Setup Checks
- Collection setup completed. At least one project exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify project access.
2. Register entry in `member-index.json` with alias `@ai:manage-action-items`
3. Confirm to member: "manage-action-items is ready. Use '@ai:manage-action-items' to create and manage action items."

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
