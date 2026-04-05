---
name: projects-collection-setup
type: collection-setup
version: 3.0.4
collection: projects
description: Org-admin setup interview for the Projects collection
upgrade_compatible: true
---

## Collection Setup Overview

This setup configures how the Projects collection works across your org. It covers project data storage, roles, default project structure (project brief, milestones, comms channel integration), and project tracking features (ideas, action items, activity logging, channel monitoring, project pulse). Each feature is presented individually — accept or skip based on what fits your org. This takes about fifteen minutes and can be updated later if your needs change.

---

## Prerequisites

- You have org admin credentials in agent-index
- The `/shared/projects/` directory exists and is writable on the remote filesystem via `aifs_write` (or you have an admin create it before proceeding)

---

## Org-Level Parameters

### Shared Projects Directory

**shared_projects_path**
- Description: The remote filesystem path (under `/shared/`) where all project data will be stored. All members with access to this collection will read and write project data here via `aifs_read`/`aifs_write`.
- Applies to: create-project, edit-project, archive-project, unarchive-project
- Interview prompt: "Where should project data be stored? The default is `/shared/projects/` — does that work for your org, or do you need a different path?"
- Accepted values: Any valid path on the remote filesystem (under `/shared/`) that exists and is writable via `aifs_write`
- Default: `/shared/projects/`
- Implication of choices: All members use the same path. If you change this after projects have been created, existing project data will need to be moved manually.

---

### Project Roles Configuration

**roles_config**
- Description: Controls whether the org defines a standard set of project roles, and whether project creators can modify that list.
- Applies to: create-project, edit-project
- Interview prompt: "How would you like to handle project roles — the labels that describe what each person does on a project, like 'Lead' or 'Contributor'? There are three options:
  1. **Org-defined, locked** — You define the roles here and every project uses exactly that list. Project creators cannot change it.
  2. **Org-defined, flexible** — You define a suggested starting list here, but project creators can add, remove, or rename roles for their specific project.
  3. **Project-defined** — You don't define any roles here. Every project team defines their own roles from scratch when the project is created.
  Which option fits how your org works?"
- Accepted values: `org-mandated` | `org-suggested` | `project-defined`
- Default: `org-suggested`
- Implication of choices:
  - `org-mandated`: Most consistent across the org. Best when roles are standardized (e.g., every project has an Owner, PM, and Contributors). Least flexible for project teams with unique structures.
  - `org-suggested`: Balances consistency with flexibility. Teams start from a common vocabulary but can adapt.
  - `project-defined`: Most flexible. Best for orgs where project structures vary widely. Requires every project creator to define roles — no defaults to fall back on.

**org_roles** (only asked if roles_config is `org-mandated` or `org-suggested`)
- Description: The org-level roles list. Each entry is a role name.
- Applies to: create-project, edit-project
- Interview prompt: "What roles should be available on projects? Give me a list — for example: Owner, Project Manager, Lead, Contributor, Reviewer, Stakeholder. You can use any names that fit your org."
- Accepted values: A list of role name strings. Minimum 1 role if roles_config is `org-mandated`. Empty list not permitted for `org-mandated`.
- Default: `["Owner", "Project Manager", "Contributor"]`
- Implication of choices: These names will appear as options when adding members to a project. For `org-mandated`, these are the only options. For `org-suggested`, project creators can extend or modify this list.

---

## Default Project Structure

The following features define what elements are available during project creation. Each one is presented to the org admin as an accept-or-skip choice. Accepted features become steps in the project creation and editing workflows. Skipped features are not presented to members.

For each accepted feature, the org admin may also configure whether the feature is **required** or **optional** during project creation:
- **required** — the member is prompted and must provide input before the project can be created
- **optional** (default) — the member is prompted but can skip and add it later via edit-project

None of these features are hard requirements at the system level. Even when marked "required" by the org admin, the enforcement is conversational — Claude prompts the member and explains the org expectation, but does not block project creation if the member insists on skipping. The project record is always created.

---

### Project Brief

**brief_enabled**
- Description: When enabled, project creation includes a structured project brief instead of a single free-text scope narrative. The brief prompts the member for multiple sections that together describe the project comprehensively.
- Applies to: create-project, edit-project
- Interview prompt: "Would you like to enable structured project briefs? When enabled, project creators are prompted for a detailed brief that includes a description, goals, success criteria, constraints, dependencies, stakeholders, and risks — instead of just a single free-text scope field. Each section is individually skippable by the member."
- Accepted values: `true` | `false`
- Default: `true`

**brief_sections** (only asked if brief_enabled is `true`)
- Description: Controls which sections appear in the project brief and whether each is required or optional for members.
- Applies to: create-project, edit-project
- Interview flow: Present each section one at a time. For each section, ask: "Include {section name} in the project brief? (accept / skip)" If accepted, ask: "Should this be required or optional during project creation?"
- Available sections:

  | Section | Description | Default |
  |---|---|---|
  | **description** | What the project is — the core narrative. Replaces the old scope field. | accepted, required |
  | **goals** | What the project aims to achieve — concrete outcomes. | accepted, optional |
  | **success_criteria** | How you know the project succeeded — measurable where possible. | accepted, optional |
  | **constraints** | Budget, timeline, regulatory, technical, or resource constraints. | accepted, optional |
  | **dependencies** | What this project depends on — other projects, external deliverables, vendor timelines. | accepted, optional |
  | **stakeholders** | People who care about the outcome but are not on the project team. Resolved against the members registry using the standard member resolution pattern. | accepted, optional |
  | **risks** | Known risks and uncertainties at project inception. | accepted, optional |

- Implication of choices: Only accepted sections are presented to members during project creation. Required sections generate a prompt that explains the org expects this field to be filled in. Optional sections are offered but easily skippable. Skipped sections do not appear in the project brief at all.

---

### Project Milestones

**milestones_enabled**
- Description: When enabled, project creation includes a step for defining key milestones and target dates. Milestones are stored as structured data in the project record and can be used by session-start tasks to surface approaching deadlines.
- Applies to: create-project, edit-project
- Interview prompt: "Would you like to enable project milestones? When enabled, project creators can define key dates and deliverables for their project. These are stored in the project record and can surface reminders when deadlines approach."
- Accepted values: `true` | `false`
- Default: `true`

**milestones_enforcement** (only asked if milestones_enabled is `true`)
- Description: Whether milestones are required or optional during project creation.
- Applies to: create-project
- Interview prompt: "Should milestones be required or optional during project creation? Even when required, the member can still skip if they're not ready — but they'll be prompted to add them."
- Accepted values: `required` | `optional`
- Default: `optional`

---

### Communications Channel Integration

**comms_channel_enabled**
- Description: When enabled, project creation includes an option to create a dedicated channel on the org's communications platform (Slack, Teams, Discord, etc.) for the project. Members added to the project are invited to the channel.
- Applies to: create-project, edit-project, archive-project, unarchive-project
- Interview prompt: "Does your org use a team communication platform like Slack, Microsoft Teams, or Discord?"
  - If yes: "Which platform?" → collect `comms_platform`
  - Then: "Would you like to enable project-specific channel creation? When enabled, project creators can optionally create a dedicated channel for their project. Team members added to the project get invited to the channel automatically."
  - If no: skip this section entirely
- Accepted values: `true` | `false`
- Default: `false` (requires explicit opt-in because it has an external dependency)

**comms_platform** (only asked if comms_channel_enabled is `true`)
- Description: The team communications platform the org uses.
- Accepted values: `slack` | `teams` | `discord` | `other`
- Default: none — must be specified
- Note: If `other` is selected, the admin provides the platform name. Channel creation will still be offered but the task will note that automatic channel creation may require a compatible MCP connector.

**Slack app prerequisite** (admin guidance — presented immediately after the admin selects `slack` as their platform, before continuing with the remaining comms parameters)
- Interview prompt: "Before we continue — channel creation requires a Slack app in your workspace that grants user-level tokens to members. If you don't already have one set up, here's what's needed:
  1. A workspace admin creates a Slack app at https://api.slack.com/apps (or uses an existing one).
  2. Under **OAuth & Permissions**, add these user token scopes: `channels:write`, `channels:manage`, `users:read.email`, and `groups:write` (the last one only needed if you plan to allow private project channels).
  3. Install the app to your workspace.
  4. Each member then authorizes the app individually — this generates a personal user token (starts with `xoxp-`) that they save to a local file. The member setup interview will walk them through that step.

  If your workspace already has a Slack app with these scopes, you're all set — just make sure members know how to authorize and save their tokens. Want to continue with the rest of the channel configuration?"
- Note: This is informational guidance, not a collected parameter. No value is stored. The admin may need to coordinate with their Slack workspace admin if they are not the same person. Do not block setup if the admin says the app doesn't exist yet — they can create it before rolling out to members.

**comms_channel_naming_template** (only asked if comms_channel_enabled is `true`)
- Description: The naming convention for project channels.
- Interview prompt: "What naming convention should project channels use? I'll substitute `{slug}` with the project's slug. For example, `proj-{slug}` would create a channel called `#proj-rebrand-2026` for a project with the slug `rebrand-2026`."
- Accepted values: Any string containing `{slug}`
- Default: `proj-{slug}`
- Implication of choices: The channel name is generated automatically from this template. Members can override the generated name during project creation if they want.

**comms_channel_enforcement** (only asked if comms_channel_enabled is `true`)
- Description: Whether channel creation is required or optional during project creation.
- Interview prompt: "Should channel creation be required or optional during project creation?"
- Accepted values: `required` | `optional`
- Default: `optional`

**comms_channel_archive_on_project_archive** (only asked if comms_channel_enabled is `true`)
- Description: Controls behavior when a project is archived.
- Interview prompt: "When a project is archived, should the system prompt the member to archive the project's channel as well?"
- Accepted values: `prompt` | `automatic` | `none`
- Default: `prompt`
- Implication of choices:
  - `prompt`: The archive-project task asks "This project has a channel #{channel_name}. Would you like to archive the channel as well?"
  - `automatic`: The channel is archived automatically when the project is archived (with a confirmation note to the member).
  - `none`: Channel is left as-is when the project is archived.

**slack_user_token_path** (only asked if comms_channel_enabled is `true` AND comms_platform is `slack`)
- Description: Default path where each member's Slack user token file is expected. The token is a per-member credential (starts with `xoxp-`) — the script acts on behalf of the individual member, not a shared bot. Each member stores their own token. Required scopes: `channels:write`, `channels:manage`, `users:read.email`, and `groups:write` (for private channels).
- Interview prompt: "Channel creation uses each member's own Slack user token so channels are created as that person. Where should members store their token file? This is a default path — members can override it during their own setup. The file should contain just the token string (starts with `xoxp-`)."
- Accepted values: Any valid local filesystem path pattern (can include `{member_workspace}` placeholder)
- Default: `{member_workspace}/.credentials/slack-user-token.txt`
- Note: The token file should contain only the token string, no other content. Members configure this path during their member-bootstrap or task setup. The `create_channel.py` script in `apps/slack-channel-creator/` reads from this path at runtime. If a member hasn't set up their token yet, channel creation gracefully falls back to `pending` status.

---

## Project Tracking

The following features enable ongoing project tracking — ideas, action items, activity logging, channel monitoring, and status reporting. These are presented after the default project structure features. Each is accept-or-skip.

Activity logging is automatically enabled if any tracking feature (ideas, action items, channel monitoring, or project pulse) is accepted. It is the foundational data layer that all other tracking features depend on.

---

### Activity Logging

**activity_log_enabled**
- Description: When enabled, projects maintain an append-only activity log (`activity-log.jsonl`) that records all meaningful project events: updates, decisions, action item changes, idea promotions, channel digests, milestone updates, and member changes. This is the foundational data layer for project tracking and is required by all other tracking features.
- Applies to: update-project, manage-action-items, project-decide, share-idea, manage-ideas, channel-digest, project-pulse
- Interview prompt: "Would you like to enable project activity logging? This creates a timestamped timeline of everything that happens in each project — updates, decisions, action items, ideas. It's the foundation for all project tracking features."
- Accepted values: `true` | `false`
- Default: `true`
- Note: Automatically set to `true` if any of ideas, action items, channel monitoring, or project pulse are enabled.

---

### Ideas

**ideas_enabled**
- Description: When enabled, members can create ideas — private explorations that can be shared with collaborators and eventually promoted to official project artifacts. Ideas provide a structured path from early thinking to actionable decisions without prematurely exposing working thoughts to the team.
- Applies to: create-idea, share-idea, manage-ideas
- Interview prompt: "Would you like to enable project ideas? Ideas let members explore concepts privately, share them with collaborators when ready, and promote approved artifacts to the project with actionable assignments. This keeps working thoughts separate from official project direction."
- Accepted values: `true` | `false`
- Default: `true`

**ideas_require_private_stage**
- Description: Controls whether ideas must start as private drafts, or whether members can create ideas directly in the shared project space.
- Interview prompt (only if ideas_enabled is `true`): "Should ideas always start as private drafts before being shared? Or should members also be able to create ideas directly in the shared project space?"
  - **Private first** — ideas always start in the member's private workspace. They must be explicitly shared to become visible to the project team.
  - **Either** — members can choose to start private or go directly to shared.
- Accepted values: `private_first` | `either`
- Default: `either`

---

### Action Items

**action_items_enabled**
- Description: When enabled, projects can track actionable work items with owners, statuses, due dates, dependencies, and update histories. Action items can be created directly, spawned from decisions, generated from promoted idea artifacts, or extracted from channel digests (with human review).
- Applies to: manage-action-items, update-project, project-decide, manage-ideas, channel-digest, project-pulse
- Interview prompt: "Would you like to enable project action items? Action items track who needs to do what, by when, and what depends on what. They can be created directly, generated from decisions or ideas, or extracted from channel conversations."
- Accepted values: `true` | `false`
- Default: `true`

---

### Channel Monitoring

**channel_monitor_enabled** (only offered if comms_channel_enabled is `true`)
- Description: When enabled, Claude can check a project's communications channel for new messages since the last check, produce a digest summary, and extract candidate action items and updates for human review. Nothing from the channel is automatically promoted — all extracted items go through a review queue.
- Applies to: channel-digest, manage-action-items
- Interview prompt: "Would you like to enable channel monitoring? When enabled, Claude can check a project's Slack/Teams/Discord channel, summarize what's been discussed, and extract potential action items and updates for you to review. Nothing is auto-promoted — you always review before anything becomes official."
- Accepted values: `true` | `false`
- Default: `true` (if comms_channel_enabled)

**channel_monitor_cadence**
- Description: Suggested cadence for channel monitoring. This is a recommendation surfaced during session-start, not an automated schedule.
- Interview prompt (only if channel_monitor_enabled is `true`): "How often should project leads be prompted to review their project channels? This is a suggestion surfaced at session start, not an automatic process."
- Accepted values: `per_session` | `daily` | `weekly` | `manual`
- Default: `daily`
- Implication of choices:
  - `per_session`: Every time a member opens a session with an active project, they're offered a channel check.
  - `daily`: Suggestion appears once per day at session start.
  - `weekly`: Suggestion appears once per week.
  - `manual`: Never prompted — members run channel-digest on demand only.

---

### Project Pulse

**project_pulse_enabled**
- Description: When enabled, provides status report generation and conversational project Q&A for stakeholders and managers. Synthesizes data from the activity log, action items, decisions, milestones, ideas, and project brief into coherent summaries and answers.
- Applies to: project-pulse
- Interview prompt: "Would you like to enable project pulse? This gives stakeholders and managers the ability to generate status reports and have conversations with Claude about a project as if Claude were the project manager — who did what, what's left, what's blocked, are we on track."
- Accepted values: `true` | `false`
- Default: `true`

**project_pulse_report_sections**
- Description: Default sections included in generated status reports. Org admin selects which sections to include.
- Interview prompt (only if project_pulse_enabled is `true`): "What should status reports include? I'll show you the available sections — accept or skip each one."
- Available sections:

  | Section | Description | Default |
  |---|---|---|
  | **executive_summary** | One-paragraph overview of project health and progress. | accepted |
  | **recent_activity** | Key events from the activity log since the last report. | accepted |
  | **action_items_summary** | Open, completed, and blocked action items with owners. | accepted |
  | **decisions_made** | Decisions recorded since the last report. | accepted |
  | **milestones_status** | Milestone progress and upcoming deadlines. | accepted |
  | **risks_and_blockers** | Current blockers, risks, and items needing attention. | accepted |
  | **ideas_in_progress** | Shared ideas and their status (if ideas_enabled). | skipped |

---

## Setup Completion

1. Write all collected parameter values to `collection-setup-responses.md`
2. Verify that the `shared_projects_path` directory exists and is writable on the remote filesystem via `aifs_exists` and `aifs_write`. If it does not exist, prompt the admin: "The directory `{path}` does not exist on the remote filesystem yet. Would you like me to create it, or do you want to use a different path?"
3. Initialize `projects-manifest.json` at `{shared_projects_path}/projects-manifest.json` on the remote filesystem via `aifs_write` if it does not already exist:
```json
{
  "last_updated": "{today}",
  "projects": []
}
```
4. Confirm to admin with a summary of everything configured:
> "Projects collection is configured. Here's what was set:
> - Project data location: {shared_projects_path}
> - Roles configuration: {plain-language description of roles_config choice}
> {if org_roles defined}: - Org roles: {list}
> - Project brief: {enabled/disabled} {if enabled: list of accepted sections with required/optional}
> - Milestones: {enabled/disabled} {if enabled: required/optional}
> - Comms channel: {enabled/disabled} {if enabled: platform, naming template, enforcement, archive behavior}
> - Activity logging: {enabled/disabled}
> - Ideas: {enabled/disabled} {if enabled: private_first/either}
> - Action items: {enabled/disabled}
> - Channel monitoring: {enabled/disabled} {if enabled: cadence}
> - Project pulse: {enabled/disabled} {if enabled: report sections}
>
> Members can now install the project tasks via '@ai:setup'. They'll be able to create and manage projects at {shared_projects_path}."

---

## Upgrade Behavior

### Preserved Responses
- `shared_projects_path` — always preserved; changing this would orphan existing project data
- `org_roles` — preserved; org admin must explicitly update roles through a separate edit flow
- `brief_sections` — preserved; changing section requirements does not affect existing projects
- `comms_platform` — preserved; changing platforms does not migrate existing channels
- `comms_channel_naming_template` — preserved; changing the template does not rename existing channels
- `ideas_require_private_stage` — preserved; changing does not affect existing ideas
- `channel_monitor_cadence` — preserved; safe to change at any time
- `project_pulse_report_sections` — preserved; safe to change at any time

### Reset on Upgrade
- None — all responses are preserved across upgrades by default

### Requires Admin Attention
- Any new parameters introduced in a new version are surfaced to the admin during upgrade
- New default project structure features added in future versions are presented as accept/skip choices during upgrade

### Migration Notes
- v1.0 → v2.0: Three new default project structure features added (project brief, milestones, comms channel). Existing orgs upgrading from v1.0 will be prompted to accept or skip each feature. Existing projects are not modified — new features only apply to projects created after the upgrade. The `scope narrative` field in existing projects remains valid and is treated as the `description` section of the project brief.
- v2.0 → v3.0: Five project tracking features added (activity logging, ideas, action items, channel monitoring, project pulse). Existing orgs upgrading from v2.0 will be prompted to accept or skip each. Existing projects do not gain tracking directories automatically — the new directories are created when a tracking task is first used on an existing project, or via edit-project.
