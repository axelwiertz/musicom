#!/usr/bin/env python3
import importlib
for name in ["numpy", "scipy"]:
    try:
        m = importlib.import_module(name)
        print(name, getattr(m, "__version__", "?"))
    except Exception as e:
        print(name, "MISSING:", e)
