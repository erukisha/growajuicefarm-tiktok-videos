"""In this town — Episode 1 (v3, told by Vince). Runs on town.blend:
  blender -b town.blend --python ep1b.py -- <work> [stills <out> <f1,f2,..> [pct]]"""
import bpy, sys, os, math, json
WORK = sys.argv[sys.argv.index("--") + 1]
exec(open(os.path.join(WORK, "townlib.py")).read())
TL = json.load(open(os.path.join(WORK, "ep1b_timeline.json")))
LINES = TL["lines"]
warp_setup(TL)
glare_on()
PI = math.pi
fa = face_angle
OFF = {}


def off(lab):
    if lab not in OFF:
        OFF[lab] = (400 + 7 * len(OFF), 400)
    return OFF[lab]


CAST = ["vince", "mia", "mom", "rosa", "sheriff", "mayor", "oldman", "dan", "bob", "noob", "jen", "kai", "lena", "tom", "ana"]
N = {lab: NPC(lab, at=off(lab)) for lab in CAST}
for n in N.values():
    n.path = [(0, off(n.label), "hold")]
    n.yaw = [(0, 0.0, "hold")]
    n.poses = [(0, "idle", "smooth")]
    n.zoff = None


def put(lab, t, xy, yaw=None, look=None):
    """Teleport (hold) to xy at t, facing yaw or toward look."""
    n = N[lab]
    n.path.append((t, xy, "hold"))
    if look is not None:
        yaw = fa(xy, look)
    if yaw is not None:
        n.yaw.append((t, yaw, "hold"))


def walk(lab, keys, ease="linear", turn=0.25):
    """keys [(t, (x, y))]: walk through them, facing the way he goes (quick turns)."""
    n = N[lab]
    for i, (t, xy) in enumerate(keys):
        if i == 0:
            n.path.append((t, xy, "hold"))
            continue
        t0, p0 = keys[i - 1]
        n.path.append((t, xy, ease))
        y = fa(p0, xy)
        n.yaw.append((t0, n.yaw[-1][1] if n.yaw else y, "hold"))
        n.yaw.append((min(t, t0 + turn), y, "smooth"))


def turn(lab, t, look, dur=0.35):
    n = N[lab]
    cur = Curve(n.yaw)(t) if n.yaw else 0.0
    n.yaw.append((t, cur, "hold"))
    n.yaw.append((t + dur, fa(n.pos(t), look), "smooth"))


def pose(lab, t, p, e="smooth"):
    N[lab].poses.append((t, p, e))


def face(lab, t, f):
    N[lab].faces.append((t, f))


def leave(lab, t):
    N[lab].path.append((t, off(lab), "hold"))


C = TL["cues"]
S = lambda k: C[k][0]
E_ = lambda k: C[k][1]
END = TL["total"]
SHERIFF = (0.0, 14.0)

# ================================================================ A. the rule (barber front) + Vince's loophole
put("dan", 0, (29.4, 17.3), look=(29.0, 20.6))
put("bob", 0, (29.9, 20.6), look=(29.4, 17.3))
face("dan", 0, "grin"); face("dan", E_("D01") + 0.15, "worried"); face("dan", S("N02") + 1.6, "sad")
face("bob", 0, "smile"); face("bob", E_("D01") + 0.1, "suspicious")
pose("dan", S("D01") - 0.3, "wave"); pose("dan", E_("D01"), "idle"); pose("dan", E_("D01") + 0.3, "shrug"); pose("dan", S("N02") + 1.4, "tired")
N["dan"].glow = [(0, 0, "hold"), (E_("D01") - 0.05, 0, "hold"), (E_("D01") + 0.22, 1.0, "out"), (S("N03"), 1.0, "linear"), (S("N03") + 0.01, 0.0, "hold")]
walk("bob", [(S("N02") + 0.9, (29.9, 20.6)), (S("N02") + 2.4, (23.0, 27.0)), (S("N02") + 4.4, (16.0, 40.0))])
leave("bob", S("N03")); leave("dan", S("N03"))
for lab, keys in (("lena", [(S("N03"), (4.0, 15.5)), (E_("N04"), (-8.0, 15.5))]), ("kai", [(S("N03"), (-6.0, 11.0)), (E_("N04"), (6.0, 11.5))])):
    walk(lab, keys); face(lab, S("N03"), "smile"); leave(lab, E_("N04") + 0.3)
VI = (16.0, 3.0)
put("vince", 0, VI, look=(16.0, -4.0))
face("vince", 0, "smug"); face("vince", S("N04") + 0.2, "grin"); face("vince", S("N04") + 1.6, "smug")
pose("vince", S("N03"), "hips"); pose("vince", S("N04") + 0.3, "think"); pose("vince", S("N04") + 1.4, "idle")
walk("vince", [(S("N04") + 0.5, VI), (S("R01") - 0.1, (28.2, 8.5))])
N["vince"].yaw.append((S("R01") - 0.05, -PI / 2, "smooth"))

# ================================================================ B. the bakery
put("rosa", S("N04"), (31.8, 8.5), yaw=PI / 2)
face("rosa", S("N04"), "smile"); face("rosa", S("R02") - 0.1, "suspicious"); face("rosa", S("V02") + 0.6, "worried"); face("rosa", S("R03"), "smile")
pose("rosa", S("R02"), "shrug"); pose("rosa", S("V02") + 0.4, "think"); pose("rosa", S("R03") - 0.2, "idle")
pose("rosa", S("R03") + 0.35, "give"); pose("rosa", E_("R03"), "wave"); pose("rosa", E_("R03") + 1.0, "idle")
face("vince", S("V01") - 0.2, "smug")
pose("vince", S("V01"), "shrug"); pose("vince", E_("V01"), "idle"); pose("vince", S("V02"), "hips"); pose("vince", S("R03") + 0.2, "idle")
pose("vince", S("R03") + 0.8, "carry"); face("vince", S("R03") + 0.9, "grin")
walk("vince", [(S("N05") - 0.2, (28.2, 8.5)), (E_("N05") + 0.4, (19.0, 2.5))])
face("vince", S("N05"), "smug")
leave("rosa", S("M01") - 0.45)

# ================================================================ C. the park
PK = S("M01") - 0.45
put("mia", PK, (-11.4, -46.4), yaw=0.0); put("mom", PK, (-6.6, -46.4), yaw=0.0)
for lab in ("mia", "mom"):
    pose(lab, PK, "sit", "hold")
N["mia"].zoff = [(0, 0.0, "hold"), (PK, 0.19, "hold"), (S("N06"), 0.0, "hold")]
N["mom"].zoff = [(0, 0.0, "hold"), (PK, -0.1, "hold"), (S("N06"), 0.0, "hold")]
face("mia", PK, "suspicious"); face("mom", PK, "smile"); face("mom", E_("M01") - 0.3, "suspicious")
pose("mia", S("M01") + 0.4, "sit_point"); pose("mia", E_("M01"), "sit")
walk("vince", [(PK, (9.0, -38.6)), (S("N06") - 0.05, (-24.0, -38.6))])
pose("vince", PK, "carry", "hold"); face("vince", PK, "grin")
N["mia"].yaw += [(PK, 0.0, "hold"), (PK + 0.4, fa((-11.4, -46.4), (0, -38.6)), "smooth"), (E_("M01"), fa((-11.4, -46.4), (-14, -38.6)), "smooth")]
N["mom"].yaw += [(S("M01") + 1.2, 0.0, "hold"), (S("M01") + 1.6, -0.4, "smooth")]
leave("vince", S("N06")); leave("mia", S("N06")); leave("mom", S("N06"))

# ================================================================ D. night: a thief in a top hat
G = S("THEFT") + 0.25            # the grab
put("mayor", S("N06"), (6.0, 13.0), look=(0, 22))
walk("mayor", [(S("N06") + 0.4, (6.0, 13.0)), (S("N06") + 1.9, (1.6, 17.8)), (G - 0.3, (0.3, 19.2))], ease="smooth")
N["mayor"].yaw.append((G - 0.25, fa((0.3, 19.2), (0, 22.5)), "smooth"))
pose("mayor", S("N06"), "sneak", "hold"); pose("mayor", G - 0.1, "grab"); pose("mayor", G + 0.5, "sneak")
walk("mayor", [(G + 0.7, (0.3, 19.2)), (E_("THEFT") + 0.2, (-6.5, 14.0))], ease="smooth")
face("mayor", S("N06"), "smug")

# ================================================================ E. the town meeting
MT = S("S01") - 0.3
ROW = {"rosa": (-15.2, 9.6), "oldman": (-10.2, 8.6), "mayor": (-5.3, 7.8), "vince": (0.6, 7.0), "mia": (5.4, 7.4),
       "mom": (10.0, 8.2), "kai": (14.6, 9.2), "ana": (-6.6, 3.4), "jen": (-11.4, 4.2), "dan": (-16.0, 5.2),
       "lena": (7.8, 3.4), "bob": (12.4, 4.2), "tom": (17.0, 5.2), "noob": (18.6, 10.6)}
CROWD = [k for k in ROW if k not in ("vince", "mayor")]
put("sheriff", MT, SHERIFF, yaw=PI)
for lab, xy in ROW.items():
    put(lab, MT, xy, look=SHERIFF); pose(lab, MT, "idle", "hold"); face(lab, MT, "neutral")
pose("sheriff", MT, "hips", "hold"); face("sheriff", MT, "suspicious")
pose("sheriff", S("S01") + 1.2, "point"); pose("sheriff", E_("S01"), "hips")
face("rosa", S("R04") - 0.1, "angry"); face("oldman", S("O01") - 0.1, "neutral")
face("mayor", MT, "smile"); face("mayor", S("Y01"), "smug"); pose("mayor", S("Y01") + 0.2, "hips"); pose("mayor", E_("Y01"), "idle")
pose("sheriff", S("S02"), "point"); face("sheriff", S("S02"), "suspicious")
face("vince", MT, "neutral"); face("vince", S("V03") - 0.1, "smug"); pose("vince", S("V03"), "shrug"); pose("vince", E_("V03") + 0.2, "idle")
turn("mia", S("M02") - 0.3, ROW["vince"]); face("mia", S("M02") - 0.3, "angry"); pose("mia", S("M02"), "point")
for i, lab in enumerate(CROWD):
    if lab == "mia":
        continue
    turn(lab, S("C01") - 0.4 + 0.04 * (i % 5), ROW["vince"], 0.4)
    face(lab, S("C01") - 0.2, "angry"); pose(lab, S("C01") - 0.1, "point" if i % 2 else "raise"); pose(lab, E_("C01") + 0.3, "idle")
turn("sheriff", S("C01") - 0.3, ROW["vince"], 0.4); turn("mayor", S("C01") - 0.3, ROW["vince"], 0.4)
face("mayor", S("C01"), "smug"); pose("mayor", S("C01"), "point"); pose("mayor", E_("C01") + 0.3, "idle")
face("vince", S("C01"), "worried"); face("vince", S("N07") + 1.2, "sad"); face("vince", S("V04") - 0.2, "neutral")
turn("vince", S("N07"), SHERIFF, 0.6)
for lab in CROWD + ["sheriff", "mayor"]:
    face(lab, E_("V04") + 0.2, "shocked")
for lab in CROWD + ["sheriff"]:
    face(lab, S("S03") + 0.4, "suspicious")
face("mayor", S("S03"), "worried")
face("vince", E_("V04") + 0.3, "shocked"); face("vince", S("N08") + 0.5, "suspicious")
turn("vince", S("N08") + 0.4, ROW["mayor"], 0.9)
pose("vince", S("V05"), "point"); pose("vince", E_("V05") + 0.3, "hips")
face("mayor", S("Y02"), "worried"); pose("mayor", S("Y02") + 0.1, "shrug"); pose("mayor", E_("Y02"), "idle")
for i, lab in enumerate(CROWD + ["sheriff"]):
    turn(lab, S("Y02") + 0.2 + 0.04 * (i % 5), ROW["mayor"], 0.45)
    face(lab, S("C02") - 0.2, "angry"); pose(lab, S("C02") - 0.1, "point" if i % 2 else "raise"); pose(lab, E_("C02") + 0.3, "idle")
face("vince", S("C02"), "smug")
face("mayor", S("Y03") - 0.2, "worried")
GL = E_("Y03")
N["mayor"].glow = [(0, 0, "hold"), (GL - 0.02, 0, "hold"), (GL + 0.12, 1.6, "out"), (GL + 0.9, 1.0, "smooth"), (END, 1.0, "linear")]
for i, lab in enumerate(CROWD + ["sheriff", "vince"]):
    pose(lab, GL + 0.05 + 0.03 * (i % 4), "block", "out"); face(lab, GL + 0.05, "shocked"); pose(lab, GL + 1.3, "idle")
    face(lab, GL + 1.4, "suspicious")
face("mayor", GL + 0.05, "shocked"); pose("mayor", GL + 0.1, "scared", "out"); face("mayor", GL + 1.2, "sad"); pose("mayor", GL + 1.4, "idle")
# ending: Vince to camera
CAMEND = (0.6, -0.4)
turn("vince", E_("GLOW2") - 0.2, CAMEND, 0.5)
face("vince", E_("GLOW2"), "grin"); face("vince", S("V06") - 0.1, "smug")
pose("vince", E_("GLOW2"), "hips")
face("mia", E_("GLOW2") + 0.6, "suspicious"); turn("mia", E_("GLOW2") + 0.4, ROW["vince"], 0.5)

# ================================================================ props: pie, lantern
pie = D["Pie"]
vin = N["vince"]


def held(n, t, fwd=1.3, right=1.45, up=3.55):
    x, y = n.pos(t); yw = Curve(n.yaw)(t)
    fx, fy = -math.sin(yw), math.cos(yw)
    rx, ry = math.cos(yw), math.sin(yw)
    return (x + fx * fwd + rx * right, y + fy * fwd + ry * right, ground_at(x, y) + up)


HO = S("R03") + 0.35


def pie_pos(t):
    if t < HO:
        return (31.8, 8.5, 3.15)
    if t < HO + 0.55:
        return lerp((31.8, 8.5, 3.15), (30.2, 8.5, 3.6), smooth((t - HO) / 0.55))
    if t < S("N06"):
        return held(vin, t)
    return (0, 0, -50)


track_vec(pie, "location", 3, pie_pos)
track_vec(pie, "rotation_euler", 3, lambda t: (0, 0, Curve(vin.yaw)(t) if HO + 0.55 <= t < S("N06") else 0))
lan, lanl = D["Lantern"], D["LanternLight"].data
may = N["mayor"]
PED = (0.0, 22.5, 4.5)
POP = GL + 0.2


def hat_top(t):
    x, y = may.pos(t)
    return (x, y, ground_at(x, y) + 5.3)


def lan_state(t):   # (location, scale)
    if t < G:
        return PED, 1.0
    if t < G + 0.6:
        u = smooth((t - G) / 0.6)
        return lerp(PED, hat_top(t), u), lerp(1.0, 0.3, u)
    if t < POP:
        return hat_top(t), 0.0
    yw = Curve(may.yaw)(POP)
    fx, fy = -math.sin(yw), math.cos(yw)
    h0 = hat_top(POP)
    if t < POP + 0.6:
        u = (t - POP) / 0.6
        return (h0[0] + fx * 2.0 * u, h0[1] + fy * 2.0 * u, h0[2] + 2.0 * math.sin(math.pi * u) * (1 - u) + (ground_at(h0[0], h0[1]) + 0.05 - h0[2]) * u * u), lerp(0.3, 1.0, min(1, u * 3))
    u = ease_out(min(1.0, (t - POP - 0.6) / 0.9))
    x0, y0 = h0[0] + fx * 2.0, h0[1] + fy * 2.0
    return (x0 + fx * 1.6 * u, y0 + fy * 1.6 * u, ground_at(x0, y0) + 0.05 + 0.2 * abs(math.sin(u * 7)) * (1 - u)), 1.0


track_vec(lan, "location", 3, lambda t: lan_state(t)[0])
track_vec(lan, "scale", 3, lambda t: (max(0.001, lan_state(t)[1]),) * 3)
track_vec(lan, "rotation_euler", 3, lambda t: ((PI / 2) * clamp((t - POP - 0.4) / 0.3), 0, (t - POP) * 6.0 * (1 - clamp((t - POP - 1.2) / 0.4))) if t >= POP else (0, 0, 0))
track(lanl, "energy", 0, lambda t: 0.0 if G + 0.55 < t < POP else (170.0 if S("N06") <= t < MT else 60.0))

# ================================================================ sky
night = Curve([(0, 0, "hold"), (S("N06"), 1.0, "hold"), (MT, 0.0, "hold")])
sky(night, lambda t: 0.0, lamps=lamps_on(night), flashes=[GL + 0.02])

def cu(t0, t1, lab, toward, dist, lens, side=0.0, dz=0.0, push_to=None):
    """Medium close-up of lab from the direction of `toward` (a point), dist units out, nudged sideways; push_to: dolly in."""
    x, y = N[lab].pos(t0 + 0.01)
    s = N[lab].arm.get("npc_scale", 1.0)
    d = V((toward[0] - x, toward[1] - y, 0)).normalized()
    p = V((-d.y, d.x, 0))
    hz = ground_at(x, y) + 4.4 * s + dz
    a = V((x, y, 0)) + d * dist + p * side
    b = V((x, y, 0)) + d * (push_to or dist) + p * side
    return (t0, t1, (a.x, a.y, hz + 0.3), (b.x, b.y, hz + 0.25), (x, y, hz - 0.2), (x, y, hz - 0.2), lens, "smooth")


VH = lambda lab, t, dz=0.0: (N[lab].pos(t)[0], N[lab].pos(t)[1], ground_at(*N[lab].pos(t)) + 4.55 * N[lab].arm.get("npc_scale", 1.0) + dz)


def follow(lab, off_xy, h, lens, dz=-0.3):
    def fn(t, u):
        x, y = N[lab].pos(t)
        return (x + off_xy[0], y + off_xy[1], h), VH(lab, t, dz), lens
    return fn


def ahead(lab, dist, h, lens, side=0.0):
    def fn(t, u):
        x, y = N[lab].pos(t); yw = Curve(N[lab].yaw)(t)
        fx, fy = -math.sin(yw), math.cos(yw)
        return (x + fx * dist + fy * side, y + fy * dist - fx * side, h), VH(lab, t, -0.4), lens
    return fn



SHOTS = [
    # A
    (0.0, S("D01") - 0.05, (8.0, -26.0, 26.0), (19.0, 8.0, 8.5), (24.0, 14.0, 2.0), (29.6, 19.0, 3.8), 26, "smooth"),
    (S("D01") - 0.05, S("N02"), (26.6, 21.4, 4.8), (26.9, 21.1, 4.8), (29.4, 17.3, 4.4), (29.4, 17.3, 4.4), 32, "smooth"),
    (S("N02"), S("N02") + 1.4, (26.8, 16.6, 4.8), (27.0, 16.9, 4.8), (29.9, 20.6, 4.5), (29.9, 20.6, 4.5), 32, "smooth"),
    (S("N02") + 1.4, S("N03") - 0.05, (22.4, 17.6, 3.4), (24.0, 17.5, 3.8), (29.4, 17.3, 3.8), (29.4, 17.3, 4.0), 30, "smooth"),
    cu(S("N03") - 0.05, S("N04") + 0.5, "vince", (16.0, -4.0), 6.6, 32, push_to=5.6),
    (S("N04") + 0.5, S("R01") - 0.9, ahead("vince", 6.2, 4.4, 30, side=0.6)),
    # B
    (S("R01") - 0.9, S("V01") - 0.05, (25.2, 6.6, 5.2), (25.8, 6.9, 5.1), (31.8, 8.6, 4.5), (31.8, 8.6, 4.5), 30, "smooth"),
    (S("V01") - 0.05, S("R02") - 0.05, (31.2, 11.6, 5.0), (31.1, 11.5, 4.95), (28.2, 8.5, 4.5), (28.2, 8.5, 4.5), 30, "smooth"),
    (S("R02") - 0.05, S("V02") - 0.05, (27.0, 11.6, 4.9), (27.1, 11.5, 4.9), (31.8, 8.5, 4.5), (31.8, 8.5, 4.5), 32, "smooth"),
    (S("V02") - 0.05, S("R03") - 0.05, (30.0, 1.0, 4.4), (30.0, 1.6, 4.4), (30.0, 8.5, 3.9), (30.0, 8.5, 3.9), 28, "smooth"),
    (S("R03") - 0.05, S("N05") - 0.1, (25.4, 12.4, 4.8), (25.6, 12.2, 4.8), (30.0, 8.5, 3.7), (30.0, 8.5, 3.7), 28, "smooth"),
    (S("N05") - 0.1, S("M01") - 0.45, ahead("vince", 5.8, 4.4, 30, side=0.8)),
    # C
    (S("M01") - 0.45, S("M01") + 0.9, (-8.0, -52.6, 4.8), (-7.6, -52.4, 4.8), (-3.0, -38.6, 3.0), (-6.0, -38.6, 3.0), 28, "smooth"),
    (S("M01") + 0.9, S("N06"), (-12.4, -42.4, 3.6), (-12.3, -42.6, 3.6), (-11.4, -46.4, 3.5), (-11.4, -46.4, 3.5), 30, "smooth"),
    # D
    (S("N06"), G - 0.45, (0.0, -1.0, 5.2), (0.0, 2.0, 5.4), (0.0, 22.0, 6.0), (0.0, 22.0, 5.6), 26, "smooth"),
    (G - 0.45, G + 1.0, (4.6, 15.4, 5.4), (4.3, 15.8, 5.4), (0.0, 21.6, 5.0), (0.0, 21.6, 5.0), 30, "smooth"),
    (G + 1.0, MT, (1.4, 17.4, 4.2), (1.2, 17.9, 4.3), (0.0, 22.5, 4.7), (0.0, 22.5, 4.8), 32, "smooth"),
    # E
    (MT, S("S01") + 1.3, (16.0, -4.0, 8.0), (15.0, -3.0, 7.6), (0.0, 10.0, 3.8), (0.0, 10.5, 3.8), 22, "smooth"),
    cu(S("S01") + 1.3, S("R04") - 0.05, "sheriff", (-3.0, 7.0), 6.4, 32),
    cu(S("R04") - 0.05, S("O01") - 0.05, "rosa", SHERIFF, 6.3, 32, side=0.8),
    cu(S("O01") - 0.05, S("Y01") - 0.05, "oldman", SHERIFF, 6.3, 32, side=0.8),
    cu(S("Y01") - 0.05, S("S02") - 0.05, "mayor", SHERIFF, 6.3, 30, side=0.8, dz=0.3),
    (S("S02") - 0.05, S("V03") - 0.05, (4.8, -0.4, 8.2), (4.7, 0.0, 8.0), (0.0, 14.0, 4.4), (0.0, 14.0, 4.4), 26, "smooth"),
    cu(S("V03") - 0.05, S("M02") - 0.3, "vince", SHERIFF, 6.2, 32, side=-0.6),
    cu(S("M02") - 0.3, S("C01") - 0.05, "mia", (2.6, 12.6), 5.8, 32, dz=-0.2),
    (S("C01") - 0.05, S("N07") - 0.1, (3.0, 19.5, 11.0), (3.0, 19.0, 10.6), (1.0, 6.5, 2.8), (1.0, 6.5, 2.8), 24, "smooth"),
    cu(S("N07") - 0.1, S("V04") - 0.05, "vince", SHERIFF, 5.4, 32, side=1.6, push_to=4.6),
    cu(S("V04") - 0.05, E_("V04") + 0.15, "vince", SHERIFF, 5.2, 34, push_to=4.9),
    (E_("V04") + 0.15, S("S03") - 0.05, (9.0, -3.0, 7.0), (9.3, -3.3, 7.1), (0.6, 8.0, 3.6), (0.6, 8.0, 3.6), 22, "smooth"),
    cu(S("S03") - 0.05, S("N08") - 0.1, "sheriff", ROW["vince"], 6.2, 32, side=0.8),
    cu(S("N08") - 0.1, S("N08") + 1.3, "vince", (2.0, 12.5), 6.0, 32),
    cu(S("N08") + 1.3, S("V05") - 0.05, "mayor", SHERIFF, 6.6, 32, side=0.6, push_to=5.0),
    (S("V05") - 0.05, S("Y02") - 0.05, (-2.35, 12.2, 5.4), (-2.35, 12.0, 5.3), (-2.35, 7.4, 4.0), (-2.35, 7.4, 4.0), 26, "smooth"),
    cu(S("Y02") - 0.05, S("C02") - 0.05, "mayor", (-2.0, 12.0), 6.0, 32, side=-0.5),
    (S("C02") - 0.05, S("Y03") - 0.1, (-14.0, 17.5, 10.4), (-13.6, 17.0, 10.0), (-5.0, 7.5, 3.0), (-5.0, 7.5, 3.0), 24, "smooth"),
    cu(S("Y03") - 0.1, GL + 0.05, "mayor", (-2.0, 12.0), 6.4, 32, push_to=5.0),
    (GL + 0.05, E_("GLOW2"), (-12.5, -1.0, 7.4), (-12.8, -1.4, 7.6), (-4.6, 8.6, 3.8), (-4.6, 8.6, 3.8), 24, "smooth"),
    cu(E_("GLOW2"), S("V06") + 0.9, "vince", CAMEND, 6.0, 32, push_to=5.2),
    (S("V06") + 0.9, END + 0.1, (7.0, 1.0, 5.0), (10.0, -6.0, 9.5), (-1.0, 9.0, 4.0), (-1.5, 12.0, 5.0), 26, "smooth"),
]


def _push(sh):
    if len(sh) == 3:
        return sh
    t0, t1, a, b, la, lb, lens, ea = sh
    d = (V(a) - V(la)).length
    if d >= 6.5:
        return sh
    k = min(1.55, 6.3 / d)
    a2 = tuple(V(la) + (V(a) - V(la)) * k)
    b2 = tuple(V(lb) + (V(b) - V(lb)) * k)
    return (t0, t1, a2, b2, la, lb, lens * 0.88, ea)



SHOTS = [_push(s) for s in SHOTS]
camera(SHOTS, shake=lambda t: 0.12 * clamp(1 - (t - GL) / 0.8) if GL <= t < GL + 0.8 else 0.0)
for n in N.values():
    n.bake()
finish("ep1b")
