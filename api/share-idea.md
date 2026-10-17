---
name: share-idea
type: task
version: 4.2.1
collection: projects
description: Make a private idea visible — three distinct moves. Share with specific people (per-person Drive grants on the idea folder in the owner's My Drive; reader or collaborator); PROMOTE into the parent project (relocates the content and adopts the project's tier — the "ready for the team" move); or unshare (revoke grants, pointer goes revoked). Owner-only; every grant goes through the core permission-changes procedure (owner confirms the exact changes; each is verified). Replaces the 3.x copy-to-shared flow.
stateful: false
produces_artifacts: false
produces_shared_artifacts: true
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - Remote filesystem access (adapter 2.5.0+)
  - "Slack / Microsoft Teams / Discord (conditional): post promotion notification to the project channel"
reads_from: "id:{member_folder_id}/ideas/, /shared/projects/, /shared/projects-index/"
writes_to: "id:{member_folder_id}/ideas/, /shared/projects/, /shared/projects-index/"
---

## About This Task

Private ideas are invisible by default (design decision 2): they live in the owner's own My Drive (`id:{member_folder_id}/ideas/{project-slug}/{idea-slug}/`) with no org-visible record. This task is how an idea becomes visible, in three graduated moves:

1. **Share with people** — selective: per-person grants on the idea folder (*share with X* = reader; *collaborator X* = writer), applied through the core permission-changes procedure with the **owner** confirming the exact changes (the folder is theirs — that's what makes it possible). The first share writes the idea's **discovery pointer** to `/shared/projects-index/` — sharing deliberately reveals the idea's title, owner, and parent project to the org while data stays gated to the grantees.
2. **Promote into the project** — the "ready for the team" move (decision 7: promotion = relocation): content is COPIED into the parent project's `ideas/{idea-slug}/`, where it adopts the project's tier automatically (org-public project → org-visible idea; private project → visible to the project's members). The My Drive original is marked moved. Collaborator assignments and action items are created as in 3.x.
3. **Unshare** — revoke grants (`unshare` changes through the procedure, each confirmed by the owner), pointer overwritten `"scope": "revoked"` (title residue accepted, strategy precedent).

Owner-only throughout. The 3.x flow (always copy-to-shared) is move 2; moves 1 and 3 are new in 4.0.

### Inputs

The member identifies the idea, the move (share / promote / unshare), and for shares the people + levels.

## Workflow

### Step 1: Identify Idea and Project

Read local `member-index.json` (`member_hash`, `member_folder_id` — missing → `@ai:update` self-provision halt) and setup responses (`ideas_enabled`, `action_items_enabled`, `activity_log_enabled`, `comms_channel_enabled`). Halt politely if ideas disabled.

Locate the idea: named → `id:{member_folder_id}/ideas/{project-slug}/{idea-slug}/` (and the member's local notes for legacy local-only ideas — see Edge Cases); unnamed → list the member's own ideas and ask. Read `idea.md`; identify the parent project and resolve ITS tier via the pointer index / the member's own private projects.

Already promoted (`status: shared|approved|moved`) → "Already with the project team — manage it via '@ai:manage-ideas'." Halt.

### Step 2: Choose the move

> *"Share `{title}` with specific people (they see just this idea), promote it into `{project}` (the whole project team gets it{ — org-visible, since the project is public} ), or unshare it?"*

Review-before-sharing as 3.x: show title/description/artifacts, offer edits to the private copy first.

### Step 3A: Share with people

1. `aifs_stat("id:{member_folder_id}/ideas/{project-slug}/{idea-slug}")` → record both `idea_folder_id` (the `id`) **and `item_drive_id` (the returned `drive_id`, adapter 2.3.0+)** in idea.md frontmatter. The idea lives on the owner's personal drive, so capturing `drive_id` is what lets a grantee open it cross-drive (C.1.3 `crossdriveread`).
2. Collect people + levels (read | collaborate).

   **Recipients.**
   - A person in `members-registry.json` → use their `sharing_identity` (email on gdrive, UPN on onedrive).
   - A name that doesn't resolve → ask for their email address. Never guess.
   - An address outside the registry is allowed. The permission-changes table marks it **outside your org**, and whether to share is the owner's call, as it would be in Drive directly. Tell the owner the recipient opens it from their storage app's "Shared with me", because agent-index discovery pointers are for org members.
3. **Apply.** Follow `/agent-index-core/internal/permission-changes.md` with one `share` change per person: resource **`id:{idea_folder_id}`** (bare ID), `resource_label` "Idea '{title}'", `is_folder: true`, role `reader`|`writer`, `source: "member_request"`; `calling_task: "share-idea"`, `confirmer: "owner"`. **Gate:** only rows `applied` or `skipped_noop` count as shared.
4. **Pointer-on-first-share** to `/shared/projects-index/{member_hash}-{project-slug}--{idea-slug}.json`:
   `{"type":"idea","name":"{title}","slug":"{idea-slug}","parent":"{project-slug}","owner":…,"owner_hash":…,"status":"active","scope":{"readers":[…],"collaborators":[…]},"location":{"folder_id":"{idea_folder_id}","item_drive_id":"{item_drive_id}"},"created":…,"last_updated":…,"owner_departed":false}`
   `item_drive_id` (from the Step 3A.1 stat; C.1.3 `crossdriveread`) is what lets a grantee on OneDrive open the idea where it physically lives on the owner's drive — a bare `id:{idea_folder_id}` resolves against the *recipient's* drive and 404s.
   **`scope`:** on the first share, `scope` lists **only** grantees whose rows are `applied` or `skipped_noop`. On a later share, never rebuild `scope` from this run's rows alone — that would drop earlier grantees who still have access. Build it from a fresh `aifs_get_permissions({path: "id:{idea_folder_id}", include_inherited: true})` read after the procedure returns (readers → `readers`, writers → `collaborators`, excluding the owner); if that read fails, use the existing pointer's `scope` ∪ this run's satisfied rows. NEVER write the pointer before the procedure returns. If no row is satisfied, write nothing; tell the owner what didn't take effect and offer to re-run.
5. Activity: only if at least one row is satisfied. If the parent project is accessible to the owner and `activity_log_enabled`, append an `idea_shared` event naming **only the satisfied grantees from this run** (org-public project) — for a PRIVATE parent project, the event goes in the project only if the owner owns/can write it. No satisfied row → no event.
6. Confirm, naming only satisfied grantees: who can now read, who can now write, that the idea's title is now org-discoverable, and that promotion is the next step when it's team-ready. For an outside-registry grantee, add that they open it from "Shared with me". List any pending rows (declined, failed, not verified) as not in effect, with "run '@ai:share-idea' again to retry". If nothing was satisfied, say only what didn't take effect — don't claim anyone has access.

### Step 3B: Promote into the project

1. Verify the member can write the project (org-public → always; private parent → owner or collaborator; otherwise: "Ask {project owner} to add you, or share the idea with them instead." Halt).
2. Collect collaborators + assignments (3.x flow, unchanged) — on an org-public project anyone can work it; assignments create action items if enabled.
3. COPY the idea directory into `{project base}/ideas/{idea-slug}/` (every file; artifacts ride along — they inherit the project's tier structurally, decision 3). Set the copied `idea.md` `status: shared`, `promoted: {ISO}`, `promoted_by`.
4. Mark the My Drive original `status: "moved-to-project"` (stub; or owner may delete it — their space, offer both).
5. Pointer: if one exists (idea was people-shared first) → overwrite: `scope` = `"org_public"` (public project) or the project's roster scope (private project), `location` = project path/folder_id. If none existed → write one ONLY when the project is org-public (a promoted idea in a PRIVATE project stays invisible org-wide, like everything else in that project).
6. Old per-person grants on the My Drive folder become moot (stub) — offer optional revocation (`unshare` changes through the procedure, `source: "current_state"`) or leave harmlessly.
7. Activity log `idea_promoted` + action items (revision-aware: `manage-action-items` § "Writing `action-items.json`", bug `20260921-8d20ea22-202128-c7e9`) + optional channel notification (3.x mechanics).
8. Confirm.

### Step 3C: Unshare

Owner-only. Follow the permission-changes procedure with one `unshare` per current grantee on `id:{idea_folder_id}` (`source: "current_state"`; removals are confirmed one at a time). Then re-read `aifs_get_permissions(id:{idea_folder_id})`. If no explicit grants remain (other than the owner), overwrite the pointer `"scope": "revoked"` (never deleted). Otherwise, overwrite `scope` with whoever still has access per that re-read (a declined or failed removal leaves that person in). The idea stays in the owner's space either way. Confirm honestly from the re-read:
- No grants remain: *"Access is revoked; the title remains visible in the org index as a revoked entry."*
- Some remain: *"{names} still have access ({removal declined or failed}). Everyone else's access is removed. Run '@ai:share-idea' and choose unshare again to finish."* Never say "Access is revoked" in this case.

## Directives

### Constraints

- **Owner-only. Never call `aifs_share`/`aifs_unshare`/`aifs_transfer_ownership` outside the core permission-changes procedure. The owner confirms the exact changes. Pointers never claim unverified state.**
- Never delete anything under /shared (pointers and project copies are overwrite/mark only).
- Promotion into a PRIVATE project must not create an org-visible pointer (the project's invisibility dominates).
- Artifact placement on promotion follows the structural rule: artifacts move WITH the idea folder.

### Edge Cases

- **Legacy local-only private ideas** (3.x stored ideas in the member's LOCAL workspace): on first touch, offer a one-time move into `id:{member_folder_id}/ideas/…` ("your ideas can now live in your private remote space so they're shareable; move this one?"). Local-only ideas can't be people-shared (nothing to grant on) — promotion still works (copy from local).
- Grantee outside the org → allowed, flagged in the table. An address the backend rejects shows as `failed` with the reason; relay it.
- Some rows not applied → pointer reflects ONLY the satisfied rows; offer to re-run.
- Parent project archived → block promotion ("unarchive first"); people-sharing still allowed.
- Owner departed scenarios are handled by remove-member's acknowledgment, not here.
