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

## Genre notes (studied 2026-11-15, after the user said v2 "feels off")
- The first spoken line IS the rule, from frame 0: "In this town, ..." No cold open.
- One main voice tells it, usually the main character in first person (here: Vince, Kokoro am_adam +3 st 1.15x, the
  user's pick). Other characters get short lines only.
- Three beats: the rule -> the disaster -> the twist. The twist recasts earlier scenes / uses a loophole in the rule /
  turns the hero's flaw into the solution. Plant clues (ep1: the thief's top hat, the Mayor answering with a question).
- Root for the hero; comedy with a bit of warmth; tight gaps (0.1-0.35 s), the longest pause right before the twist.
- Episode 1 v3 = `ep1b.py` (67.7 s): told by Vince; the town blames the question-liar, he tells the truth and doesn't
  glow, then catches the Mayor with his own trick.
