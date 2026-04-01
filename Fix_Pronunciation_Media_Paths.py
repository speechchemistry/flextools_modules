# -*- coding: utf-8 -*-
#
#   Fix Pronunciation Media Paths
#
#   Converts 'Media\\' prefix to 'AudioVisual\\' in pronunciation media file paths.
#
#   Tim Kempton
#   March 2026
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Fix Pronunciation Media Paths",
        FTM_Version    : 0.2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Converts 'Media' prefix to 'AudioVisual' in pronunciation media file paths",
        FTM_Help       : None,
        FTM_Description: 
"""
Finds any pronunciation media file paths that start with 'Media' and changes
them to start with 'AudioVisual'.
""" }


#----------------------------------------------------------------
# The main processing function

# This code was primarily produced by FlexToolsMCP

def MainFunction(project, report, modifyAllowed):
    """
    Main entry point for the FlexTools module.

    Args:
        project: FLExProject instance providing access to the FieldWorks database
        report: Reporter object for logging (report.Info, report.Warning, report.Error)
        modifyAllowed: Boolean indicating if database modifications are permitted
    """
    count = 0
    changed = 0
    for entry in project.LexiconAllEntries():
        for pron in entry.PronunciationsOS:
            for media in pron.MediaFilesOS:
                file_obj = getattr(media, "MediaFileRA", None)
                if file_obj is None:
                    continue
                path = getattr(file_obj, "InternalPath", None)
                if not path:
                    continue
                if path.startswith("Media\\"):
                    new_path = path.replace("Media\\", "AudioVisual\\", 1)
                    if modifyAllowed:
                        file_obj.InternalPath = new_path
                    report.Info(f"{'[DRY RUN] ' if not modifyAllowed else ''}Changed {path} to {new_path}")
                    changed += 1
                count += 1
    report.Info(f"Scanned {count} media files, changed {changed}")

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction, docs = docs)