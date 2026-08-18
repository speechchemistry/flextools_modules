# SPEC.md

The source of truth for what each module in this repository does and guarantees: the FLEx fields it reads and writes, its match and transform rules, and its prerequisites. See [AGENTS.md's Specification section](AGENTS.md#specification) for how this file and `AGENTS.md` divide up.

This file records only behaviour that is implemented today. Anything else belongs under [Not Yet Specified](#not-yet-specified).

## Fix Pronunciation Media Paths

Module: `Fix_Pronunciation_Media_Paths.py`. `FTM_ModifiesDB` is true.

**Reads.** Every entry from `LexiconAllEntries()`, then each `entry.PronunciationsOS` → `pron.MediaFilesOS` → `media.MediaFileRA` → `file_obj.InternalPath`. A media object with no `MediaFileRA`, or whose `InternalPath` is missing or empty, is skipped and not counted.

**Match rule.** An `InternalPath` that starts with the exact prefix `Media\`. The comparison is case-sensitive, and the prefix must be at the start of the path.

**Transform.** The first occurrence of `Media\` is replaced with `AudioVisual\`; the rest of the path is left untouched. Nothing else about the media object or the entry changes.

**Writes.** `file_obj.InternalPath`, and only when `modifyAllowed` is true.

**Reporting.** One `report.Info` line per matched path (`Changed <old> to <new>`), prefixed with `[DRY RUN] ` when `modifyAllowed` is false, followed by a final `Scanned <n> media files, changed <m>` summary. `n` counts media files that had a non-empty `InternalPath`; `m` counts those that matched the prefix.

**Prerequisites.** None beyond an open FLEx project.

## Extract Chao Tone Letters From Accent Notation

Module: `Extract_Chao_tone_letters_from_accent_notation.py`, with the conversion itself in `Lib/chao_tones.py`. `FTM_ModifiesDB` is true.

The canonical copy of this module, its converter and this specification now live in [flex-string-converters](https://github.com/speechchemistry/flex-string-converters) (where the converter is `converters/chao_tones.py`). What follows is a mirror kept during the move: change it there, not here.

**Reads.** The lexeme form of every entry, via `LexiconGetLexemeForm(entry)`. The lexeme form is read in the project's default vernacular writing system, so that writing system must be the one holding the accent notation.

**Transform.** Applied by `convert()` in `Lib/chao_tones.py`, which the module imports. It takes and returns a plain string and needs no FLEx project, so the same rules hold whether it is called from FlexTools, from the command line, or as a FLEx Process:

1. The input is normalised to NFD, so accents are separate combining code points.
2. Each recognised combining accent is replaced by its Chao tone letters:

   | Code point | Example | Output |
   | --- | --- | --- |
   | `U+030B` | ő | `˥` |
   | `U+0301` | ó | `˦` |
   | `U+0304` | ō | `˧` |
   | `U+0300` | ò | `˨` |
   | `U+030F` | ȍ | `˩` |
   | `U+030C` | ǒ | `˨˦` |
   | `U+0302` | ô | `˦˨` |
   | `U+1DC4` | o᷄ | `˧˦` |
   | `U+1DC5` | o᷅ | `˨˧` |
   | `U+1DC8` | o᷈ | `˨˦˨` |
   | `U+1DC6` | o᷆ | `˧˨` |
   | `U+1DC7` | o᷇ | `˦˧` |
   | `U+1DC9` | o᷉ | `˦˨˦` |

   The contour values for `U+030C`, `U+0302`, `U+1DC4`, `U+1DC5` and `U+1DC8` are deliberately more internally consistent than the IPA chart's.
3. Every run of characters that is neither whitespace nor a tone letter collapses to a single space.
4. Any three-space run collapses to two spaces, so a word gap stays wider than a within-word gap.
5. Leading and trailing whitespace is stripped.

Substitutions in step 2 are simultaneous, not sequential, so an output tone letter is never re-matched as input. Example: `[nə̀jɛ᷅t]` → `˨ ˨˧`.

**Writes.** The entry-level custom field named `Pitch`, via `LexiconSetFieldText(entry, flagsField, chao_letters, ws)`, and only when `modifyAllowed` is true.

- The value **replaces** whatever the field held, so running the module twice over the same entries leaves the same result as running it once.
- Entries whose converted result is the empty string are **left untouched**, so a `Pitch` value entered by hand is never cleared by a lexeme form that carries no tone marks. The consequence is that removing the tone marks from a lexeme form leaves the previous `Pitch` value in place.
- `ws` is the project's default vernacular writing system — the same one the lexeme form is read from — unless the module's `PITCH_WS` constant names another. It is always passed explicitly, because `LexiconSetFieldText` otherwise defaults to the default *analysis* writing system, which would store text that a vernacular field never displays.
- `LexiconAddTagToField` is deliberately not used: it reads the field back without a writing system, which raises `AttributeError` on a multi-string custom field.

**Reporting.** The type of the `Pitch` field and the writing system being written to (that line prefixed with `[DRY RUN] ` when `modifyAllowed` is false), then an entry count, then a progress bar over all entries (`report.ProgressStart` / `report.ProgressUpdate`), then one `report.Info` line per entry showing `<lexeme form> -> <tone letters>`, then a final `Wrote Pitch for <n> of <total> entries; left <m> unchanged (no tone marks found)` summary (`Would write` and the `[DRY RUN] ` prefix when `modifyAllowed` is false).

The `Pitch` field's type is reported using `LexiconFieldIsStringType` and `LexiconFieldIsAnyStringType`. `LexiconFieldIsMultiType` is deliberately not used: in flexlibs 1.2.8 and flexlibs2 2.3.1 it reads `FLExLCM.CellarMultiTypes`, a name `FLExLCM` never defines, so it raises `AttributeError` for every field.

**Prerequisites.**

- An entry-level custom field called `Pitch` must exist (Tools > Configure > Custom Fields…). If it is missing and `modifyAllowed` is true, the module reports `The entry-level Pitch field is missing` via `report.Error` and continues in read-only mode: it still reports every conversion but writes nothing.
- The writing system holding the source lexeme form must be the project's default vernacular writing system (Format > Set up vernacular writing systems…).
- The `Pitch` field must show that same writing system, since that is the alternative the module writes. A `Pitch` field configured for the analysis writing system will not display what is written unless `PITCH_WS` is changed to match.

**Downstream.** Values land in `Pitch` so they can be moved to the desired field with Bulk Edit Entries in FLEx.

**Command line.** `Lib/chao_tones.py` is also runnable directly. Text given as arguments is converted one result per line, in the order given. With no arguments it reads standard input line by line and writes one converted line per input line, so it works as a filter in a pipeline. Results go to stdout and diagnostics to stderr; stdin and stdout are both read and written as UTF-8 regardless of the console's own encoding. The conversion applied is the same `convert()` documented above.

## Not Yet Specified

Behaviours that are not pinned down yet. Add to the sections above as each is settled or implemented, rather than speculating here.

- Behaviour when an entry has no lexeme form in the default vernacular writing system.
- Reading a source form from a writing system other than the default vernacular.
- Case-insensitive or non-initial matching of the `Media\` prefix, and any other media path prefixes worth rewriting.
