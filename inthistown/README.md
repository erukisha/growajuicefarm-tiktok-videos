# "In this town" — Roblox-style story series (separate from Grow a Juice Farm)

Each episode is 60+ seconds, made fully in Blender with generic blocky Roblox NPCs (no real avatars, no juice-game assets).

`src/` holds the source the PC's Blender downloads (work dir `C:\Users\eruki\Videos\inthistown`):

- `faces.png` — face atlas (12 expressions: smile, talk, talk2, smug, worried, shocked, angry, sad, blink, suspicious, grin, neutral)
- `build_npcs.py` → `npcs.blend`: 15 generic NPCs (`AV_<name>`), storylib-compatible rigs, per-character `Glow_<name>` node group (the lie glow)
- `build_town.py` → `town.blend`: plaza + fountain, Town Hall (Golden Lantern pedestal), Bakery, Barber, General Store, houses + alley, park; sky/lights named like storylib expects; bloom
- `townlib.py` — storylib (from the juice pipeline) + `NPC` class: faces, lip flap from line audio, blinks, glow; flat town ground
- `ep1.py` + `ep1_timeline.json` — Episode 1 "The Golden Lantern" (83.5 s)
- `ep1_audio.m4a`, `captions.webm` — mixed audio (Kokoro voices + synthesized SFX/music) and the caption overlay

Cast voices (Kokoro): narrator am_michael, Vince am_puck, Mia af_sky +3.5 st, Mom af_bella, Rosa af_heart, Sheriff am_onyx −0.5 st,
Mayor bm_lewis, Old man bm_george −1.5 st, Dan am_eric, Bob am_liam.
