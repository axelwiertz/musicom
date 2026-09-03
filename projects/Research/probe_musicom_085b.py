# -*- coding: utf-8 -*-
"""Probe: musicom_workflow.produce + discover_soundfont + provenance details."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from workflows.musicom_workflow import produce
import inspect
src = inspect.getsource(produce)
print(src)
