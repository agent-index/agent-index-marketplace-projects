---
name: projects-tutorial
type: skill
version: 4.3.0
collection: projects
description: Explains the projects collection to members — projects (public by default), ideas (private and invisible by default), the structural artifact-inheritance rule, sharing, promotion, membership, custody, and lifecycle — through a guided tour or targeted answers.
stateful: false
always_on_eligible: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
---

## About This Skill

The projects collection is your org's project lifecycle system: structured project records, private idea exploration, action items with assignments, decisions, channel digests, and status reports. Since 4.0 it runs on the org's two-tier access model. When giving concrete examples, read the pointer index (`/shared/projects-index/`) so they reflect the actual install.

## Topics

**Topic 1: Projects — public by default**

A project is the foundational record everything else hangs from: brief, milestones, roster, action items, decisions, artifacts, activity log. Projects are **org-public by default**: they live in the org commons, every member can see and contribute, every write is attributed in the activity log, and the org keeps the project no matter who comes or goes. Creation prompts the choice; you can also create a **private** project — it lives in your own My Drive and is *completely invisible* to everyone else until you add a member or make it public. Move between tiers anytime: `@ai:transition-project` (note: taking a project private doesn't un-publish what the org already saw).

**Topic 2: Membership**

On a public project the roster is bookkeeping — who plays what role; access is uniform anyway. On a **private** project, the roster IS the access list: adding a member (`@ai:edit-project`) applies a real Drive grant that you, the owner, approve on a review page — and the very first member you add ends the project's invisibility (its title and owner appear in the org directory; the data stays gated to the roster).

**Topic 3: Ideas — private and invisible by default**

An idea is your thinking space attached to a project. By default it lives in YOUR own space and **no one can see that it exists** — no list, no name, nothing. That's deliberate: premature visibility changes what people write down. When you're ready, `@ai:share-idea` offers three moves: **share with specific people** (they get read or read+write on just that idea; the idea's title becomes org-discoverable at that moment), **promote into the project** (the team move — the idea relocates into the project and takes on the project's visibility), or **unshare**. You can also create an idea directly in the project if it was never meant to be private.

**Topic 4: Artifacts — inheritance is automatic**

Documents and files live INSIDE whatever they belong to: drop an artifact into a public project and it's org-visible; into your private idea and it's exactly as private as the idea, including anyone you've shared the idea with. No separate permissions to manage — the folder does the work. If you deliberately want an artifact MORE visible than its parent (say, publishing one document from a private idea), the override prompt warns you explicitly and the public record won't reveal where it came from.

**Topic 5: Action items, decisions, reports, digests**

These are project-record material: they always follow the project's visibility, with no per-item questions. On private projects, you can only assign action items to people who actually have access — the task offers to add them as members first.

**Topic 5a: Action item IDs, fields, and tags (4.2)**

Every action item gets an ID like `MOB-014`. The `MOB` part is the project's prefix, and you choose it when you create the project — the system suggests one from the project name and you accept it or type your own. It's unique across the org, so `MOB-014` identifies one specific item anywhere you paste it: a branch name, a Slack message, a pull request.

There's one rule worth understanding rather than just obeying: **you can change the prefix freely until the project's first action item exists, and then it's fixed.** That sounds strict, and the reason is that the ID stops being ours the moment it's used. Once `MOB-014` is in a branch name or a document, renaming the prefix would make that reference wrong, and renumbering items would break every other reference at the same time. So the prefix locks while it's still free to change, and stays put once anything depends on it. A project that already had action items keeps the prefix it was already using — if its items are `AC-001…AC-040`, the next one is `AC-041`. **Existing IDs are never renumbered**, including ones that predate any prefix convention; if some of your older IDs don't match the current scheme, they stay as they are. The first time you add an item to such a project, you'll be offered the chance to reserve its prefix so another project can't take it.

Your org may also define **fields** on action items — a type, an effort estimate, whatever it tracks. These are set up by an admin and shared by every project, so if you see them, they're org-wide; if you don't, your org hasn't defined any. Ask your admin if you want one.

**Tags** are yours: free-form labels on projects and on action items, added by anyone, no setup required. When you tag an item, the tags already used in that project are offered so a vocabulary builds instead of fragmenting. Project tags and item tags are separate — tagging a project doesn't tag its items.

What you can ask today: `project-pulse` will tell you how many open bugs a project has, or total effort per person, **for one project at a time**. There's no org-wide view across all projects yet.

**Topic 6: Custody and lifecycle**

Public projects belong to the org permanently. Private projects and ideas belong to YOU — if you leave the org, they (and any shares you made) go with your account, outside org control; the org directory annotates ever-shared ones "owner departed," and current recipients can adopt a copy. Rule of thumb: real org work belongs public; private is for exploration. Archival hides a project from default listings (data stays; unarchive anytime); a never-shared private project can be permanently deleted by its owner — it was invisible, so it vanishes cleanly. Anything ever shared keeps a permanent name-record in the directory.

**Topic 7: Day-to-day verbs**

`@ai:create-project`, `@ai:edit-project`, `@ai:update-project` ("I finished the API work"), `@ai:manage-action-items`, `@ai:create-idea` / `@ai:share-idea` / `@ai:manage-ideas`, `@ai:project-decide`, `@ai:channel-digest`, `@ai:project-pulse`, `@ai:archive-project` / `@ai:unarchive-project`, `@ai:transition-project`.

## Q&A routing

- "Who can see this project/idea?" → Topics 1–3 (tier + pointer scope; `view-permissions`-style answers come from the pointer + live ACLs).
- "Why can't I see X's idea?" → Topic 3 (invisible is the default; ask them to share it).
- "How do I publish one doc from my private work?" → Topic 4 (widening override).
- "What happens if I leave?" → Topic 6.
- "Why can't I assign this to Sam?" → Topic 5 (private project access).
- "Why is my action item called AI-001 instead of something useful?" → Topic 5a (the project has no prefix set; `@ai:edit-project` can set one if the project hasn't issued items yet).
- "Can I change the project's action-item prefix?" → Topic 5a (freely before the first item; locked after, because IDs are referenced outside agent-index).
- "How do I mark an action item as a bug?" → Topic 5a (only if your admin has defined a field for it — fields are org-wide, not per-project).
- "Field or tag?" → Topic 5a (fields are admin-defined and one-value-per-item; tags are yours and free-form).
