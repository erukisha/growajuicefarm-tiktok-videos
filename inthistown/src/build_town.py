"""The town set for "In this town" (generic Roblox look, nothing from Grow a Juice Farm).
  blender -b --factory-startup --python build_town.py -- <work dir> [views]
Writes <work>/town.blend with the same lights/world names storylib.py expects (Sun, Moon, Fill, MoonBall, world value
nodes Night / Dawn / SkyStrength), 1080x1920 Eevee, a bloom pass for the lie glow.
Layout (x east, y north, 1 unit = 1 stud): plaza centred on 0,0 with the fountain; Town Hall north (steps y 19-24, top
landing z 1.6, Golden Lantern pedestal at 0, 22); east road x 20-30, shops east of it facing west (Bakery y -2..12,
Barber y 15..27); south road y -30..-20; park south of it (bench at -8, -40); west road x -30..-20, houses west of it
with the alley y 4..8 running west to a fence at x -48."""
import bpy, bmesh, os, sys, math, random, mathutils

V = mathutils.Vector
argv = sys.argv[sys.argv.index("--") + 1:]
WORK = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
random.seed(11)


def lin(c):
    return tuple(((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in c)


COLS = {}


def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); sc.collection.children.link(c); COLS[name] = c
    return COLS[name]


MATS = {}


def mat(name, rgb, rough=0.45, metal=0.0, emit=None, kind=None, rgb2=None, scale=1.0):
    key = name
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = lin(rgb) + (1,)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.3
    if emit:
        p.inputs["Emission Color"].default_value = lin(emit[0]) + (1,)
        p.inputs["Emission Strength"].default_value = emit[1]
    if kind:   # Roblox-ish material textures in world space
        tc = nt.nodes.new("ShaderNodeTexCoord")
        if kind == "brick":
            t = nt.nodes.new("ShaderNodeTexBrick")
            t.inputs["Color1"].default_value = lin(rgb) + (1,)
            t.inputs["Color2"].default_value = lin(rgb2 or rgb) + (1,)
            t.inputs["Mortar"].default_value = lin((225, 215, 200)) + (1,)
            t.inputs["Scale"].default_value = 0.9 * scale
            t.inputs["Mortar Size"].default_value = 0.025
            t.inputs["Brick Width"].default_value = 0.9; t.inputs["Row Height"].default_value = 0.35
            nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
            nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
        elif kind == "planks":
            t = nt.nodes.new("ShaderNodeTexWave"); t.wave_type = "BANDS"; t.bands_direction = "Z"
            t.inputs["Scale"].default_value = 0.6 * scale; t.inputs["Distortion"].default_value = 0.0
            r = nt.nodes.new("ShaderNodeValToRGB")
            r.color_ramp.elements[0].color = lin(rgb) + (1,); r.color_ramp.elements[1].color = lin(rgb2 or rgb) + (1,)
            r.color_ramp.interpolation = "CONSTANT"
            nt.links.new(tc.outputs["Object"], t.inputs["Vector"]); nt.links.new(t.outputs["Fac"], r.inputs[0])
            nt.links.new(r.outputs[0], p.inputs["Base Color"])
        elif kind == "tiles":
            t = nt.nodes.new("ShaderNodeTexChecker"); t.inputs["Scale"].default_value = 0.25 * scale
            t.inputs["Color1"].default_value = lin(rgb) + (1,); t.inputs["Color2"].default_value = lin(rgb2 or rgb) + (1,)
            nt.links.new(tc.outputs["Generated"] if False else tc.outputs["Object"], t.inputs["Vector"])
            nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
        elif kind == "noise":
            t = nt.nodes.new("ShaderNodeTexNoise"); t.inputs["Scale"].default_value = 0.08 * scale
            r = nt.nodes.new("ShaderNodeValToRGB")
            r.color_ramp.elements[0].color = lin(rgb) + (1,); r.color_ramp.elements[1].color = lin(rgb2 or rgb) + (1,)
            nt.links.new(tc.outputs["Object"], t.inputs["Vector"]); nt.links.new(t.outputs["Fac"], r.inputs[0])
            nt.links.new(r.outputs[0], p.inputs["Base Color"])
    MATS[key] = m
    return m


def box(name, size, center, m, c="Town", bevel=0.06, rot=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = V((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col(c).objects.link(o)
    o.location = center
    if rot:
        o.rotation_euler = rot
    me.materials.append(m)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    return o


def bx(name, x0, x1, y0, y1, z0, z1, m, c="Town", bevel=0.06):   # box by extents
    return box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m, c, bevel)


def cyl(name, r, h, center, m, c="Town", verts=32, r2=None, rot=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=h)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col(c).objects.link(o)
    o.location = center
    if rot:
        o.rotation_euler = rot
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"
    return o


def ball(name, r, center, m, c="Town", scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col(c).objects.link(o)
    o.location = center; o.scale = scale
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    return o


def text(name, body, size, loc, rot, m, c="Town", extrude=0.08, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = "CENTER"
    try:
        f = bpy.data.fonts.load("C:\\Windows\\Fonts\\arialbd.ttf"); cu.font = f
    except Exception:
        pass
    o = bpy.data.objects.new(name, cu); col(c).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    cu.materials.append(m)
    return o


# ---------------------------------------------------------------- palette
GRASS = mat("Grass", (88, 170, 70), 0.8, kind="noise", rgb2=(70, 150, 58))
ASPH = mat("Asphalt", (70, 72, 78), 0.85, kind="noise", rgb2=(58, 60, 66), scale=4)
WALK = mat("Sidewalk", (196, 196, 190), 0.75, kind="tiles", rgb2=(184, 184, 178), scale=1.0)
PLAZA = mat("Plaza", (222, 206, 172), 0.7, kind="tiles", rgb2=(206, 188, 152), scale=0.8)
LINE = mat("RoadLine", (250, 220, 70), 0.6)
WHITE = mat("White", (245, 245, 240), 0.5)
STONE = mat("Stone", (220, 214, 200), 0.6)
STONE2 = mat("StoneDark", (170, 164, 152), 0.65)
GLASS = mat("Window", (130, 190, 230), 0.08, 0.0)
GLASS_N = mat("WindowNight", (255, 214, 140), 0.3, emit=((255, 196, 110), 0.0))   # lit windows: emission animated at night
WOOD = mat("Wood", (140, 92, 56), 0.7, kind="planks", rgb2=(124, 80, 48), scale=3)
DARK = mat("DarkTrim", (55, 50, 48), 0.6)
ROOF_R = mat("RoofRed", (176, 62, 52), 0.6)
ROOF_B = mat("RoofBlue", (60, 92, 150), 0.6)
ROOF_G = mat("RoofGreen", (70, 120, 80), 0.6)
GOLD = mat("Gold", (255, 196, 60), 0.25, 0.9)
WATER = mat("Water", (90, 170, 230), 0.05, emit=((140, 200, 255), 0.15))
LEAF = mat("Leaves", (70, 160, 70), 0.75, kind="noise", rgb2=(52, 136, 56), scale=6)
TRUNK = mat("Trunk", (110, 76, 50), 0.8)
METAL = mat("LampPost", (40, 44, 50), 0.4, 0.6)
BULB = mat("LampBulb", (255, 236, 190), 0.3, emit=((255, 220, 160), 0.0))

# ---------------------------------------------------------------- ground, roads, plaza
bx("Ground", -300, 300, -300, 300, -0.4, -0.02, GRASS, bevel=0)
bx("RoadE", 20, 30, -80, 19, -0.05, 0.0, ASPH, bevel=0)
bx("RoadW", -30, -20, -80, 19, -0.05, 0.0, ASPH, bevel=0)
bx("RoadS", -80, 80, -30, -20, -0.05, 0.001, ASPH, bevel=0)
bx("RoadN", -80, 80, 44, 54, -0.05, 0.0, ASPH, bevel=0)
for i in range(-14, 4):   # dashed centre lines
    bx("DashE%d" % i, 24.85, 25.15, i * 6, i * 6 + 3, 0.0, 0.02, LINE, bevel=0)
    bx("DashW%d" % i, -25.15, -24.85, i * 6, i * 6 + 3, 0.0, 0.02, LINE, bevel=0)
for i in range(-13, 13):
    bx("DashS%d" % i, i * 6, i * 6 + 3, -25.15, -24.85, 0.001, 0.021, LINE, bevel=0)
bx("Plaza", -20, 20, -20, 19.5, -0.05, 0.05, PLAZA, bevel=0)
for nm, a in (("WalkE", (30, 33, -80, 44)), ("WalkW", (-33, -30, -80, 44)), ("WalkS", (-80, 80, -33, -30))):
    bx(nm, a[0], a[1], a[2], a[3], -0.05, 0.22, WALK, bevel=0.02)
# crosswalk stripes from the plaza to the shops
for i in range(6):
    bx("Cross%d" % i, 20.6, 29.4, 3.0 + i * 1.2, 3.6 + i * 1.2, 0.0, 0.02, WHITE, bevel=0)
    bx("CrossW%d" % i, -29.4, -20.6, 3.0 + i * 1.2, 3.6 + i * 1.2, 0.0, 0.02, WHITE, bevel=0)
    bx("CrossS%d" % i, -6 + i * 2.2, -5 + i * 2.2, -29.4, -20.6, 0.001, 0.021, WHITE, bevel=0)

# ---------------------------------------------------------------- fountain
cyl("FountainRim", 5.2, 1.2, (0, -2, 0.6), STONE, verts=48, bevel=0.15)
cyl("FountainWater", 4.7, 0.2, (0, -2, 1.0), WATER, verts=48)
cyl("FountainStem", 0.9, 3.0, (0, -2, 2.0), STONE)
cyl("FountainBowl", 2.2, 0.5, (0, -2, 3.6), STONE, r2=1.2, rot=(math.pi, 0, 0))
cyl("FountainTop", 0.5, 1.4, (0, -2, 4.4), STONE2)
ball("FountainBall", 0.6, (0, -2, 5.3), GOLD)
for i in range(4):   # benches round the plaza
    a = i * math.pi / 2 + math.pi / 4
    cx, cy = 11 * math.cos(a), -2 + 11 * math.sin(a)
    b = bx("PlazaBench%d" % i, cx - 2, cx + 2, cy - 0.6, cy + 0.6, 1.0, 1.25, WOOD)
    b.rotation_euler = (0, 0, a + math.pi / 2)
    for k, d in enumerate((-1.6, 1.6)):
        lg = box("PlazaBenchLeg%d_%d" % (i, k), (0.25, 1.0, 1.0), (cx + d * math.cos(a + math.pi / 2), cy + d * math.sin(a + math.pi / 2), 0.5), METAL)
        lg.rotation_euler = (0, 0, a + math.pi / 2)

# ---------------------------------------------------------------- Town Hall (north)
TH = mat("TownHallWall", (238, 228, 205), 0.6, kind="brick", rgb2=(228, 216, 190), scale=0.7)
bx("TH_Body", -16, 16, 25, 42, 0, 15, TH)
bx("TH_Base", -16.5, 16.5, 24.5, 42.5, 0, 1.6, STONE2)
for i, z in enumerate((0.4, 0.8, 1.2, 1.6)):   # front steps, y 19..24
    bx("TH_Step%d" % i, -10, 10, 19 + i * 1.25, 24.6, 0, z, STONE, bevel=0.03)
bx("TH_Landing", -10, 10, 23.0, 25.0, 0, 1.6, STONE, bevel=0.03)
for i, x in enumerate((-8.5, -4.5, 4.5, 8.5)):   # columns
    cyl("TH_Col%d" % i, 0.75, 11.8, (x, 23.8, 1.6 + 5.9), WHITE, verts=24)
    bx("TH_ColCap%d" % i, x - 1.0, x + 1.0, 22.8, 24.8, 13.4, 13.9, WHITE)
bx("TH_Porch", -10.5, 10.5, 22.5, 25.2, 13.9, 15.0, WHITE)
# pediment (triangle) over the porch
me = bpy.data.meshes.new("TH_Pediment"); bm = bmesh.new()
pts = [(-11, 22.4, 15), (11, 22.4, 15), (0, 22.4, 20.2), (-11, 25.2, 15), (11, 25.2, 15), (0, 25.2, 20.2)]
vs = [bm.verts.new(p) for p in pts]
for f in ((0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)):
    bm.faces.new([vs[i] for i in f])
bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("TH_Pediment", me); col("Town").objects.link(o); me.materials.append(WHITE)
bx("TH_Roof", -16.5, 16.5, 25, 42.5, 15, 16.2, ROOF_B)
bx("TH_Tower", -3.5, 3.5, 30, 37, 16.2, 24, TH)
bx("TH_TowerRoof", -4, 4, 29.5, 37.5, 24, 24.8, ROOF_B)
cyl("TH_Spire", 3.2, 4.5, (0, 33.5, 27.1), ROOF_B, verts=4, r2=0.05, rot=(0, 0, math.pi / 4))
cyl("TH_Clock", 2.2, 0.3, (0, 29.85, 20.2), WHITE, rot=(math.pi / 2, 0, 0))
cyl("TH_ClockRim", 2.4, 0.2, (0, 29.95, 20.2), GOLD, rot=(math.pi / 2, 0, 0))
bx("TH_HandH", -0.12, 0.12, 29.6, 29.7, 20.2, 21.3, DARK, bevel=0)
bx("TH_HandM", -0.08, 0.08, 29.6, 29.7, 19.0, 20.2, DARK, bevel=0)
bx("TH_Door", -2.6, 2.6, 24.4, 25.05, 1.6, 8.6, WOOD)
bx("TH_DoorTrim", -3.0, 3.0, 24.35, 24.9, 8.6, 9.2, GOLD)
for i, x in enumerate((-13, -6.5, 6.5, 13)):
    for j, z in enumerate((4.0, 10.0)):
        if abs(x) < 7 and j == 0:
            continue
        bx("TH_Win%d_%d" % (i, j), x - 1.3, x + 1.3, 24.9, 25.06, z - 1.8, z + 1.8, GLASS_N, bevel=0.02)
        bx("TH_WinF%d_%d" % (i, j), x - 1.5, x + 1.5, 24.85, 25.0, z - 2.0, z + 2.0, WHITE, bevel=0.02)
text("TH_Sign", "TOWN HALL", 1.5, (0, 22.35, 14.45), (math.pi / 2, 0, 0), GOLD, extrude=0.05)
# the Golden Lantern pedestal on the landing (the lantern itself is built by the scene scripts)
bx("TH_Pedestal", -0.9, 0.9, 21.6, 23.4, 1.6, 4.2, STONE2)
bx("TH_PedestalTop", -1.1, 1.1, 21.4, 23.6, 4.2, 4.5, GOLD)
# flagpoles
for x in (-12, 12):
    cyl("TH_Pole%d" % x, 0.15, 12, (x, 21.0, 6.0), METAL, verts=12)
    bx("TH_Flag%d" % x, x, x + 3.2, 20.95, 21.05, 9.5, 11.6, mat("Flag", (200, 50, 60), 0.7), bevel=0)


# ---------------------------------------------------------------- shops (east side, facing west toward the plaza)
def shop(tag, y0, y1, wall, roof, awn, sign, signc=(255, 255, 255), depth=14, h=10, kind="brick"):
    x0, x1 = 33, 33 + depth
    w = mat(tag + "Wall", wall, 0.6, kind=kind, rgb2=tuple(max(0, c - 18) for c in wall))
    bx(tag + "_Body", x0, x1, y0, y1, 0, h, w)
    bx(tag + "_Roof", x0 - 0.4, x1 + 0.4, y0 - 0.4, y1 + 0.4, h, h + 0.8, roof)
    bx(tag + "_Parapet", x0 - 0.5, x0 + 0.3, y0 - 0.4, y1 + 0.4, h, h + 2.2, roof)
    ym = (y0 + y1) / 2
    # big shop window + door
    bx(tag + "_WinL", x0 - 0.1, x0 + 0.05, y0 + 1.2, ym - 1.6, 1.4, 5.6, GLASS_N, bevel=0.02)
    bx(tag + "_WinR", x0 - 0.1, x0 + 0.05, ym + 1.6, y1 - 1.2, 1.4, 5.6, GLASS_N, bevel=0.02)
    bx(tag + "_Door", x0 - 0.12, x0 + 0.05, ym - 1.3, ym + 1.3, 0.2, 5.4, WOOD)
    bx(tag + "_DoorKnob", x0 - 0.3, x0 - 0.1, ym + 0.8, ym + 1.0, 2.6, 2.8, GOLD, bevel=0)
    bx(tag + "_Sill", x0 - 0.4, x0 + 0.05, y0 + 1.0, y1 - 1.0, 1.1, 1.4, DARK)
    # striped awning
    am1, am2 = mat(tag + "Awn1", awn, 0.7), mat(tag + "Awn2", (250, 250, 250), 0.7)
    n = int((y1 - y0) / 1.4)
    for i in range(n):
        yy = y0 + i * (y1 - y0) / n
        a = box(tag + "_Awn%d" % i, (3.4, (y1 - y0) / n, 0.15), (x0 - 1.5, yy + (y1 - y0) / n / 2, 6.5), am1 if i % 2 else am2, bevel=0)
        a.rotation_euler = (0, math.radians(-22), 0)
    # sign board above the awning
    bx(tag + "_SignBoard", x0 - 0.35, x0 - 0.05, ym - 5, ym + 5, 7.6, 9.6, DARK)
    text(tag + "_Sign", sign, 1.35, (x0 - 0.42, ym, 8.6), (math.pi / 2, 0, -math.pi / 2), mat(tag + "SignTxt", signc, 0.4, emit=(signc, 0.6)), extrude=0.05)
    return x0, ym


shop("Bakery", -4, 12, (250, 214, 200), ROOF_R, (230, 90, 110), "BAKERY", (255, 245, 230), kind="planks")
shop("Barber", 15, 27, (200, 222, 240), ROOF_B, (40, 90, 200), "BARBER", (255, 255, 255))
shop("Shop3", -22, -8, (240, 226, 160), ROOF_G, (60, 160, 90), "GENERAL STORE", (255, 255, 230))
# bakery counter window (Rosa serves through it) and a pie on display
bx("Bakery_Counter", 30.6, 33.2, 6.5, 10.5, 0.2, 2.9, WOOD)
bx("Bakery_CounterTop", 30.3, 33.3, 6.3, 10.7, 2.9, 3.15, mat("CounterTop", (245, 240, 230), 0.4))
# barber pole
cyl("Barber_Pole", 0.35, 3.0, (32.4, 15.6, 4.0), mat("BarberPole", (230, 40, 50), 0.3), verts=16)
ball("Barber_PoleTop", 0.42, (32.4, 15.6, 5.6), GOLD)


# ---------------------------------------------------------------- west side: houses and the alley (y 4..8)
def house(tag, x0, x1, y0, y1, wall, roof, h=9, facing="east", door_y=None):
    w = mat(tag + "Wall", wall, 0.6, kind="planks", rgb2=tuple(max(0, c - 15) for c in wall), scale=1.0)
    bx(tag + "_Body", x0, x1, y0, y1, 0, h, w)
    # gable roof along x
    me = bpy.data.meshes.new(tag + "_Roof"); bm = bmesh.new()
    xm = (x0 + x1) / 2
    pts = [(x0 - 0.6, y0 - 0.6, h), (x1 + 0.6, y0 - 0.6, h), (xm, y0 - 0.6, h + 4.5), (x0 - 0.6, y1 + 0.6, h), (x1 + 0.6, y1 + 0.6, h), (xm, y1 + 0.6, h + 4.5)]
    vs = [bm.verts.new(p) for p in pts]
    for f in ((0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)):
        bm.faces.new([vs[i] for i in f])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(tag + "_Roof", me); col("Town").objects.link(o); me.materials.append(roof)
    fx = x1 if facing == "east" else x0
    sgn = 1 if facing == "east" else -1
    dy = door_y if door_y is not None else (y0 + y1) / 2
    bx(tag + "_Door", fx - 0.05 * sgn - 0.06, fx + 0.06, dy - 1.2, dy + 1.2, 0.2, 5.2, WOOD)
    for i, yy in enumerate((y0 + 2.5, y1 - 2.5)):
        if abs(yy - dy) > 2.5:
            bx(tag + "_Win%d" % i, fx - 0.05, fx + 0.07, yy - 1.1, yy + 1.1, 2.4, 5.0, GLASS_N, bevel=0.02)
        bx(tag + "_UWin%d" % i, fx - 0.05, fx + 0.07, yy - 1.0, yy + 1.0, 6.2, 8.0, GLASS_N, bevel=0.02)


house("HouseW1", -48, -33, 9, 22, (120, 170, 210), ROOF_R, h=10)
house("HouseW2", -48, -33, -12, 3, (240, 190, 120), ROOF_G, h=9)
house("HouseW3", -48, -33, 26, 40, (220, 130, 120), ROOF_B, h=9)
house("HouseW4", -48, -33, -34, -16, (180, 220, 160), ROOF_R, h=9)
# the alley y 4..8: dead end at a tall wooden fence, a dumpster and crates
bx("Alley_Floor", -48, -33, 3, 9, -0.05, 0.03, mat("AlleyFloor", (120, 118, 112), 0.85, kind="noise", rgb2=(104, 100, 96), scale=5), bevel=0)
bx("Alley_Fence", -49.5, -48.5, 2.5, 9.5, 0, 7, WOOD)
bx("Alley_Dumpster", -47.6, -44.4, 3.1, 4.9, 0, 2.6, mat("Dumpster", (60, 120, 80), 0.5))
bx("Alley_DumpLid", -47.7, -44.3, 3.0, 5.0, 2.6, 2.85, mat("DumpLid", (40, 90, 60), 0.5))
for i, (x, y, s) in enumerate(((-42.6, 3.8, 1.4), (-41.2, 3.7, 1.0), (-42.6, 3.8, 0.9))):
    z = 0.7 if i < 2 else 1.4 + 0.45
    bx("Alley_Crate%d" % i, x - s / 2, x + s / 2, y - s / 2, y + s / 2, z - s / 2 if i < 2 else 1.4, z + s / 2 if i < 2 else 1.4 + s, WOOD)

# ---------------------------------------------------------------- park (south): bench, trees, path, a lamp
bx("Park_Path", -30, 12, -44, -40.5, -0.05, 0.04, mat("Path", (200, 180, 140), 0.85, kind="noise", rgb2=(186, 166, 128), scale=3), bevel=0)
bx("Park_Bench", -14.2, -3.8, -46.8, -45.6, 1.1, 1.35, WOOD)
bx("Park_BenchBack", -14.2, -3.8, -47.2, -46.9, 1.35, 2.9, WOOD)
for x in (-13.6, -9.0, -4.4):
    bx("Park_BenchLeg%d" % x, x - 0.15, x + 0.15, -47.0, -45.7, 0, 1.1, METAL)


def tree(tag, x, y, s=1.0):
    cyl(tag + "_Trunk", 0.55 * s, 5 * s, (x, y, 2.5 * s), TRUNK, verts=12)
    ball(tag + "_Leaf1", 3.0 * s, (x, y, 6.5 * s), LEAF)
    ball(tag + "_Leaf2", 2.2 * s, (x + 1.6 * s, y + 0.6 * s, 5.6 * s), LEAF)
    ball(tag + "_Leaf3", 2.0 * s, (x - 1.4 * s, y - 0.8 * s, 5.8 * s), LEAF)


for i, (x, y, s) in enumerate(((-18, -38, 1.0), (-2, -52, 1.2), (8, -36, 0.9), (-26, -54, 1.1), (14, -50, 1.0), (-12, -58, 1.3),
                               (40, -40, 1.0), (55, -10, 1.2), (-60, 20, 1.1), (-58, -20, 1.0), (60, 30, 1.0), (-22, 60, 1.2),
                               (20, 62, 1.1), (-40, 60, 1.0), (45, 60, 1.2), (-17, 30, 0.8), (17, 30, 0.8))):
    tree("Tree%d" % i, x, y, s)
# bushes along the plaza
for i in range(8):
    ball("Bush%d" % i, 1.0, (-18 + i * 5.1 if i < 4 else 2.7 + (i - 4) * 5.1, -18.6, 0.6), LEAF, scale=(1.4, 0.9, 0.8))

# street lamps (bulb emission + point lights are animated by sky())
LAMPS = [(-19, -19), (19, -19), (-19, 17), (19, 17), (31.5, -6), (31.5, 29), (-31.5, 14), (-31.5, -14), (-19, -42.6), (6, -42.6)]
for i, (x, y) in enumerate(LAMPS):
    cyl("LampPost%d" % i, 0.18, 7.0, (x, y, 3.5), METAL, verts=12)
    box("LampHead%d" % i, (0.9, 0.9, 1.0), (x, y, 7.3), METAL)
    ball("LampBulb%d" % i, 0.38, (x, y, 6.8), BULB)

# ---------------------------------------------------------------- background ring of houses + hills (fills the sky edges)
for i in range(18):
    a = i / 18 * 2 * math.pi
    r = 120 + random.uniform(-10, 20)
    x, y = r * math.cos(a), r * math.sin(a)
    w, d, h = random.uniform(10, 18), random.uniform(10, 16), random.uniform(8, 16)
    wc = random.choice([(240, 200, 150), (180, 210, 240), (230, 160, 140), (200, 230, 180), (245, 235, 210)])
    b = box("BG_House%d" % i, (w, d, h), (x, y, h / 2), mat("BG%d" % i, wc, 0.7))
    b.rotation_euler = (0, 0, a)
    rf = box("BG_Roof%d" % i, (w + 1, d + 1, 1.0), (x, y, h + 0.5), random.choice([ROOF_R, ROOF_B, ROOF_G]))
    rf.rotation_euler = (0, 0, a)
for i in range(10):
    a = i / 10 * 2 * math.pi + 0.2
    ball("Hill%d" % i, 60, (230 * math.cos(a), 230 * math.sin(a), -30), mat("Hill", (100, 175, 80), 0.9), scale=(1.6, 1.6, 0.8))
for i in range(30):
    a = random.uniform(0, 2 * math.pi); r = random.uniform(70, 150)
    tree("BGTree%d" % i, r * math.cos(a), r * math.sin(a), random.uniform(1.0, 1.6))

# ---------------------------------------------------------------- props built for the scenes (kept in collection "Props")
# Golden Lantern: on the pedestal at (0, 22.5, 4.5); scene scripts move it (Vince's backpack, the alley)
LAN_GLASS = mat("LanternGlass", (255, 230, 150), 0.1, emit=((255, 200, 90), 3.0))
lan = bpy.data.objects.new("Lantern", None); col("Props").objects.link(lan); lan.location = (0, 22.5, 4.5)
parts = [cyl("Lan_Base", 0.55, 0.22, (0, 0, 0.11), GOLD, "Props", verts=6),
         cyl("Lan_Glass", 0.42, 1.0, (0, 0, 0.72), LAN_GLASS, "Props", verts=6),
         cyl("Lan_Top", 0.55, 0.22, (0, 0, 1.33), GOLD, "Props", verts=6),
         cyl("Lan_Cap", 0.45, 0.45, (0, 0, 1.66), GOLD, "Props", verts=6, r2=0.08),
         cyl("Lan_Ring", 0.2, 0.06, (0, 0, 1.95), GOLD, "Props", rot=(math.pi / 2, 0, 0))]
for k in range(6):
    a = k * math.pi / 3
    parts.append(box("Lan_Bar%d" % k, (0.06, 0.06, 1.0), (0.44 * math.cos(a), 0.44 * math.sin(a), 0.72), GOLD, "Props", bevel=0))
for p in parts:
    p.parent = lan
ll = bpy.data.lights.new("LanternLight", "POINT"); ll.energy = 60; ll.color = lin((255, 200, 110)); ll.shadow_soft_size = 0.5
llo = bpy.data.objects.new("LanternLight", ll); col("Props").objects.link(llo); llo.parent = lan; llo.location = (0, 0, 0.8)
# a pie (the bakery scene)
pie = bpy.data.objects.new("Pie", None); col("Props").objects.link(pie); pie.location = (31.8, 8.5, 3.15)
for p in (cyl("Pie_Tin", 0.75, 0.14, (0, 0, 0.07), mat("Tin", (190, 190, 195), 0.3, 0.8), "Props", r2=0.6),
          cyl("Pie_Crust", 0.7, 0.28, (0, 0, 0.2), mat("Crust", (226, 170, 90), 0.7), "Props", bevel=0.08),
          cyl("Pie_Fill", 0.52, 0.06, (0, 0, 0.35), mat("Cherry", (180, 30, 50), 0.35), "Props")):
    p.parent = pie

# ---------------------------------------------------------------- render settings (same as the juice pipeline's base)
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100
sc.render.fps = 30
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.45
ee = sc.eevee
ee.taa_render_samples = 16
for attr, val in [("use_shadows", True), ("use_raytracing", False), ("shadow_ray_count", 1), ("shadow_step_count", 6),
                  ("use_gtao", True), ("gtao_distance", 2.0), ("fast_gi_distance", 6.0)]:
    try:
        setattr(ee, attr, val)
    except Exception:
        pass
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"

# bloom for the glow (compositor glare); Blender 5 keeps the compositor in a node group
try:
    ng = bpy.data.node_groups.new("TownComp", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    for k, v in (("Type", "Bloom"), ("Quality", "High"), ("Threshold", 1.0), ("Strength", 0.85), ("Size", 0.7), ("Saturation", 1.0)):
        if k in gl.inputs:
            try:
                gl.inputs[k].default_value = v
            except Exception as ex:
                print("GLARE", k, ex)
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.compositing_node_group = ng
    COMP = "group"
except Exception as ex:
    COMP = "none: %r" % ex
print("COMPOSITOR", COMP)

# ---------------------------------------------------------------- sky + lights (names storylib.sky() drives)
w = bpy.data.worlds.new("Town_Sky"); sc.world = w; w.use_nodes = True
nt = w.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputWorld"); bg = nt.nodes.new("ShaderNodeBackground")
geo = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(geo.outputs["Window"], sep.inputs[0])
day = nt.nodes.new("ShaderNodeValToRGB"); night = nt.nodes.new("ShaderNodeValToRGB"); dawn = nt.nodes.new("ShaderNodeValToRGB")
for ramp, lo, hi in [(day, (165, 215, 255), (60, 145, 235)), (night, (30, 36, 84), (8, 10, 30)), (dawn, (255, 170, 110), (90, 120, 200))]:
    ramp.color_ramp.elements[0].color = lin(lo) + (1,); ramp.color_ramp.elements[1].color = lin(hi) + (1,)
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
mix1 = nt.nodes.new("ShaderNodeMix"); mix1.data_type = "RGBA"
mix2 = nt.nodes.new("ShaderNodeMix"); mix2.data_type = "RGBA"
vn = nt.nodes.new("ShaderNodeValue"); vn.name = "Night"; vn.outputs[0].default_value = 0.0
vd = nt.nodes.new("ShaderNodeValue"); vd.name = "Dawn"; vd.outputs[0].default_value = 0.0
nt.links.new(vn.outputs[0], mix1.inputs["Factor"]); nt.links.new(day.outputs["Color"], mix1.inputs[6]); nt.links.new(night.outputs["Color"], mix1.inputs[7])
nt.links.new(vd.outputs[0], mix2.inputs["Factor"]); nt.links.new(mix1.outputs[2], mix2.inputs[6]); nt.links.new(dawn.outputs["Color"], mix2.inputs[7])
vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260.0
nt.links.new(geo.outputs["Window"], vo.inputs["Vector"])
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.035, 0.0
nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
sm = nt.nodes.new("ShaderNodeMath"); sm.operation = "MULTIPLY"
nt.links.new(mr.outputs["Result"], sm.inputs[0]); nt.links.new(vn.outputs[0], sm.inputs[1])
ad = nt.nodes.new("ShaderNodeMix"); ad.data_type = "RGBA"; ad.blend_type = "ADD"; ad.inputs["Factor"].default_value = 1.0
nt.links.new(mix2.outputs[2], ad.inputs[6]); nt.links.new(sm.outputs[0], ad.inputs[7])
nt.links.new(ad.outputs[2], bg.inputs["Color"])
bs = nt.nodes.new("ShaderNodeValue"); bs.name = "SkyStrength"; bs.outputs[0].default_value = 1.0
nt.links.new(bs.outputs[0], bg.inputs["Strength"]); nt.links.new(bg.outputs[0], out.inputs[0])

sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 4.2; sun.angle = math.radians(4); sun.color = lin((255, 244, 228))
so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(48), math.radians(14), math.radians(-30))
moon = bpy.data.lights.new("Moon", "SUN"); moon.energy = 0.0; moon.angle = math.radians(2); moon.color = lin((150, 175, 255))
mo = bpy.data.objects.new("Moon", moon); sc.collection.objects.link(mo); mo.rotation_euler = (math.radians(50), math.radians(-25), math.radians(150))
fill = bpy.data.lights.new("Fill", "SUN"); fill.energy = 0.9; fill.color = lin((200, 220, 255)); fill.use_shadow = False
fo = bpy.data.objects.new("Fill", fill); sc.collection.objects.link(fo); fo.rotation_euler = (math.radians(70), 0, math.radians(180))
mb = ball("MoonBall", 9, (60, 420, 170), mat("MoonMat", (255, 250, 225), 0.5, emit=((255, 250, 225), 3.0)), "Sky")
mb.visible_shadow = False
sc["lamps"] = [list(p) for p in LAMPS]

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORK, "town.blend"))
print("TOWN OK", len(bpy.data.objects))

if len(argv) > 1 and argv[1] == "views":   # a few probe stills of the set
    out = os.path.join(WORK, "views"); os.makedirs(out, exist_ok=True)
    cd = bpy.data.cameras.new("Probe"); cd.sensor_fit = "VERTICAL"; cd.sensor_height = 36
    cam = bpy.data.objects.new("Probe", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.rotation_mode = "QUATERNION"
    sc.render.resolution_percentage = 40
    VIEWS = {"square": ((0, -46, 16), (0, 12, 5), 24), "townhall": ((0, 4, 4.5), (0, 24, 7), 22),
             "bakery": ((22, 9, 4), (33, 7, 3.5), 26), "alley": ((-31, 6, 4), (-48, 6, 2.5), 24),
             "park": ((-8, -34, 4.5), (-8, -46, 2.0), 28), "aerial": ((60, -70, 55), (0, 5, 0), 22)}
    for k, (p, l, lens) in VIEWS.items():
        cam.location = p; cam.rotation_quaternion = (V(l) - V(p)).to_track_quat("-Z", "Y"); cd.lens = lens
        sc.render.filepath = os.path.join(out, k + ".png")
        bpy.ops.render.render(write_still=True)
    print("VIEWS OK")
