# Action-Item Fields — Admin Guide

**Introduced:** projects 4.2.0 · **Audience:** org admins · **Config file:** `action-item-fields.json` (org root, provisioned by setup)

Action items ship with a fixed core — title, owner, status, due date, dependencies. Beyond that, what an org needs to record varies: one org wants to separate bugs from regular work, another wants effort estimates, another wants a compliance flag. Rather than guess, 4.2 lets you define those fields yourself, and change them whenever your needs change.

**The collection ships no field definitions.** After upgrading, `action-item-fields.json` contains an empty list and nothing about action items changes. Fields appear only once you add them.

## Where this lives

`action-item-fields.json`, provisioned at the org root. Readable by every member, writable by admins. Its shipped state:

```json
{ "schema_version": 1, "fields": [] }
```

## Defining a field

Each entry in `fields` describes one field:

| Key | Required | Meaning |
|---|---|---|
| `key` | yes | Stored name. Lowercase with underscores. **Permanent** — see [Renaming](#renaming-a-field). |
| `label` | yes | What members see. Change freely. |
| `type` | yes | One of `string`, `number`, `single-select`, `date`. |
| `options` | `single-select` only | The permitted values. |
| `unit` | `number` only | Display suffix, e.g. `pts`, `days`. |
| `default` | no | Value assumed when an item has none. `null` if omitted. |
| `status` | yes | `active` or `deprecated`. |

### The four types

**`single-select`** — one value from a list you control. Use it for any dimension where an item should hold exactly one value.

```json
{ "key": "type", "label": "Type", "type": "single-select",
  "options": ["item", "bug"], "default": "item", "status": "active" }
```

**`number`** — a numeric value, summed and averaged in `project-pulse`. Give it a `unit` or reports show a bare number.

```json
{ "key": "estimated_size", "label": "Size", "type": "number",
  "unit": "pts", "default": null, "status": "active" }
```

**`string`** — free text. Not aggregated and not reliably filterable; if you find yourself wanting to group by it, it should have been a `single-select`.

**`date`** — an ISO date, stored `YYYY-MM-DD`.

Those two examples are the requests that prompted this feature, shown here as illustrations. They are **not** installed — add them only if they suit your org.

## Adding a field later

Add the entry. That is the whole operation.

Existing action items — including every item created before the field existed — do not change. An item with no value for a field **reads as that field's default**, resolved at the moment it is read. No file is rewritten, no migration runs, and there is no window where items are half-updated.

This is deliberate. Rewriting every `action-items.json` in the org to insert a default would be a mass write across every project for no new information, and that operation class has already destroyed action-item and activity-log files here.

## Changing a field

- **`label`, `unit`, `default`** — change freely. Changing a `default` also changes what existing valueless items report, since defaults resolve at read time.
- **`options`, adding a value** — safe. New value becomes available immediately.
- **`options`, removing a value** — items already holding it keep it. `project-pulse` and `manage-action-items` will show the stored value and flag it as no longer valid rather than rewriting it. Prefer deprecating the whole field over quietly narrowing a list people have been using.
- **`type`** — do not change it. Existing values were validated against the old type. Deprecate and define a new field instead.

## Deprecating a field

Set `"status": "deprecated"`. The field stops being offered when members create or edit items, and existing values remain visible and clearable. Nothing is deleted.

**Deprecate rather than delete.** If you remove an entry outright, items still holding values become unrecognized data: the value shows with its raw key and no label, and it is excluded from every aggregate. It is not lost, but nothing can interpret it.

## Renaming a field

There is no rename. A `key` is how existing values are stored, so changing it orphans every value already recorded under the old name.

To effectively rename: define a new field with the new key, deprecate the old one, and let members move values across as they touch items. If you only want different wording, change the `label` — that is what it is for.

## What gets rejected

A definition that breaks any of these is **skipped at read time** — that definition only, not the whole file, so one bad entry cannot take your working fields down with it. The rejected key and reason are reported to whoever hit it, so it surfaces rather than failing silently.

- No `key`, or a `key` that duplicates an earlier definition (the first one wins)
- A `type` outside `string`, `number`, `single-select`, `date`
- `single-select` with a missing or empty `options` array
- `options` on any type other than `single-select`, or `unit` on any type other than `number`
- A **non-null** `default` that is not one of the field's own `options` (`single-select`), or is not numeric (`number`). `default: null` means "no default" and is valid on every type
- A `status` other than `active` or `deprecated`

Nothing validates this file when you save it — there is no schema check at write time. These rules are enforced when a capability reads the config, which is why they are listed here rather than left implicit.

## Should it be a field or a tag?

Both were added in 4.2 and they solve different problems.

**A field** when an item should hold exactly one value on a dimension you want to count, sum, or report on. Fields are defined by you, shared by every project, and appear in `project-pulse` breakdowns.

**A tag** when labels are emergent, overlapping, and local. Any member can add a tag to a project or an action item without asking you. Tags are not aggregated across a dimension, and nothing stops an item carrying two tags that ought to be mutually exclusive.

Rule of thumb: if you would be annoyed to find an item tagged both `mobile` and `web`, that dimension wants to be a `single-select` field. If a heavily-used tag turns out to be a real dimension, promote it — define the field, and members set it as they touch items.

## What fields do not do yet

Field values are queryable **within a project**. `project-pulse` will tell you how many open bugs a project has and total effort per assignee for that project.

There is no cross-project or org-wide rollup in 4.2 — "every open bug across the org" is not answerable yet. That needs a cross-project query capability, which is tracked separately and deliberately not in this release. Worth knowing before you define a field expecting an org-wide dashboard.

## If something goes wrong

A missing, empty, or unparseable `action-item-fields.json` all behave the same way: no fields are offered, and everything else works normally. Members are told the config could not be read; they are never blocked from recording work. Fields are additive, and their absence never stops the core job.
