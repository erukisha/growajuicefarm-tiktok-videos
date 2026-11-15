import json, soundfile as sf, numpy as np
D = json.load(open("durations.json")); L = {l[0]: l for l in json.load(open("lines.json"))}
# (id, gap before) ; beats: ("@NAME", length)
SEQ = [("N01", 0.15), ("D01", 0.1), ("@GLOW1", 0.55), ("N02", 0.0), ("N03", 0.25), ("N04", 0.2), ("R01", 0.35), ("V01", 0.15),
       ("R02", 0.25), ("V02", 0.2), ("R03", 0.45), ("N05", 0.35), ("M01", 0.45), ("N06", 0.5), ("@THEFT", 2.4),
       ("S01", 0.3), ("R04", 0.15), ("O01", 0.15), ("Y01", 0.15), ("S02", 0.3), ("V03", 0.15), ("M02", 0.35), ("C01", 0.15),
       ("N07", 0.35), ("V04", 0.25), ("@NOGLOW", 1.3), ("S03", 0.0), ("N08", 0.3), ("V05", 0.25), ("Y02", 0.15), ("C02", 0.15),
       ("Y03", 0.3), ("@GLOW2", 1.7), ("N09", 0.0), ("V06", 0.15), ("@END", 2.6)]
t = 0.0; cues = {}; lines = []
for k, g in SEQ:
    if k.startswith("@"):
        cues[k[1:]] = [round(t, 3), round(t + g, 3)]; t += g; continue
    t += g; d = D[k]
    a, sr = sf.read("wav2/%s.wav" % k); hop = sr // 30
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]); m = rms.max() + 1e-9
    mouth = [2 if r > 0.55 * m else (1 if r > 0.18 * m else 0) for r in rms]
    narr = k.startswith("N")
    cues[k] = [round(t, 3), round(t + d, 3)]
    lines.append({"id": k, "who": "narr" if narr else L[k][1], "text": L[k][2], "t": round(t, 3), "d": d, "nt": round(t, 3), "nd": d, "mouth": mouth})
    t += d
TOTAL = round(t, 3)
json.dump({"total": TOTAL, "cues": cues, "lines": lines, "segs": [[0, TOTAL, 0, TOTAL]]}, open("timeline.json", "w"))
print("total", TOTAL); print({k: v for k, v in cues.items()})
