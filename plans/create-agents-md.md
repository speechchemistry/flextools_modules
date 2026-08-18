# Create AGENTS.md for flextools_modules

Status: approved and implemented 2026-08-18. Historical record — where this plan disagrees with the
current `AGENTS.md`, `SPEC.md`, or code, those win. See [Changes after approval](#changes-after-approval).

## Context

This repo has no `AGENTS.md`, so human and AI contributors have no written statement of its
conventions. Two sibling repos already have one — `audio_label_file_conversions` (Python) and
`lexicon_file_conversions` (R) — and their shared core (Scope, Core Principles, Working Style,
Libraries And Dependencies) is byte-identical boilerplate that should carry over verbatim so the
three repos stay consistent.

What must change is everything below the principles: this repo contains standalone **FlexTools
modules** ([Fix_Pronunciation_Media_Paths.py](Fix_Pronunciation_Media_Paths.py),
[Extract_Chao_tone_letters_from_accent_notation.py](Extract_Chao_tone_letters_from_accent_notation.py)),
not CLI scripts or a spec-driven converter, and there is no test suite yet. The intended outcome is
a short, honest AGENTS.md describing how this repo actually works, plus the sibling repos' process
conventions (plain-text questions, `plans/`, Markdown anchors), which the user has confirmed should
apply here too.

The user also intends to add a `SPEC.md` and skills to this repo, so AGENTS.md carries over the R
repo's `## Specification` and `## Skills` sections — adapted to FLEx module behaviour rather than the
CSV↔LIFT data model, and written so they hold from day one rather than describing a mature spec.

## Deliverable

- New file `AGENTS.md` at the repo root.
- New file `SPEC.md` — a minimal skeleton so AGENTS.md's references aren't dangling links: a short
  intro naming it the source of truth for what each module does and guarantees, one section per
  existing module documenting current observable behaviour (match rule, what is written where,
  dry-run behaviour, prerequisites), and a `## Not Yet Specified` section to grow into. Kept
  deliberately thin — it records only what the code already does today.
- New directory `.claude/skills/` is **not** created yet: AGENTS.md's `## Skills` section states
  where skills live and when to add one, with no skill listed until the first real procedure exists.
- New file `plans/create-agents-md.md` — this approved plan, committed per the `plans/` convention
  the file itself adopts (this also makes the `plans/*.md` Markdown exception real rather than
  hypothetical).

No existing files change.

## AGENTS.md structure

Sections marked **verbatim** are copied unchanged from the sibling repos.

1. `# AGENTS.md` + "Guidance for human and AI contributors working in this repository." — **verbatim**
2. `## Scope` — **verbatim** ("This file applies to the whole repository.")
3. `## Core Principles` — **verbatim** (prefer common, well-maintained libraries over custom ad hoc
   logic; keep changes focused and minimal; do not modify unrelated files)
4. `## Specification` — adapted from the R repo, same four rules with this repo's subject matter:
   - `SPEC.md` is the source of truth for what each module does and guarantees — the FLEx fields it
     reads and writes, its match/transform rules, and its prerequisites.
   - Whenever a change alters or clarifies a rule `SPEC.md` covers, update `SPEC.md` in the same
     change — don't let it drift out of sync with the code.
   - If code and `SPEC.md` disagree, that's a bug: fix whichever is wrong, don't silently favour one.
   - Don't speculatively extend `SPEC.md` to cover modules or behaviours that aren't implemented yet;
     add to it incrementally, tracking the rest in
     [SPEC.md's Not Yet Specified section](SPEC.md#not-yet-specified).
   - Keep the R repo's **split of concerns** bullet, retargeted: `AGENTS.md` documents how to work in
     this repo (process, conventions, workflow); `SPEC.md` documents what the modules do and
     guarantee. Repo-wide engineering conventions that happen to describe behaviour (e.g. reporting
     via the `report` object, honouring `modifyAllowed`) stay in `AGENTS.md` since they apply
     uniformly across modules; `SPEC.md` is reserved for each module's data contract.
5. `## Skills` — from the R repo: task-specific procedures live under `.claude/skills/<name>/SKILL.md`
   rather than in this file, so `AGENTS.md` stays a set of always-applicable rules; add a skill when
   a procedure is followed occasionally rather than always. No skill is listed yet — the bullet list
   starts empty and gains its first entry when a real procedure is written (a likely first candidate:
   the end-to-end procedure for adding a new FlexTools module — header block, `docs` dict,
   `MainFunction`, README section, `SPEC.md` section).
6. `## Markdown Conventions` — from the R repo: don't number Markdown headings; reference a heading
   elsewhere by anchor link and its actual name, not a number; keep the `plans/*.md` exception
   (a plan is a point-in-time record — don't retroactively renumber it). Condense the R repo's
   three long bullets to the same three rules with a one-clause rationale each, since this repo has
   far fewer docs to cross-reference.
7. `## Working Style` — **verbatim** from the R repo, all five bullets: check existing patterns in
   nearby files first; ask for confirmation before non-trivial behaviour changes; ask a clarifying
   yes/no question when a requirement is ambiguous; **ask clarifying questions in plain chat text,
   not via a multiple-choice/quick-answer UI widget**; save non-trivial implementation plans to
   `plans/<descriptive-name>.md` and re-sync on revision.
8. `## Libraries And Dependencies` — **verbatim** (reuse existing deps and idioms; add a package only
   when it clearly improves reliability, readability, or maintainability; prefer widely adopted
   packages over hand-rolled implementations)
9. `## FlexTools Module Conventions` — new; replaces the R repo's `## R Code Conventions` and both
   repos' `## CLI Script Conventions`, neither of which applies (these modules are loaded by
   FlexTools, not invoked as CLIs). Every bullet below is observable in the two existing modules:
   - Each module is a single self-contained `.py` file at the repo root, named after what it does,
     opening with a header comment block: title, one-line purpose, author, month/year, and
     `Platforms: Python .NET and IronPython`.
   - Standard shape, in order: `# -*- coding: utf-8 -*-`, `from flextoolslib import *`, a `docs`
     dict (`FTM_Name`, `FTM_Version`, `FTM_ModifiesDB`, `FTM_Synopsis`, `FTM_Help`,
     `FTM_Description`), `MainFunction(project, report, modifyAllowed)`, and finally
     `FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)` — that name is
     required by FlexTools and must be spelled exactly.
   - Bump `FTM_Version` in `docs` whenever a module's behaviour changes.
   - Honour `modifyAllowed`: when false, do the same reading and reporting but write nothing — a
     genuine dry run (see the `[DRY RUN]` prefix in
     [Fix_Pronunciation_Media_Paths.py](Fix_Pronunciation_Media_Paths.py)).
   - Report through the `report` object (`report.Info` / `report.Warning` / `report.Error`), never
     `print` — this is the FlexTools counterpart of the sibling repos' stdout/stderr rule. Use
     `report.ProgressStart` / `report.ProgressUpdate` for whole-lexicon passes.
   - Fail gracefully on missing prerequisites (e.g. a required custom field): `report.Error` and
     degrade to read-only rather than raising.
   - Reach FLEx data through `flextoolslib` / `FLExProject` helpers (`LexiconAllEntries`,
     `LexiconGetLexemeForm`, `LexiconGetEntryCustomFieldNamed`, `LexiconAddTagToField`, …) in
     preference to raw LCM attribute walking; where the model may not hold an object, guard with
     `getattr(obj, "Name", None)`.
   - Keep pure logic in module-level functions separate from `MainFunction`, so it can be tested
     without a FLEx project and reused as a FLEx Process (see `convert()` in
     [Extract_Chao_tone_letters_from_accent_notation.py](Extract_Chao_tone_letters_from_accent_notation.py)).
   - Add brief comments for non-obvious logic so future readers can follow intent (carried over from
     the R repo's code-conventions section, which is language-neutral in spirit).
10. `## Data Safety` — new, short; the genuinely repo-specific risk is that these modules mutate a
   live FLEx project. Keep every write behind `modifyAllowed`; prefer narrowly scoped edits
   (e.g. `path.replace("Media\\", "AudioVisual\\", 1)` on a matched prefix, not a global rewrite);
   preserve the README's standing instruction that users back up their FLEx project first.
11. `## Testing Approach` — short and forward-looking (per the user's answer), three bullets:
    prefer approval testing for the pure helper functions, which need no FLEx project to run; keep
    approved artifacts human-reviewable and deterministic so diffs are meaningful; on a mismatch,
    produce a received artifact for review rather than auto-accepting.
12. `## Documentation` — new, short. The README is the user-facing description of each module, so a
    new or behaviour-changed module updates its README section in the same change. Also record the
    attribution practice already in the repo: a module incorporating third-party code names the
    author and licence in its source header, and the README's Attributions line explains the
    resulting combined licence.

Sections deliberately **not** carried over: `## Data Normalization And Scrubbing` and
`## XML Output Formatting` (this repo produces no XML artifacts or scrubbed fixtures), the R repo's
`testthat`-specific bullets, and both repos' `## CLI Script Conventions` (superseded by the `report`
object rule in FlexTools Module Conventions).

## Verification

- Read `AGENTS.md` end to end: every rule must describe something observable in this repo today,
  and no rule may reference a file or directory that won't exist after this change (`SPEC.md` and
  `plans/` will; `.claude/skills/` is described as a location, not linked to).
- Read `SPEC.md` against the two modules: each documented behaviour must be what the code actually
  does today, with anything unimplemented sitting under `## Not Yet Specified` instead.
- Check the one cross-file anchor link resolves: the `SPEC.md#not-yet-specified` link in AGENTS.md
  must match an actual `## Not Yet Specified` heading in `SPEC.md`.
- Cross-check the FlexTools Module Conventions section against both modules:
  `grep -n "FTM_\|modifyAllowed\|report\.\|FlexToolsModule\|getattr" *.py` — the documented shape
  must match the actual code, not an idealised version of it.
- Confirm the shared sections are still byte-identical to the siblings, diffing against the fetched
  copies in the scratchpad (`py_AGENTS.md`, `r_AGENTS.md`).
- Confirm no numbered headings: `grep -nE '^#+ +[0-9]+\.' AGENTS.md SPEC.md` returns nothing
  (`plans/*.md` is exempt by convention).
- `git status` shows exactly three additions: `AGENTS.md`, `SPEC.md`, and
  `plans/create-agents-md.md`.

## Follow-up (outside the repo)

Save the confirmed preference — ask clarifying questions in plain chat text, not via a
quick-answer widget — to memory as `feedback`, so it applies in future sessions here too.

## Changes after approval

Appended rather than edited into the body above, so the approved plan stays readable as what it was.
All of these are in the current `AGENTS.md`, which supersedes this plan where they differ.

- **Testing Approach** names `pytest` (tests under `tests/`, run as `python -m pytest`), records that
  `flextoolslib` must be stubbed in `tests/conftest.py` for tests to run off Windows, prefers
  parametrized assertions while outputs are short strings, and adds TDD red/green/refactor. The
  plan's three generic approval-testing bullets were replaced.
- **`CLAUDE.md` added** — a seven-line stub whose only content is an `@AGENTS.md` import, because
  Claude Code reads `CLAUDE.md` and not `AGENTS.md`. Without it, nothing loaded `AGENTS.md`
  automatically in Claude Code.
- **`## Agent Agnosticism` section added** as the second section: `AGENTS.md` is the single source of
  truth, a tool-specific entry point is a pointer never a copy, and anything always-applicable stays
  out of tool-specific locations.
- **`## Skills` expanded** with what keeps skills usable outside Claude Code: the Agent Skills open
  format restricted to its six standard frontmatter fields, the listing in `AGENTS.md` as the
  discovery mechanism for other agents, and keeping `.claude/skills/` committed. The neutral-home
  plus stub arrangement was considered and rejected as unnecessary indirection.
- **`## Plans` section added**, defining the lifecycle this section is part of: a plan is a
  historical record, never a source of truth, frozen once implemented, with later decisions appended
  rather than edited in.
- **The "Approval-test fixtures and approved artifacts for `convert()`" bullet was removed from
  `SPEC.md`'s Not Yet Specified list** — test infrastructure is process, so it belongs in
  `AGENTS.md` under the plan's own split-of-concerns rule.
- **The `plans/*.md` numbering exception was deleted from `## Markdown Conventions`** (by Tim). The
  `## Plans` rule against retroactively editing an implemented plan covers the same ground more
  generally.
