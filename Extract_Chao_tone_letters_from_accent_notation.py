# -*- coding: utf-8 -*-
#
#   Extract Chao tone letters from accent notation
#
#   Goes through all the lexeme forms and extracts Chao tone letters (only) 
#   from any accent notation and puts it into a Custom Pitch field 
#
#   Tim Kempton
#   August 2024
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *
import re
import unicodedata
import regex

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Extract Chao tone letters from accent notation and put in pitch field",
        FTM_Version    : 0.4,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Extracts Chao tone letters (only) from any accent notation",
        FTM_Help       : None,
        FTM_Description: 
"""
Goes through all the lexeme forms and extracts Chao tone letters (only) 
from any accent notation and puts it into a Custom Pitch field. You can use
Bulk Edit Entries in Flex to move these to the desired field
""" }


#----------------------------------------------------------------
# The main processing function

# contains code fragments by C D Farrow 

def MainFunction(project, report, modifyAllowed):
    """
    This is the main processing function.
    
    """
    AddReportToField = modifyAllowed
    flagsField = project.LexiconGetEntryCustomFieldNamed("Pitch")
    if AddReportToField and not flagsField:
        report.Error("The entry-level Pitch field is missing")
        AddReportToField = False

    report.Info("Lexicon contains:")
    numberEntries = project.LexiconNumberOfEntries()
    report.Info("    %d entries" % numberEntries)
    report.ProgressStart(numberEntries)

    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)
        lexeme_form_itsstring = project.LexiconGetLexemeForm(entry)
        chao_letters = convert(lexeme_form_itsstring)
        report.Info(lexeme_form_itsstring + " -> " + chao_letters)
        if AddReportToField:
            project.LexiconAddTagToField(entry,flagsField,chao_letters)
    


# The following find and replace function is by Darius Bacon
# from: https://stackoverflow.com/a/765835 CC-BY-SA
def multisub(subs, subject):
    "Simultaneously perform all substitutions on the subject string."
    pattern = '|'.join('(%s)' % re.escape(p) for p, s in subs)
    substs = [s for p, s in subs]
    replace = lambda m: substs[m.lastindex - 1]
    return re.sub(pattern, replace, subject)

def convert(input_string): # function is named "convert" so it can be used as an SIL Flex Process
    # ensure string is decomposed into separate code points
    input_decomposed = unicodedata.normalize('NFD',input_string)
    # replace all possible accents with chao tone letters
    chao_in_text = multisub([('\u030B','˥'), # ő
                       ('\u0301','˦'), # ó
                       ('\u0304','˧'), # ō
                       ('\u0300','˨'), # ò
                       ('\u030F','˩'), # ȍ
                       ('\u030C','˨˦'), # ǒ trying to be more consistent than IPA chart
                       ('\u0302','˦˨'), # ô trying to be more consistent than IPA chart
                       ('\u1DC4','˧˦'), # o᷄ trying to be more consistent than IPA chart
                       ('\u1DC5','˨˧'), # o᷅ trying to be more consistent than IPA chart
                       ('\u1DC8','˨˦˨'), # o᷈ trying to be more consistent than IPA chart
                       ('\u1DC6','˧˨'), # o᷆
                       ('\u1DC7','˦˧'), # o᷇
                       ('\u1DC9','˦˨˦')], # o᷉
                       input_decomposed)
    # find any run of items that aren't a space or tone letter and replace it with a space
    # the six characters in the first part were suggested by ChatGPT
    chao_in_spaces = regex.sub(r'[^\s˥˦˧˨˩]+',' ',chao_in_text)
    # convert any three space runs between words to two space runs
    # (three spaces occur after any codas and before another word)
    chao_two_space_gaps = regex.sub(r'   ','  ',chao_in_spaces)
    # then just remove any initial whitespace
    no_leading_spaces = regex.sub(r'^\s+','',chao_two_space_gaps)
    # remove any leading whitespace
    output = regex.sub(r'\s+$','',no_leading_spaces)
    return output

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
