# Changelog

Every fix to the NoCodeHack Roblox Engine, newest first: what you saw, why it happened, what changed, and how it was tested.
Found a problem? Open an issue or comment on the video, it lands here.

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
