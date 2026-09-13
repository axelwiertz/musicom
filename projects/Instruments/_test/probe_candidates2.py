# -*- coding: utf-8 -*-
"""Probe pipeline GM_PROGRAMS labels for candidate instruments."""
import inspect
import re
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("count", len(labels))
for i in [6, 45, 46, 47, 48]:
    print(i, repr(labels[i]))
