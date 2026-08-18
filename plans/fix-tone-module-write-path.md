# Make the tone module's write path robust, then spin off a converters repo

Status: approved 2026-08-18. Phase 1 implemented and verified on Windows 2026-08-18 (commits
`cfce661`, `749dccf`). Phase 2 implemented 2026-08-18 as
[flex-string-converters](https://github.com/speechchemistry/flex-string-converters); not yet
verified in FlexTools. Historical record — where this plan disagrees with the current `AGENTS.md`,
`SPEC.md`, or code, those win. See [Changes after approval](#changes-after-approval).

## Context

The longer-term aim is to invert this repo's emphasis: **the string converter is the product, and
the FlexTools module is one of several ways to run it**. `flextoolslib` installs only on Windows
alongside FieldWorks, so anything inside a module file cannot be imported or tested anywhere else; a
converter is equally useful from the command line and as a FLEx Process; and
`Extract_Chao_tone_letters_from_accent_notation.py` is 73 lines of which exactly one does domain work
(`convert(lexeme_form_itsstring)`). `Lib/chao_tones.py` already proves the shape.

Before that move, the module that would become the template needs its write path made reliable.

### What is actually wrong — corrected

An earlier draft of this plan claimed the write path is simply broken. That was too strong. **The
write call is identical in every revision** — `project.LexiconAddTagToField(entry, flagsField,
chao_letters)` appears unchanged in all six commits, and in the pre-refactor
`old_Extract_Chao_tone_letters_from_accent_notation.py` still sitting in the FlexTools `Tim Module`
folder, whose `MainFunction` is line-for-line identical to today's. The refactor changed nothing on
this path, which is consistent with Tim's recollection that the original script worked.

The `AttributeError` reported in `flextools-wrapper-brief.md` is nonetheless real, and the source
shows exactly when it fires. `LexiconAddTagToField`
([FLExProject.py:1159](file:///mnt/c/Users/timke/AppData/Local/Programs/Python/Python312/Lib/site-packages/flexlibs/code/FLExProject.py))
calls `LexiconGetFieldText` with **no** writing system, reaching `GetCustomFieldValue` (line 938):

```python
if fieldType in FLExLCM.CellarStringTypes:            # {String}        → fine
    return ITsString(...get_StringProp(hvo, fieldID))
elif fieldType in FLExLCM.CellarMultiStringTypes:     # {MultiUnicode, MultiString}
    mua = self.project.DomainDataByFlid.get_MultiStringProp(hvo, fieldID)
    if languageTagOrHandle:
        return mua.get_String(WSHandle)               # fine
    else:
        return ITsString(mua.BestAnalysisVernacularAlternative)   # AttributeError
```

So the failure is **conditional on the field's type, not on the script**:

- `Pitch` as a `String` field → first branch → `LexiconAddTagToField` works.
- `Pitch` as a `MultiUnicode` field → third branch → raises every time.

In FLEx, a single-line-text custom field configured with one **specific** writing system is a
`String` field; one configured with a **magic** writing system (Analysis, or Vernacular) is
`MultiUnicode`. Tim has confirmed `Pitch` uses the vernacular writing system. **Leading hypothesis:
`Pitch` was originally created against a specific WS and later reconfigured to the magic Vernacular
setting, moving it from the working branch to the broken one.** This is a hypothesis, not an
established fact — the plan below neither depends on it nor needs it resolved first, and includes a
one-line runtime check that settles it.

Note also that flexlibs 1.2.8 and flexlibs2 2.3.1 are byte-identical in this branch, so the library
version is not the variable.

## Phase 1 — make the module robust (this repo, this change)

### The fix

Replace the `LexiconAddTagToField` call with a writing-system-explicit overwrite:

```python
project.LexiconSetFieldText(entry, flagsField, chao_letters, pitchWS)
```

`LexiconSetFieldText` (line 1060) branches on field type and handles **both** `CellarStringTypes` and
`CellarMultiStringTypes` correctly, and never reads the old value, so it cannot reach the broken
path. **This works whichever type `Pitch` turns out to be** — which is why the hypothesis above does
not need settling first.

### The writing system

`Pitch` is a vernacular-WS field, but `LexiconSetFieldText` defaults to the **default analysis** WS,
which would store text the field never displays — indistinguishable from a no-op. flexlibs has no
helper for a field's own WS (no `GetFieldWs` anywhere in `FLExProject.py`), so pass one explicitly.

Passing a language tag works despite the helper's name: `__WSHandleAnalysis` (line 645) uses
`DefaultAnalWs` only as the fallback when the argument is `None`, otherwise resolving the tag via
`WSHandle()`; an unrecognised tag raises `FP_WritingSystemError`, failing loudly.

```python
# Pitch is a vernacular-WS field, but LexiconSetFieldText defaults to the
# analysis WS, which would store text the field never displays.
PITCH_WS = None    # None = the project's default vernacular WS; or a language tag

pitchWS, pitchWSName = (project.GetDefaultVernacularWS() if PITCH_WS is None
                        else (PITCH_WS, PITCH_WS))
report.Info("Writing Pitch in the %s writing system" % pitchWSName)
```

This matches the read side: `LexiconGetLexemeForm` already defaults to the default vernacular WS, and
[SPEC.md](../SPEC.md) already requires the accent notation to live there.

### The diagnostic that settles the mystery

At startup, report what `Pitch` actually is, using the helpers flexlibs already provides —
`LexiconFieldIsStringType(fieldID)` (documented as reporting whether a field is "suitable for use
with `LexiconAddTagToField()`") and `LexiconFieldIsMultiType(fieldID)`. Two lines, and the next run
tells us definitively which branch the field takes, confirming or killing the hypothesis and warning
the next person off `LexiconAddTagToField`.

### One behaviour question this forces

`LexiconAddTagToField` appended with `"; "` and skipped values already present; `LexiconSetFieldText`
replaces. Overwrite is right for a value derived deterministically from the lexeme form — re-running
becomes idempotent instead of accumulating. This settles the first bullet in
[SPEC.md's Not Yet Specified section](../SPEC.md#not-yet-specified).

**Still open, and the one I'd like confirmed:** with overwrite, an empty conversion result would clear
`Pitch` for entries with no tone marks, wiping anything entered by hand. AGENTS.md's data-safety rule
favours the narrower edit, so I recommend **skipping entries whose result is empty** and reporting the
count. The cost is that removing tone marks from a lexeme form leaves a stale `Pitch` value behind.
This settles the second Not-Yet-Specified bullet either way.

### Also in Phase 1

- Bump `FTM_Version` 0.5 → 0.6.
- Update the **Writes** paragraph and **Prerequisites** of [SPEC.md](../SPEC.md)'s tone section
  (naming the writing system written to), and delete the two Not-Yet-Specified bullets this settles.
- Update the module's README section for the changed write behaviour.
- Leave `Lib/chao_tones.py` untouched — no conversion behaviour changes.

### Housekeeping outside the repo (worth doing, needs your say-so)

`Modules/Tim Module/` contains `old_Extract_Chao_tone_letters_from_accent_notation.py` and
`FixMediaPaths.py`. Both are top-level `.py` files, so FlexTools **imports and executes them at
startup** and registers the old module as a second entry ("Old Extract Chao tone letters…"). Renaming
them with a leading `__`, or deleting them, avoids running two versions side by side while verifying.

### Tests

Follow TDD; red first. `flextoolslib` cannot be imported off Windows, so add the `sys.modules` stub in
`tests/conftest.py` that AGENTS.md already describes, load the module by path, and drive
`MainFunction` with fake `project` / `report` objects — the glue's first-ever coverage:

- `modifyAllowed=False` → no `LexiconSetFieldText` calls at all.
- `modifyAllowed=True` → called with the converted text **and** a writing-system argument.
- Missing `Pitch` → `report.Error`, no writes, conversions still reported.
- Empty conversion result → skipped (per the decision above).
- `LexiconAddTagToField` is never called.

### Verification

1. `python -m pytest` from the repo root — existing tone tests plus the new wrapper tests pass.
2. On Windows, run with changes **disabled**: output unchanged, plus the new writing-system and
   field-type lines. Record what the field-type line says — that is the hypothesis check.
3. Run with changes **enabled** on a backed-up project; confirm `Pitch` visibly holds the tone letters
   in FLEx.
4. Re-run with changes enabled: values replaced, not accumulated with `"; "`.

## Phase 2 — spin off the converters repo (separate change, once Phase 1 is verified)

Sketched so Phase 1 is built in the right direction; not implemented as part of this plan.

Verified against `ModuleManager.LoadAll` and `flextools.log`: the scanner lists `*.py` at the **top
level of each module folder only**, never recursing; **`Lib` is not special-cased**, so any subfolder
name is skipped identically (the shipped `Chinese/` folder has both `Lib/` and `Utilities/`, and the
log lists only its four top-level files); non-`.py` files are ignored; and files starting with `__`
are skipped *before* import, which is how `Examples/__Template.py` ships safely.

So the new repo root can double as the FlexTools module folder:

```
<new-repo>/
  README.md  AGENTS.md  SPEC.md  LICENSE            ← ignored by the scanner
  Extract_Chao_tone_letters_from_accent_notation.py ← the Phase 1 wrapper, moved once proven
  __Template_converter_module.py                    ← minimal template; `__` keeps it un-imported
  converters/chao_tones.py                          ← the product: convert() + CLI
  tests/
```

`Fix_Pronunciation_Media_Paths.py` stays behind: it walks LCM objects, so its value is the traversal,
not a string function. No shared "field-to-field pass" helper — with one converter there is nothing to
generalise from, and the fake-project tests capture the testability win without it.

Open for Phase 2: repo name and location; whether to package with `pyproject.toml`; whether to
preserve git history for `Lib/chao_tones.py` and `tests/`.

## Changes after approval

- **The hypothesis was confirmed on the live project.** Verification on Windows showed
  `Pitch` reporting as a `MultiUnicode`/`MultiString` field — the branch where
  `LexiconAddTagToField` raises — matching the leading hypothesis above.
- **`LexiconFieldIsMultiType` turned out to be broken too**, as a second, independent flexlibs
  defect: it reads `FLExLCM.CellarMultiTypes`, a name `FLExLCM` never defines, so it raises
  `AttributeError` for every field in both flexlibs 1.2.8 and flexlibs2 2.3.1. The diagnostic uses
  `LexiconFieldIsAnyStringType` instead (a field that is a string type but not a `String` is one of
  the multi-string types), and reports whole sentences (`"The Pitch field is a ... field"`) rather
  than a bare type name.
- **The summary line was rewritten** after the first Windows run: naming only the entries left
  unchanged (`Left 1453 entries unchanged`) read as though nothing had converted, even though 8
  entries had. It now reports both counts: `Wrote Pitch for <n> of <total> entries; left <m>
  unchanged (no tone marks found)` (`Would write` / `[DRY RUN] ` prefix when `modifyAllowed` is
  false).
- `FTM_Version` was bumped twice as a result — 0.5 → 0.6 for the write-path fix, then 0.6 → 0.7 for
  the reporting fix — rather than once to 0.6 as originally planned.

### Phase 2 decisions (settled 2026-08-18, at implementation)

- **Repo name and location:** `speechchemistry/flex-string-converters`, public. "FLEx" because the
  audience is FLEx users and the repo root is a FlexTools module folder; "string" because that is
  the discipline the repo enforces, and what keeps `Fix_Pronunciation_Media_Paths.py` out of it.
- **No packaging.** No `pyproject.toml` for now; distribution is copying the checkout.
- **No git history preserved.** A single clean initial commit, rather than a `filter-repo` split.
- **The tone module lives in both repos for now.** `flex-string-converters` is canonical; the copy
  in `flextools_modules` is a mirror, marked as such by a pointer line in its README section and at
  the top of its `SPEC.md` section. Deleting the mirror is a follow-up once the new repo's copy has
  been run in FlexTools.
- **The two copies differ by one line**, not byte-identical as first assumed: the new repo's
  converter folder is `converters/`, so the module's `sys.path` insert names that instead of `Lib/`.
- The new repo also got its own `AGENTS.md` (converter conventions split out from the FlexTools
  module conventions), `CLAUDE.md` pointer, `SPEC.md` (converter specified first, module second),
  `README.md`, and the GPL 3 `LICENSE`. `plans/` was not copied — the record stays here.
