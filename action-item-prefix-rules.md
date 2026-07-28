# Action-Item ID Prefix — Rules Reference

**Introduced:** projects 4.2.0 · **Referenced by:** `create-project`, `edit-project`, `transition-project`, `manage-action-items`

Action item IDs are `{PREFIX}-{NNN}` (e.g. `MOB-014`). The prefix belongs to the project, is unique across the org, and becomes immutable once the project has issued its first item. This file is the single definition of the derivation, validation and claim rules — capabilities reference it rather than restating it, so the rules cannot drift between them.

## 1. Why the constraints exist

A prefix is part of an **identifier**, not metadata. Identifiers are referenced from places agent-index does not control — git branch names, Slack messages, pull requests, release notes, documents. Once `MOB-014` exists in the world, it cannot be renamed or reissued without making an external reference wrong. Every rule below follows from that.

## 2. Reserved prefixes

**`AI` is reserved and can never be claimed.** It is the implicit prefix for every project created before 4.2 and for any project that has not set one (§6). If a project could claim `AI`, its items would collide with the existing IDs of every unprefixed project in the org.

## 3. Derivation (the suggested candidate)

Deterministic, so the same name always suggests the same prefix:

1. Split the project name on whitespace and hyphens.
2. Drop stop-words: `a an the of for and to in on at by with`. If nothing remains, keep the original words.
3. Strip characters outside `A-Za-z0-9` from each remaining word.
4. **Drop any word that does not begin with a letter.** If nothing remains, keep the words from step 3. (Without this step a name like "2026 Planning" derives `2P`, which fails validation and falls all the way through to `PRJ` — discarding the perfectly good word next to the year.)
5. **Two or more words remain:** take the first character of each of the first four words.
6. **One word remains:** take its first three characters — or fewer if the word is shorter.
7. Uppercase the result.
8. If the result is shorter than 2 characters, or does not begin with a letter, use `PRJ`.

Worked examples — each traceable through the steps above:

| Project name | Steps | Candidate |
|---|---|---|
| Mobile App Redesign | 3 words, all letter-initial → `M`+`A`+`R` | `MAR` |
| Payments | 1 word → first three characters | `PAY` |
| The Library of Congress Import | drop `the`, `of` → `L`+`C`+`I` | `LCI` |
| 2026 Planning | drop `2026` (step 4) → 1 word → first three | `PLA` |
| Q1 | 1 word, letter-initial, 2 characters — valid as-is | `Q1` |
| 2026 | drop `2026` → nothing left → keep it → `202` begins with a digit | `PRJ` |

**These examples are normative.** They were corrected on 2026-07-27 after a rehearsal walkthrough found two of them ("2026 Planning" and "Q1") contradicting the algorithm they were meant to illustrate — the algorithm produced `PRJ` for both. An implementation that disagrees with this table is wrong, and a change to the algorithm must re-derive every row.

## 4. Validation (derived or member-supplied)

- Matches `^[A-Z][A-Z0-9]{1,5}$` — 2 to 6 characters, uppercase, **must begin with a letter**. A leading digit would make `12-001` ambiguous against a bare sequence number.
- Is not `AI` (§2).
- Is available (§5).

Reject with the specific reason, never a generic "invalid". A member who typed `mob` should be told it must be uppercase, not that their input was rejected.

## 5. Availability and claiming

The registry is `/shared/prefix-registry/{PREFIX}.json` — **one file per prefix**. A single shared registry file would be a read-modify-write race across every member creating a project, which is the torn-write class this org has already had to recover from. One file per claim removes the race by construction.

**Availability check (no write):** `aifs_exists("/shared/prefix-registry/{PREFIX}.json")`.

**Claim protocol (the write):**

1. `aifs_exists` — if present, the prefix is taken; resolve per §6 and retry.
2. `aifs_write` the record:
   ```json
   { "prefix": "MOB", "owner_hash": "{member_hash}",
     "claimed": "{ISO 8601}", "visibility": "org_public",
     "project_slug": "{slug}" }
   ```
3. **Read it back and confirm `owner_hash` is ours.** This is the guard, not the `exists` check: the backend permits same-named siblings, so check-then-write is not atomic. If the read-back shows another owner, another member won the race — take the next candidate and retry.
4. Bounded at **3 attempts**. After that, ask the member to choose a prefix directly rather than looping.

**Private-project hygiene:** when the project is private, `project_slug` is **omitted entirely** — not blanked, not obfuscated. The registry is org-visible, and 4.0's pointer-hygiene principle holds that an org-visible record must never name or imply an invisible project. `visibility` is `private`.

**Claim before writing the project record.** Never write `action_item_prefix` into `project.md` or a pointer until the claim has been confirmed by read-back.

## 6. Collision resolution

When a candidate is taken: extend it by appending the next unused character from the source words (up to 6 characters), then, if still taken, append a numeric suffix `2`–`99` while respecting the 6-character limit. Present the resolved candidate to the member — never claim silently on their behalf.

## 7. Confirmation is mandatory

The suggested prefix is **always presented for explicit acceptance**, and the member may override it. A derived abbreviation that reads clearly to the deriving algorithm is often ambiguous to a human encountering it in a branch name months later, so the member gets the final say.

## 8. Immutability

- **Before the project's first action item:** the prefix may be changed freely. Claim the new prefix and confirm it **before** releasing the old one, so the project is never left with no claim.
- **After the first action item exists:** the prefix is locked. Refuse the change and explain that IDs are already in circulation. This is a refusal with a reason, never a silent no-op.

  "Has issued an item" means **either** a non-empty `items` array **or** `next_id` greater than 1. The second clause matters: items can be deferred out of the list or removed by hand, and an empty `items` array with `next_id` at 4 means three IDs were issued and may still be referenced outside agent-index. Checking only the array would unlock a project whose IDs are already in the world.

  If `action-items.json` cannot be read at all, **fail closed** — treat the project as having issued items and refuse. Wrongly refusing costs a member a prefix they wanted; wrongly allowing mints IDs that collide with items nobody could see.
- **Existing IDs are never renumbered**, under any circumstance.
- `prefix_history` on the project record retains superseded prefixes so previously issued IDs still resolve. Consumers must therefore resolve a prefix to a project by lookup, never by assuming a pattern-derived mapping is permanent — even though a project has exactly one *active* prefix at any moment.

## 9. Absent prefix

A project with no `action_item_prefix` (every project created before 4.2, and any project whose owner declined to set one) reads as `AI`. This is resolved **at read time**; nothing is written to bring an existing project into the new scheme.

## 10. Claim lifetime

- `archive-project` **retains** the claim — an archived project's IDs must still resolve.
- A claim is released only on a permitted prefix change (§8), and only after the replacement is confirmed.
- A registry entry whose project no longer exists is reported by validation tooling but **never auto-deleted**: an archived or transitioned project's claim is legitimate.
