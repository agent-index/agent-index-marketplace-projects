---
name: create-project-setup
type: setup
version: 1.0.0
collection: projects
description: Setup interview for the create-project task
target: create-project
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup takes about one minute. It connects your create-project task to your org's shared project directory so you're ready to create projects right away.

---

## Pre-Setup Checks

- `collection-setup-responses.md` is readable → if not: "The Projects collection hasn't been fully configured by your org admin yet. Contact them to complete collection setup before you can install this task."
- `shared_projects_path` from collection setup exists and is readable → if not: check `aifs_auth_status()` and attempt automatic re-authentication if `authenticated: false`. If re-auth succeeds, retry. If not: "The shared projects directory doesn't appear to be accessible. I tried to restore your connection but wasn't able to. Try '@ai:member-bootstrap' to troubleshoot."

---

## Parameters

### Org-Mandated Parameters [org-mandated]

**shared_projects_path** [org-mandated]
- Description: The remote filesystem path where all project data is stored (accessed via `aifs_*` MCP tools)
- Value source: injected from collection org-setup-responses
- Member visibility: read-only (Claude may explain the value if asked)

**roles_config** [org-mandated]
- Description: How project roles are managed across the org
- Value source: injected from collection org-setup-responses
- Member visibility: read-only

**org_roles** [org-mandated]
- Description: The org-defined roles list (may be empty if roles_config is project-defined)
- Value source: injected from collection org-setup-responses
- Member visibility: read-only

### Member-Defined Parameters [member-defined]

**slack_user_token_path** [member-defined] (only asked if comms_channel_enabled is `true` AND comms_platform is `slack`)
- Description: Path to this member's Slack user token file. The token is used when creating project channels and inviting members — the channel is created as this member, not a shared bot.
- Default: inherited from collection setup's `slack_user_token_path` (typically `{member_workspace}/.credentials/slack-user-token.txt`)
- Ask: "Channel creation uses your personal Slack token. The org default path is `{slack_user_token_path}`. Does that work for you, or do you store it somewhere else?"
- Validation: Check that the file exists and contains a string starting with `xoxp-`. If not found: "I can't find a Slack token at that path. You can set this up later — channel creation will just be marked as pending until it's configured. Would you like me to walk you through getting a Slack user token?"

---

## Setup Completion

1. Write all collected parameter values to `setup-responses.md`
2. Write the installed instance to `/members/{member-id}/tasks/create-project/`
3. Write `manifest.json`
4. Register entry in `member-index.json` with alias `@ai:create-project`
5. Confirm to member: "create-project is installed. Say '@ai:create-project' or 'create project' whenever you're ready to start a new project."

---

## Upgrade Behavior

### Preserved Responses
All responses are injected from collection setup — they are preserved automatically when the collection upgrades.

### Reset on Upgrade
None.

### Requires Member Attention
Any new org-level parameters introduced in a collection upgrade will be surfaced.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
