---
name: create-idea
type: task
version: 3.0.0
collection: projects
description: Creates a new idea for a project — a private exploration space for developing concepts, designs, or proposals before sharing them with the team.
stateful: false
produces_artifacts: true
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
reads_from: null
writes_to: null
---

## About This Task

An idea is a private workspace for developing a concept, design, or proposal related to a project. Ideas let members think, iterate, and refine without exposing unfinished thinking to the project team. When an idea is ready, the member shares it via `share-idea`, which promotes it to the project's shared space and invites collaborators.

Ideas are stored in the member's private workspace at `/members/{member_hash}/ideas/{project-slug}/{idea-slug}/`. They are invisible to other members until explicitly shared.

If the org admin has set `ideas_require_private_stage` to `either`, members can also create ideas directly in the shared project space (skipping the private stage). In this case the idea is immediately visible to the project team.

### Inputs

The member provides: which project this idea belongs to, a title, a description, and optionally initial artifacts (files, documents) and external references (links to Figma, Miro, Google Drive, etc.).

### Outputs

For private ideas:
- `/members/{member_hash}/ideas/{project-slug}/{idea-slug}/idea.md` — the idea record
- `/members/{member_hash}/ideas/{project-slug}/{idea-slug}/artifacts/` — directory for files
- `/members/{member_hash}/ideas/{project-slug}/{idea-slug}/references/` — directory for external links

For direct-to-shared ideas (if `ideas_require_private_stage` is `either` and member chooses shared):
- `{shared_projects_path}/{project-slug}/ideas/{idea-slug}/idea.md` — the idea record
- Plus artifacts and references directories in the project space
- Activity log entry recording the idea creation

### Cadence & Triggers

On demand, whenever a member wants to start exploring a concept for a project.

---

## Workflow

### Step 1: Read Org Configuration and Identify Project

Read `collection-setup-responses.md` to get `shared_projects_path`, `ideas_enabled`, and `ideas_require_private_stage`.

If `ideas_enabled` is `false`: surface "Ideas aren't enabled for your org's project setup. Contact your org admin if you'd like this feature." Halt.

If the member named a project in their invocation: use that name. Read `projects-manifest.json` and find the matching active project.

If the member did not name a project: ask "Which project is this idea for?"

If the project cannot be found or is archived: surface the issue and halt.

**On success:** Proceed to Step 2.

---

### Step 2: Determine Visibility

**If `ideas_require_private_stage` is `private_first`:**
Inform the member: "This idea will start as a private draft in your workspace. When you're ready, you can share it with the project team via '@ai:share-idea'." Set visibility to `private`.

**If `ideas_require_private_stage` is `either`:**
Ask: "Would you like to start this as a private draft (only you can see it), or create it directly in the shared project space?"
Record the member's choice.

**On success:** Proceed to Step 3.

---

### Step 3: Collect Idea Details

Ask: "What's the title of this idea?"

Accept any non-empty string. Generate the slug: lowercase, spaces and special characters replaced with hyphens.

Check for slug collisions in the target directory (private or shared). If a collision exists, ask for a different title or append a number.

Ask: "Describe the idea — what are you thinking, what problem does it solve, what's the concept?"

Accept any non-empty string. Encourage depth: "Take as much space as you need. This is your thinking space — the more context you capture now, the more useful it is when you come back to it."

**On success:** Proceed to Step 4.

---

### Step 4: Collect Artifacts and References (Optional)

Ask: "Do you have any files or documents to include? These could be mockups, specs, diagrams — anything that supports the idea."

If yes: collect file paths or references. Files provided in the session are copied to the idea's `/artifacts/` directory.

Ask: "Any external links to include? Figma boards, Miro canvases, Google Docs, or any other URLs?"

If yes: collect links one at a time. For each, ask for a label (short description of what the link points to) and optionally the platform type (figma, miro, google_drive, notion, other). Record as structured references.

If no for both: proceed with no artifacts or references.

**On success:** Proceed to Step 5.

---

### Step 5: Confirm and Write

Present a summary:

> **New Idea for '{project name}'**
> Title: {title}
> Slug: {slug}
> Visibility: {Private draft / Shared with project}
> Description: {first 2-3 sentences}
> Artifacts: {count, or "None"}
> References: {count, or "None"}
>
> Create this idea?

Wait for confirmation.

On confirmation:

1. Create the idea directory structure:
   - Private: `/members/{member_hash}/ideas/{project-slug}/{idea-slug}/artifacts/` and `/references/`
   - Shared: `{shared_projects_path}/{project-slug}/ideas/{idea-slug}/artifacts/` and `/references/`

2. Write `idea.md`:
   ```
   ---
   title: {title}
   slug: {idea-slug}
   project: {project-slug}
   status: draft (if private) | shared (if direct-to-shared)
   author:
     display_name: {member display_name}
     member_hash: {member_hash}
     email: {member email}
   created: {today YYYY-MM-DD}
   last_updated: {today YYYY-MM-DD}
   parent_idea: null
   collaborators: [] (empty if private; can be populated if shared via Step 2 choice)
   references:
   {each reference as YAML object with type, url, label — empty array if none}
   promoted_artifacts: []
   ---

   ## Description

   {idea description}
   ```

3. Copy any provided artifact files to `/artifacts/`.

4. If the idea is direct-to-shared: append an activity log entry to `{shared_projects_path}/{project-slug}/activity/activity-log.jsonl`:
   ```json
   {
     "timestamp": "{ISO 8601}",
     "type": "idea_created",
     "author_hash": "{member_hash}",
     "author_name": "{display_name}",
     "idea_slug": "{idea-slug}",
     "idea_title": "{title}",
     "summary": "Created shared idea: {title}"
   }
   ```

5. Confirm to member:
   - If private: "Idea '{title}' created in your private workspace. You can continue developing it any time, or share it with the team via '@ai:share-idea'."
   - If shared: "Idea '{title}' created in the shared project space for '{project name}'. Team members can see it now. Add collaborators via '@ai:manage-ideas'."

---

## Directives

### Behavior

Keep idea creation lightweight and encouraging. The whole point is to lower the barrier to capturing early thinking. Don't over-structure the interview — a title and description are all that's needed to get started.

If the member provides a stream-of-consciousness description, accept it as-is. Don't ask them to restructure or refine. The refinement happens over time as they iterate on the idea.

### Constraints

Never create an idea for an archived project.

Never write a private idea anywhere other than the member's own `/members/{member_hash}/ideas/` directory.

Never create a direct-to-shared idea if `ideas_require_private_stage` is `private_first`.

The idea slug must be unique within its target directory. Always check for collisions.

### Edge Cases

If the member's private ideas directory for this project doesn't exist yet: create `/members/{member_hash}/ideas/{project-slug}/` on first use.

If the project's shared ideas directory doesn't exist yet: create `{shared_projects_path}/{project-slug}/ideas/` on first use.

If the project's activity log directory doesn't exist yet (e.g., project predates tracking features): create `{shared_projects_path}/{project-slug}/activity/` and initialize an empty `activity-log.jsonl` on first use.

If the member provides a link but no label: use the URL domain as the label (e.g., "figma.com link").
