# -*- coding: utf-8 -*-
"""List implemented SP methods from the canonical registry."""
import json
from workflows.musicom_workflow import SP_METHODS

print(json.dumps({k: v for k, v in SP_METHODS.items()}, indent=1, default=str))
