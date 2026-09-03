# -*- coding: utf-8 -*-
"""Probe: inspect write_grid_visualization kwargs."""
import inspect
from visualization.grid import write_grid_visualization
src = inspect.getsource(write_grid_visualization)
print(src)
