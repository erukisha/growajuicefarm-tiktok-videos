"""In this town — Episode 1: The Golden Lantern. Runs on town.blend:
  blender -b town.blend --python ep1.py -- <work> [stills <out> <f1,f2,..> [pct]]"""
import bpy, sys, os, math, json
WORK = sys.argv[sys.argv.index("--") + 1]
exec(open(os.path.join(WORK, "townlib.py")).read())
TL = json.load(open(os.path.join(WORK, "ep1_timeline.json")))
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


# ================================================================ SCENE 1: the rule (barber front), 0 - 10.9
put("dan", 0, (29.4, 17.3), look=(29.0, 20.6))
put("bob", 0, (29.9, 20.6), look=(29.4, 17.3))
face("dan", 0, "grin"); face("dan", 1.45, "worried"); face("dan", 8.9, "sad")
face("bob", 0, "smile"); face("bob", 1.2, "suspicious"); face("bob", 2.9, "neutral")
pose("dan", 0.2, "wave"); pose("dan", 1.0, "idle"); pose("dan", 1.5, "shrug"); pose("dan", 2.6, "idle"); pose("dan", 8.9, "tired")
N["dan"].glow = [(0, 0, "hold"), (1.1, 0, "hold"), (1.38, 1.0, "out"), (10.9, 1.0, "linear"), (10.95, 0.0, "hold")]
walk("bob", [(2.9, (29.9, 20.6)), (4.4, (23.0, 27.0)), (6.5, (16.0, 40.0))])
leave("bob", 6.6)
turn("dan", 3.2, (23.0, 27.0), 0.5)
turn("dan", 8.8, (24.0, 17.3), 0.6)
leave("dan", 11.0)
# strollers on the plaza (rule montage)
for lab, keys in (("ana", [(6.5, (-14, -12)), (10.9, (2, -15))]), ("kai", [(6.5, (12, 10)), (10.9, (-6, 13))]),
                  ("tom", [(6.5, (-15, 8)), (10.9, (-10, -8))]), ("jen", [(6.5, (16.5, -12)), (10.9, (14.5, 6))]),
                  ("lena", [(6.5, (-4, 17.6)), (10.9, (12, 17.6))]), ("noob", [(6.5, (8, -14)), (10.9, (15, -4))])):
    walk(lab, keys)
    face(lab, 6.5, "smile")
    leave(lab, 11.0)
pose("noob", 6.5, "wave")

# ================================================================ SCENE 2: Vince arrives, 10.9 - 12.9
walk("vince", [(10.9, (25.5, -13.0)), (12.9, (26.2, -1.5))])
face("vince", 10.9, "smug")

# ================================================================ SCENE 3: the bakery, 12.9 - 25.8
put("rosa", 12.9, (31.8, 8.5), yaw=PI / 2)
put("vince", 12.9, (28.5, 8.5), yaw=-PI / 2)
face("rosa", 12.9, "smile"); face("rosa", 16.2, "suspicious"); face("rosa", 17.8, "worried"); face("rosa", 19.3, "smile")
face("vince", 12.9, "smile"); face("vince", 15.0, "smug"); face("vince", 20.5, "grin"); face("vince", 23.6, "smug")
pose("rosa", 12.9, "idle"); pose("rosa", 16.3, "shrug"); pose("rosa", 17.6, "think"); pose("rosa", 19.1, "idle")
pose("rosa", 19.9, "give"); pose("rosa", 20.8, "wave"); pose("rosa", 22.2, "idle")
pose("vince", 12.9, "idle"); pose("vince", 15.0, "shrug"); pose("vince", 16.2, "idle"); pose("vince", 17.4, "hips")
pose("vince", 19.2, "idle"); pose("vince", 20.3, "carry")
walk("vince", [(20.9, (28.5, 8.5)), (25.8, (13.0, -3.0))])
leave("rosa", 25.9)

# ================================================================ SCENE 4: montage, 25.8 - 29.2
put("kai", 25.8, (30.1, 18.4), yaw=0.0)
put("ana", 25.8, (30.1, 15.6), yaw=0.0)
walk("vince", [(25.8, (26.0, 23.6)), (26.3, (30.0, 21.9))])
N["vince"].yaw.append((26.3, fa((30.0, 21.9), (30.1, 18.4)), "smooth"))
face("vince", 25.8, "smug"); face("kai", 25.8, "smile"); face("kai", 26.9, "suspicious"); face("ana", 25.8, "neutral")
pose("kai", 26.9, "shrug"); pose("kai", 27.4, "idle")
walk("kai", [(27.0, (30.1, 18.4)), (27.4, (29.6, 17.9))])
leave("kai", 27.45); leave("ana", 27.45)
put("tom", 27.4, (32.0, -13.6), yaw=PI / 2)
put("vince", 27.4, (29.4, -15.2), yaw=fa((29.4, -15.2), (32.0, -13.6)))
face("tom", 27.4, "smile"); face("tom", 28.7, "suspicious"); face("vince", 27.4, "smug")
pose("tom", 28.6, "think"); pose("vince", 27.4, "carry")
leave("tom", 29.25)

# ================================================================ SCENE 5: the park, 29.2 - 35.1
put("mia", 29.2, (-11.4, -46.4), yaw=0.0)
put("mom", 29.2, (-6.6, -46.4), yaw=0.0)
for lab in ("mia", "mom"):
    pose(lab, 29.2, "sit", "hold")
N["mia"].zoff = [(0, 0.0, "hold"), (29.2, 0.19, "hold"), (35.1, 0.0, "hold")]
N["mom"].zoff = [(0, 0.0, "hold"), (29.2, -0.1, "hold"), (35.1, 0.0, "hold")]
pose("mia", 30.4, "sit_point"); pose("mia", 32.2, "sit")
face("mia", 29.2, "suspicious"); face("mom", 29.2, "smile"); face("mom", 33.6, "suspicious")
walk("vince", [(29.2, (8.0, -41.8)), (35.1, (-24.0, -41.8))])
N["mia"].yaw += [(29.2, 0.0, "hold"), (29.6, fa((-11.4, -46.4), (2, -41.8)), "smooth"), (32.3, fa((-11.4, -46.4), (-14, -41.8)), "smooth"),
                 (32.6, -0.35, "smooth")]
N["mom"].yaw += [(32.2, 0.0, "hold"), (32.6, 0.35, "smooth")]

# ================================================================ SCENE 6: night, the lantern goes missing, 35.1 - 39.6
walk("vince", [(35.1, (5.0, 14.0)), (36.4, (1.6, 17.8)), (37.1, (0.3, 19.9))], ease="smooth")
N["vince"].yaw.append((37.1, fa((0.3, 19.9), (0, 22.5)), "smooth"))
pose("vince", 35.1, "sneak", "hold"); pose("vince", 37.1, "grab"); pose("vince", 37.8, "sneak")
face("vince", 35.1, "smug")
walk("vince", [(38.2, (0.3, 19.9)), (39.6, (-6.5, 14.0))], ease="smooth")
leave("mia", 35.15); leave("mom", 35.15)

# ================================================================ SCENE 7: the town meeting, 39.6 - 65.0
SHERIFF = (0.0, 14.0)
ROW = {"rosa": (-15.2, 9.6), "oldman": (-10.2, 8.6), "mayor": (-5.3, 7.8), "vince": (0.6, 7.0), "mia": (5.4, 7.4),
       "mom": (10.0, 8.2), "kai": (14.6, 9.2), "ana": (-6.6, 3.4), "jen": (-11.4, 4.2), "dan": (-16.0, 5.2),
       "lena": (7.8, 3.4), "bob": (12.4, 4.2), "tom": (17.0, 5.2), "noob": (18.6, 10.6)}
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
walk("vince", [(66.3, ROW["vince"]), (66.75, (-4.0, 11.6)), (67.6, (-18.0, 12.6)), (68.1, (-24.0, 10.0)), (68.6, (-31.0, 6.0)),
               (69.4, (-39.0, 6.6)), (69.9, (-43.0, 6.9))])
N["vince"].stride = 3.4
pose("vince", 69.9, "cower"); face("vince", 69.9, "worried")
N["vince"].yaw.append((70.0, fa((-43.0, 6.9), (-36, 6)), "smooth"))
for lab, lag, start, end in (("sheriff", 0.45, SHERIFF, (-37.6, 6.0)), ("mia", 0.75, ROW["mia"], (-33.0, 6.2)),
                             ("rosa", 1.3, ROW["rosa"], (-29.4, 3.4)), ("kai", 1.25, ROW["kai"], (-29.4, 8.8))):
    pts = [(66.3 + lag, start)]
    if lab in ("mia", "kai"):
        pts.append((66.9 + lag, (start[0] - 1.5, 12.4)))
    lane = {"sheriff": 6.0, "mia": 6.2, "kai": 8.8}.get(lab, 6.0)
    pts += [(67.7 + lag, (-18.0, 12.6)), (68.2 + lag, (-24.0, 10.0 if lab != "kai" else 11.0)), (68.9 + lag, (-29.0, lane)), (69.7 + lag * 0.5, end)]
    if lab == "rosa":
        pts = [(66.3 + lag, start), (67.4 + lag, (-24.0, 7.6)), (67.9 + lag, (-26.5, 3.4)), (68.6 + lag, end)]
    walk(lab, pts)
    N[lab].yaw.append((69.9 + lag * 0.5, fa(end, (-43.0, 6.9)), "smooth"))
    face(lab, 66.3, "angry")
for lab in ("oldman", "mayor", "mom", "ana", "tom", "jen", "dan", "lena", "bob", "noob"):
    leave(lab, 67.0)
pose("sheriff", 70.4, "hips"); face("sheriff", 70.4, "smug")
pose("vince", 72.0, "idle"); face("vince", 72.3, "shocked"); face("vince", 73.0, "sad")

# ================================================================ SCENE 9: the twist, 73.6 - end
END = 83.5
MAYOR = (-3.0, 20.6)
put("mayor", 73.6, MAYOR, look=(0, 12))
pose("mayor", 73.6, "give", "hold"); pose("mayor", 74.6, "idle"); face("mayor", 73.6, "grin")
CROWD2 = {"sheriff": (6.9, 16.0), "vince": (2.3, 16.2), "mia": (-2.3, 16.0), "mom": (-6.9, 15.8), "rosa": (-11.5, 15.6),
          "kai": (11.5, 15.6), "ana": (-13.8, 11.4), "jen": (-9.2, 11.3), "dan": (-4.6, 11.2), "oldman": (0.0, 11.0),
          "lena": (4.6, 11.2), "bob": (9.2, 11.3), "tom": (13.8, 11.4), "noob": (18.2, 13.0)}
for lab, xy in CROWD2.items():
    put(lab, 73.6, xy, look=MAYOR)
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
        x, y = -44.0 + 0.3 * u, 6.9 - 0.3 * u
        return (x, y, 3.0 * (1 - u * u) + 0.02)
    if t < 73.6:
        u = ease_out((t - 72.45) / 1.15)
        return (lerp(-43.7, -38.8, u), lerp(6.6, 6.0, u), 0.02 + 0.25 * abs(math.sin(u * 6.0)) * (1 - u))
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
    (0.0, 1.15, (22.6, 18.9, 4.3), (23.0, 18.9, 4.3), (29.6, 18.9, 3.7), (29.6, 18.9, 3.7), 26, "smooth"),
    (1.15, 1.9, (26.6, 21.4, 4.8), (26.9, 21.1, 4.8), (29.4, 17.3, 4.4), (29.4, 17.3, 4.4), 32, "smooth"),
    (1.9, 2.9, (26.8, 16.6, 4.8), (27.0, 16.9, 4.8), (29.9, 20.6, 4.5), (29.9, 20.6, 4.5), 32, "smooth"),
    (2.9, 6.6, (24.2, 14.2, 4.4), (16.0, -12.0, 18.0), (29.4, 17.3, 3.8), (0.0, 16.0, 6.0), 28, "smooth"),
    (6.6, 8.9, (0.0, -25.0, 7.5), (0.0, -21.5, 6.5), (0.0, 0.0, 2.8), (0.0, 2.0, 3.0), 26, "smooth"),
    (8.9, 10.9, (22.4, 17.6, 3.4), (24.0, 17.5, 3.8), (29.4, 17.3, 3.8), (29.4, 17.3, 4.0), 30, "smooth"),
    (10.9, 12.9, ahead("vince", 7.5, 2.0, 28)),
    (12.9, 14.9, (25.6, 6.8, 5.2), (25.8, 6.9, 5.1), (31.8, 8.6, 4.5), (31.8, 8.6, 4.5), 30, "smooth"),
    (14.9, 16.3, (31.2, 11.6, 5.0), (31.1, 11.5, 4.95), (28.5, 8.5, 4.5), (28.5, 8.5, 4.5), 30, "smooth"),
    (16.3, 17.3, (27.0, 11.6, 4.9), (27.1, 11.5, 4.9), (31.8, 8.5, 4.5), (31.8, 8.5, 4.5), 32, "smooth"),
    (17.3, 19.2, (30.2, 1.0, 4.4), (30.2, 1.6, 4.4), (30.2, 8.5, 3.9), (30.2, 8.5, 3.9), 28, "smooth"),
    (19.2, 20.9, (25.4, 12.4, 4.8), (25.6, 12.2, 4.8), (30.2, 8.5, 3.7), (30.2, 8.5, 3.7), 28, "smooth"),
    (20.9, 23.6, follow("vince", (-9.0, -3.5), 4.0, 30, -0.8)),
    (23.6, 25.8, ahead("vince", 5.4, 4.6, 30, side=0.8)),
    (25.8, 27.4, (24.6, 16.2, 4.8), (24.8, 16.5, 4.8), (30.0, 20.0, 4.2), (30.0, 20.0, 4.2), 28, "smooth"),
    (27.4, 29.2, (27.0, -11.6, 4.3), (27.2, -11.8, 4.3), (31.0, -14.8, 3.9), (31.0, -14.8, 3.9), 30, "smooth"),
    (29.2, 30.6, (-8.0, -51.6, 4.6), (-7.6, -51.4, 4.6), (-3.0, -41.6, 3.2), (-6.0, -41.6, 3.2), 28, "smooth"),
    (30.6, 32.3, (-11.6, -40.6, 3.9), (-11.6, -40.9, 3.9), (-11.4, -46.2, 3.5), (-11.4, -46.2, 3.5), 32, "smooth"),
    (32.3, 35.1, (-9.0, -37.6, 4.4), (-9.0, -38.2, 4.3), (-9.0, -46.2, 3.4), (-9.0, -46.2, 3.4), 28, "smooth"),
    (35.1, 37.0, (0.0, -1.0, 5.2), (0.0, 1.5, 5.4), (0.0, 22.0, 6.0), (0.0, 22.0, 5.6), 26, "smooth"),
    (37.0, 38.4, (3.6, 18.8, 5.6), (3.3, 19.1, 5.5), (0.1, 22.2, 4.6), (0.1, 22.2, 4.6), 30, "smooth"),
    (38.4, 39.6, (1.4, 17.4, 4.2), (1.2, 17.9, 4.3), (0.0, 22.5, 4.7), (0.0, 22.5, 4.8), 32, "smooth"),
    (39.6, 41.5, (16.0, -4.0, 8.0), (15.0, -3.0, 7.6), (0.0, 10.0, 3.8), (0.0, 10.5, 3.8), 22, "smooth"),
    cu(41.5, 43.2, "sheriff", (-3.0, 7.0), 6.4, 32),
    cu(43.2, 44.0, "rosa", SHERIFF, 6.3, 32, side=0.8),
    cu(44.0, 44.8, "oldman", SHERIFF, 6.3, 32, side=0.8),
    cu(44.8, 46.2, "mayor", SHERIFF, 6.3, 30, side=0.8, dz=0.3),
    (46.2, 47.2, (4.8, -0.4, 8.2), (4.7, 0.0, 8.0), (0.0, 14.0, 4.4), (0.0, 14.0, 4.4), 26, "smooth"),
    cu(47.2, 49.6, "vince", SHERIFF, 6.2, 32, side=-0.6),
    cu(49.6, 51.1, "mia", ROW["vince"], 5.6, 32, side=1.4, dz=-0.2),
    cu(51.1, 52.0, "vince", ROW["mia"], 5.6, 32, side=-1.4),
    (52.0, 54.8, (3.0, 14.2, 5.0), (3.0, 13.8, 4.9), (3.0, 7.2, 3.9), (3.0, 7.2, 3.9), 26, "smooth"),
    cu(54.8, 56.3, "vince", SHERIFF, 5.8, 34, side=0.5),
    (56.3, 58.5, (3.0, 19.5, 11.0), (3.0, 19.0, 10.6), (1.0, 6.5, 2.8), (1.0, 6.5, 2.8), 24, "smooth"),
    cu(58.5, 60.48, "vince", SHERIFF, 6.6, 34, push_to=5.0),
    (60.48, 62.5, (9.0, -3.0, 7.0), (9.4, -3.4, 7.2), (0.6, 8.0, 3.6), (0.6, 8.0, 3.6), 22, "smooth"),
    cu(62.5, 65.0, "sheriff", ROW["vince"], 6.2, 32, side=0.8),
    cu(65.0, 66.7, "vince", SHERIFF, 6.0, 32, side=0.4),
    (66.7, 69.2, (-6.0, -14.0, 20.0), (-14.0, -14.0, 19.0), (-6.0, 10.0, 2.0), (-32.0, 7.0, 2.0), 26, "smooth"),
    (69.2, 70.4, (-31.0, 5.6, 9.8), (-31.8, 5.8, 9.4), (-41.5, 6.6, 1.4), (-42.6, 6.8, 1.2), 28, "smooth"),
    (70.4, 72.0, (-46.8, 6.0, 4.6), (-46.6, 6.1, 4.5), (-37.0, 6.0, 4.0), (-37.0, 6.0, 4.0), 26, "smooth"),
    (72.0, 73.6, lambda t, u: ((-34.6, 4.6, 1.6), (lan_pos(t)[0], lan_pos(t)[1], max(0.7, min(2.4, lan_pos(t)[2] + 0.6))), 30)),
    (73.6, 75.5, (0.0, 3.0, 8.0), (0.0, 4.5, 8.0), (0.0, 22.0, 5.4), (0.0, 22.0, 5.6), 26, "smooth"),
    cu(75.5, 77.5, "mayor", (0.0, 12.0), 6.3, 32, side=0.6),
    cu(77.5, 79.6, "mayor", (0.0, 12.0), 5.6, 30, side=-0.5, push_to=4.8),
    (79.6, 81.0, (-7.0, 23.0, 8.4), (-6.8, 23.1, 8.2), (1.0, 13.5, 3.6), (1.0, 13.5, 3.6), 24, "smooth"),
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
