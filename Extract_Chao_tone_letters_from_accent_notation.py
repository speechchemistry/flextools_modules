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

# FlexTools imports this file by path, which doesn't put its folder on
# sys.path, so point Python at Lib/ before importing the shared conversion
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib"))
from chao_tones import convert

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Extract Chao tone letters from accent notation and put in pitch field",
        FTM_Version    : 0.5,
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

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
