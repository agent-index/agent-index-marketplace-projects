---
name: channel-digest-setup
type: setup
version: 3.0.4
collection: projects
description: Setup for the channel-digest task
target: channel-digest
target_type: task
upgrade_compatible: true
---

## Setup Overview
Configures channel-digest to monitor your project's communication channel (Slack, Microsoft Teams, or Discord) for new messages, summarize them, and extract action items.

---

## Pre-Setup Checks
- Collection setup completed. Comms channel configured for at least one project.

---

## Parameters
No member-configurable parameters.

---

## Setup Completion
1. Verify comms channel access.
2. Register entry in `member-index.json` with alias `@ai:channel-digest`
3. Confirm to member: "channel-digest is ready. Use '@ai:channel-digest' to summarize new messages and extract action items from your project's communication channel."

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
