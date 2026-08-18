# Reuse the Chao tone conversion outside FlexTools

Status: approved 2026-08-18, not yet implemented.

## Context

`convert()` in [Extract_Chao_tone_letters_from_accent_notation.py](../Extract_Chao_tone_letters_from_accent_notation.py)
is pure string→string logic needing no FLEx project, but it sits in a file whose first import is
`from flextoolslib import *`, which only installs on Windows alongside FieldWorks. So the conversion
can't be used from a command line, a script, or a test on any other platform. The goal is one shared
source of truth for the conversion, usable from FlexTools, from the command line over stdin, and as a
FLEx Process, with no duplicated substitution table.

### FlexTools supports a shared library file — verified, not assumed

Checked against the installed `flextoolslib` 2024.7.9
(`…\Python312\Lib\site-packages\flextoolslib\code\FTModules.py`) and the FlexTools 2.3.1 tree:

- `ModuleManager.LoadAll` scans **one level deep only** — top-level subfolders of `Modules` plus the
  `Modules` root. A `.py` inside a `Lib/` subfolder is never imported as a module. `flextools.log`
  proves it: `From library 'Path Test': []`, because that folder's only `.py` is in `Path Test/Lib/`.
- Modules are imported with `importlib.util.spec_from_file_location(...)`, so `__file__` is set and a
  `sys.path` bootstrap from inside the module works.
- `FTModules.py` calls `site.addsitedir(MODULES_PATH)`, so `.pth` files in `Modules` are honoured —
  how the bundled Chinese modules do it (`chinese.pth` → `Chinese/Lib/`, then
  `from ChineseUtilities import …`).
- `Modules\readme.md` documents the pattern: library files go in a sub-folder referenced by a `.pth`.

This plan uses the `Lib/` layout but bootstraps `sys.path` from `__file__` rather than a `.pth`,
because the `.pth` must sit in the `Modules` root — outside the folder a user copies from this repo.
Bootstrapping keeps the repo self-installing.

## Convention change this plan makes deliberately

[AGENTS.md](../AGENTS.md) rules this out in three places, and amending it is part of this change, per
its own rule that documentation is updated in the same change rather than left to drift:

- *"Each module is a single self-contained `.py` file at the repo root"* — still true of modules;
  shared pure logic gains an exception.
- *"Stub it in `tests/conftest.py` … without splitting helpers out of the single-file module"* — that
  rationale disappears for `convert()`, which tests can now import directly.
- *"they are not command-line scripts. The conventions below replace the usual CLI stdout/stderr
  rules"* — no longer true once `Lib/chao_tones.py` has a CLI.

None of the three is a considered prohibition. They were written descriptively —
[create-agents-md.md](create-agents-md.md) states that every bullet in that section is "observable in
the two existing modules", and both happened to be single files. The `conftest.py` bullet was added
after approval, when the only goal was running tests off Windows, which stubbing solves without
splitting; CLI reuse, which stubbing cannot solve, was not in view.

The alternative — keeping one file and guarding `from flextoolslib import *` in a `try`/`except` —
was considered and rejected: the `docs` dict and `FlexToolsModule` are built from `flextoolslib`
names, so they would have to be created conditionally, and a swallowed `ImportError` on Windows would
make the module silently vanish from the FlexTools list instead of failing loudly.

### Exact AGENTS.md edits

- **FlexTools Module Conventions preamble** — after "they are not command-line scripts", add: *except
  for shared helpers under `Lib/`, which are usable from the command line and follow the CLI Script
  Conventions below.*
- **Single-file bullet** — keep as is, and append: *Pure logic that is also used outside FlexTools (a
  command-line tool, a FLEx Process) may live in a shared file under `Lib/`, imported by the module
  after adding that folder to `sys.path` from `__file__`. Keep it in `Lib/` rather than beside the
  module: FlexTools scans each module folder one level deep, so a sibling `.py` would be imported and
  warned about as a failed module.*
- **Pure-logic bullet** — repoint the example to `convert()` in `Lib/chao_tones.py`, imported by
  `Extract_Chao_tone_letters_from_accent_notation.py`.
- **Testing stub bullet** — replace the "without splitting helpers out of the single-file module"
  rationale with: *Test shared `Lib/` helpers by importing them directly, since they have no
  `flextoolslib` import. Where a test must import a module file itself, stub `flextoolslib` in
  `tests/conftest.py` (insert a stub into `sys.modules`, then load the module by path) so tests still
  run on any platform.*
- **New `## CLI Script Conventions` section** — the sibling repos' two bullets verbatim (result
  content only to stdout; progress, diagnostics and errors to stderr), placed before
  `## Testing Approach` to match their ordering.

## Deliverables

```
flextools_modules/
  Extract_Chao_tone_letters_from_accent_notation.py   # edited: imports the helper
  Lib/chao_tones.py                                   # new: shared logic + CLI
  tests/conftest.py                                   # new: puts Lib/ on sys.path
  tests/test_chao_tones.py                            # new
  AGENTS.md  SPEC.md  README.md                       # edited
  plans/reuse-conversion-outside-flextools.md         # new: this plan
```

**Every file this plan changes is inside this repo.** Nothing is written to the FlexTools
installation or anywhere else on the C drive — the C drive was read during planning only, to confirm
the `Lib/` layout works. Deploying to `Modules\Tim Module\` stays a manual step done on Windows
(`Lib/` must be copied along with the module file).

## Shared module: Lib/chao_tones.py

- Move `multisub` and `convert` **verbatim** — same table, same steps, same behaviour, so
  [SPEC.md](../SPEC.md)'s transform rules stay true unchanged. Keep the Darius Bacon CC-BY-SA
  attribution comment with the function it belongs to.
- Keep the name `convert` so the file still works as a FLEx Process — and it is now a better Process
  file, having no `flextoolslib` import.
- Header comment block in the repo's house style (title, one-line purpose, author, month and year),
  with the platform line adapted: this file is plain Python 3, not a FlexTools module.
- CLI following the sibling repo's shape (`saymore_eaf_to_saymore_tsv.py` in
  `audio_label_file_conversions`): `argparse`, a `main()`, `if __name__ == '__main__':`.
  - Words given as arguments are converted one per line; with no arguments it reads stdin line by
    line and writes one converted line per input line, so it pipes.
  - Results to stdout, diagnostics to stderr, per the sibling repos' CLI rule.
  - Force UTF-8 on stdin/stdout (`reconfigure(encoding="utf-8")`) so the IPA and Chao output survives
    a Windows console code page.
- Keep the `regex` import for byte-identical behaviour. All four patterns would work under the stdlib
  `re`, which would drop the only third-party dependency for CLI users — worth doing as a separate
  change once the tests exist, not while moving code.

## FlexTools module changes

- Remove `multisub`, `convert`, and the now-unused `re` / `unicodedata` / `regex` imports.
- After `from flextoolslib import *`, add the bootstrap, with a brief comment explaining why (`Lib/`
  is not on `sys.path`; FlexTools imports this file by path):

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib"))
from chao_tones import convert
```

- `MainFunction` is untouched — it already only calls `convert(...)`.
- Bump `FTM_Version` 0.4 → 0.5: FLEx-visible behaviour is unchanged, but what a user must copy to
  install it is not.

## Tests

Per [AGENTS.md's Testing Approach](../AGENTS.md#testing-approach): `pytest`, under `tests/`, run as
`python -m pytest` from the repo root. TDD — write these first and watch them fail against the
not-yet-existing `Lib/chao_tones.py`.

- `tests/conftest.py`: insert `Lib/` into `sys.path` so `import chao_tones` resolves from the repo
  root. No `flextoolslib` stub is needed, since no test imports the module file.
- `tests/test_chao_tones.py`: small parametrized assertions while outputs are short strings —
  - the SPEC/README example `nə̀jɛ᷅t` → `˨ ˨˧`
  - one case per row of
    [SPEC.md's accent table](../SPEC.md#extract-chao-tone-letters-from-accent-notation), so the
    mapping can't silently drift
  - precomposed (NFC) input gives the same result as decomposed (NFD)
  - multi-word input: two spaces between words, none leading or trailing
  - text with no tone marks, and empty input, both → `""`
  - tone letters already present in the input are preserved

## SPEC.md

Under [Extract Chao Tone Letters From Accent Notation](../SPEC.md#extract-chao-tone-letters-from-accent-notation):

- Note that `convert()` now lives in `Lib/chao_tones.py` and is imported by the module; the transform
  rules themselves are unchanged.
- Add a short **Command line** paragraph giving the contract: arguments converted one per line,
  otherwise stdin read line by line with one output line per input line; results on stdout,
  diagnostics on stderr; UTF-8 in and out.

## README.md

- Note that the module now needs `Lib/` copied alongside it into the FlexTools module folder.
- Add a short "Command line use" section with the piping example.
- Point the FLEx Process note at `Lib/chao_tones.py`.
- Attributions line still covers the Farrow (LGPL 2.1) and Bacon (CC-BY-SA) code, now split across
  two files — say which file holds which.

## Verification

- `python -m pytest` from the repo root: all pass. Confirm they failed first (TDD red).
- `echo 'nə̀jɛ᷅t' | python3 Lib/chao_tones.py` → `˨ ˨˧`, matching SPEC.md's example.
- `python3 Lib/chao_tones.py 'nə̀jɛ᷅t' 'ǒlō'` → one line per argument;
  `printf 'nə̀jɛ᷅t\nǒlō\n' | python3 Lib/chao_tones.py` → two lines, order preserved.
- Refactor is behaviour-preserving: run the `convert` from `git show HEAD:…` and the new one over the
  same word list and diff — expect zero differences.
- FlexTools on Windows — **manual, done by Tim**, the only step touching anything outside the repo:
  copy the module plus `Lib/` into `Modules\Tim Module\`, run it with modification disabled first,
  confirm it appears in the list and reports as before. Check `flextools.log` has no
  `FlexToolsModule not found` warning for `chao_tones.py` — it is in `Lib/`, so it should not be
  scanned at all.
- `grep -nE '^#+ +[0-9]+\.' AGENTS.md SPEC.md README.md plans/*.md` returns nothing (no numbered
  headings).
- Cross-check AGENTS.md against the code: every amended bullet must describe what the repo now
  actually does.
