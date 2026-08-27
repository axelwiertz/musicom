import importlib
for mod in ['midiutil', 'mido', 'struct']:
    try:
        importlib.import_module(mod)
        print(f"{mod}: available")
    except ImportError:
        print(f"{mod}: NOT available")