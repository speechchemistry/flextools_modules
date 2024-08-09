# flextools_modules
Modules written for [FlexTools](https://github.com/cdfarrow/flextools) to process SIL FieldWorks Language Explorer (FLEx) files. This modules are in development, please ensure that you backup your FLEx file before using them. 

## Extract Chao tone letters from accent notation and put in Pitch field

`Extract_Chao_tone_letters_from_accent_notation.py`

Goes through all the lexeme forms and extracts Chao tone letters (only) 
from any accent notation and puts it into a Custom Pitch field. You can use
Bulk Edit Entries in Flex to move these to the desired field. 

This FlexTool module requires that you set the source lexeme field writing system as the default vernacular language. To do this in Flex use the menu item Format > Set up vernacular writing systems... then ensure that the writing system in the top right is the desired one (using the up and down arrow buttons). It also requires that you create an
 entry level custom field called "Pitch" (Tools > Configure > Custom Fields...)

 The module should also work as a Flex Process once Flex allows Python 3 processes (at the time of writing it only allows Python 2 processes but the developers are working on upgrading this).
