# AGENTS.md

Guidance for human and AI contributors working in this repository.

## Scope

- This file applies to the whole repository.

## Agent Agnosticism

- This repository targets no particular agent or vendor. `AGENTS.md` is the single source of truth for contributor guidance: add every rule here, not to a tool-specific file.
- A tool-specific entry point is a pointer, never a second copy. `CLAUDE.md` exists only because Claude Code reads `CLAUDE.md` and not `AGENTS.md`; it holds one import of this file and no guidance of its own. If another tool needs its own entry point, add the same kind of one-line pointer.
- Where a procedure has to live in a tool-specific location (`.claude/skills/`), keep it a procedure — occasional, task-triggered steps. Anything always-applicable stays here, so an agent or person reading only this file still gets every rule that matters.

## Core Principles

- Prefer common, well-maintained libraries and packages over custom ad hoc logic.
- Keep changes focused and minimal for the requested task.
- Do not modify unrelated files.

## Specification

- `SPEC.md` is the source of truth for what each module does and guarantees: the FLEx fields it reads and writes, its match and transform rules, and its prerequisites.
- Whenever a change alters or clarifies a rule `SPEC.md` covers, update `SPEC.md` in the same change — do not let it drift out of sync with the code.
- If code and `SPEC.md` disagree, that is a bug: fix whichever is wrong, do not silently favour one.
- Do not speculatively extend `SPEC.md` to cover modules or behaviours that aren't implemented yet; add to it incrementally as each is actually built (see [SPEC.md's Not Yet Specified section](SPEC.md#not-yet-specified)).
- **Split of concerns:** `AGENTS.md` documents how to work in this repo (process, conventions, workflow). `SPEC.md` documents what the modules do and guarantee (each module's FLEx data contract). Repo-wide engineering conventions that happen to describe behaviour (e.g. reporting through the `report` object, honouring `modifyAllowed`) stay in `AGENTS.md` since they apply uniformly across modules; `SPEC.md` is reserved for the per-module contract specifically.

## Skills

Task-specific procedures live under `.claude/skills/<name>/SKILL.md` rather than in this file, so `AGENTS.md` stays a set of always-applicable rules. Add a new skill when a procedure is followed occasionally rather than always.

The directory name is Claude Code's (it discovers skills only there), but the files are not tool-specific and every agent can use them:

- Write each one to the [Agent Skills](https://agentskills.io) open format: YAML frontmatter using only the six standard fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`), then plain Markdown instructions. Tool-specific frontmatter fields and body features are rejected or ignored outside the tool that added them.
- List every skill below with a link. Other agents don't scan `.claude/skills/`, and many file searches skip dot-directories, so this list is how anything other than Claude Code finds them.
- Keep `.claude/skills/` committed to git. If a `.gitignore` is ever added, do not ignore `.claude/` wholesale, or the procedures become invisible to everyone else.
- Any agent or person can be pointed straight at a `SKILL.md` and told to follow it; nothing in the format requires a particular tool.

Skills in this repository:

- _(none yet)_

## Plans

- A plan in `plans/` is a historical record of what was approved, never a source of truth for how the repo works. Where a plan disagrees with the current code, `SPEC.md`, or `AGENTS.md`, those win — read them instead, and do not "fix" the plan to match.
- Keep re-syncing a plan while it is still being planned and implemented (see [Working Style](#working-style)). Once implementation is complete the plan freezes: don't rewrite it, renumber it, or restate later decisions inside it.
- Give each plan a status line under its title recording when it was approved and whether it has been implemented, so a reader knows immediately whether it describes the present or the past.
- When decisions changed after approval, append a short list of those changes to the end of the plan rather than editing the body. Appending keeps the record honest; editing destroys it.

## Markdown Conventions

- **Don't number Markdown headings** (`## 2. Pitch field`, `## 1. Decide the match rule`) in any file in this repo — `SPEC.md`, skills (`SKILL.md`), and other reference docs — unless there's a specific reason a given file needs it. A numbered heading shifts whenever a section is inserted or reordered above it, silently breaking every cross-reference to it.
- **Reference a heading elsewhere by Markdown anchor link and its actual name, not a number**: `[SPEC.md's Not Yet Specified section](SPEC.md#not-yet-specified)`, not `SPEC.md §3`. An anchor link survives reordering; only a heading rename breaks it, and that's a one-time, greppable fix (`grep -rn '#anchor-slug'`) rather than a renumbering cascade.

## Working Style

- Before changing behaviour, check existing patterns in nearby files and follow them.
- When behaviour changes are non-trivial, ask for confirmation before implementing.
- If a requirement is ambiguous and could alter behaviour, ask a clarifying yes/no question first.
- Ask clarifying questions in plain chat text, not via a multiple-choice/quick-answer UI widget.
- Save non-trivial implementation plans to `plans/<descriptive-name>.md` in the repo (not only wherever the tool's own ephemeral plan-mode file lives), so they're preserved and reviewable via git history. This is not a one-time save: whenever the plan is revised (e.g. new information surfaces mid-planning), re-sync `plans/<name>.md` with the latest approved version before or immediately after implementation starts.

## Libraries And Dependencies

- Reuse existing dependencies and idioms already present in the repo when possible.
- Add a new package only when it clearly improves reliability, readability, or maintainability.
- Prefer widely adopted packages over hand-rolled implementations.

## FlexTools Module Conventions

These modules are loaded and run by [FlexTools](https://github.com/cdfarrow/flextools) against a live FLEx project; they are not command-line scripts. The conventions below replace the usual CLI stdout/stderr rules.

- Each module is a single self-contained `.py` file at the repo root, named after what it does, opening with a header comment block: title, one-line purpose, author, month and year, and `Platforms: Python .NET and IronPython`.
- Keep the standard shape, in this order: `# -*- coding: utf-8 -*-`, `from flextoolslib import *`, a `docs` dict (`FTM_Name`, `FTM_Version`, `FTM_ModifiesDB`, `FTM_Synopsis`, `FTM_Help`, `FTM_Description`), `MainFunction(project, report, modifyAllowed)`, and finally `FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction, docs = docs)`. FlexTools looks up that last name exactly, so it must be spelled as written.
- Bump `FTM_Version` in `docs` whenever a module's behaviour changes.
- Honour `modifyAllowed`: when it is false, do the same reading and reporting but write nothing, so a preview run is a genuine dry run (see the `[DRY RUN]` prefix in `Fix_Pronunciation_Media_Paths.py`).
- Report through the `report` object (`report.Info`, `report.Warning`, `report.Error`), never `print` — this is the FlexTools counterpart of separating result output from diagnostics. Use `report.ProgressStart` and `report.ProgressUpdate` for passes over the whole lexicon.
- Fail gracefully on missing prerequisites (e.g. a required custom field): `report.Error` and degrade to read-only rather than raising.
- Reach FLEx data through the `flextoolslib` project helpers (`LexiconAllEntries`, `LexiconNumberOfEntries`, `LexiconGetLexemeForm`, `LexiconGetEntryCustomFieldNamed`, `LexiconAddTagToField`, …) in preference to walking raw LCM attributes. Where the model may not hold an object, guard with `getattr(obj, "Name", None)` and skip rather than assume.
- Keep pure logic in module-level functions separate from `MainFunction`, so it can be exercised without a FLEx project and reused as a FLEx Process (see `convert()` in `Extract_Chao_tone_letters_from_accent_notation.py`).
- Add brief comments for non-obvious logic so future readers can follow intent.

## Data Safety

- These modules modify a live FLEx project, and FLEx has no undo across a FlexTools run. Keep every write behind `modifyAllowed`.
- Prefer narrowly scoped edits over broad rewrites: replace a matched prefix once (`path.replace("Media\\", "AudioVisual\\", 1)`) rather than substituting everywhere in a value.
- Keep the README's standing instruction that users back up their FLEx project before running these modules; don't remove or soften it.

## Testing Approach

- Use `pytest`, with tests under `tests/`, run as `python -m pytest` from the repo root.
- Test the pure helper functions (e.g. `convert()`), which need no FLEx project. `MainFunction` needs a live FLEx project, so verify it by running the module in FlexTools with modification disabled first.
- `flextoolslib` only installs on Windows alongside FieldWorks, so importing a module file fails elsewhere at its top-level `from flextoolslib import *`. Stub it in `tests/conftest.py` (insert a stub `flextoolslib` into `sys.modules`, then load the module by path) so tests run on any platform without splitting helpers out of the single-file module.
- Prefer small parametrized assertions while a helper's output is short strings. Switch to approval testing when output becomes large or awkward to assert inline: the checked-in artifact is the approved one, a mismatch produces a received artifact for review, and changes are never auto-accepted without explicit confirmation.
- Keep approved artifacts human-reviewable and deterministic so diffs are meaningful.
- Follow TDD for behaviour changes: add or extend the test and confirm it fails first (red), write the minimum implementation to make it pass (green), then refactor with the tests as a safety net.

## Documentation

- `README.md` is the user-facing description of each module. A new module, or a behaviour change to an existing one, updates its README section in the same change.
- When a module incorporates third-party code, name the author and licence in the module's source header, and record the resulting combined licence in the README's Attributions line.
