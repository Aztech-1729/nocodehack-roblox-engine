# Changelog

Every fix to the NoCodeHack Roblox Engine, newest first: what you saw, why it happened, what changed, and how it was tested.
Found a problem? Open an issue or comment on the video, it lands here.

## 1.4.1 · 2026-11-15 · "Washed-out" drafts explained

**What you saw:** in the draft, night close-ups looked blown out: grey hair, pale faces.

**Why:** the draft is a fast preview with approximate light. The same frame in the real render looks right (brown hair,
normal face). Claude was judging, and showing you, the draft as if it were final.

**What changed:** the skill now tells Claude never to judge light from the draft. It renders one real frame of the
scene (about a minute) before changing colours or light, and tells you the draft is a rough preview.

**Tested:** the washed-out close-up from a test story rendered at `mid`: correct colours in 14 seconds.

## 1.4.0 · 2026-11-15 · Anime fights get the real flame aura

**What you saw:** in Dragon Ball style fights the power-up aura was a plain glowing ball, not the flames in the README clips.

**Why:** the flame sprites are Roblox Creator Store images, so they are not stored in this repo, and the setup never
downloaded them. Without them the engine falls back to simple glow spheres.

**What changed:** `python tools/fetch_library.py public` now also downloads the 14 aura sprites from Roblox's public
image service (no Roblox Studio needed), and `status` shows an `aura` line. When the engine updates, Claude re-runs any
missing setup step by itself.

**Tested:** clean install without the sprites: 14/14 downloaded, all pixel-identical to the ones used for the README clips.

## 1.3.0 · 2026-11-15 · More camera moments: Claude writes richer stories and fixes its own draft

**What you saw:** flat Shorts: few shots, characters standing still, a dark silhouette, odd framing, "no camera moments".

**Why:** the engine's camera cuts on actions: reactions, entrances, props, big emotions. A first story written from the
skill had 9 beats and 7 shots for two scenes, so the camera had little to cut to. The skill also only said "look at the
draft", so Claude saw problems and stopped there.

**What changed (SKILL.md):**
- "Make it look good": a beat every 1-1.5 s, a reaction to every line, an entrance, a prop the hero looks at or grabs (the
  engine adds a close-up on it), one big emotion beat per scene (the engine adds an extreme close-up), 4-6 faces per
  character, shirts that contrast with the yellow skin, readable night colours.
- "Draft fix loop": Claude lists what is wrong in the draft frames and fixes it with the engine's own keys (opening
  framing, faces under hair, silhouettes, backs of heads, fights from behind), up to 3 rounds, and tells you what it fixed.

**Tested:** the same idea ("kid sneaks cookies at night, dad catches him") written before and after the rules.
Before: 9 beats, 15 camera shots. After: 15 beats, 20 camera shots, an entrance through the door, readable dad, 8+ faces.

| Before | After |
|---|---|
| <img src="docs/img/changelog/1.3.0_before.jpg" width="400"> | <img src="docs/img/changelog/1.3.0_after.jpg" width="400"> |

## 1.2.0 · 2026-11-15 · Claude tells you when a new version is out

**What you saw:** nothing. Fixes were published on GitHub, but the skill on your PC stayed old and nobody told you.

**Why:** the plugin on your PC only updates when you update it, and the skill never checked for a newer version.

**What changed:** at the start of every session the skill reads one tiny public file from this repo (the version number;
nothing about you is sent). If a newer version is out, Claude tells you once, with the update command and a link to this
changelog. Offline or GitHub down: it skips the check and carries on.

**Tested:** older copy -> `UPDATE 1.1.0 (you have 1.0.0)`; same version -> `OK 1.1.0`; no network -> `OK (no check)`.

## 1.1.0 · 2026-11-14 · Hair setup now gets all 49 Roblox hairs (was 14)

**What you saw:** after the Roblox Studio setup step, many hairs were missing (characters fell back to plain hair), and
some characters wore the wrong hair.

**Why:** the setup grabs each hair from Roblox Studio's download cache. It only looked at files written in the 1-2 seconds
while each hair loaded, so a hair Studio had already downloaded before was missed. In that time slot it also took the
biggest mesh it saw, which could belong to another hair (a Super Saiyan hair got a 35,826-vertex mesh instead of its own
5,607), and the first texture it saw, sometimes a blurry 64 px copy.

**What changed:**
- The hair step now searches Studio's whole cache. Each mesh is recognised by its exact vertex and triangle count, each
  texture by a tiny 16x16 fingerprint and its original size (stored as numbers in the manifest; no Roblox files ship).
- A mesh from the time slot is only accepted if its shape matches; a wrong texture is replaced.
- If the cache only holds a low-res texture, the public Roblox thumbnail is used instead.
- `hair_qa.py` and `outfit_qa.py` no longer crash on a fresh install.
- Running the step twice is now safe.

**Tested:** clean install, real setup steps through Roblox Studio: 49/49 hairs. All 49 meshes have the same vertices as
the reference library, 46/49 textures are pixel-identical (2 differ by about 1/255, one is 700 px instead of 1000 px),
and all 49 sit correctly on the head in the hair check sheet.

- Already installed? The hair step now repairs old installs: a hair with the wrong mesh is detected (vertex count) and
  replaced. Tested on a simulated old install: 2 wrong meshes replaced, 10 missing hairs restored, 49/49.
- The skill now updates your project's engine copy by itself when a new version is out (your stories, fetched Roblox
  files and `.env` are kept), and links this changelog.

**How to get it:** run `/plugin marketplace update nocodehack-roblox-engine`, then use the skill as usual. Claude updates
your engine and asks you to open Roblox Studio for the hair step again (about 2 minutes).
