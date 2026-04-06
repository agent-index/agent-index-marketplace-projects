---
name: create-idea-setup
type: setup
version: 3.0.0
collection: projects
description: Setup for the create-idea task
target: create-idea
target_type: task
upgrade_compatible: true
---

## Setup Overview
Creates a new private exploration space for ideas within a project.

---

## Pre-Setup Checks
- Collection setup completed. At least one project exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify project access.
2. Register entry in `member-index.json` with alias `@ai:create-idea`
3. Confirm to member: "create-idea is ready. Use '@ai:create-idea' to start exploring new ideas for your projects."

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
