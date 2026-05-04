---
name: project-pulse-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the project-pulse task
target: project-pulse
target_type: task
upgrade_compatible: true
---

## Setup Overview
Generates status reports and enables conversational Q&A about project progress and status.

---

## Pre-Setup Checks
- Collection setup completed. At least one project exists.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify project access.
2. Register entry in `member-index.json` with alias `@ai:project-pulse`
3. Confirm to member: "project-pulse is ready. Use '@ai:project-pulse' to generate status reports and discuss project progress."

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
