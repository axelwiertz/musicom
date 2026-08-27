import os, glob
cands = glob.glob("/opt/data/micromamba/envs/musicom/**/*TimGM6mb.sf2", recursive=True)
print("micromamba:", cands)
cands2 = glob.glob("/opt/data/micromamba/envs/musicom/**/*.sf2", recursive=True)
print("all sf2:", cands2[:20])
# check env PATH fluidsynth
for p in ("/opt/data/micromamba/envs/musicom/bin/fluidsynth",):
    print(p, "->", os.path.exists(p))