# Activity Log Append (internal procedure)

**Used by:** every projects capability that adds an entry to a project's `activity/activity-log.jsonl`. These are channel-digest, create-idea, create-project, manage-action-items, manage-ideas, project-decide, project-pulse, share-idea, transition-project and update-project. Each one cites this file at the step where it appends. Read it from this collection's read base: Google Drive `id:{folder_id}/internal/activity-log-append.md`, with `folder_id` from the `projects` entry in org-config `installed_collections[]`; OneDrive `/projects/internal/activity-log-append.md`.

**Why it exists.** Two failures:
- An unguarded append can silently drop another member's entry if both write at once.
- Bug `20261021-6b8d7f00-100220-5106` wiped a project's whole log. `aifs_read` returned the raw JSONL, the agent tried to parse it as one JSON document, the parse failed silently, and it wrote back only the new entry.

This procedure prevents both.

`{log}` below is `{project base}/activity/activity-log.jsonl`, with `{project base}` as the calling task resolved it (org-public → `/shared/projects/{slug}/`; private → the owner's space).

## The file format

The log is JSONL: one complete JSON object per line, LF line endings, and a trailing newline. The entries in task files are shown pretty-printed for reading. Write each one compact, on a single line. Never wrap the log in an array or an object, and never parse the whole file as one JSON document.

## Appending an entry

1. **Stat first.** `aifs_stat({log})` and keep its `revision`.
   - If the stat says the file doesn't exist, re-address once with the other form (core `runtime-reference.md` § "Addressing: Owned Content and Sharing"). If it still doesn't exist, go to "Creating the log" below.
   - Stat comes before the read on purpose. If the file changes between the two calls, the guarded write in step 6 conflicts and retries. Read-first, the order in core `collection-authoring-guide.md` § "The `if_revision` pattern for shared state files", can pair the newer revision with the older content, and then the write overwrites the other member's entry.
2. **Read it as text.** `aifs_read({log})`. Split the content into lines and parse each non-blank line as one JSON object. Keep the lines exactly as read, and count the entries (`N`).
3. **If the read or any line's parse fails, stop.** Write nothing. Never treat the file as empty or start a new one. Tell the member: "I couldn't read this project's activity log ({reason}), so I didn't add the entry ({summary}). Nothing in the log was changed."
4. **Build the new content.** The existing lines, unchanged and in order, then the new entry as one compact line, then a newline.
5. **Check before writing.** The new content must have exactly `N + 1` entries, and its first `N` lines must be identical to the lines read in step 2. If not, stop as in step 3. Never write a log with fewer entries than it had.
6. **Write with the guard.** `aifs_write` to `{log}` with `"if_revision": "{revision}"`, passing the content via `content_file` (a local temp file), because a long log can exceed the inline limit.
7. **On `REVISION_CONFLICT`,** another member wrote in between. Go back to step 1: stat again, read again, and re-apply the same entry to the fresh copy. Retry up to 5 times. If it still conflicts, stop, write nothing more, and tell the member: "Someone else is updating this project's activity log right now, so I didn't add the entry ({summary}). Try again in a moment." Never fall back to an unguarded write.

## Creating the log

Do this only when step 1 found no file after re-addressing. That happens for a new project (create-project) or one that predates activity tracking.
- Create `{project base}/activity/` if needed.
- Write the new entry as the file's only line, with a trailing newline. This is a plain write.

Never create the log in response to a failed read or parse of an existing file (step 3).
