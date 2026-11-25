import sys
mods = {}
for m in ['numpy', 'scipy', 'soundfile']:
    try:
        mod = __import__(m)
        mods[m] = getattr(mod, '__version__', 'ok')
    except Exception as e:
        mods[m] = 'MISSING: %s' % e
print(mods)
print(sys.version)
