---
name: project-decide-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the project-decide task
target: project-decide
target_type: task
upgrade_compatible: true
---

## Setup Overview
Records official project decisions with rationale and spawned action items.

---

## Pre-Setup Checks
- Collection setup completed. At least one project exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify project access.
2. Register entry in `member-index.json` with alias `@ai:project-decide`
3. Confirm to member: "project-decide is ready. Use '@ai:project-decide' to record official project decisions."

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
