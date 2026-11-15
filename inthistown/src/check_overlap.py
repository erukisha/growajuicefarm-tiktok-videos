"""Clipping check: people inside each other or inside solid props. Runs on the built episode .blend:
  blender -b ep1.blend --python check_overlap.py -- <work> <out.json> [step]
Every `step` frames, each pair of characters closer than 7 units is tested part-by-part (oriented boxes, SAT), and each
character against nearby solid set pieces. Reports runs of frames with overlaps."""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V

argv = sys.argv[sys.argv.index("--") + 1:]
WORK, OUT = argv[0], argv[1]
STEP = int(argv[2]) if len(argv) > 2 else 3
sc = bpy.context.scene
SHRINK = 0.1
ARMS = [o for o in sc.objects if o.type == "ARMATURE" and o.name.startswith("AV_")]
PARTS = {a.name: [c for c in a.children if c.type == "MESH"] for a in ARMS}
SOLID_PREFIX = ("LampPost", "FountainRim", "FountainStem", "Alley_Dumpster", "Alley_Crate", "Alley_Fence", "Park_Bench",
                "PlazaBench", "Bakery_Counter", "TH_Pedestal", "TH_Col", "Barber_Pole", "HouseW", "Bakery_Body", "Barber_Body",
                "Shop3_Body", "TH_Body", "TH_Base")
ALLOW = {("AV_rosa", "Bakery_Counter"), ("AV_mia", "Park_Bench"), ("AV_mom", "Park_Bench")}
SOLIDS = [o for o in sc.objects if o.type == "MESH" and o.name.startswith(SOLID_PREFIX) and "_Roof" not in o.name]


def obb(o, shrink=SHRINK):
    mw = o.matrix_world
    bb = [V(c) for c in o.bound_box]
    lo = V((min(c.x for c in bb), min(c.y for c in bb), min(c.z for c in bb)))
    hi = V((max(c.x for c in bb), max(c.y for c in bb), max(c.z for c in bb)))
    c = mw @ ((lo + hi) / 2)
    m3 = mw.to_3x3()
    axes, half = [], []
    for i in range(3):
        col = V((m3[0][i], m3[1][i], m3[2][i]))
        L = col.length
        axes.append(np.array(col / max(L, 1e-9)))
        half.append(max(0.0, (hi[i] - lo[i]) / 2 * L - shrink))
    return np.array(c), np.array(axes), np.array(half)


def sat(A, B):
    ca, Aa, ha = A
    cb, Ab, hb = B
    if min(ha) <= 0 or min(hb) <= 0:
        return False
    d = cb - ca
    tests = list(Aa) + list(Ab) + [np.cross(a, b) for a in Aa for b in Ab]
    for ax in tests:
        n = np.linalg.norm(ax)
        if n < 1e-6:
            continue
        ax = ax / n
        ra = sum(h * abs(np.dot(a, ax)) for a, h in zip(Aa, ha))
        rb = sum(h * abs(np.dot(b, ax)) for b, h in zip(Ab, hb))
        if abs(np.dot(d, ax)) > ra + rb:
            return False
    return True


hits = {}
FPS = sc.render.fps
for f in range(sc.frame_start, sc.frame_end + 1, STEP):
    sc.frame_set(f)
    live = [a for a in ARMS if abs(a.matrix_world.translation.x) < 250 and a.matrix_world.to_scale().x > 0.05]
    boxes = {a.name: [(p.name, obb(p)) for p in PARTS[a.name]] for a in live}
    for i in range(len(live)):
        a = live[i]
        pa = a.matrix_world.translation
        for j in range(i + 1, len(live)):
            b = live[j]
            if (b.matrix_world.translation - pa).length > 7:
                continue
            bad = next(((x, y) for x, A in boxes[a.name] for y, B in boxes[b.name] if sat(A, B)), None)
            if bad:
                hits.setdefault("%s|%s" % (a.name, b.name), []).append([f, bad[0], bad[1]])
        for s in SOLIDS:
            if (a.name, next((p for p in SOLID_PREFIX if s.name.startswith(p)), "")) in ALLOW:
                continue
            if (s.matrix_world.translation - pa).length > 14:
                continue
            S = obb(s, 0.02)
            bad = next((x for x, A in boxes[a.name] if sat(A, S)), None)
            if bad:
                hits.setdefault("%s|%s" % (a.name, s.name), []).append([f, bad, s.name])
# compress into runs
rep = []
for k, fr in hits.items():
    fr.sort()
    run = [fr[0]]
    for x in fr[1:]:
        if x[0] - run[-1][0] <= STEP:
            run.append(x)
        else:
            rep.append({"pair": k, "t0": round((run[0][0] - 1) / FPS, 2), "t1": round((run[-1][0] - 1) / FPS, 2), "parts": run[0][1:]})
            run = [x]
    rep.append({"pair": k, "t0": round((run[0][0] - 1) / FPS, 2), "t1": round((run[-1][0] - 1) / FPS, 2), "parts": run[0][1:]})
rep.sort(key=lambda r: r["t0"])
json.dump(rep, open(OUT, "w"), indent=0)
print("OVERLAP RUNS", len(rep))
