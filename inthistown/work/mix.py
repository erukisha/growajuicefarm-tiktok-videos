import json, sys, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/tiktok-factory/engine")
import sfx
SR = 48000
TL = json.load(open("timeline.json")); T = TL["total"]
N = int(T * SR) + SR
dia = np.zeros(N); fx = np.zeros(N); mus = np.zeros(N)
def put(buf, t, x, g=1.0):
    i = int(t * SR); x = np.asarray(x) * g; j = min(N, i + len(x)); buf[i:j] += x[:j - i]
for ln in TL["lines"]:
    a, sr = sf.read("wav/%s.wav" % ln["id"]); assert sr == SR
    put(dia, ln["t"], a)
# ---------------- sfx
def murmur(d, seed=3):
    rng = np.random.default_rng(seed); n = int(d * SR)
    x = sfx._band(rng.standard_normal(n), 250, 1400, 2)
    am = np.interp(np.arange(n), np.linspace(0, n, int(d * 9) + 2), rng.uniform(0.2, 1.0, int(d * 9) + 2))
    env = np.minimum(1, np.minimum(np.arange(n) / (0.25 * SR), (n - np.arange(n)) / (0.4 * SR)))
    return sfx._fin(x * am * env)
def glow_snd():
    return np.concatenate([sfx.sparkle(0.9)]) 
put(fx, 1.1, sfx.sparkle(0.9), 0.5); put(fx, 1.1, sfx.twinkle(), 0.35)
for t in (2.85, 10.85, 25.75, 27.35, 29.15, 66.65, 73.55):
    put(fx, t, sfx.whoosh(0.34), 0.22)
put(fx, 12.85, sfx.swish(), 0.2)
put(fx, 20.35, sfx.pop(), 0.35)
put(fx, 16.35, sfx.blip(), 0.15)
put(fx, 35.05, sfx.rumble(0.9), 0.35)
put(fx, 37.45, sfx.swish(), 0.35)
put(fx, 38.0, sfx.thump(), 0.25)
put(fx, 39.55, sfx.ding(1318.0), 0.18)
put(fx, 43.15, sfx.tick(), 0.25); put(fx, 43.95, sfx.tick(), 0.25); put(fx, 44.75, sfx.tick(), 0.25)
put(fx, 49.35, murmur(1.6), 0.28)
put(fx, 56.25, murmur(2.2, 5), 0.3)
for i in range(4):
    put(fx, 58.6 + i * 0.45, sfx.heartbeat(), 0.45)
put(fx, 59.2, sfx.riser(1.25), 0.35)
put(fx, 60.42, sfx.boom(), 0.6); put(fx, 60.44, sfx.sparkle(1.2), 0.55); put(fx, 60.44, sfx.zap(), 0.3)
put(fx, 62.45, sfx.ding(880.0), 0.15)
put(fx, 66.25, sfx.swish(), 0.35)
for k in range(13):   # running feet
    put(fx, 66.4 + k * 0.27, sfx.thump(), 0.16)
put(fx, 69.9, sfx.thud(), 0.3)
put(fx, 72.0, sfx.swish(), 0.25); put(fx, 72.45, sfx.thud(), 0.4); put(fx, 72.47, sfx.ding(2093.0), 0.25)
for k in range(5):
    put(fx, 72.6 + k * 0.18, sfx.tick(), 0.18)
put(fx, 77.5, sfx.scratch(), 0.5)
put(fx, 77.65, sfx.sparkle(1.4), 0.5); put(fx, 77.65, sfx.twinkle(), 0.3)
put(fx, 80.95, sfx.boom(), 0.35)
# ---------------- music (synthesized here: our own audio)
def ks(f, d, decay=0.996, bright=0.5, seed=0):
    n = int(d * SR); p = max(2, int(SR / f)); rng = np.random.default_rng(seed)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * (bright * buf[i % p] + (1 - bright) * buf[(i + 1) % p]) if True else 0
    return out
_cache = {}
def pluck(f, d=0.6, decay=0.994):
    k = (round(f, 2), d, decay)
    if k not in _cache:
        x = ks(f, d, decay, 0.5, int(f)); x *= np.exp(-np.arange(len(x)) / (SR * d * 0.5)); _cache[k] = x / (np.abs(x).max() + 1e-9)
    return _cache[k]
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def pad(freqs, d, seed=0):
    t = np.arange(int(d * SR)) / SR
    x = sum(np.sin(2 * np.pi * f * t + i) + 0.4 * np.sin(2 * np.pi * f * 2.003 * t) for i, f in enumerate(freqs))
    env = np.minimum(1, np.minimum(t / 0.8, (d - t) / 0.8))
    return x * env / len(freqs)
def kick():
    t = np.arange(int(0.25 * SR)) / SR; return np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
def hat(seed=1):
    t = np.arange(int(0.05 * SR)) / SR; return sfx._hp(np.random.default_rng(seed).standard_normal(len(t)), 7000) * np.exp(-t * 80)
PROG = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]   # C G Am F
def theme(t0, t1, bpm=112, gain=1.0, drums=True, oct_=0):
    b = 60 / bpm; t = t0; i = 0
    while t < t1 - 0.05:
        ch = PROG[(i // 8) % 4]
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        put(mus, t, pluck(note(ch[pat[i % 8]] + 12 + oct_), 0.5), 0.22 * gain)
        if i % 4 == 0:
            put(mus, t, pluck(note(ch[0] - 12 + oct_), 0.9, 0.997), 0.35 * gain)
        if drums:
            if i % 4 == 0: put(mus, t, kick(), 0.35 * gain)
            if i % 2 == 1: put(mus, t, hat(i), 0.08 * gain)
        t += b / 2; i += 1
theme(0.0, 35.0, 112, 1.0)
# night: sneaky low pizzicato in A minor
b = 60 / 96
for i, m in enumerate([45, 48, 52, 48, 45, 47, 48, 51, 52, 51, 48, 47] * 1):
    tt = 35.15 + i * b / 2
    if tt < 39.5: put(mus, tt, pluck(note(m), 0.35, 0.99), 0.45)
# meeting: low pad + clock tick
put(mus, 39.6, pad([note(45), note(52), note(57)], 16.8), 0.18)
for k in range(int((56.2 - 39.8) / 0.8)):
    put(mus, 39.8 + k * 0.8, sfx.tick(), 0.05)
put(mus, 56.3, pad([note(46), note(53), note(58)], 2.4), 0.22)
# chase
theme(65.1, 73.5, 150, 1.0, True, 2)
# reprise until the scratch
theme(73.6, 77.5, 112, 0.8)
put(mus, 78.0, pad([note(44), note(51), note(56), note(59)], 5.5), 0.2)
mix = dia * 1.0 + fx * 0.9 + mus * 0.55
mix = mix[: int((T + 0.2) * SR)]
mix /= max(1.0, np.abs(mix).max() / 0.95)
sf.write("ep1_mix.wav", mix, SR)
print("ok", len(mix) / SR)
