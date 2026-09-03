# -*- coding: utf-8 -*-
"""Probe: render via produce() adapter for both phase MIDIs (SP-001).

Creates a scratch project-less test to confirm produce() writes Audio/ under
project dir, returns ProduceResult, and stats. Will be reused by render script.
"""
import os, sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from workflows.musicom_workflow import produce
import inspect
print(inspect.signature(produce))
print([m for m in dir(produce.__globals__.get("ProduceResult", object)) if not m.startswith("_")] if hasattr(produce, "__globals__") else "n/a")
import workflows.musicom_workflow as wf
print("ProduceResult fields:", [f for f in dir(wf.ProduceResult) if not f.startswith("_")])
