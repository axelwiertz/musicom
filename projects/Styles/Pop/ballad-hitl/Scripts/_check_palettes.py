import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl/Scripts")
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import by_name
from phase1_compose import build_ballad, VariantSpec, PALETTES, PALETTE_ORDER, REGISTER

ok = True
for name in PALETTE_ORDER:
    pal = PALETTES[name]
    c = build_ballad(seed=7, variant=VariantSpec(palette=pal))
    valid, msg = c.validate()
    if not valid:
        print(f"{name}: VALIDATE FAIL {msg}")
        ok = False
        continue
    print(f"== palette {name}")
    for v in c.voices:
        row = v["row"]
        lo, hi, n = 999, 0, 0
        for col in range(len(c.sections)):
            u = c.matrix.get_unit((row, col))
            if u is None:
                continue
            for p in u.pitches:
                if p > 0:
                    lo, hi, n = min(lo, p), max(hi, p), n + 1
        inst = None
        for role, iname in pal.items():
            if role == v["name"]:
                inst = by_name(iname)
        flag = ""
        if inst and inst.range_min is not None:
            if lo < inst.range_min or hi > inst.range_max:
                flag = f"  <-- OUT OF RANGE ({inst.range_min}-{inst.range_max})"
                ok = False
        print(f"   {v['name']:6s} {pal[v['name']]:20s} prog={v['program']:3d} "
              f"ch={v['channel']} n={n:4d} range={lo}-{hi}{flag}")
print("\nALL IN RANGE" if ok else "\nRANGE PROBLEMS FOUND")
