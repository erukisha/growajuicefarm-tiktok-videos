import json, subprocess, os, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/tts/models/kokoro-v1.0.onnx", "/home/claude/tts/models/voices-v1.0.bin")
VO = {"nar": ("am_adam", 3), "dan": ("am_eric", 0), "bob": ("am_liam", 0), "vince": ("am_adam", 3), "rosa": ("af_heart", 0),
      "mia": ("af_sky", 3.5), "mom": ("af_bella", 0), "sheriff": ("am_onyx", -0.5), "mayor": ("bm_lewis", 0.5),
      "oldman": ("bm_george", -1.5), "crowd": ("am_fenrir", 0)}
CROWD = ["am_fenrir", "af_nicole", "am_eric", "af_heart", "bm_george", "am_liam"]
lines = json.load(open("lines.json")); out = {}
os.makedirs("wav2", exist_ok=True)
def proc(raw, dst, semis, speed=1.0):
    r = 2 ** (semis / 12)
    af = "asetrate=24000*%f,aresample=48000,atempo=%f," % (r, speed / r) if semis else "aresample=48000,"
    af += "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-16:TP=-1.5"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "1", dst], check=True)
for lid, who, text, spd in lines:
    if who == "crowd":
        mix = None
        for i, v in enumerate(CROWD):
            a, sr = k.create(text, voice=v, speed=spd * (0.95 + 0.04 * i), lang="en-us")
            pad = np.zeros(int(sr * 0.03 * i)); a = np.concatenate([pad, a])
            mix = a if mix is None else (np.pad(mix, (0, max(0, len(a) - len(mix)))) + np.pad(a, (0, max(0, len(mix) - len(a)))))
        # say it twice
        gap = np.zeros(int(sr * 0.25)); mix = np.concatenate([mix, gap, mix]) / len(CROWD) * 2.2
        sf.write("raw.wav", mix, sr)
        proc("raw.wav", "wav2/%s.wav" % lid, 0)
    else:
        v, semis = VO[who]
        a, sr = k.create(text.replace("Roblox", "Rowblox"), voice=v, speed=spd, lang="en-us")
        sf.write("raw.wav", a, sr)
        proc("raw.wav", "wav2/%s.wav" % lid, semis, 1.15 if who == "vince" else 1.0)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "wav2/%s.wav" % lid], capture_output=True, text=True).stdout)
    out[lid] = round(d, 3)
json.dump(out, open("durations.json", "w"), indent=0)
print(out, sum(out.values()))
