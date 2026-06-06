---
name: transition-project-setup
type: setup
version: 4.0.0
collection: projects
description: Setup for the transition-project task
target: transition-project
target_type: task
upgrade_compatible: true
---

## Setup Overview
Validates that the collection is installed and the member's private space exists. No member-specific configuration.

## Pre-Setup Checks
- Collection installed (setup responses present)
- `member_folder_id` present in `member-index.json` (if missing, `@ai:update` self-provisions)

## Parameters
No member-configurable parameters.

## Setup Completion
1. Register entry in `member-index.json` with alias `@ai:transition-project`
2. Confirm to member: "You can move projects between private and org-public tiers with '@ai:transition-project'."

## Upgrade Behavior

### Preserved Responses
N/A.

### Reset on Upgrade
N/A.

### Requires Member Attention
None.

### Migration Notes
- New in collection 4.0.0.
