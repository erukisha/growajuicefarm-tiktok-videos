"""Generic Roblox NPC library for the "In this town" series (no real avatars).
Blocky R15 bodies (Roblox's classic blocky proportions, smooth plastic), atlas faces switched by the head object's
"face" property, a per-character "Glow" node group (value 0..1 makes the whole body glow gold).
Rig + bone names match the juice pipeline's storylib Person (Root, LowerTorso, UpperTorso, Head, UpperArm.L ...).
  blender -b --factory-startup --python build_npcs.py -- <work dir> [lineup]
Writes <work>/npcs.blend: collection + armature AV_<name> per character (feet at origin, facing +Y, right hand +X)."""
import bpy, bmesh, os, sys, math, mathutils

V = mathutils.Vector
argv = sys.argv[sys.argv.index("--") + 1:]
WORK = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
FACES = os.path.join(WORK, "faces.png")
FACE_IMG = bpy.data.images.load(FACES)
FACE_IMG.pack()

FACE = {"smile": 0, "talk": 1, "talk2": 2, "smug": 3, "worried": 4, "shocked": 5, "angry": 6, "sad": 7, "blink": 8,
        "suspicious": 9, "grin": 10, "neutral": 11}


def lin(c):
    return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)


# ---------------------------------------------------------------- characters
SKIN = {"light": (234, 196, 160), "tan": (204, 152, 110), "brown": (150, 100, 70), "dark": (100, 66, 46),
        "noob": (245, 205, 48), "pale": (245, 215, 190)}
CHARS = {
    "vince":  dict(skin="light", shirt=(110, 70, 190), sleeves="long", pants=(40, 42, 52), shoes=(25, 25, 28),
                   hair=("swoop", (45, 30, 22)), extras=["backpack", "hood"]),
    "mia":    dict(skin="tan", shirt=(255, 205, 60), sleeves="short", pants=(70, 120, 210), shoes=(220, 60, 70),
                   hair=("pigtails", (90, 52, 30)), scale=0.8),
    "mom":    dict(skin="tan", shirt=(70, 170, 110), sleeves="short", pants=(60, 70, 110), shoes=(120, 70, 40),
                   hair=("long", (95, 55, 30))),
    "rosa":   dict(skin="brown", shirt=(250, 250, 250), sleeves="short", pants=(60, 60, 70), shoes=(40, 40, 40),
                   hair=("bun", (30, 22, 18)), hat="chef", extras=["apron"]),
    "sheriff": dict(skin="light", shirt=(196, 160, 104), sleeves="long", pants=(92, 64, 40), shoes=(60, 38, 22),
                    hair=("short", (70, 45, 28)), hat="cowboy", extras=["badge", "mustache", "belt"]),
    "mayor":  dict(skin="pale", shirt=(32, 44, 92), sleeves="long", pants=(32, 44, 92), shoes=(15, 15, 15),
                   hair=("short", (200, 200, 205)), hat="tophat", extras=["tie", "mustache_grey"]),
    "oldman": dict(skin="light", shirt=(150, 150, 160), sleeves="long", pants=(100, 90, 80), shoes=(70, 50, 35),
                   hair=("bald", (230, 230, 230)), extras=["beard", "glasses"]),
    "dan":    dict(skin="dark", shirt=(240, 120, 40), sleeves="short", pants=(50, 80, 140), shoes=(240, 240, 240),
                   hair=("spiky", (25, 20, 18))),
    "bob":    dict(skin="light", shirt=(60, 160, 220), sleeves="short", pants=(90, 90, 100), shoes=(200, 60, 50),
                   hair=("bowl", (230, 160, 40))),
    "noob":   dict(skin="noob", shirt=(13, 105, 172), sleeves="none", pants=(40, 160, 70), shoes=(40, 160, 70),
                   hair=("bald", (0, 0, 0))),
    "jen":    dict(skin="pale", shirt=(240, 110, 170), sleeves="short", pants=(240, 240, 245), shoes=(240, 110, 170),
                   hair=("ponytail", (240, 200, 90))),
    "kai":    dict(skin="brown", shirt=(30, 30, 34), sleeves="short", pants=(160, 130, 90), shoes=(250, 250, 250),
                   hair=("short", (20, 18, 16)), hat="cap", hatc=(220, 50, 50)),
    "lena":   dict(skin="dark", shirt=(160, 90, 220), sleeves="long", pants=(40, 40, 60), shoes=(30, 30, 30),
                   hair=("long", (20, 16, 14))),
    "tom":    dict(skin="tan", shirt=(200, 60, 60), sleeves="short", pants=(60, 60, 70), shoes=(30, 30, 30),
                   hair=("beanie", (70, 120, 90))),
    "ana":    dict(skin="light", shirt=(255, 160, 90), sleeves="short", pants=(80, 140, 200), shoes=(255, 255, 255),
                   hair=("bun", (150, 60, 30))),
}


# ---------------------------------------------------------------- mesh helpers
def link(o, col):
    col.objects.link(o)
    return o


def box(name, size, loc, mat, col, bevel=0.07):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = V((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), col)
    o.location = loc
    me.materials.append(mat)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"
    for p in me.polygons:
        p.use_smooth = True
    return o


def cyl(name, r, h, loc, mat, col, ry=None, bevel=0.0, verts=32, rot=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    if ry:
        for v in bm.verts:
            v.co.y *= ry / r
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), col)
    o.location = loc
    if rot:
        o.rotation_euler = rot
    me.materials.append(mat)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 4; b.limit_method = "ANGLE"
    for p in me.polygons:
        p.use_smooth = True
    return o


def sphere(name, r, loc, mat, col, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=r)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), col)
    o.location = loc; o.scale = scale
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return o


def cone(name, r1, r2, h, loc, mat, col, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r1, radius2=r2, depth=h)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), col)
    o.location = loc; o.rotation_euler = rot
    me.materials.append(mat)
    return o


# ---------------------------------------------------------------- materials (glow via a per-character node group)
def glow_group(lab):
    g = bpy.data.node_groups.new("Glow_" + lab, "ShaderNodeTree")
    g.interface.new_socket("Glow", in_out="OUTPUT", socket_type="NodeSocketFloat")
    out = g.nodes.new("NodeGroupOutput")
    v = g.nodes.new("ShaderNodeValue"); v.name = "GLOW"; v.outputs[0].default_value = 0.0
    g.links.new(v.outputs[0], out.inputs[0])
    return g


GOLD = lin((255, 206, 80))


def plastic(name, rgb, glow, rough=0.42, metal=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = lin(rgb) + (1,)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.35
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = glow; gn.name = "GlowIn"
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1.6
    nt.links.new(gn.outputs[0], mul.inputs[0])
    p.inputs["Emission Color"].default_value = GOLD + (1,)
    if emit:   # a part that is always lit (the lantern flame): add its own emission on top
        add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = emit[1]
        nt.links.new(mul.outputs[0], add.inputs[0]); nt.links.new(add.outputs[0], p.inputs["Emission Strength"])
        p.inputs["Emission Color"].default_value = lin(emit[0]) + (1,)
    else:
        nt.links.new(mul.outputs[0], p.inputs["Emission Strength"])
    return m


def head_mat(name, skin, glow):
    """Skin with the face atlas: cylindrical projection in the head's own space, cell picked by the object's "face"."""
    m = plastic(name, skin, glow)
    nt = m.node_tree; N, L = nt.nodes.new, nt.links.new
    p = nt.nodes["Principled BSDF"]
    tc = N("ShaderNodeTexCoord"); sep = N("ShaderNodeSeparateXYZ"); L(tc.outputs["Object"], sep.inputs[0])
    at = N("ShaderNodeMath"); at.operation = "ARCTAN2"; L(sep.outputs["X"], at.inputs[0]); L(sep.outputs["Y"], at.inputs[1])

    def math(op, a, b=None, val=None):
        n = N("ShaderNodeMath"); n.operation = op
        (L(a, n.inputs[0]) if not isinstance(a, (int, float)) else n.inputs[0].__setattr__("default_value", a))
        if b is not None:
            (L(b, n.inputs[1]) if not isinstance(b, (int, float)) else n.inputs[1].__setattr__("default_value", b))
        return n.outputs[0]
    cu = math("ADD", math("DIVIDE", at.outputs[0], 1.9), 0.5)          # 0..1 across the face (left to right)
    cv = math("ADD", math("DIVIDE", sep.outputs["Z"], 1.15), 0.5)      # 0..1 bottom to top
    attr = N("ShaderNodeAttribute"); attr.attribute_type = "OBJECT"; attr.attribute_name = "face"
    f = math("ROUND", attr.outputs["Fac"])
    col = math("MODULO", f, 4.0)
    row = math("FLOOR", math("DIVIDE", f, 4.0))
    rfb = math("SUBTRACT", 2.0, row)
    u = math("DIVIDE", math("ADD", col, cu), 4.0)
    v = math("DIVIDE", math("ADD", rfb, cv), 3.0)
    cmb = N("ShaderNodeCombineXYZ"); L(u, cmb.inputs[0]); L(v, cmb.inputs[1])
    tex = N("ShaderNodeTexImage"); tex.image = FACE_IMG; tex.extension = "CLIP"; tex.interpolation = "Linear"
    L(cmb.outputs[0], tex.inputs[0])
    # mask: inside the cell and on the front of the head
    inside = math("MULTIPLY", math("MULTIPLY", math("GREATER_THAN", cu, 0.0), math("LESS_THAN", cu, 1.0)),
                  math("MULTIPLY", math("GREATER_THAN", cv, 0.0), math("LESS_THAN", cv, 1.0)))
    front = math("GREATER_THAN", sep.outputs["Y"], 0.0)
    a = math("MULTIPLY", math("MULTIPLY", tex.outputs["Alpha"], inside), front)
    mix = N("ShaderNodeMix"); mix.data_type = "RGBA"
    L(a, mix.inputs["Factor"]); mix.inputs[6].default_value = lin(skin) + (1,); L(tex.outputs["Color"], mix.inputs[7])
    L(mix.outputs[2], p.inputs["Base Color"])
    # features don't glow: scale the emission by (1 - a)
    em = p.inputs["Emission Strength"].links[0].from_socket
    keep = math("MULTIPLY", em, math("SUBTRACT", 1.0, a))
    L(keep, p.inputs["Emission Strength"])
    return m


# ---------------------------------------------------------------- one character
J = {"root": V((0, 0, 2.15)), "waist": V((0, 0, 2.4)), "neck": V((0, 0, 4.02))}
for s, x in ((".L", -1.5), (".R", 1.5)):
    J["shoulder" + s] = V((x, 0, 3.78)); J["elbow" + s] = V((x, 0, 3.05)); J["wrist" + s] = V((x, 0, 2.3))
for s, x in ((".L", -0.5), (".R", 0.5)):
    J["hip" + s] = V((x, 0, 1.95)); J["knee" + s] = V((x, 0, 1.0)); J["ankle" + s] = V((x, 0, 0.22))


def build(lab, c):
    col = bpy.data.collections.new("AV_" + lab); sc.collection.children.link(col)
    glow = glow_group(lab)
    skin = SKIN[c["skin"]]
    mS = plastic("Skin_" + lab, skin, glow)
    mT = plastic("Shirt_" + lab, c["shirt"], glow)
    mP = plastic("Pants_" + lab, c["pants"], glow)
    mF = plastic("Shoes_" + lab, c["shoes"], glow)
    hs, hc = c["hair"]
    mH = plastic("Hair_" + lab, hc, glow, rough=0.6)
    sl = c["sleeves"]
    P = {}
    P["Foot.L"] = box(lab + "_FootL", (0.96, 1.12, 0.26), (-0.5, 0.08, 0.13), mF, col)
    P["Foot.R"] = box(lab + "_FootR", (0.96, 1.12, 0.26), (0.5, 0.08, 0.13), mF, col)
    P["LowerLeg.L"] = box(lab + "_LLegL", (0.96, 0.96, 0.82), (-0.5, 0, 0.62), mP, col)
    P["LowerLeg.R"] = box(lab + "_LLegR", (0.96, 0.96, 0.82), (0.5, 0, 0.62), mP, col)
    P["UpperLeg.L"] = box(lab + "_ULegL", (0.99, 0.99, 1.0), (-0.5, 0, 1.5), mP, col)
    P["UpperLeg.R"] = box(lab + "_ULegR", (0.99, 0.99, 1.0), (0.5, 0, 1.5), mP, col)
    P["LowerTorso"] = box(lab + "_LTorso", (2.0, 1.0, 0.5), (0, 0, 2.2), mP if c.get("tuck", True) else mT, col)
    P["UpperTorso"] = box(lab + "_UTorso", (2.0, 1.0, 1.62), (0, 0, 3.2), mT, col)
    armU = mS if sl == "none" else mT
    armL = mT if sl == "long" else mS
    for s, x in ((".L", -1.5), (".R", 1.5)):
        P["UpperArm" + s] = box(lab + "_UArm" + s, (0.96, 0.96, 0.96), (x, 0, 3.52), armU, col)
        P["LowerArm" + s] = box(lab + "_LArm" + s, (0.92, 0.92, 0.74), (x, 0, 2.68), armL, col)
        P["Hand" + s] = box(lab + "_Hand" + s, (0.9, 0.9, 0.36), (x, 0, 2.15), mS, col)
    head = cyl(lab + "_Head", 0.64, 1.18, (0, 0, 4.63), head_mat("Head_" + lab, skin, glow), col, ry=0.62, bevel=0.3, verts=40)
    head["face"] = 0.0
    P["Head"] = head
    H = 4.63   # head centre
    hp = []   # hair/hat parts -> head bone
    # ---- hair
    if hs in ("short", "swoop", "long", "bun", "pigtails", "ponytail", "spiky"):
        hp.append(cyl(lab + "_HairCap", 0.69, 0.42, (0, -0.02, H + 0.44), mH, col, ry=0.67, bevel=0.18, verts=40))
        hp.append(box(lab + "_HairBack", (1.32, 0.5, 0.95), (0, -0.4, H + 0.12), mH, col, bevel=0.2))
    if hs == "swoop":
        hp.append(box(lab + "_Swoop", (1.05, 0.34, 0.34), (-0.18, 0.5, H + 0.5), mH, col, bevel=0.14))
        hp[-1].rotation_euler = (0, math.radians(-14), 0)
        hp.append(box(lab + "_SwoopTip", (0.46, 0.3, 0.3), (0.42, 0.55, H + 0.28), mH, col, bevel=0.12))
    if hs in ("short", "bun", "ponytail", "pigtails", "long"):
        hp.append(box(lab + "_Fringe", (1.1, 0.22, 0.2), (0, 0.55, H + 0.5), mH, col, bevel=0.08))
    if hs == "long":
        hp.append(box(lab + "_HairLong", (1.36, 0.52, 1.7), (0, -0.36, H - 0.45), mH, col, bevel=0.2))
        for x in (-0.66, 0.66):
            hp.append(box(lab + "_HairSide", (0.18, 0.6, 1.2), (x, 0.0, H - 0.1), mH, col, bevel=0.07))
    if hs == "bun":
        hp.append(sphere(lab + "_Bun", 0.36, (0, -0.42, H + 0.72), mH, col))
    if hs == "ponytail":
        hp.append(cyl(lab + "_Pony", 0.2, 1.1, (0, -0.72, H - 0.15), mH, col, rot=(math.radians(18), 0, 0)))
    if hs == "pigtails":
        for x in (-0.82, 0.82):
            hp.append(sphere(lab + "_Pig", 0.3, (x, -0.15, H + 0.2), mH, col, scale=(1, 1, 1.25)))
    if hs == "spiky":
        for i, (x, y) in enumerate([(-0.4, 0.2), (0, 0.25), (0.4, 0.2), (-0.25, -0.25), (0.25, -0.25), (0, -0.05)]):
            hp.append(cone(lab + "_Spike%d" % i, 0.24, 0.0, 0.55, (x, y, H + 0.8), mH, col,
                           rot=(math.radians(-y * 50), math.radians(x * 40), 0)))
    if hs == "bowl":
        hp.append(cyl(lab + "_Bowl", 0.71, 0.62, (0, 0, H + 0.36), mH, col, ry=0.69, bevel=0.2, verts=40))
        hp.append(box(lab + "_BowlEdge", (1.44, 1.42, 0.12), (0, 0, H + 0.1), mH, col, bevel=0.05))
    if hs == "beanie":
        mB = plastic("Beanie_" + lab, hc, glow, rough=0.8)
        hp.append(cyl(lab + "_Beanie", 0.7, 0.62, (0, 0, H + 0.42), mB, col, ry=0.68, bevel=0.22, verts=40))
        hp.append(sphere(lab + "_Pom", 0.18, (0, 0, H + 0.86), mB, col))
    # ---- hats
    hat = c.get("hat")
    if hat == "chef":
        mW = plastic("Chef_" + lab, (252, 252, 252), glow, rough=0.7)
        hp.append(cyl(lab + "_ChefBand", 0.7, 0.32, (0, 0, H + 0.62), mW, col, ry=0.68))
        hp.append(sphere(lab + "_ChefPuff", 0.62, (0, 0, H + 1.02), mW, col, scale=(1.15, 1.1, 0.75)))
    if hat == "cowboy":
        mC = plastic("Hat_" + lab, (150, 100, 55), glow, rough=0.7)
        hp.append(cyl(lab + "_Brim", 1.15, 0.08, (0, 0, H + 0.6), mC, col, ry=1.05, bevel=0.03))
        hp.append(cyl(lab + "_Crown", 0.62, 0.62, (0, 0, H + 0.92), mC, col, ry=0.58, bevel=0.14))
        hp.append(cyl(lab + "_HatBand", 0.635, 0.14, (0, 0, H + 0.68), plastic("Band_" + lab, (60, 35, 20), glow), col, ry=0.595))
    if hat == "tophat":
        mK = plastic("Top_" + lab, (20, 20, 24), glow, rough=0.3)
        hp.append(cyl(lab + "_TBrim", 0.95, 0.07, (0, 0, H + 0.6), mK, col, ry=0.9, bevel=0.03))
        hp.append(cyl(lab + "_TCrown", 0.6, 1.0, (0, 0, H + 1.12), mK, col, ry=0.56))
        hp.append(cyl(lab + "_TBand", 0.61, 0.16, (0, 0, H + 0.72), plastic("TBand_" + lab, (170, 30, 40), glow), col, ry=0.57))
    if hat == "cap":
        mC = plastic("Cap_" + lab, c.get("hatc", (200, 40, 40)), glow)
        hp.append(cyl(lab + "_CapTop", 0.7, 0.4, (0, -0.02, H + 0.48), mC, col, ry=0.68, bevel=0.18, verts=40))
        hp.append(box(lab + "_Visor", (1.0, 0.7, 0.07), (0, 0.78, H + 0.36), mC, col, bevel=0.03))
    # ---- extras
    ex = c.get("extras", [])
    torso_x = []
    if "apron" in ex:
        mA = plastic("Apron_" + lab, (255, 255, 255), glow, rough=0.75)
        torso_x.append(box(lab + "_Apron", (1.6, 0.06, 1.9), (0, 0.53, 2.65), mA, col, bevel=0.02))
    if "badge" in ex:
        mG = plastic("Gold_" + lab, (255, 200, 60), glow, rough=0.25, metal=0.8)
        st = cone(lab + "_Badge", 0.26, 0.26, 0.06, (-0.55, 0.53, 3.5), mG, col, rot=(math.radians(90), 0, 0))
        st.data.polygons  # 16-gon stand-in for a star, reads as a badge at this size
        torso_x.append(st)
    if "belt" in ex:
        torso_x.append(box(lab + "_Belt", (2.04, 1.04, 0.18), (0, 0, 2.42), plastic("Belt_" + lab, (50, 30, 18), glow), col, bevel=0.02))
    if "tie" in ex:
        mR = plastic("Tie_" + lab, (190, 30, 40), glow)
        torso_x.append(box(lab + "_Tie", (0.28, 0.05, 1.1), (0, 0.52, 3.35), mR, col, bevel=0.03))
        torso_x.append(box(lab + "_Collar", (0.9, 0.05, 0.22), (0, 0.52, 3.92), plastic("Collar_" + lab, (250, 250, 250), glow), col, bevel=0.02))
    if "backpack" in ex:
        mB = plastic("Pack_" + lab, (40, 110, 90), glow, rough=0.7)
        torso_x.append(box(lab + "_Pack", (1.5, 0.7, 1.45), (0, -0.85, 3.05), mB, col, bevel=0.15))
        torso_x.append(box(lab + "_PackFlap", (1.3, 0.12, 0.5), (0, -1.22, 3.4), mB, col, bevel=0.05))
    if "hood" in ex:
        torso_x.append(box(lab + "_Hood", (1.4, 0.55, 0.32), (0, -0.4, 4.0), mT, col, bevel=0.12))
    for nm, rgb in (("mustache", c["hair"][1]), ("mustache_grey", (215, 215, 220))):
        if nm in ex:
            mM = plastic("Must_" + lab, rgb, glow, rough=0.7)
            hp.append(box(lab + "_Must", (0.62, 0.12, 0.13), (0, 0.63, H - 0.1), mM, col, bevel=0.05))
    if "beard" in ex:
        mBd = plastic("Beard_" + lab, (235, 235, 238), glow, rough=0.8)
        hp.append(box(lab + "_Beard", (1.0, 0.3, 0.55), (0, 0.5, H - 0.5), mBd, col, bevel=0.18))
    if "glasses" in ex:
        mK = plastic("Glass_" + lab, (25, 25, 30), glow)
        for x in (-0.24, 0.24):
            g = cyl(lab + "_Lens", 0.16, 0.04, (x, 0.645, H + 0.1), mK, col, rot=(math.radians(90), 0, 0))
            hp.append(g)
        hp.append(box(lab + "_Bridge", (0.18, 0.04, 0.04), (0, 0.65, H + 0.12), mK, col, bevel=0))
    # ---- armature (same bone names as storylib's Person)
    up = V((0, 0, 1))
    B = {"Root": (J["root"], J["root"] + up * 0.4, None),
         "LowerTorso": (J["root"], J["waist"], "Root"),
         "UpperTorso": (J["waist"], J["neck"], "LowerTorso"),
         "Head": (J["neck"], J["neck"] + up * 1.2, "UpperTorso")}
    for s in (".L", ".R"):
        B["UpperArm" + s] = (J["shoulder" + s], J["elbow" + s], "UpperTorso")
        B["LowerArm" + s] = (J["elbow" + s], J["wrist" + s], "UpperArm" + s)
        B["Hand" + s] = (J["wrist" + s], J["wrist" + s] - up * 0.4, "LowerArm" + s)
        B["UpperLeg" + s] = (J["hip" + s], J["knee" + s], "LowerTorso")
        B["LowerLeg" + s] = (J["knee" + s], J["ankle" + s], "UpperLeg" + s)
        B["Foot" + s] = (J["ankle" + s], J["ankle" + s] + V((0, 0.35, -0.2)), "LowerLeg" + s)
    ad = bpy.data.armatures.new("AVRig_" + lab)
    arm = link(bpy.data.objects.new("AV_" + lab, ad), col)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for n, (h, t, p) in B.items():
        eb = ad.edit_bones.new(n); eb.head, eb.tail = h, t; eb.roll = 0
        if p:
            eb.parent = ad.edit_bones[p]; eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()

    def bone_parent(o, bone):
        mw = o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = bone
        o.matrix_world = mw
    for n, o in P.items():
        bone_parent(o, n)
    for o in hp:
        bone_parent(o, "Head")
    for o in torso_x:
        bone_parent(o, "UpperTorso")
    for o in col.objects:
        if o.type == "MESH":
            o.name = "AVp_%s_%s" % (lab, o.name)
    arm["glow_group"] = glow.name
    arm["head"] = head.name
    s = c.get("scale", 1.0)
    arm["npc_scale"] = s
    col.hide_render = True
    return arm


for lab, c in CHARS.items():
    build(lab, c)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORK, "npcs.blend"))
print("NPCS OK", len(CHARS))

if len(argv) > 1 and argv[1] == "lineup":
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.68, 0.85, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sun = bpy.data.lights.new("S", "SUN"); sun.energy = 3.2
    so = bpy.data.objects.new("S", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(25))
    for i, lab in enumerate(CHARS):
        bpy.data.collections["AV_" + lab].hide_render = False
        a = bpy.data.objects["AV_" + lab]
        a.location = (-(i % 8) * 3.6, 0, -(i // 8) * 7.0)
        s = a["npc_scale"]; a.scale = (s, s, s)
    # one face each, and one of them glowing, to check the shaders
    for i, lab in enumerate(CHARS):
        bpy.data.objects[bpy.data.objects["AV_" + lab]["head"]]["face"] = float(i % 12)
    bpy.data.node_groups["Glow_dan"].nodes["GLOW"].outputs[0].default_value = 1.0
    cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"; cd.ortho_scale = 30
    cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (-12.6, 40, -0.6); cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1000
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform = "Standard"
    sc.render.filepath = os.path.join(WORK, "npc_lineup.png")
    bpy.ops.render.render(write_still=True)
    print("LINEUP OK")
