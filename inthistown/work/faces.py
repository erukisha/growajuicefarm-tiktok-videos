# Face atlas for the generic Roblox NPCs: 4 x 3 cells of 256 px (drawn at 4x, downsampled). Index = row*4+col.
from PIL import Image, ImageDraw
S = 1024; W, H = 4 * S, 3 * S
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
K = (20, 20, 22, 255); RED = (120, 20, 30, 255); WH = (255, 255, 255, 255); TONG = (215, 80, 90, 255)
NAMES = ["smile", "talk", "talk2", "smug", "worried", "shocked", "angry", "sad", "blink", "suspicious", "grin", "neutral"]

def cell(i):
    return (i % 4) * S, (i // 4) * S

def P(i, x, y):  # cell-normalized -> pixels
    ox, oy = cell(i); return ox + x * S, oy + y * S

def eye(i, cx, cy, w=0.075, h=0.16, lid=0.0):
    x0, y0 = P(i, cx - w / 2, cy - h / 2); x1, y1 = P(i, cx + w / 2, cy + h / 2)
    d.ellipse([x0, y0, x1, y1], fill=K)
    if lid > 0:  # cover the top part (half-closed)
        d.rectangle([x0 - 6, y0 - 6, x1 + 6, y0 + (y1 - y0) * lid], fill=(0, 0, 0, 0))
    hx, hy = P(i, cx - w * 0.12, cy - h * 0.22)
    if lid < 0.45:
        r = S * 0.016; d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=WH)

def eyes(i, y=0.40, sep=0.13, **k):
    eye(i, 0.5 - sep, y, **k); eye(i, 0.5 + sep, y, **k)

def arc(i, cx, cy, w, h, a0, a1, width=0.028):
    x0, y0 = P(i, cx - w / 2, cy - h / 2); x1, y1 = P(i, cx + w / 2, cy + h / 2)
    d.arc([x0, y0, x1, y1], a0, a1, fill=K, width=int(S * width))

def line(i, pts, width=0.026):
    d.line([P(i, *p) for p in pts], fill=K, width=int(S * width), joint="curve")
    for p in (pts[0], pts[-1]):
        x, y = P(i, *p); r = S * width / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=K)

def brow(i, x0, y0, x1, y1, width=0.03):
    line(i, [(x0, y0), (x1, y1)], width)

def open_mouth(i, cx, cy, w, h, teeth=True):
    x0, y0 = P(i, cx - w / 2, cy - h / 2); x1, y1 = P(i, cx + w / 2, cy + h / 2)
    d.chord([x0, y0 - (y1 - y0), x1, y1], 0, 180, fill=K)
    d.chord([x0 + 14, y0 - (y1 - y0) + 14, x1 - 14, y1 - 14], 0, 180, fill=RED)
    tx0, ty0 = P(i, cx - w * 0.22, cy + h * 0.15); tx1, ty1 = P(i, cx + w * 0.22, cy + h * 0.5 - 0.01)
    d.ellipse([tx0, ty0, tx1, ty1], fill=TONG)
    if teeth:
        d.rectangle([x0 + 30, y0 - 2, x1 - 30, y0 + (y1 - y0) * 0.22], fill=WH)

def o_mouth(i, cx, cy, w, h):
    x0, y0 = P(i, cx - w / 2, cy - h / 2); x1, y1 = P(i, cx + w / 2, cy + h / 2)
    d.ellipse([x0, y0, x1, y1], fill=K)
    d.ellipse([x0 + 12, y0 + 12, x1 - 12, y1 - 12], fill=RED)

def sweat(i, cx, cy):
    x, y = P(i, cx, cy); r = S * 0.045
    d.polygon([(x, y - r * 2.1), (x - r * 0.95, y - r * 0.1), (x + r * 0.95, y - r * 0.1)], fill=(120, 200, 255, 255))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 200, 255, 255))
    d.ellipse([x - r * 0.45, y - r * 0.6, x - r * 0.05, y - r * 0.1], fill=WH)

# 0 smile
eyes(0); arc(0, 0.5, 0.60, 0.36, 0.20, 20, 160)
# 1 talk (open)
eyes(1); open_mouth(1, 0.5, 0.63, 0.30, 0.16)
# 2 talk2 (small open)
eyes(2); o_mouth(2, 0.5, 0.66, 0.16, 0.10)
# 3 smug
eye(3, 0.37, 0.41, lid=0.45); eye(3, 0.63, 0.41, lid=0.45)
brow(3, 0.30, 0.27, 0.44, 0.30); brow(3, 0.56, 0.25, 0.70, 0.21)
line(3, [(0.36, 0.64), (0.50, 0.65), (0.60, 0.62), (0.67, 0.57)])
# 4 worried + sweat
eyes(4, y=0.42, h=0.15)
brow(4, 0.30, 0.27, 0.44, 0.22); brow(4, 0.56, 0.22, 0.70, 0.27)
line(4, [(0.38, 0.67), (0.44, 0.64), (0.50, 0.67), (0.56, 0.64), (0.62, 0.67)], 0.022)
sweat(4, 0.80, 0.30)
# 5 shocked
eyes(5, y=0.40, w=0.10, h=0.20)
brow(5, 0.30, 0.20, 0.44, 0.18); brow(5, 0.56, 0.18, 0.70, 0.20)
o_mouth(5, 0.5, 0.68, 0.17, 0.20)
# 6 angry
eyes(6, y=0.43, h=0.14)
brow(6, 0.29, 0.27, 0.45, 0.34, 0.035); brow(6, 0.55, 0.34, 0.71, 0.27, 0.035)
arc(6, 0.5, 0.72, 0.30, 0.16, 200, 340)
# 7 sad
eyes(7, y=0.43, h=0.14)
brow(7, 0.30, 0.30, 0.44, 0.25); brow(7, 0.56, 0.25, 0.70, 0.30)
arc(7, 0.5, 0.72, 0.28, 0.14, 205, 335)
# 8 blink (smile)
arc(8, 0.37, 0.43, 0.11, 0.08, 200, 340, 0.026); arc(8, 0.63, 0.43, 0.11, 0.08, 200, 340, 0.026)
arc(8, 0.5, 0.60, 0.36, 0.20, 20, 160)
# 9 suspicious
eye(9, 0.37, 0.42, lid=0.55); eye(9, 0.63, 0.42, lid=0.55)
brow(9, 0.29, 0.31, 0.45, 0.33, 0.032); brow(9, 0.55, 0.30, 0.71, 0.28, 0.032)
line(9, [(0.40, 0.66), (0.60, 0.66)])
# 10 grin (wide, teeth)
eyes(10, y=0.40)
x0, y0 = P(10, 0.30, 0.56); x1, y1 = P(10, 0.70, 0.74)
d.chord([x0, y0 - (y1 - y0), x1, y1], 0, 180, fill=K)
d.chord([x0 + 14, y0 - (y1 - y0) + 14, x1 - 14, y1 - 14], 0, 180, fill=WH)
d.line([P(10, 0.32, 0.59), P(10, 0.68, 0.59)], fill=K, width=10)
# 11 neutral
eyes(11); line(11, [(0.41, 0.64), (0.59, 0.64)])

img = img.resize((W // 4, H // 4), Image.LANCZOS)
img.save("faces.png", optimize=True)
prev = Image.new("RGBA", img.size, (214, 170, 130, 255)); prev.alpha_composite(img); prev.save("faces_preview.png")
print("ok", img.size)
