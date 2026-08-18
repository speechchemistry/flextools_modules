# -*- coding: utf-8 -*-
#
#   Shared test setup
#
#   Puts Lib/ on sys.path so the shared helpers can be imported by name
#   (import chao_tones) when pytest is run from the repo root.
#

import sys
from pathlib import Path

LIB_PATH = Path(__file__).resolve().parent.parent / "Lib"
sys.path.insert(0, str(LIB_PATH))
