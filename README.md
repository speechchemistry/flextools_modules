# flextools_modules
Modules written for [FlexTools](https://github.com/cdfarrow/flextools) to process SIL FieldWorks Language Explorer (FLEx) files. These modules are in development, please ensure that you backup your FLEx file before using them. 

`Fix_Pronunciation_Media_Paths.py`

Finds any pronunciation media file paths that start with 'Media' and changes them to start with 'AudioVisual'. This module was written using [FlexToolsMCP](https://github.com/MattGyverLee/FlexToolsMCP).

`Extract_Chao_tone_letters_from_accent_notation.py`

The canonical copy of this module now lives in [flex-string-converters](https://github.com/speechchemistry/flex-string-converters), alongside the converter it calls. The copy here is a mirror kept during the move; change it there, not here.

Goes through all the lexeme forms and extracts Chao tone letters (only) 
from any accent notation and puts it into a Custom Pitch field. For example [nə̀jɛ᷅t] -> [˨ ˨˧]. You can use
Bulk Edit Entries in Flex to move these to the desired field. 

Running it again replaces the Pitch value rather than adding to it, so a second run over the same entries leaves the same result as the first. Entries whose lexeme form has no tone marks are left alone, so a Pitch value you typed in yourself is never cleared.

This FlexTool module requires that you set the source lexeme field writing system as the default vernacular language. To do this in Flex use the menu item Format > Set up vernacular writing systems... then ensure that the writing system in the top right is the desired one (using the up and down arrow buttons). It also requires that you create an
 entry level custom field called "Pitch" (Tools > Configure > Custom Fields...)

The Pitch field should show that same default vernacular writing system, because that is the one the module writes to. Each run reports which writing system it used and what type the Pitch field is, so you can check. If your Pitch field uses a different writing system, set the `PITCH_WS` constant near the top of the module to its language tag.

The conversion itself lives in `Lib/chao_tones.py`, so copy the `Lib` folder into your FlexTools Modules folder alongside `Extract_Chao_tone_letters_from_accent_notation.py`, keeping the same structure. FlexTools only looks one folder deep for modules, so nothing in `Lib` is mistaken for a module of its own.

 `Lib/chao_tones.py` should also work as a Flex Process once Flex allows Python 3 processes (at the time of writing it only allows Python 2 processes but the developers are working on upgrading this).

## Command line use

`Lib/chao_tones.py` can be run on its own, so the same conversion is available outside FlexTools. It converts any text given as arguments, and otherwise reads lines from standard input:

```
$ echo 'nə̀jɛ᷅t' | python3 Lib/chao_tones.py
˨ ˨˧

$ python3 Lib/chao_tones.py 'nə̀jɛ᷅t' 'ǒlō'
˨ ˨˧
˨˦ ˧
```

It needs Python 3 and the `regex` package (`pip install regex`); `flextoolslib` and FieldWorks are not required.

Attributions: This module includes code from C D Farrows (licensed under LGPL 2.1) in `Extract_Chao_tone_letters_from_accent_notation.py` and Darius Bacon (licensed under CC-BY-SA) in `Lib/chao_tones.py`. Combining these licences results in a GPL 3 licence. Please see the source code for more attribution information.
