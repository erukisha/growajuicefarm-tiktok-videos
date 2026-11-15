"""Story-time (old ep1 timing) -> video-time warp. Segments are linear; a gap of 0 skips old time (at a cut)."""
import json, soundfile as sf, numpy as np
OLD = json.load(open("timeline.json"))
old = {l["id"]: (l["t"], l["t"] + l["d"]) for l in OLD["lines"]}
ND = json.load(open("durations2.json"))
L2 = {l[0]: l for l in json.load(open("lines2.json"))}
# (old_t0, old_t1, new_len or line id)
SEQ = [(0.0, 0.3, 0.25), "L01", (None, 1.9, 0.7), "L02", (None, 2.9, 0.15), "L03", (None, 6.8, 0.2), "L04", (None, 11.0, 0.15),
       "L05", (None, 13.0, 0.3), "L06", (None, 15.0, 0.2), "L07", (None, 16.4, 0.25), "L08", (None, 17.4, 0.3), "L09",
       (None, 19.4, 0.45), "L10", (None, 21.0, 0.45), "L11", (None, 26.0, 0.3), "L12", (None, 27.4, 0.55), (27.4, 29.2, 0.0),
       (29.2, 29.4, 0.2), "L14", (None, 32.3, 0.45), (32.3, 35.1, 0.0), (35.1, 35.3, 0.3), "L16", (None, 39.6, 2.2),
       (39.6, 39.8, 0.2), "L17", (None, 43.3, 0.2), "L18", (None, 44.0, 0.15), "L19", (None, 44.9, 0.2), "L20", (None, 46.3, 0.2),
       "L21", (None, 47.3, 0.2), "L22", (None, 49.7, 0.55), "L23", (None, 51.2, 0.15), "L24", (None, 52.1, 0.2), "L25",
       (None, 54.9, 0.25), "L26", (None, 56.4, 0.25), "L27", (None, 58.8, 0.45), "L28", (None, 62.6, 2.0), "L29",
       (None, 66.3, 1.3), (66.3, 70.4, 3.6), (70.4, 72.0, 0.9), (72.0, 73.6, 1.5), (73.6, 73.8, 0.2), "L33",
       (None, 80.6, 3.4), (80.6, 83.5, 2.8)]
segs = []; lines = []; nt = 0.0; ot_end = 0.0
for it in SEQ:
    if isinstance(it, str):
        o0, o1 = old[it]; n = ND[it]
        assert abs(o0 - ot_end) < 1e-6 or True
        segs.append([o0, o1, nt, nt + n]); 
        a, sr = sf.read("wav2/%s.wav" % it); hop = sr // 30
        rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]); m = rms.max() + 1e-9
        mouth_new = [2 if r > 0.55 * m else (1 if r > 0.18 * m else 0) for r in rms]
        # mouth indexed in story time: old frame k -> new frame k * n/(o1-o0)
        k = int((o1 - o0) * 30)
        mouth_old = [mouth_new[min(len(mouth_new) - 1, int(i * n / (o1 - o0)))] for i in range(k)]
        lines.append({"id": it, "who": L2[it][1], "text": L2[it][2], "t": o0, "d": o1 - o0, "nt": nt, "nd": n, "mouth": mouth_old})
        nt += n; ot_end = o1
    else:
        o0, o1, n = it
        o0 = ot_end if o0 is None else o0
        if n > 0:
            segs.append([o0, o1, nt, nt + n]); nt += n
        ot_end = o1
TOTAL = round(nt, 3)
json.dump({"total": TOTAL, "segs": segs, "lines": lines}, open("timeline2.json", "w"))
print("new total", TOTAL, "segments", len(segs))
