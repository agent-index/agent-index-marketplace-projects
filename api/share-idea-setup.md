---
name: share-idea-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the share-idea task
target: share-idea
target_type: task
upgrade_compatible: true
---

## Setup Overview
Promotes a private idea to the project's shared space and invites collaborators to contribute.

---

## Pre-Setup Checks
- Collection setup completed. At least one private idea exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify shared projects directory access.
2. Register entry in `member-index.json` with alias `@ai:share-idea`
3. Confirm to member: "share-idea is ready. Use '@ai:share-idea' to promote ideas to the shared workspace."

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
