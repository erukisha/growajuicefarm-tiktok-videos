"""Toolkit for the "In this town" episodes: storylib.py (the juice pipeline's animation core: Person, camera, sky, baking)
on top of town.blend, with the generic NPCs from npcs.blend. A scene script does
    exec(open(os.path.join(WORK, "townlib.py")).read())
then setup(total), builds actors with NPC(...), camera(...), finish(name).
Extra over storylib: faces (expression keys + lip flap from the line audio + blinks), the lie glow, flat town ground."""
import os
exec(open(os.path.join(WORK, "storylib.py")).read())

FACE = {"smile": 0, "talk": 1, "talk2": 2, "smug": 3, "worried": 4, "shocked": 5, "angry": 6, "sad": 7, "blink": 8,
        "suspicious": 9, "grin": 10, "neutral": 11}
OPEN_EYES = {"smile", "worried", "shocked", "angry", "sad", "grin", "neutral", "talk", "talk2"}


# ---------------------------------------------------------------- town ground (no ray casts: awnings and counters)
def ground_at(x, y):
    if abs(x) < 10 and 19.0 <= y < 25.0:              # Town Hall steps
        if y < 20.25:
            return 0.4
        if y < 21.5:
            return 0.8
        if y < 22.75:
            return 1.2
        return 1.6
    if abs(x) < 20 and -20 < y < 19.5:
        return 0.05
    if (30 < abs(x) < 33 and y < 44) or (-33 < y < -30 and abs(x) < 80):
        return 0.22
    if -44 <= y <= -40.5 and -30 <= x <= 12:
        return 0.04
    return 0.0


def ground_warm():
    pass


def cast(label):
    append_collection(os.path.join(WORK, "npcs.blend"), "AV_" + label)
    arm = D["AV_" + label]
    arm.location = (0, 0, 0); arm.rotation_euler = (0, 0, 0)
    arm["r6"] = False
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm


POSES.update({
    "hips": {"UpperArm.L": (10, 35, 0), "UpperArm.R": (10, -35, 0), "LowerArm.L": (20, 0, -60), "LowerArm.R": (20, 0, 60)},
    "think": {"UpperArm.L": (40, 12, 0), "LowerArm.L": (95, 0, 0), "UpperArm.R": (75, -10, 0), "LowerArm.R": (110, 0, 20),
              "Head": (-6, 10, 0)},
    "give": {"UpperArm.L": (0, 7, 0), "UpperArm.R": (70, -4, 0), "LowerArm.R": (15, 0, 0), "UpperTorso": (8, 0, 0)},
    "carry": {"UpperArm.L": (0, 7, 0), "UpperArm.R": (45, -8, 0), "LowerArm.R": (60, 0, 0)},
    "sneak": {"UpperArm.L": (30, 15, 0), "UpperArm.R": (30, -15, 0), "LowerArm.L": (50, 0, 0), "LowerArm.R": (50, 0, 0),
              "UpperTorso": (22, 0, 0), "Head": (-10, 0, 0), "UpperLeg.L": (15, 0, 0), "UpperLeg.R": (15, 0, 0),
              "LowerLeg.L": (-25, 0, 0), "LowerLeg.R": (-25, 0, 0)},
    "grab": {"UpperArm.L": (0, 7, 0), "UpperArm.R": (100, -5, 0), "LowerArm.R": (10, 0, 0), "UpperTorso": (14, 0, 0)},
    "sit": {"UpperArm.L": (10, 5, 0), "UpperArm.R": (10, -5, 0), "LowerArm.L": (40, 0, 0), "LowerArm.R": (40, 0, 0),
            "UpperLeg.L": (90, 0, 0), "UpperLeg.R": (90, 0, 0), "LowerLeg.L": (-90, 0, 0), "LowerLeg.R": (-90, 0, 0)},
    "sit_point": {"UpperArm.L": (10, 5, 0), "UpperArm.R": (85, 0, -12), "LowerArm.L": (40, 0, 0),
                  "UpperLeg.L": (90, 0, 0), "UpperLeg.R": (90, 0, 0), "LowerLeg.L": (-90, 0, 0), "LowerLeg.R": (-90, 0, 0)},
    "cower": {"UpperArm.L": (120, 25, 0), "UpperArm.R": (120, -25, 0), "LowerArm.L": (70, 0, 0), "LowerArm.R": (70, 0, 0),
              "UpperTorso": (18, 0, 0), "Head": (14, 0, 0), "UpperLeg.L": (25, 0, 0), "UpperLeg.R": (25, 0, 0),
              "LowerLeg.L": (-40, 0, 0), "LowerLeg.R": (-40, 0, 0)},
    "cuffs": {"UpperArm.L": (-20, 20, 0), "UpperArm.R": (-20, -20, 0), "LowerArm.L": (10, 0, 0), "LowerArm.R": (10, 0, 0),
              "Head": (12, 0, 0), "UpperTorso": (6, 0, 0)},
})


class NPC(Person):
    """Person from npcs.blend plus a face track, lip flap and the glow. faces: [(t, name)] (held until the next key);
    glow: [(t, value, ease)] 0..1 (1 = full lie glow)."""
    def __init__(self, label, at=(0, 0), yaw=0.0, weapon=None):
        Person.__init__(self, label, weapon)
        self.label = label
        self.head = D[self.arm["head"]]
        self.glowg = bpy.data.node_groups[self.arm["glow_group"]]
        self.faces = [(0, "smile")]
        self.glow = None
        self.path = [(0, at, "linear")]
        self.yaw = [(0, yaw, "linear")]
        self.blink_seed = sum(ord(c) for c in label)
        s = self.arm.get("npc_scale", 1.0)
        if s != 1.0:
            self.scale = [(0, s, "linear")]

    def speed(self, t):
        a, b = V(self.pos(t - 0.05)), V(self.pos(t + 0.05))
        v = (b - a).length / 0.1
        return 0.0 if v > 40 else v   # teleports at cuts don't walk

    def bake(self):
        Person.bake(self)
        keys = sorted(self.faces, key=lambda k: k[0])
        rnd = random.Random(self.blink_seed)
        blinks, t = [], rnd.uniform(0.5, 3)
        while t < TOTAL:
            blinks.append(t); t += rnd.uniform(2.2, 4.8)
        speaking = [ln for ln in LINES if ln["who"] == self.label]

        def base(t):
            f = keys[0][1]
            for k in keys:
                if k[0] <= t:
                    f = k[1]
            return f

        def face(t):
            b = base(t)
            for ln in speaking:
                if ln["t"] <= t < ln["t"] + ln["d"]:
                    i = int((t - ln["t"]) * FPS)
                    m = ln["mouth"][i] if i < len(ln["mouth"]) else 0
                    if m and b not in ("blink",):
                        if b in ("worried", "shocked", "sad", "angry"):
                            return FACE["talk2"] if m == 1 else FACE["shocked" if b == "shocked" else "talk"]
                        return FACE["talk2"] if m == 1 else FACE["talk"]
            if b in OPEN_EYES and any(bt <= t < bt + 0.12 for bt in blinks):
                return FACE["blink"]
            return FACE[b]
        track(self.head, '["face"]', 0, face)
        if self.glow:
            gc = Curve(self.glow)
            track(self.glowg, 'nodes["GLOW"].outputs[0].default_value', 0,
                  lambda t: max(0.0, gc(t)) * (1 + 0.06 * math.sin(t * 9.0)))
            ld = bpy.data.lights.new("GlowL_" + self.label, "POINT"); ld.color = lin((255, 206, 90)); ld.shadow_soft_size = 2.0
            lo = bpy.data.objects.new("GlowL_" + self.label, ld); sc.collection.objects.link(lo)
            lo.parent = self.arm; lo.location = (0, 0.6, 3.4)
            track(ld, "energy", 0, lambda t: 70.0 * max(0.0, gc(t)))


def lamps_on(night):
    """Street lamps, lit windows and bulbs follow the night curve."""
    lamps = []
    for (x, y) in sc.get("lamps", []):
        lamps.append(((x, y, 6.2), (255, 214, 150), lambda t: 700.0 * night(t)))
    for mname, k in (("LampBulb", 8.0), ("WindowNight", 2.2)):
        m = bpy.data.materials.get(mname)
        if m:
            track(m.node_tree, 'nodes["Principled BSDF"].inputs["Emission Strength"].default_value', 0, lambda t, k=k: k * night(t))
    return lamps


def glare_on():
    ng = getattr(sc, "compositing_node_group", None)
    if ng:
        for n in ng.nodes:
            if n.bl_idname == "CompositorNodeGlare":
                n.inputs["Type"].default_value = "Bloom"
                for k, v in (("Threshold", 1.6), ("Strength", 0.45), ("Size", 0.5)):
                    n.inputs[k].default_value = v
        sc.render.use_compositing = True
