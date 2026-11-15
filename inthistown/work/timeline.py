import json, soundfile as sf, numpy as np
D = json.load(open("durations.json"))
L = {l[0]: l for l in json.load(open("lines.json"))}
START = {"L01": 0.3, "L02": 1.9, "L03": 2.9, "L04": 6.8, "L05": 11.0, "L06": 13.0, "L07": 15.0, "L08": 16.4, "L09": 17.4,
         "L10": 19.4, "L11": 21.0, "L12": 26.0, "L13": 27.6, "L14": 29.4, "L15": 32.4, "L16": 35.3, "L17": 39.8, "L18": 43.3,
         "L19": 44.0, "L20": 44.9, "L21": 46.3, "L22": 47.3, "L23": 49.7, "L24": 51.2, "L25": 52.1, "L26": 54.9, "L27": 56.4,
         "L28": 58.8, "L29": 62.6, "L30": 65.2, "L31": 67.0, "L32": 70.4, "L33": 73.8, "L34": 80.6}
TOTAL = 83.5
out = {"total": TOTAL, "lines": []}
prev_end = 0
for lid in sorted(START):
    s, d = START[lid], D[lid]
    assert s >= prev_end - 0.01, (lid, s, prev_end)
    prev_end = s + d
    a, sr = sf.read("wav/%s.wav" % lid)
    hop = sr // 30
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
    m = rms.max() + 1e-9
    mouth = [2 if r > 0.55 * m else (1 if r > 0.18 * m else 0) for r in rms]
    out["lines"].append({"id": lid, "who": L[lid][1], "text": L[lid][2], "t": s, "d": round(d, 3), "mouth": mouth})
print("last end", prev_end, "total", TOTAL)
json.dump(out, open("timeline.json", "w"))
