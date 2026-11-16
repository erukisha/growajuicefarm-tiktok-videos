import json, sys, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/tiktok-factory/engine"); import sfx
exec(open("/home/claude/itt/ep1/mix.py").read().split("# ---------------- sfx")[0].split("TL = json.load")[0])
SR = 48000; TL = json.load(open("timeline.json")); T = TL["total"]; C = TL["cues"]
S = lambda k: C[k][0]; E = lambda k: C[k][1]
N = int(T * SR) + SR
dia = np.zeros(N); fx = np.zeros(N); mus = np.zeros(N)
def put(buf, t, x, g=1.0):
    i = int(t * SR); x = np.asarray(x) * g; j = min(N, i + len(x)); buf[i:j] += x[:j - i]
for ln in TL["lines"]:
    a, sr = sf.read("wav2/%s.wav" % ln["id"]); put(dia, ln["t"], a)
src = open("/home/claude/itt/ep1/mix.py").read()
exec(src[src.index("def murmur"):src.index("def glow_snd")])
exec(src[src.index("def ks("):src.index("theme(0.0, 35.0")])
GL = E("Y03")
put(fx, E("D01") - 0.05, sfx.sparkle(0.9), 0.5); put(fx, E("D01") - 0.05, sfx.twinkle(), 0.35)
for t in (S("N03") - 0.05, S("R01") - 0.2, S("M01") - 0.5, S("S01") - 0.35):
    put(fx, t, sfx.whoosh(0.34), 0.22)
put(fx, S("N04") + 1.4, sfx.ding(1568.0), 0.18)          # "a question can't be a lie"
put(fx, S("R03") + 0.9, sfx.pop(), 0.35)
put(fx, S("N05") + 0.1, sfx.cash(), 0.25)
put(fx, S("N06"), sfx.rumble(0.9), 0.35)
G = S("THEFT") + 0.25
put(fx, G, sfx.swish(), 0.35); put(fx, G + 0.6, sfx.thump(), 0.2)
put(fx, S("Y01") + 0.3, sfx.blip(), 0.12)
put(fx, S("M02") - 0.1, sfx.swish(), 0.25)
put(fx, S("C01") - 0.1, murmur(2.0, 5), 0.3)
for i in range(4): put(fx, S("V04") - 1.8 + i * 0.45, sfx.heartbeat(), 0.45)
put(fx, E("V04") + 0.15, sfx.slide(False), 0.2)            # silence... nothing happens
put(fx, S("N08") + 0.4, sfx.riser(1.5), 0.25)
put(fx, S("C02") - 0.1, murmur(2.0, 7), 0.3)
for i in range(3): put(fx, S("Y03") - 1.2 + i * 0.45, sfx.heartbeat(), 0.45)
put(fx, GL, sfx.boom(), 0.6); put(fx, GL + 0.02, sfx.sparkle(1.2), 0.55); put(fx, GL + 0.02, sfx.zap(), 0.3)
put(fx, GL + 0.2, sfx.boing(), 0.35); put(fx, GL + 0.8, sfx.thud(), 0.3); put(fx, GL + 0.82, sfx.ding(2093.0), 0.25)
put(fx, S("V06") + 0.75, sfx.twinkle(), 0.35)
# music
def mput(t, x, g): put(mus, t, x, g)
_put = put
def put(buf, t, x, g=1.0): _put(buf, t, x, g)
theme(0.0, S("N06") - 0.1, 112, 0.9)
b = 60 / 96
for i, mm in enumerate([45, 48, 52, 48, 45, 47, 48, 51, 52, 51, 48, 47, 45, 48, 52, 48]):
    tt = S("N06") + i * b / 2
    if tt < S("S01") - 0.4: mput(tt, pluck(note(mm), 0.35, 0.99), 0.45)
mput(S("S01") - 0.3, pad([note(45), note(52), note(57)], S("N07") - S("S01") + 0.3), 0.18)
k = 0
while S("S01") + k * 0.8 < S("N07"):
    mput(S("S01") + k * 0.8, sfx.tick(), 0.05); k += 1
mput(S("N07"), pad([note(43), note(50), note(55)], E("V04") - S("N07")), 0.2)
mput(S("N08"), pad([note(46), note(53), note(58)], GL - S("N08")), 0.2)
theme(E("GLOW2") - 0.2, T, 120, 0.8)
mix = dia + fx * 0.9 + mus * 0.55
mix = mix[: int((T + 0.2) * SR)]; mix /= max(1.0, np.abs(mix).max() / 0.95)
sf.write("mix.wav", mix, SR); print("ok", len(mix) / SR)
