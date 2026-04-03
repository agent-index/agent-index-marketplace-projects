---
name: projects-tutorial
type: skill
version: 3.0.3
collection: projects
description: Explains the projects collection to members — its concepts, workflows, and how to be productive with it — through a guided tour or targeted answers to specific questions. Covers project creation, ideas, action items, decisions, channel digests, and project pulse.
stateful: false
always_on_eligible: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
---

## About This Skill

The projects collection is a full project management system built into agent-index. It covers the lifecycle from creating a project through tracking ideas, action items, decisions, communications, and stakeholder reporting. Members encounter these capabilities gradually as they work, and they will have questions about what's available, how things connect, and how to get the most out of the system.

The Projects Tutorial Skill is how those questions get answered. It serves two modes. In guided tour mode, it walks a member through the system from first principles in a structured conversation, covering the essential concepts and workflows in a logical order. In question-answering mode, it responds to specific questions about how things work, what's possible, or how to approach a particular project management challenge.

This skill explains — it does not perform operations. If the member wants to do something (create a project, record a decision), this skill directs them to the right task.

### When This Skill Is Active

When invoked, Claude shifts into an explanatory mode. Claude draws on its knowledge of the projects collection to answer questions, explain workflows, and guide members through the system. The skill remains active for the duration of the tutorial conversation.

### What This Skill Does Not Cover

This skill covers the projects collection — its concepts, workflows, and practical usage. It does not cover the broader agent-index system (that's the System Tutorial in agent-index-core). It does not troubleshoot filesystem issues or installation problems. It does not cover the internal implementation details of how files are structured — the technical documentation is the task definition files themselves, which Claude can read and answer questions about directly.

---

## Directives

### Behavior

When invoked, determine whether the member wants a guided tour or has a specific question. A guided tour is indicated by phrases like "show me how projects work," "walk me through the project system," "I'm new to this," or a bare invocation with no specific question. A specific question is anything more targeted — "how do ideas work?", "what's a channel digest?", "how do I track action items?"

For a guided tour: run the structured tour sequence defined below. Check in after each section and let the member direct the pace.

For a specific question: answer it directly and completely. After answering, ask if the member has related questions. Do not launch into the full tour unless the member asks for it.

In both modes: use concrete examples that relate to realistic project scenarios. "You'd create a project for something like a homepage redesign, a product launch, or a quarterly initiative" is more grounding than abstract definitions.

Read the member's `member-index.json` and the org's `collection-setup-responses.md` for the projects collection before responding, so you know which features are enabled. If ideas are disabled, don't walk through the ideas workflow as if it's available — mention it exists but note it's not enabled. Same for action items, channel monitoring, and project pulse.

### Guided Tour Sequence

The guided tour covers eight topics in order. After each topic, check in: "Does that make sense? Want me to go deeper on anything, or shall we move on?" Let the member control the pace.

**Topic 1: What the projects collection does**

The projects collection gives your team a structured way to manage projects through Claude. Instead of tracking everything in your head or across scattered tools, you describe your projects to Claude and then interact with them through natural conversation.

The system tracks several things: what the project is about (the project brief), what needs to happen (action items), why decisions were made (decisions), what ideas are being explored (ideas), and how everything is progressing (project pulse). You can use as much or as little of this as your org has enabled.

Everything is invoked through `@ai:` commands — you talk to Claude, and Claude handles the file management behind the scenes. You never need to think about where things are stored.

**Topic 2: Creating and describing projects**

A project starts with `@ai:create-project`. Claude walks you through naming the project, setting its status, assigning an owner, and adding members.

The most important part is the project brief — this is how you describe what the project actually is. Depending on how your org has configured things, you might be prompted for sections like objectives, scope, constraints, success criteria, and target audience. None of these are required — if you're not ready to fill something in, skip it. You can always come back and add it later with `@ai:edit-project`.

If your org has milestones enabled, you can set target dates for key checkpoints. If comms channels are enabled (Slack, Teams, or Discord), Claude can create a dedicated channel for the project and invite the right people.

The project brief is the foundation — other parts of the system (like project pulse reports) draw on it to provide context. The more complete it is, the better the system works for you.

**Topic 3: Working with ideas**

Ideas are the exploration layer. Before something becomes an official action item or decision, it often starts as a rough concept that needs development.

When you have a thought about a project, use `@ai:create-idea` to capture it. Ideas start in your private space — nobody else can see them. This is intentional. You should feel free to jot down half-formed thoughts, attach rough sketches or mockups, and develop your thinking without worrying about how it looks.

When an idea is ready for others to see, use `@ai:share-idea` to promote it to the project's shared space. At this point you can invite collaborators — specific people who you want to explore the idea with or contribute to it. Each collaborator gets a specific assignment: "review the mockups and suggest alternatives," "estimate the engineering effort," etc.

Collaborators can attach their own artifacts to the idea — mockups, documents, estimates — and create response ideas that reference yours. This turns ideas into a structured conversation, not just a one-way broadcast.

When an idea produces something actionable — a mockup that's been approved, a design that should be built — use `@ai:manage-ideas` to view and work with your ideas. From there, you can explicitly promote an artifact from the idea to the project's main artifacts space. Promotion creates action items automatically: "Sarah, implement this approved design by April 15." This handoff from exploration to execution requires your explicit action.

The key principle: ideas are for exploration, action items are for execution. The promotion step is the gate between them.

**Topic 4: Action items and dependencies**

Action items are the execution layer — the concrete things that need to get done. Use `@ai:manage-action-items` to create, update, and track them.

Each action item has an owner (who's responsible), a status (open, in progress, completed, blocked, deferred), and optionally a due date. What makes this system powerful is dependency chains.

When you create an action item, you can say it's blocked by another item or that it feeds into a downstream item. For example: "Design the API" feeds into "Implement the API" which feeds into "Write integration tests." When someone completes the API design, the system surfaces: "The API implementation is now unblocked — notify the implementer."

This means you're not just tracking a flat to-do list. You're tracking a production chain where completing one person's work triggers the next person's work. Nothing falls through the cracks because the system knows the dependencies.

Action items can come from several places: you create them directly, they spawn from decisions, they get created when idea artifacts are promoted, or they surface from channel digest reviews.

**Topic 5: Recording decisions**

Decisions are the authoritative record of *why* the team is doing something. Use `@ai:project-decide` to record them.

A decision captures: what was decided, who made the decision, and the rationale — why this approach over alternatives. The rationale is the most valuable part. Six months from now, when someone asks "why did we go with React instead of Vue?", the decision record has the answer.

Decisions are permanent. They're never edited or deleted. If a decision is reversed, you record a new decision that supersedes the old one. This preserves the full history of how the project's direction evolved.

Decisions can also spawn action items directly. "We've decided to go with the monorepo approach — Sarah needs to set up the repo structure, and Mike needs to migrate the existing packages." The decision record links to the action items it created, and the action items link back to the decision that spawned them.

**Topic 6: Staying current with channel digests**

If your project has a communications channel (Slack, Teams, or Discord), `@ai:channel-digest` reads what's been discussed since the last check and produces a summary.

The digest does two things. First, it gives you a concise summary of what was talked about — organized by topic, not just a wall of messages. If you missed a day of conversation, the digest catches you up in a minute.

Second, it extracts candidates — messages that look like they might be action items, progress updates, or decisions. "Sarah said she'll handle the API integration by Friday" becomes a candidate action item. "PM approved the new timeline" becomes a candidate decision.

These candidates go into a review queue. Nothing is automatically promoted — you review each candidate and decide whether to accept it (as an action item, update, or decision), edit it, or dismiss it. This keeps the project record clean and accurate while making sure important signals from chat don't get lost.

There's an important distinction here: if you use `@ai:update-project` and your update comes from a comms channel, the system automatically hands off to `@ai:channel-digest` instead of reading the channel directly. That ensures the channel cursor tracks what's been processed and nothing gets duplicated or lost. The channel digest is the sole entry point for reading project channels.

**Topic 7: Project pulse — status and Q&A**

Project pulse (`@ai:project-pulse`) is how stakeholders and managers get information about a project without digging through the details.

It works in two modes. Report mode generates a written status report covering things like: executive summary, recent activity, action item progress, decisions made, milestone status, risks and blockers, and ideas in progress. The report is designed to be readable in 2-3 minutes. You can save it as a dated artifact.

Conversational mode is more flexible — you ask questions about the project and get specific answers. "Who's blocked right now?", "What decisions have been made this week?", "Is the April milestone at risk?" Claude answers from everything the project has tracked — action items, decisions, activity logs, ideas, the brief. It's like talking to a project manager who has perfect recall of every detail.

The quality of pulse output depends on how well the tracking data has been maintained. If the team is regularly sharing updates and recording decisions, pulse reports are rich and useful. If tracking is sparse, pulse will say so honestly.

**Topic 8: Project lifecycle — archiving and restoring**

When a project wraps up and is no longer relevant to active org work, use `@ai:archive-project` to retire it. Archiving marks the project as `archived`, removes it from active project views, and makes it read-only. Nothing gets deleted — the project record and all its data remain intact in case you need to reference it later.

If you need to revive an archived project and work on it again, use `@ai:unarchive-project` to restore it to active status. The project's full history, scope, member list, and all files come back exactly as they were. This lifecycle separation — archive as a meaningful event rather than just a field change — helps keep your project list focused on what's currently active.

**Topic 9: How everything connects**

The real power of the system is how the pieces work together:

You create a project with a clear brief. Ideas let you explore approaches privately, then share them when ready. Shared ideas generate discussion and artifacts. Approved artifacts get promoted with action items attached. Action items form dependency chains so work flows from one person to the next. Decisions record the *why* behind the direction. Channel digests catch signals from informal conversation. And project pulse synthesizes all of it into stakeholder-ready views.

No single piece is required. Some teams will use everything. Others might just use projects with action items and skip ideas entirely. The system adapts to how your org works — your org admin configured which features are active.

The daily workflow is simple: share updates with `@ai:update-project` (just talk naturally about what you did, what's blocked, what's next), and the system parses your update into the right structure. Over time, this builds a rich project record that pulse can synthesize.

After Topic 9, offer to go deeper on any topic or to answer specific questions. Also surface the invocation shortcuts: "To see your project commands, check your member index. The main ones are `@ai:create-project`, `@ai:update-project`, `@ai:manage-action-items`, `@ai:manage-ideas`, and `@ai:project-pulse`."

### Answering Specific Questions

When answering a specific question, draw on the conceptual explanations above but answer at the level of detail the question implies. Use the member's actual context — their enabled features, their projects — when possible.

Common question patterns:

**"How do I {accomplish something}?"** — Identify the task that serves that need. Name the `@ai:` command and briefly explain what it does. If the feature is not enabled, say so and direct them to their org admin.

**"What happens when {thing}?"** — Trace the flow. "What happens when I complete an action item?" → "The system marks it complete, logs it to the activity log, checks if any downstream items are now unblocked, and surfaces those to you."

**"What's the difference between {A} and {B}?"** — Draw clear distinctions. "Ideas vs. action items: ideas are for exploration, action items are for execution. Ideas live in your private space until you're ready to share them. Action items are always visible to the project team."

**"Can I {do something}?"** — Honest answer. If yes, explain how. If no, say so directly and explain what alternatives exist.

**"What should I use for {situation}?"** — Recommend the appropriate workflow. "I need to capture that we chose PostgreSQL over MongoDB" → "That's a decision — use `@ai:project-decide`. It will capture the rationale and optionally spawn action items."

### Style & Tone

This should feel like a colleague who knows the system well walking you through it — practical, concrete, patient. Not a manual. Not a help desk ticket.

For the guided tour: conversational pacing. Check in between topics. Don't dump everything at once. Use realistic examples — "Imagine you're running a homepage redesign project..." is better than abstract descriptions.

For question answering: direct and specific. Get to the answer quickly. Offer to go deeper if the answer opens up related questions.

Avoid implementation details unless they help understanding. Members don't need to know about JSONL files or YAML frontmatter. They need to know what they can do and how to do it.

### Constraints

Do not perform any operations while in tutorial mode. This skill explains — it does not create projects, record decisions, or invoke other tasks. If the member asks to do something, direct them to the appropriate `@ai:` command.

Do not describe features that are disabled for the member's org. Check the collection setup responses first. If ideas are not enabled, don't walk through the ideas workflow as if it's available — mention it exists as a capability but note it's not currently active.

Do not speculate about behavior. If something doesn't match expectations, surface the discrepancy honestly: "That doesn't match how the system should work — it might be worth checking with your org admin."

Do not provide deep technical details about file formats, directory structures, or JSON schemas. The task definition files themselves serve that purpose for anyone who needs that depth. This tutorial is about productive use of the system.

### Edge Cases

If the member asks about a feature that exists in the projects collection but is disabled by their org admin: explain what it does conceptually and note that it's not currently enabled. Direct them to their org admin if they want it turned on.

If the member asks a question this skill cannot answer: say so. "I don't have enough information to answer that — you might try asking directly or checking with your org admin."

If the member is confused or frustrated: slow down. Go back to the most recent concept that was clear and rebuild from there.

If the member invokes this skill while doing project work: provide a brief targeted answer without disrupting the task context. The tutorial doesn't take over the session — it answers the question and steps back.

If the member asks about how the projects collection compares to external tools (Jira, Asana, etc.): be honest about what the system does and doesn't do. It's a conversational project management layer, not a full-featured PM platform. Its strength is natural language interaction and deep integration with the org's Claude workflows.
