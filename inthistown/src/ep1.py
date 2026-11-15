"""In this town — Episode 1: The Golden Lantern. Runs on town.blend:
  blender -b town.blend --python ep1.py -- <work> [stills <out> <f1,f2,..> [pct]]"""
import bpy, sys, os, math, json
WORK = sys.argv[sys.argv.index("--") + 1]
exec(open(os.path.join(WORK, "townlib.py")).read())
TL = json.load(open(os.path.join(WORK, "ep1_timeline.json")))
LINES = TL["lines"]
setup(TL["total"])
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


# ================================================================ SCENE 1: the rule (barber front), 0 - 10.9
put("dan", 0, (31.2, 17.3), look=(30.4, 20.2))
put("bob", 0, (33.6, 20.9), look=(31.2, 17.3))
walk("bob", [(0.0, (33.6, 20.9)), (0.7, (31.7, 20.5))])
N["bob"].yaw.append((0.7, fa((31.7, 20.5), (31.2, 17.3)), "smooth"))
face("dan", 0, "grin"); face("dan", 1.45, "worried"); face("dan", 8.9, "sad")
face("bob", 0, "smile"); face("bob", 1.2, "suspicious"); face("bob", 2.9, "neutral")
pose("dan", 0.2, "wave"); pose("dan", 1.0, "idle"); pose("dan", 1.5, "shrug"); pose("dan", 2.6, "idle"); pose("dan", 8.9, "tired")
N["dan"].glow = [(0, 0, "hold"), (1.1, 0, "hold"), (1.38, 1.0, "out"), (10.9, 1.0, "linear"), (10.95, 0.0, "hold")]
walk("bob", [(2.9, (31.7, 20.5)), (3.3, (31.5, 22.0)), (6.5, (31.5, 40.0))])
leave("bob", 6.6)
turn("dan", 3.2, (31.5, 30.0), 0.5)
turn("dan", 8.8, (24.0, 17.3), 0.6)
leave("dan", 11.0)
# strollers on the plaza (rule montage)
for lab, keys in (("ana", [(6.5, (-14, -12)), (10.9, (2, -15))]), ("kai", [(6.5, (12, 10)), (10.9, (-6, 13))]),
                  ("tom", [(6.5, (-15, 8)), (10.9, (-10, -8))]), ("jen", [(6.5, (14, -10)), (10.9, (8, 6))]),
                  ("lena", [(6.5, (-4, 14)), (10.9, (12, 14))]), ("noob", [(6.5, (8, -14)), (10.9, (15, -4))])):
    walk(lab, keys)
    face(lab, 6.5, "smile")
    leave(lab, 11.0)
pose("noob", 6.5, "wave")

# ================================================================ SCENE 2: Vince arrives, 10.9 - 12.9
walk("vince", [(10.9, (25.5, -13.0)), (12.9, (26.2, -1.5))])
face("vince", 10.9, "smug")

# ================================================================ SCENE 3: the bakery, 12.9 - 25.8
put("rosa", 12.9, (32.2, 8.5), yaw=PI / 2)
put("vince", 12.9, (29.3, 8.5), yaw=-PI / 2)
face("rosa", 12.9, "smile"); face("rosa", 16.2, "suspicious"); face("rosa", 17.8, "worried"); face("rosa", 19.3, "smile")
face("vince", 12.9, "smile"); face("vince", 15.0, "smug"); face("vince", 20.5, "grin"); face("vince", 23.6, "smug")
pose("rosa", 12.9, "idle"); pose("rosa", 16.3, "shrug"); pose("rosa", 17.6, "think"); pose("rosa", 19.1, "idle")
pose("rosa", 19.9, "give"); pose("rosa", 20.8, "wave"); pose("rosa", 22.2, "idle")
pose("vince", 12.9, "idle"); pose("vince", 15.0, "shrug"); pose("vince", 16.2, "idle"); pose("vince", 17.4, "hips")
pose("vince", 19.2, "idle"); pose("vince", 20.3, "carry")
walk("vince", [(20.9, (29.3, 8.5)), (25.8, (13.0, -3.0))])
leave("rosa", 25.9)

# ================================================================ SCENE 4: montage, 25.8 - 29.2
put("kai", 25.8, (31.5, 19.2), yaw=0.0)
put("ana", 25.8, (31.5, 17.3), yaw=0.0)
walk("vince", [(25.8, (28.4, 21.0)), (26.3, (31.4, 20.7))])
N["vince"].yaw.append((26.3, fa((31.4, 20.7), (31.5, 19.2)), "smooth"))
face("vince", 25.8, "smug"); face("kai", 25.8, "smile"); face("kai", 26.9, "suspicious"); face("ana", 25.8, "neutral")
pose("kai", 26.9, "shrug"); pose("kai", 27.4, "idle")
walk("kai", [(27.0, (31.5, 19.2)), (27.4, (31.3, 18.4))])
leave("kai", 27.45); leave("ana", 27.45)
put("tom", 27.4, (32.0, -13.6), yaw=PI / 2)
put("vince", 27.4, (29.4, -15.2), yaw=fa((29.4, -15.2), (32.0, -13.6)))
face("tom", 27.4, "smile"); face("tom", 28.7, "suspicious"); face("vince", 27.4, "smug")
pose("tom", 28.6, "think"); pose("vince", 27.4, "carry")
leave("tom", 29.25)

# ================================================================ SCENE 5: the park, 29.2 - 35.1
put("mia", 29.2, (-9.0, -46.4), yaw=0.0)
put("mom", 29.2, (-7.0, -46.4), yaw=0.0)
for lab in ("mia", "mom"):
    pose(lab, 29.2, "sit", "hold")
N["mia"].zoff = [(0, 0.0, "hold"), (29.2, 0.19, "hold"), (35.1, 0.0, "hold")]
N["mom"].zoff = [(0, 0.0, "hold"), (29.2, -0.1, "hold"), (35.1, 0.0, "hold")]
pose("mia", 30.4, "sit_point"); pose("mia", 32.2, "sit")
face("mia", 29.2, "suspicious"); face("mom", 29.2, "smile"); face("mom", 33.6, "suspicious")
walk("vince", [(29.2, (8.0, -41.8)), (35.1, (-24.0, -41.8))])
N["mia"].yaw += [(29.2, 0.0, "hold"), (29.6, fa((-9, -46.4), (2, -41.8)), "smooth"), (32.3, fa((-9, -46.4), (-12, -41.8)), "smooth"),
                 (32.6, -0.35, "smooth")]
N["mom"].yaw += [(32.2, 0.0, "hold"), (32.6, 0.35, "smooth"), (33.6, fa((-7, -46.4), (-16, -41.8)), "smooth")]

# ================================================================ SCENE 6: night, the lantern goes missing, 35.1 - 39.6
walk("vince", [(35.1, (5.0, 14.0)), (36.4, (1.6, 18.6)), (37.1, (0.4, 21.0))], ease="smooth")
N["vince"].yaw.append((37.1, fa((0.4, 21.0), (0, 22.5)), "smooth"))
pose("vince", 35.1, "sneak", "hold"); pose("vince", 37.1, "grab"); pose("vince", 37.8, "sneak")
face("vince", 35.1, "smug")
walk("vince", [(38.2, (0.4, 21.0)), (39.6, (-6.5, 15.0))], ease="smooth")
leave("mia", 35.15); leave("mom", 35.15)

# ================================================================ SCENE 7: the town meeting, 39.6 - 65.0
SHERIFF = (0.0, 14.0)
ROW = {"rosa": (-7.0, 8.6), "oldman": (-4.6, 7.7), "mayor": (-2.2, 7.2), "vince": (1.0, 7.0), "mia": (3.5, 7.4),
       "mom": (5.5, 7.8), "kai": (7.8, 8.7), "ana": (-9.4, 9.8), "tom": (9.9, 10.0), "jen": (-6.4, 5.3), "dan": (-8.9, 6.2),
       "lena": (6.5, 5.1), "bob": (8.9, 6.0), "noob": (10.9, 7.6)}
put("sheriff", 39.6, SHERIFF, yaw=PI)
for lab, xy in ROW.items():
    put(lab, 39.6, xy, look=SHERIFF)
    pose(lab, 39.6, "idle", "hold")
    face(lab, 39.6, "neutral")
pose("sheriff", 39.6, "hips", "hold"); face("sheriff", 39.6, "suspicious")
pose("sheriff", 41.6, "idle"); pose("sheriff", 42.4, "point"); pose("sheriff", 43.2, "hips")
face("rosa", 43.2, "angry"); face("oldman", 43.9, "neutral"); face("mayor", 44.8, "smug")
pose("sheriff", 46.2, "point"); face("sheriff", 46.2, "angry")
face("vince", 39.6, "smile"); face("vince", 47.2, "smug"); pose("vince", 47.3, "shrug"); pose("vince", 49.2, "hips")
turn("mia", 49.5, ROW["vince"]); face("mia", 49.5, "suspicious"); pose("mia", 49.6, "hips")
turn("vince", 51.0, ROW["mia"]); face("vince", 51.0, "smug")
pose("mia", 52.1, "point"); face("mia", 52.1, "angry")
face("vince", 54.6, "worried"); pose("vince", 54.8, "shrug"); pose("vince", 56.2, "idle")
for lab in ("rosa", "oldman", "mayor", "mom", "kai", "ana", "tom", "jen", "dan", "lena", "bob", "noob"):
    turn(lab, 55.9 + 0.05 * ((sum(map(ord, lab)) % 5)), ROW["vince"], 0.4)
    face(lab, 56.2, "angry")
    pose(lab, 56.3, "point" if (sum(map(ord, lab)) % 2) else "raise")
turn("sheriff", 56.0, ROW["vince"], 0.4)
turn("vince", 56.4, SHERIFF, 0.5)
for lab in ("rosa", "oldman", "mayor", "mom", "kai", "ana", "tom", "jen", "dan", "lena", "bob", "noob", "mia"):
    pose(lab, 58.3, "idle")
    face(lab, 58.4, "suspicious")
face("vince", 58.6, "worried")
N["vince"].glow = [(0, 0, "hold"), (60.42, 0, "hold"), (60.56, 1.6, "out"), (61.3, 1.0, "smooth"), (73.6, 1.0, "linear"),
                   (73.62, 0.55, "hold")]
for lab in ("rosa", "oldman", "mayor", "mom", "kai", "ana", "tom", "jen", "dan", "lena", "bob", "noob", "mia", "sheriff"):
    pose(lab, 60.5 + 0.03 * ((sum(map(ord, lab)) % 4)), "block", "out")
    face(lab, 60.5, "shocked")
    pose(lab, 62.0, "idle")
face("vince", 60.5, "shocked"); pose("vince", 60.5, "scared", "out"); face("vince", 61.6, "worried"); pose("vince", 62.0, "idle")
face("sheriff", 62.2, "suspicious"); pose("sheriff", 62.4, "hips")
for lab in ("rosa", "oldman", "mom", "kai", "ana", "tom", "jen", "dan", "lena", "bob", "noob", "mia"):
    face(lab, 62.1, "suspicious")
face("mayor", 62.1, "grin")

# ================================================================ SCENE 8: the chase, 65.0 - 73.6
face("vince", 65.0, "worried"); pose("vince", 65.0, "shrug"); pose("vince", 66.2, "idle")
walk("vince", [(66.3, ROW["vince"]), (67.2, (-11.0, 5.6)), (68.6, (-31.0, 6.0)), (69.4, (-41.0, 6.4)), (69.9, (-45.8, 7.3))])
N["vince"].stride = 3.4
pose("vince", 69.9, "cower"); face("vince", 69.9, "worried")
N["vince"].yaw.append((70.0, fa((-45.8, 7.3), (-36, 6)), "smooth"))
for lab, lag, end in (("sheriff", 0.5, (-37.0, 6.0)), ("mia", 0.8, (-35.5, 7.2)), ("rosa", 1.0, (-35.0, 4.9)), ("kai", 1.2, (-34.0, 6.3))):
    p0 = SHERIFF if lab == "sheriff" else ROW[lab]
    walk(lab, [(66.3 + lag, p0), (68.3 + lag, (-20.0, 6.0)), (69.6 + lag, (-30.0, 6.0)), (70.4 + lag * 0.4, end)])
    N[lab].yaw.append((70.6 + lag * 0.4, fa(end, (-45.8, 7.3)), "smooth"))
    face(lab, 66.3, "angry")
for lab in ("oldman", "mayor", "mom", "ana", "tom", "jen", "dan", "lena", "bob", "noob"):
    leave(lab, 67.0)
pose("sheriff", 70.4, "hips"); face("sheriff", 70.4, "smug")
pose("vince", 72.0, "idle"); face("vince", 72.3, "shocked"); face("vince", 73.0, "sad")

# ================================================================ SCENE 9: the twist, 73.6 - end
END = TL["total"]
put("mayor", 73.6, (-1.9, 23.6), look=(0, 12))
pose("mayor", 73.6, "give", "hold"); pose("mayor", 74.6, "idle"); face("mayor", 73.6, "grin")
CROWD2 = {"sheriff": (2.6, 16.2), "vince": (4.3, 16.6), "mia": (-2.4, 15.6), "mom": (-4.3, 15.4), "rosa": (-6.4, 16.0),
          "kai": (7.0, 15.0), "ana": (-8.6, 14.6), "tom": (8.8, 13.2), "jen": (-5.2, 12.8), "dan": (-1.0, 12.4),
          "lena": (2.2, 12.6), "bob": (5.4, 12.6), "noob": (-9.8, 12.0), "oldman": (0.6, 14.4)}
for lab, xy in CROWD2.items():
    put(lab, 73.6, xy, look=(-1.9, 23.6))
    pose(lab, 73.6, "idle", "hold")
    face(lab, 73.6, "smile")
pose("vince", 73.6, "cuffs", "hold"); face("vince", 73.6, "sad"); pose("sheriff", 73.6, "hips", "hold")
N["mayor"].glow = [(0, 0, "hold"), (77.6, 0, "hold"), (79.0, 1.0, "in"), (END, 1.0, "linear")]
face("mayor", 77.7, "neutral"); face("mayor", 78.5, "worried"); pose("mayor", 78.3, "think"); pose("mayor", 79.6, "shrug")
for lab in CROWD2:
    if lab != "vince":
        face(lab, 78.2 + 0.05 * ((sum(map(ord, lab)) % 6)), "shocked")
        face(lab, 79.4 + 0.05 * ((sum(map(ord, lab)) % 6)), "suspicious")
face("vince", 78.4, "shocked"); face("vince", 79.3, "grin")
pose("mia", 79.6, "point")

# ================================================================ props: pie, apples, lantern
pie = D["Pie"]
vin = N["vince"]


def held(t, fwd=1.3, right=1.45, up=3.55):
    x, y = vin.pos(t); yw = Curve(vin.yaw)(t)
    fx, fy = -math.sin(yw), math.cos(yw)
    rx, ry = math.cos(yw), math.sin(yw)
    return (x + fx * fwd + rx * right, y + fy * fwd + ry * right, ground_at(x, y) + up)


def pie_pos(t):
    if t < 19.9:
        return (31.8, 8.5, 3.15)
    if t < 20.45:
        u = smooth((t - 19.9) / 0.55)
        return lerp((31.8, 8.5, 3.15), (30.5, 8.5, 3.6), u)
    if t < 35.1:
        return held(t)
    return (0, 0, -50)


track_vec(pie, "location", 3, pie_pos)
track_vec(pie, "rotation_euler", 3, lambda t: (0, 0, Curve(vin.yaw)(t) if 20.45 <= t < 35.1 else 0))
# apples at the general store
crate = bpy.data.objects.new("AppleCrate", None); sc.collection.objects.link(crate); crate.location = (31.6, -16.4, 0.22)
WOODM = bpy.data.materials.get("Wood"); RED = bpy.data.materials.new("Apple"); RED.use_nodes = True
RED.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = lin((220, 40, 40)) + (1,)
RED.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
bpy.ops.mesh.primitive_cube_add(size=1, location=(31.6, -16.4, 0.82)); cb = bpy.context.active_object; cb.scale = (1.6, 1.6, 1.2)
cb.data.materials.append(WOODM)
for i in range(9):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(31.6 + (i % 3 - 1) * 0.5, -16.4 + (i // 3 - 1) * 0.5, 1.55))
    bpy.context.active_object.data.materials.append(RED)
    bpy.ops.object.shade_smooth()
# the Golden Lantern
lan, lanl = D["Lantern"], D["LanternLight"].data
PED = (0.0, 22.5, 4.5)


def lan_pos(t):
    if t < 37.45:
        return PED
    if t < 38.0:   # in Vince's hand, then into the backpack
        return held(t, fwd=1.1, right=1.2, up=3.2)
    if t < 72.0:
        return (0, 0, -60)
    if t < 72.45:   # tumbles out of the backpack
        u = (t - 72.0) / 0.45
        x, y = -45.8 + 0.3 * u, 7.3 - 0.5 * u
        return (x, y, 3.0 * (1 - u * u) + 0.02)
    if t < 73.6:
        u = ease_out((t - 72.45) / 1.15)
        return (lerp(-45.5, -40.2, u), lerp(6.8, 6.1, u), 0.02 + 0.25 * abs(math.sin(u * 6.0)) * (1 - u))
    return PED


track_vec(lan, "location", 3, lan_pos)
track_vec(lan, "rotation_euler", 3, lambda t: (PI / 2 * clamp((t - 72.2) / 0.3), 0, (t - 72.45) * 9.0 * (1 - clamp((t - 73.2) / 0.4)))
          if 72.0 <= t < 73.6 else (0, 0, 0))
track(lanl, "energy", 0, lambda t: 0.0 if 37.95 < t < 72.0 else (160.0 if 35.1 <= t < 39.6 else 50.0))

# ================================================================ sky, lamps
night = Curve([(0, 0, "hold"), (35.1, 1.0, "hold"), (39.6, 0.0, "hold")])
dawn = lambda t: 0.0
sky(night, dawn, lamps=lamps_on(night), flashes=[60.44])

# ================================================================ camera
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
    (0.0, 1.15, (24.6, 18.9, 4.3), (25.0, 18.9, 4.3), (31.4, 18.9, 3.7), (31.4, 18.9, 3.7), 26, "smooth"),
    (1.15, 1.9, (28.9, 19.9, 4.6), (29.2, 19.6, 4.6), (31.2, 17.3, 4.5), (31.2, 17.3, 4.5), 38, "smooth"),
    (1.9, 2.9, (29.3, 18.2, 4.6), (29.4, 18.4, 4.6), (31.7, 20.5, 4.6), (31.7, 20.5, 4.6), 38, "smooth"),
    (2.9, 6.6, (26.2, 14.2, 4.4), (16.0, -12.0, 18.0), (31.2, 17.3, 3.8), (0.0, 16.0, 6.0), 28, "smooth"),
    (6.6, 8.9, (0.0, -25.0, 7.5), (0.0, -21.5, 6.5), (0.0, 0.0, 2.8), (0.0, 2.0, 3.0), 26, "smooth"),
    (8.9, 10.9, (25.4, 17.6, 3.2), (27.0, 17.5, 3.8), (31.2, 17.3, 3.8), (31.2, 17.3, 4.0), 32, "smooth"),
    (10.9, 12.9, ahead("vince", 7.5, 2.0, 28)),
    (12.9, 14.9, (27.4, 7.1, 5.0), (27.6, 7.2, 4.9), (32.2, 8.6, 4.5), (32.2, 8.6, 4.5), 32, "smooth"),
    (14.9, 16.3, (31.1, 10.3, 4.8), (31.0, 10.2, 4.75), (29.3, 8.5, 4.6), (29.3, 8.5, 4.6), 36, "smooth"),
    (16.3, 17.3, (28.5, 10.5, 4.7), (28.6, 10.4, 4.7), (32.2, 8.5, 4.5), (32.2, 8.5, 4.5), 40, "smooth"),
    (17.3, 19.2, (30.8, 1.8, 4.2), (30.8, 2.4, 4.2), (30.8, 8.5, 3.9), (30.8, 8.5, 3.9), 30, "smooth"),
    (19.2, 20.9, (27.3, 10.6, 4.4), (27.5, 10.4, 4.4), (31.0, 8.5, 3.7), (31.0, 8.5, 3.7), 30, "smooth"),
    (20.9, 23.6, follow("vince", (-9.0, -3.5), 4.0, 30, -0.8)),
    (23.6, 25.8, ahead("vince", 5.4, 4.6, 30, side=0.8)),
    (25.8, 27.4, (27.9, 16.6, 4.4), (28.1, 16.9, 4.4), (31.4, 19.9, 4.3), (31.4, 19.9, 4.3), 30, "smooth"),
    (27.4, 29.2, (27.0, -11.6, 4.3), (27.2, -11.8, 4.3), (31.0, -14.8, 3.9), (31.0, -14.8, 3.9), 30, "smooth"),
    (29.2, 30.6, (-8.0, -51.6, 4.6), (-7.6, -51.4, 4.6), (-3.0, -41.6, 3.2), (-6.0, -41.6, 3.2), 28, "smooth"),
    (30.6, 32.3, (-9.3, -42.8, 3.7), (-9.3, -43.0, 3.7), (-9.0, -46.2, 3.6), (-9.0, -46.2, 3.6), 36, "smooth"),
    (32.3, 35.1, (-8.0, -40.4, 3.8), (-8.0, -40.9, 3.8), (-8.0, -46.2, 3.7), (-8.0, -46.2, 3.7), 28, "smooth"),
    (35.1, 37.0, (0.0, -1.0, 5.2), (0.0, 1.5, 5.4), (0.0, 22.0, 6.0), (0.0, 22.0, 5.6), 26, "smooth"),
    (37.0, 38.4, (3.6, 18.8, 5.6), (3.3, 19.1, 5.5), (0.1, 22.2, 4.6), (0.1, 22.2, 4.6), 30, "smooth"),
    (38.4, 39.6, (1.4, 17.4, 4.2), (1.2, 17.9, 4.3), (0.0, 22.5, 4.7), (0.0, 22.5, 4.8), 32, "smooth"),
    (39.6, 41.5, (13.5, -0.5, 6.8), (12.5, 0.5, 6.4), (0.0, 11.0, 3.8), (0.0, 11.5, 3.8), 24, "smooth"),
    (41.5, 43.2, (1.6, 9.9, 4.6), (1.4, 10.3, 4.6), (0.0, 14.0, 4.5), (0.0, 14.0, 4.5), 32, "smooth"),
    (43.2, 44.0, (-5.0, 10.1, 4.6), (-5.0, 10.1, 4.6), (-7.0, 8.6, 4.6), (-7.0, 8.6, 4.6), 34, "smooth"),
    (44.0, 44.8, (-3.1, 9.8, 4.6), (-3.1, 9.8, 4.6), (-4.6, 7.7, 4.6), (-4.6, 7.7, 4.6), 34, "smooth"),
    (44.8, 46.2, (-1.4, 9.9, 5.0), (-1.4, 9.8, 5.0), (-2.2, 7.2, 4.9), (-2.2, 7.2, 4.9), 32, "smooth"),
    (46.2, 47.2, (2.9, 2.6, 6.4), (2.8, 3.0, 6.3), (0.0, 14.0, 4.4), (0.0, 14.0, 4.4), 26, "smooth"),
    (47.2, 49.6, (0.6, 10.1, 4.7), (0.65, 9.8, 4.7), (1.0, 7.0, 4.6), (1.0, 7.0, 4.6), 34, "smooth"),
    (49.6, 51.1, (1.9, 8.8, 3.9), (1.9, 8.7, 3.9), (3.5, 7.4, 3.7), (3.5, 7.4, 3.7), 34, "smooth"),
    (51.1, 52.0, (3.0, 8.4, 4.7), (2.9, 8.4, 4.7), (1.0, 7.0, 4.6), (1.0, 7.0, 4.6), 36, "smooth"),
    (52.0, 54.8, (4.9, 11.0, 4.5), (4.7, 10.8, 4.4), (2.2, 7.2, 3.9), (2.2, 7.2, 3.9), 26, "smooth"),
    (54.8, 56.3, (0.6, 9.8, 4.7), (0.62, 9.6, 4.7), (1.0, 7.0, 4.6), (1.0, 7.0, 4.6), 36, "smooth"),
    (56.3, 58.5, (3.0, 18.5, 10.5), (3.0, 18.0, 10.0), (1.0, 6.5, 2.8), (1.0, 6.5, 2.8), 24, "smooth"),
    (58.5, 60.48, (0.75, 10.6, 4.8), (0.9, 9.4, 4.7), (1.0, 7.0, 4.6), (1.0, 7.0, 4.6), 34, "in"),
    (60.48, 62.5, (6.4, -1.4, 6.6), (6.8, -1.8, 6.8), (1.0, 8.0, 3.6), (1.0, 8.0, 3.6), 24, "smooth"),
    (62.5, 65.0, (0.9, 11.1, 4.6), (0.8, 11.3, 4.6), (0.0, 14.0, 4.5), (0.0, 14.0, 4.5), 32, "smooth"),
    (65.0, 66.7, (0.95, 10.1, 4.6), (0.95, 10.0, 4.6), (1.0, 7.0, 4.4), (1.0, 7.0, 4.4), 32, "smooth"),
    (66.7, 69.2, (-6.0, -16.0, 18.0), (-14.0, -16.0, 17.0), (-12.0, 6.0, 2.0), (-35.0, 6.0, 2.0), 26, "smooth"),
    (69.2, 70.4, (-32.8, 5.0, 6.6), (-33.6, 5.2, 6.2), (-44.5, 6.6, 1.8), (-45.4, 6.8, 1.6), 28, "smooth"),
    (70.4, 72.0, (-45.6, 4.5, 3.6), (-45.4, 4.6, 3.6), (-36.5, 6.0, 4.3), (-36.5, 6.0, 4.3), 30, "smooth"),
    (72.0, 73.6, lambda t, u: ((-37.2, 4.6, 1.3), (lan_pos(t)[0], lan_pos(t)[1], max(0.7, min(2.4, lan_pos(t)[2] + 0.6))), 30)),
    (73.6, 75.5, (0.0, 4.5, 7.5), (0.0, 6.0, 7.6), (0.0, 22.0, 5.4), (0.0, 22.0, 5.6), 26, "smooth"),
    (75.5, 77.5, (-0.6, 18.2, 6.4), (-0.7, 18.5, 6.4), (-1.9, 23.6, 6.2), (-1.9, 23.6, 6.2), 32, "smooth"),
    (77.5, 79.6, (-0.8, 19.2, 6.5), (-0.9, 19.6, 6.4), (-1.9, 23.6, 5.9), (-1.9, 23.6, 5.9), 30, "smooth"),
    (79.6, 81.0, (-6.5, 23.0, 8.2), (-6.3, 23.1, 8.0), (0.5, 14.5, 3.6), (0.5, 14.5, 3.6), 24, "smooth"),
    (81.0, END + 0.1, (0.0, 9.0, 5.2), (0.0, -4.0, 9.5), (-0.8, 22.5, 6.0), (-0.5, 22.5, 7.0), 26, "smooth"),
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
camera(SHOTS, shake=lambda t: 0.12 * clamp(1 - (t - 60.45) / 0.8) if 60.45 <= t < 61.3 else 0.0)

# ================================================================ bake (zoff wrap), finish
for n in N.values():
    n.bake()
    if n.zoff:
        zc = Curve(n.zoff)
        for i, (o, p, idx, g, c) in enumerate(TRACKS):
            if o is n.arm and p == "location" and idx == 2:
                TRACKS[i] = (o, p, idx, (lambda g=g, zc=zc: [v + zc(t) for v, t in zip(g(), TIMES)]), c)
finish("ep1")
