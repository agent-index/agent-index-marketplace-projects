---
name: create-project
type: task
version: 3.0.0
collection: projects
description: Creates a new project in the org's shared project registry, including ownership, brief, milestones, team members, roles, optional comms channel, and project tracking directories.
stateful: false
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - system: "Slack / Microsoft Teams / Discord (conditional)"
    access_required: "Channel creation, member invitation (only if comms_channel_enabled)"
    contact: "org admin"
reads_from: null
writes_to: null
---

## About This Task

Creating a project establishes the foundational record that all subsequent project work hangs from. This task guides the member through defining the project's name, ownership, brief, milestones, team members, roles, and communications channel — then writes the project record to the org's shared project registry and registers it in the projects manifest.

Which steps appear during project creation depends on what the org admin enabled during collection setup. The core steps (name, owner/PM, roles, members) are always present. Optional steps (project brief, milestones, comms channel) appear only if the org admin accepted them during setup.

A project created through this task is immediately visible to all members with access to the shared projects directory. The project record is the source of truth for everything about the project.

### Inputs

The member provides: project name, owner, project manager, and — depending on org configuration — project brief sections, milestones, comms channel preferences, initial member list, and roles.

### Outputs

Two files are written upon successful completion:

- `{shared_projects_path}/{project-slug}/project.md` — the full project record
- `{shared_projects_path}/projects-manifest.json` — updated with the new project entry

The project directory structure is also created:
```
{shared_projects_path}/{project-slug}/
  project.md
  /assets/
  /state/
    current-state.md
    channel-cursor.json          (if comms channel enabled)
    review-queue.json            (if channel monitoring enabled)
  /artifacts/
  /activity/                     (if activity logging enabled)
    activity-log.jsonl
  /ideas/                        (if ideas enabled)
  /decisions/                    (if activity logging enabled)
  action-items.json              (if action items enabled)
```

### Cadence & Triggers

Run once per project at project inception. Not repeatable for the same project — if a project already exists at the generated slug, this task surfaces that and offers to open `edit-project` instead.

---

## Workflow

### Step 1: Read Org Configuration

Read `collection-setup-responses.md` from the collection's setup directory on the remote filesystem via `aifs_read`. Extract:
- `shared_projects_path` — where to write project data
- `roles_config` — how roles are handled (`org-mandated`, `org-suggested`, or `project-defined`)
- `org_roles` — the org-defined roles list (if applicable)
- `brief_enabled` — whether the structured project brief is enabled
- `brief_sections` — which sections are accepted and their enforcement (required/optional)
- `milestones_enabled` — whether milestones are enabled
- `milestones_enforcement` — whether milestones are required or optional
- `comms_channel_enabled` — whether comms channel integration is enabled
- `comms_platform` — which platform (slack, teams, discord, other)
- `comms_channel_naming_template` — channel naming template
- `comms_channel_enforcement` — whether channel creation is required or optional
- `slack_user_token_path` — path to the Slack bot token file (if comms_platform is `slack`)
- `activity_log_enabled` — whether project activity logging is enabled
- `ideas_enabled` — whether project ideas are enabled
- `action_items_enabled` — whether action items are enabled

Verify that `shared_projects_path` exists and is writable on the remote filesystem (via `aifs_exists` and a test `aifs_write`). If not:

**On failure:** Surface: "The shared projects directory at `{path}` isn't accessible. This may be a filesystem connectivity issue — try '@ai:member-bootstrap' to check your remote filesystem connection, or contact your org admin if the directory hasn't been created yet." Halt.

**On success:** Proceed to Step 2.

---

### Step 2: Collect Project Name

Ask: "What is the name of this project?"

Accept any non-empty string. Generate the slug immediately: lowercase, spaces and special characters replaced with hyphens, consecutive hyphens collapsed to one, leading and trailing hyphens removed.

Show the member the generated slug: "I'll use `{slug}` as the project's directory name — that's how it will appear in the filesystem."

Check whether `{shared_projects_path}/{slug}/` already exists. If it does:

**On conflict:** Surface: "A project with the slug `{slug}` already exists. This might be '{existing project name}'. Would you like to edit that project instead, or choose a different name for this new project?" Do not proceed until resolved.

**On success:** Proceed to Step 3 with confirmed name and slug.

---

### Step 3: Collect Owner and Project Manager

Ask: "Who is the project owner?"

Then ask: "Who is the project manager? This can be the same person as the owner, or someone different."

For each person named (owner, PM), resolve their identity against the members registry:

1. Read `/members-registry.json` from the remote filesystem via `aifs_read`
2. Search for a match by `display_name` (case-insensitive partial match is acceptable — e.g., "Bill" matches "Bill Smith")
3. If exactly one match is found: confirm with the member — "That's {display_name} ({email}), correct?" If confirmed, record the person as a **registered member** with their `member_hash`, `display_name`, and `email`.
4. If multiple matches are found: present all matches and ask the member to clarify which person they mean.
5. If no match is found: record the person as an **unregistered member** using the name provided. Note to the member: "{name} isn't in the org's member registry yet. I'll add them by name for now — once they're set up in agent-index, you can link their full identity via '@ai:edit-project'."
6. If the member says "me" or "I am" or similar self-references: use the running member's identity (already resolved at session start from their `member_hash`).

Do not assume the member running this task is either the owner or PM — always ask explicitly.

**On success:** Proceed to Step 4.

---

### Step 4: Collect Project Brief

**If `brief_enabled` is `false`:** fall back to the simple scope narrative. Ask: "Give me a description of this project — what it is, what it's meant to achieve, and any relevant context. This becomes the project's scope narrative and can be as brief or detailed as you like." Accept any non-empty string. Proceed to Step 5.

**If `brief_enabled` is `true`:** guide the member through each accepted section in order. For each section in `brief_sections`:

Introduce the brief: "Let's put together the project brief. I'll walk you through a few sections — skip any you're not ready for yet, you can always add them later."

For each accepted section, present the prompt below. If the section is marked `required`, note the org expectation: "Your org considers this a key part of the project brief." If the member wants to skip a required section, accept the skip but note: "No problem — you can add this later with '@ai:edit-project'. Your org does recommend filling this in when you can."

| Section | Prompt |
|---|---|
| **description** | "Describe the project — what it is and what it's about. This is the core narrative." |
| **goals** | "What are the goals of this project? What outcomes are you aiming for?" |
| **success_criteria** | "How will you know this project has succeeded? What does 'done' look like — any measurable targets?" |
| **constraints** | "Are there any known constraints? Budget, timeline, regulatory requirements, technical limitations, resource limits?" |
| **dependencies** | "Does this project depend on anything external — other projects, vendor deliverables, approvals, or specific timelines?" |
| **stakeholders** | "Are there stakeholders who care about this project's outcome but aren't on the project team? These could be executives, clients, partner teams, etc." |
| **risks** | "Are there any known risks or uncertainties? Things that could go wrong or that you're keeping an eye on?" |

For the **stakeholders** section: resolve each named person against the members registry using the same process as Step 3. Store stakeholders as structured person objects (display_name, member_hash, email).

Collect each section's content as the member provides it. Empty/skipped sections are recorded as `null` in the project record.

**On success:** Proceed to Step 5.

---

### Step 5: Collect Milestones

**If `milestones_enabled` is `false`:** skip this step entirely. Proceed to Step 6.

**If `milestones_enabled` is `true`:**

If enforcement is `required`: "Let's define the key milestones for this project. Your org recommends every project have at least a few milestones with target dates."

If enforcement is `optional`: "Would you like to define key milestones and target dates for this project? You can skip this and add them later."

If the member wants to add milestones, collect them one at a time:
- Ask: "What's the milestone?" — accept a short name/description
- Ask: "What's the target date?" — accept a date in any reasonable format, normalize to `YYYY-MM-DD`
- Ask: "Any more milestones, or are you done?"

Continue until the member says they're done. Minimum: zero milestones (even if enforcement is `required` — see Directives).

Each milestone is stored as:
```yaml
- name: "Design review"
  target_date: "2026-04-15"
  status: pending
```

Valid milestone statuses: `pending`, `completed`, `missed`, `deferred`. All milestones start as `pending` at creation.

**On success:** Proceed to Step 6.

---

### Step 6: Configure Project Roles

Behavior depends on `roles_config` from Step 1:

**If `org-mandated`:**
Do not ask the member about roles. The org-defined roles list is injected directly. Inform the member: "Your org has defined the following roles for all projects: {org_roles list}. These are fixed and will be used for this project."

**If `org-suggested`:**
Present the org roles list: "Your org suggests these roles as a starting point: {org_roles list}. You can use these as-is, add new roles, or remove any that don't apply to this project."
Ask: "Would you like to use this list, or make changes?"
Accept additions, removals, or a full replacement. Record the final list.

**If `project-defined`:**
Ask: "What roles will people play on this project? Define as many or as few as you need — for example: Lead, Contributor, Reviewer."
Require at least one role before proceeding.

**On success:** Proceed to Step 7 with confirmed roles list.

---

### Step 7: Collect Initial Member List

Ask: "Would you like to add team members now, or do that later via '@ai:edit-project'?"

If the member wants to add members now:
- Ask for a name and role assignment, one at a time
- Role must be selected from the confirmed roles list from Step 6
- For each person named, resolve their identity against the members registry using the same process as Step 3:
  1. Search `/members-registry.json` on the remote filesystem via `aifs_read` by `display_name` (case-insensitive partial match)
  2. If exactly one match: confirm — "That's {display_name} ({email}), correct?" If confirmed, record as a registered member with `member_hash`, `display_name`, and `email`.
  3. If multiple matches: present all and ask for clarification.
  4. If no match: record as unregistered with the provided name. Note: "{name} isn't in the org's member registry yet. I'll add them by name for now — once they're set up in agent-index, you can link their full identity via '@ai:edit-project'."
- Continue until the member says they are done
- Minimum: zero members — this step is optional

If the member wants to skip: record an empty members list and proceed.

**On success:** Proceed to Step 8.

---

### Step 8: Comms Channel

**If `comms_channel_enabled` is `false`:** skip this step entirely. Proceed to Step 9.

**If `comms_channel_enabled` is `true`:**

Generate the default channel name from the naming template: replace `{slug}` in `comms_channel_naming_template` with the project slug.

If enforcement is `required`: "Your org uses {comms_platform} for project communication. I'll create a channel called `#{generated_channel_name}` for this project. Would you like to use that name, or choose a different one?"

If enforcement is `optional`: "Your org uses {comms_platform} for project communication. Would you like me to create a dedicated channel for this project? I'd call it `#{generated_channel_name}`."

If the member wants a channel:
- Confirm or customize the channel name
- Record `comms_channel_name` and `comms_channel_enabled: true` for this project
- Note: the actual channel creation and member invitations happen in Step 9 (after confirmation), not here

If the member skips: record `comms_channel_name: null` for this project.

**On success:** Proceed to Step 9.

---

### Step 9: Confirm and Write

Present a complete summary of everything collected:

> **New Project Summary**
> Name: {name}
> Slug: {slug}
> Owner: {owner display_name} {(email) if registered, or "(not in org registry)" if unregistered}
> Project Manager: {pm display_name} {(email) if registered, or "(not in org registry)" if unregistered}
> {if brief_enabled and any sections filled}: Brief: {list sections that have content}
> {if milestones collected}: Milestones: {count} defined
> Roles: {roles list}
> Members: {for each: display_name (role) — with email if registered, or "(not in org registry)" if unregistered}
> {if comms channel}: Channel: #{comms_channel_name} on {comms_platform}
>
> Ready to create this project?

Wait for explicit confirmation before writing anything.

On confirmation:

1. Create the project directory structure on the remote filesystem via `aifs_write`:
   ```
   {shared_projects_path}/{slug}/
     /assets/
     /state/
     /artifacts/
   ```
   If `activity_log_enabled`: also create `/activity/` and initialize empty `activity-log.jsonl`.
   If `ideas_enabled`: also create `/ideas/`.
   If `activity_log_enabled`: also create `/decisions/`.
   If `action_items_enabled`: initialize `action-items.json`:
   ```json
   { "last_updated": "{today}", "next_id": 1, "items": [] }
   ```

2. Write `project.md`. The full format:

   ```
   ---
   name: {name}
   slug: {slug}
   status: active
   owner:
     display_name: {display_name}
     member_hash: {member_hash or null}
     email: {email or null}
   project_manager:
     display_name: {display_name}
     member_hash: {member_hash or null}
     email: {email or null}
   created: {today YYYY-MM-DD}
   last_updated: {today YYYY-MM-DD}
   roles:
   {roles as YAML list}
   members:
   {each member as a YAML object with display_name, member_hash (or null), email (or null), and role — empty array if none}
   milestones:
   {each milestone as a YAML object with name, target_date, status — empty array if milestones_enabled is false or none defined}
   comms_channel:
     enabled: {true or false}
     platform: {comms_platform or null}
     channel_name: {channel name or null}
     status: {active, pending, archived, or null if not enabled}
   ---

   {if brief_enabled}:
   ## Project Brief

   {for each accepted section that has content}:
   ### {Section Title}

   {section content}

   {for each accepted section that was skipped}:
   ### {Section Title}

   *Not yet defined.*

   {if brief_enabled is false}:
   ## Project Scope

   {scope narrative}
   ```

   For registered members (found in the registry), `member_hash` and `email` are populated from the registry. For unregistered members, `member_hash` and `email` are `null`.

3. Write an initial `current-state.md` to `/state/`:
   ```
   # {name} — Current State
   **Last Updated:** {today}
   **Session Count:** 1

   ## Status
   Project created. No active work sessions yet.

   ## Open Items
   {if any brief sections were skipped that are marked required}: - Fill in project brief: {list of skipped required sections}
   {if milestones_enforcement is required and no milestones defined}: - Define project milestones
   {if comms_channel was skipped and enforcement is required}: - Create project comms channel
   {otherwise}: None.

   ## Persistent Context
   None yet.

   ## Artifact Index
   None yet.
   ```

4. Read `projects-manifest.json` from the remote filesystem via `aifs_read`. Add the new entry:
   ```json
   {
     "slug": "{slug}",
     "name": "{name}",
     "status": "active",
     "owner": "{owner display_name}",
     "owner_hash": "{owner member_hash or null}",
     "created": "{today YYYY-MM-DD}",
     "has_channel": {true or false}
   }
   ```
   Update `last_updated` on the manifest. Write the file to the remote filesystem via `aifs_write`.

5. If comms channel is enabled for this project: attempt to create the channel on the configured platform.

   **For Slack (`comms_platform` is `slack`):**
   Use the bundled `create_channel.py` script in `apps/slack-channel-creator/`. Read `slack_user_token_path` from `collection-setup-responses.md`. Run:

   ```bash
   python {apps_path}/slack-channel-creator/create_channel.py \
       --name "{channel_name}" \
       --token-file "{slack_user_token_path}" \
       --topic "Project channel for {project name}" \
       --purpose "Coordination channel for the {project name} project" \
       --invite "{comma-separated emails of registered members}"
   ```

   The script outputs JSON. Parse the result:
   - If `ok: true`: set `comms_channel.status: active`. Report: "Channel `#{channel_name}` has been created on Slack." If `invites.failed` is non-empty, note which members couldn't be invited and why (e.g., "user_not_found" means they aren't in the Slack workspace).
   - If `ok: false` with `error: name_taken`: the channel already exists. Note: "A channel called `#{channel_name}` already exists in Slack. I've recorded it in the project — you may want to verify it's the right channel." Set `comms_channel.status: active`.
   - If `ok: false` with any other error: set `comms_channel.status: pending`. Note: "Channel creation failed ({error}). The channel is noted as pending — you can create it later via '@ai:edit-project' or manually in Slack."
   - If the script is not found or `slack_user_token_path` is not configured: set `comms_channel.status: pending`. Note: "Channel creation isn't configured yet — the Slack bot token path may be missing from collection setup. The channel `#{channel_name}` is noted as pending."

   **For other platforms (Teams, Discord, other):**
   - Use the appropriate MCP connector for the platform if available
   - Create the channel with the confirmed name
   - Set the channel topic/description to: "Project channel for {project name}"
   - Invite all registered project members (owner, PM, and team members with non-null `member_hash`) to the channel. Unregistered members cannot be invited — note them: "{name} couldn't be invited to the channel because they're not in the org registry yet."
   - **If the connector is not available:** do not fail. Record the channel as pending: "Channel creation is enabled but I can't reach {comms_platform} right now. The channel `#{channel_name}` is noted as pending — you can create it later via '@ai:edit-project'." Set `comms_channel.status: pending` in the project record.
   - **If channel creation succeeds:** set `comms_channel.status: active` in the project record. Confirm: "Channel `#{channel_name}` has been created on {comms_platform} and {N} members have been invited."

6. If `activity_log_enabled`: append the first activity log entry to `{project}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "project_created",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "summary": "Project '{name}' created by {display_name}"
   }
   ```

7. Confirm to member:
   > "Project '{name}' has been created. You can find it at `{shared_projects_path}/{slug}/`. To edit it later, say '@ai:edit-project' or 'edit project {name}'."

**On any write failure:** Surface the specific file that failed to write via `aifs_write`, leave any successfully written files in place, and advise the member to retry or check remote filesystem connectivity via '@ai:member-bootstrap'.

---

## Directives

### Behavior

Collect all information conversationally before writing anything. Never write partial project records — the full summary confirmation in Step 9 is the single gate before any filesystem writes.

Guide the member naturally through the interview. Not every member will know exactly what to say for each brief section — offer encouragement: "Even a sentence or two is fine — you can always expand it later with 'edit project'."

For the project brief, keep the tone light and conversational. Don't make it feel like filling out a form. If the member provides information for multiple sections in a single message, capture what they've given and only ask about the remaining sections.

Steps 1–8 may be completed in any order if the member volunteers information out of sequence. If a member says "I want to create a project called Rebrand 2026, owned by Sarah Kim, with a Lead and Contributor role and a milestone for design review on April 15th," accept what was given and ask only for what is still missing.

No step is a hard blocker. Even when the org admin has marked a feature as "required," the member can still skip it. The enforcement is conversational — Claude explains the org expectation, but always allows the member to proceed. The project record is always created. Skipped required items are noted in `current-state.md` as open items.

### Output Standards

`project.md` must always be written with complete YAML frontmatter — no optional fields omitted. If a value was not collected (e.g., empty members list, no milestones), write it as an empty array, not as an absent field. Brief sections that were skipped are written as `*Not yet defined.*` in the body, not omitted.

`projects-manifest.json` must always be valid JSON after writing. Read it before writing, parse it, add the entry, serialize it back. Never write the manifest as a string substitution — always parse and serialize properly.

### Constraints

Never write to the filesystem before the Step 9 confirmation. All writes happen together after explicit confirmation.

Never generate a slug that collides with an existing project directory. The collision check in Step 2 is mandatory.

Never allow `archived` as a status on project creation. All new projects are `active`.

Never allow the roles list to be empty for `org-mandated` or `org-suggested` configurations. If the member tries to remove all roles under `org-suggested`, surface: "Projects need at least one role. What would you like to keep?"

Comms channel creation is always best-effort. A failure to create a channel or invite members must never block project creation. Log the failure in the project record and note it to the member.

### Edge Cases

If the member provides a project name that generates a slug already in use but the existing project is archived: surface both options — "There's an archived project with the slug `{slug}`. You can create a new project with a different name, or contact your org admin about unarchiving the existing one."

If `projects-manifest.json` does not exist at the expected path (e.g., collection was installed but setup was not completed): surface: "The projects manifest file is missing. This usually means the collection setup wasn't completed. Ask your org admin to run the Projects collection setup." Halt — do not create the manifest file from within this task.

If the member provides a project name with only special characters that produce an empty slug after normalization: ask for a different name.

If collection-setup-responses.md cannot be read: halt with "The Projects collection setup information couldn't be read. Try '@ai:setup' to check your installation, or contact your org admin."

If the member provides stakeholder names for the brief that partially match multiple registry entries: use the same disambiguation flow as Step 3 — present all matches and ask for clarification.

If a milestone target date is in the past: accept it but note: "That date has already passed — want to adjust it, or is that intentional?"
