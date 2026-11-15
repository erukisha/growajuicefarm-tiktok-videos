"""Caption + title overlay for ep1 as a transparent VP9 webm (1080x1920, 30 fps)."""
import json, os, re, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
TL = json.load(open("timeline.json")); T = TL["total"]; FPS = 30; Wd, Hd = 1080, 1920
F = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
fcap = ImageFont.truetype(F, 74); fhook = ImageFont.truetype(F, 92); fend = ImageFont.truetype(F, 120)
YEL = (255, 214, 64, 255); WH = (255, 255, 255, 255); BK = (0, 0, 0, 255)
# chunks: (t0, t1, [(word, w0, w1)])
chunks = []
for ln in TL["lines"]:
    words = ln["text"].replace("...", "… ").split()
    words = [w for w in words if w.strip("…")]
    wts = [len(w) + 2 for w in words]; tot = sum(wts); t = ln["t"]; timed = []
    for w, k in zip(words, wts):
        d = ln["d"] * k / tot; timed.append((w.strip("…").upper() if False else w.strip("…"), t, t + d)); t += d
    i = 0
    while i < len(timed):
        n = 3 if len(timed) - i != 4 else 4
        grp = timed[i:i + n]; i += n
        chunks.append((grp[0][1], grp[-1][2] + 0.08, grp))
def text_img(draw, xy, s, font, fill, stroke=10):
    draw.text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=BK, anchor="mm")
def frame(t):
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im); drew = False
    if t < 2.85:   # hook
        a = 1.0
        for k, line in enumerate(["EVERY LIE", "MAKES YOU GLOW"]):
            text_img(d, (Wd / 2, 300 + k * 110), line, fhook, YEL if k else WH, 12)
        drew = True
    if t >= 81.0:   # end card
        text_img(d, (Wd / 2, 780), "WHO ELSE", fend, WH, 14); text_img(d, (Wd / 2, 920), "IS LYING?", fend, YEL, 14)
        text_img(d, (Wd / 2, 1080), "Part 2 soon", fcap, WH, 9)
        return im, True
    for c0, c1, grp in chunks:
        if c0 <= t < c1:
            words = [g[0] for g in grp]
            widths = [d.textlength(w + " ", font=fcap) for w in words]
            x = Wd / 2 - sum(widths) / 2
            for (w, w0, w1), wd in zip(grp, widths):
                col = YEL if w0 <= t < w1 + 0.05 else WH
                d.text((x, 1340), w, font=fcap, fill=col, stroke_width=9, stroke_fill=BK, anchor="lm")
                x += wd
            drew = True
    return im, drew
os.makedirs("capfr", exist_ok=True)
nF = int(T * FPS); prev = None; blank = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
blank.save("capfr/blank.png")
lst = open("capfr/list.txt", "w")
for f in range(nF):
    t = f / FPS
    im, drew = frame(t)
    key = im.tobytes() if drew else b""
    if key != prev:
        name = "capfr/f%05d.png" % f
        (im if drew else blank).save(name); cur = name; prev = key
    lst.write("file '%s'\nduration %.6f\n" % (os.path.basename(cur), 1 / FPS))
lst.write("file '%s'\n" % os.path.basename(cur)); lst.close()
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "capfr/list.txt", "-r", "30",
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-row-mt", "1", "-deadline", "good", "-cpu-used", "4",
                "captions.webm"], check=True)
print("ok", os.path.getsize("captions.webm"))
