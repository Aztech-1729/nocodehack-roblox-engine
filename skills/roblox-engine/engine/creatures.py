"""creatures.py - big creatures and custom models in a story (scene key `creatures`): a dragon, a monster, a robot, a car...
Kinds (SKILL.md "New assets": Claude tries 1, then 2):
  'rbx:<slug>'  1) a Creator Store model fetched ONCE through Roblox Studio into assets/rbxsets/<id>_<slug> (the same import as Roblox
                   sets: tools/fetch_library.py model <id> <slug>), reused by every later story
  'dragon' ...  2) a part-built blocky model made here, no Studio needed (KINDS: dragon.py, the rest beasts.py)
Movement type `moves` (MOVES; beasts.py has the motion): a part-built kind has its own (DEFAULT); a Creator Store model gets it
once at import (python tools/rbx_set_import.py moves <slug> <type> -> creature.json), a story can override it.
A creature is registered like a prop: shots `on: ["Dragon"]`, `look: "Dragon"`, walks away from it all work by its name.
  {"name": "Dragon", "kind": "dragon", "at": [0, 0], "yaw": 180, "scale": 1, "color": "#3FA34D",
   "path": [{"t": 0, "at": [0, 40], "z": 30}, {"t": 2.0, "at": [0, 0], "z": 0}],    # flies / walks between points (studs, seconds)
   "flap": [0, 3.0], "hover": [2.0, 6.0], "roar": [[2.4, 3.2]]}                     # [from, to] seconds; flap/roar only on part-built kinds
"""
import math
import bpy

S = 0.5
KINDS = ('dragon', 'ogre', 'wolf', 'snake', 'spider', 'ghost')   # part-built kinds; everything else is 'rbx:<slug>'
MOVES = ('biped', 'quadruped', 'flyer', 'slither', 'crawler', 'floater')
DEFAULT = {'dragon': 'flyer', 'ogre': 'biped', 'wolf': 'quadruped', 'snake': 'slither', 'spider': 'crawler', 'ghost': 'floater'}


def moves(c):
    """Movement type: the story's `moves`, else the one saved with the Creator Store model, else the part-built kind's own."""
    kind = str(c.get('kind', 'dragon'))
    if c.get('moves'): return c['moves']
    if kind.startswith('rbx:'):
        import json, os, sets
        try: f = os.path.join(sets.rbx_dir(kind[4:]), 'creature.json')
        except KeyError: return None
        if not os.path.exists(f): return None
        try: return json.load(open(f, encoding='utf-8')).get('moves')   # a truncated/hand-edited file degrades to 'path only'
        except (OSError, ValueError, AttributeError): return None       # (the build must not die on saved data it wrote itself)
    return DEFAULT.get(kind)


def _subject(root):
    """The mesh the camera frames (camera.py measures bound_box): the biggest mesh under root."""
    ms = [o for o in root.children_recursive if o.type == 'MESH']
    vol = lambda o: math.prod(max(c[i] for c in o.bound_box) - min(c[i] for c in o.bound_box) for i in range(3)) * math.prod(o.matrix_world.to_scale())
    return max(ms, key=vol) if ms else root


def make(c):
    """Place one creature (story dict) at frame 0. Returns (root empty, subject mesh for the camera)."""
    name, kind = c['name'], str(c.get('kind', 'dragon'))
    at, z, yaw, k = c.get('at', [0, 0]), c.get('z', 0), c.get('yaw', 0), c.get('scale', 1.0)
    if kind == 'dragon':
        import dragon
        root = dragon.make_dragon(name, **{x: c[x] for x in ('color', 'belly', 'wing') if x in c}, scale=k)
    elif kind in KINDS:
        import beasts
        root = beasts.BUILDERS[kind](name, **{x: c[x] for x in ('color', 'belly') if x in c}, scale=k)
    elif kind.startswith('rbx:'):
        import sets
        r = sets.rbx_set(kind[4:], at=(0, 0), rot=0, scale=k)['root']
        root = bpy.data.objects.new(f'{name} root', None); bpy.context.scene.collection.objects.link(root)
        body = bpy.data.objects.new(f'{name} body', None); bpy.context.scene.collection.objects.link(body)   # the type's motion moves this
        body.parent = root; r.parent = body
    else: raise KeyError(f"creature kind '{kind}' -> 'dragon' or 'rbx:<slug>' (a Creator Store model in assets/rbxsets)")
    root.location = (at[0] * S, at[1] * S, z * S); root.rotation_euler = (0, 0, math.radians(yaw))
    root.keyframe_insert('location', frame=0); root.keyframe_insert('rotation_euler', frame=0)
    bpy.context.view_layer.update()
    subj = _subject(root); subj['creature_root'] = root.name   # camera.py frames the whole creature
    return root, subj


def animate(root, c, fps, log, f_end=None):
    """Key the story motion: path (fly/walk with the nose along the travel), flap, hover, roar, then the movement type's motion
    up to f_end (legs from the distance walked, wave, bob...). Seconds -> frames. A heavy biped's footfalls shake the camera."""
    F = lambda t: round(t * fps)
    notes = log.setdefault('notes', [])
    kind = str(c.get('kind', 'dragon')); part_built = kind in KINDS; mv = moves(c)
    pts = c.get('path') or []
    if pts:
        keys, yaw = [], c.get('yaw', 0)
        for i, p in enumerate(pts):
            nx = pts[min(i + 1, len(pts) - 1)]; pv = pts[max(i - 1, 0)]
            dx, dy = (nx['at'][0] - p['at'][0], nx['at'][1] - p['at'][1]) if i + 1 < len(pts) else (p['at'][0] - pv['at'][0], p['at'][1] - pv['at'][1])
            if abs(dx) + abs(dy) > 0.5: yaw = math.degrees(math.atan2(dx, -dy))   # face = local -Y: nose along the travel
            keys.append((F(p['t']), (p['at'][0], p['at'][1], p.get('z', 0)), p.get('yaw', yaw)))
        if kind == 'dragon':
            import dragon; dragon.fly(root, keys)
        else:
            for f, (x, y, z), yw in keys:
                root.location = (x * S, y * S, z * S); root.rotation_euler = (0, 0, math.radians(yw))
                root.keyframe_insert('location', frame=f); root.keyframe_insert('rotation_euler', frame=f)
    if kind == 'dragon':
        import dragon
        if c.get('flap'): dragon.flap(root, F(c['flap'][0]), F(c['flap'][1]))
        if c.get('hover'): dragon.hover(root, F(c['hover'][0]), F(c['hover'][1]))
        for a, b in c.get('roar', []): dragon.roar(root, F(a), F(b))
    elif c.get('flap') or c.get('roar'):
        notes.append(f"{c['name']}: flap/roar need the part-built dragon (other kinds have no wings or jaw)")
    if not part_built and c.get('hover'):   # a whole-model bob for Creator Store models
        a, b = F(c['hover'][0]), F(c['hover'][1])
        zk = sorted((f, z) for f, (x, y, z), _ in keys) if pts else []   # the path's own z keys: the bob rides the flight instead
        def z_at(f):                                                     # of pinning to the LAST key's z (a hover during a descent
            if not zk: return root.location.z                            # teleported the model to ground level mid-flight)
            if f <= zk[0][0]: return zk[0][1]
            if f >= zk[-1][0]: return zk[-1][1]
            for (f0_, z0_), (f1_, z1_) in zip(zk, zk[1:]):
                if f0_ <= f <= f1_: return z0_ + (z1_ - z0_) * (f - f0_) / max(1, f1_ - f0_)
            return zk[-1][1]
        for f in range(a, b + 1, 6):
            root.location.z = z_at(f) + 0.2 * S * math.sin(2 * math.pi * (f - a) / 24); root.keyframe_insert('location', index=2, frame=f)
    if mv is None: return   # no type saved: path only
    import beasts
    ends = [F(p['t']) for p in pts] + [F(x) for s in (c.get('sit') or [],) for x in s[1:2]] + [F(t) + fps for t in c.get('pounce', [])]
    f1 = max([f_end or 0, *ends]) + fps
    own = []
    if c.get('sit') or c.get('pounce'):
        if part_built and mv == 'quadruped':
            for t in c.get('pounce', []): own.append(beasts.pounce(root, F(t), fps))
            if c.get('sit'): beasts.sit(root, F(c['sit'][0]), F(c['sit'][1])); own.append((F(c['sit'][0]), F(c['sit'][1])))
        else: notes.append(f"{c['name']}: sit/pounce need the part-built wolf (a quadruped with legs)")
    if any(c.get(k) is not None for k in ('attack', 'hit', 'startle', 'die')):   # one-off beats own their frames
        if part_built:
            import actions
            for t in c.get('attack', []): own.append(actions.attack(root, kind, F(t)))
            for t in c.get('startle', []): own.append(actions.startle(root, kind, F(t)))
            for h in c.get('hit', []): t, side = (h, 0) if isinstance(h, (int, float)) else h; own.append(actions.hit(root, kind, F(t), side))
            if c.get('die') is not None: own.append((actions.die(root, kind, F(c['die']))[0], 10 ** 9))   # dead stays dead
        else: notes.append(f"{c['name']}: attack/hit/startle/die need a part-built creature ({', '.join(KINDS)})")
    tr = beasts.track(root, 0, f1)
    falls = [] if (c.get('heavy', kind == 'ogre') and mv == 'biped') else None
    if kind == 'dragon' and mv == 'flyer': pass   # its flying is keyed above
    elif not part_built: beasts.whole_model(root, beasts._find(root, c['name'] + ' body'), mv, tr, fps, falls)
    elif mv in ('biped', 'quadruped', 'crawler'): beasts.gait(root, tr, fps, falls, own)
    elif mv == 'slither': beasts.slither(root, tr, fps, skip=own)
    elif mv == 'floater': beasts.float_about(root, tr, fps, skip=own)
    if mv != DEFAULT.get(kind) and part_built: notes.append(f"{c['name']}: moves '{mv}' on a {kind} (built for '{DEFAULT[kind]}')")
    if falls: log.setdefault('impact_frames', []).extend(falls)   # heavy steps shake the camera that shows them
    if part_built: beasts.idle_life(root, kind, tr, fps, own + ([(F(c['flap'][0]), F(c['flap'][1]))] if c.get('flap') else []))


def react(spec, cast, fps, log, sc, step=2):
    """NOTICE pass, run on the FINAL cast motion (build.py, before the shots): each part-built creature's head ('<name> neck',
    a floater turns its whole body) follows its `look` target, else whoever nearby talks or moves (closer wins a tie). A new
    target snaps the head round fast for ~0.25 s - the noticing beat - then it tracks smoothly. Clamped to 70 deg each side."""
    talks = {}
    for b in spec.get('beats', []):
        if b.get('talk') and b.get('who'): talks.setdefault(b['who'], []).append((b['t'], b['t'] + float(b['talk'])))
    crs = [c for c in spec.get('creatures', []) if str(c.get('kind', 'dragon')) in KINDS and bpy.data.objects.get(c['name'])]
    if not crs or not cast: return
    heads = {c['name']: bpy.data.objects.get(c['name'] + ' neck') or bpy.data.objects.get(c['name'] + ' body') for c in crs}
    track = {c['name']: [] for c in crs}; pos = []
    for f in range(0, sc.frame_end + 1, step):
        sc.frame_set(f)
        pos.append((f, {n: tuple(ch.root.matrix_world.translation.xy / S) for n, ch in cast.items()}))
        for c in crs:
            h = heads[c['name']]; base = h.parent.matrix_world if h.parent else bpy.data.objects[c['name']].matrix_world
            track[c['name']].append((tuple(h.matrix_world.translation.xy / S), base.to_euler().z))
    for c in crs:
        h = heads[c['name']]; looks = c.get('look'); looks = [[0, looks]] if isinstance(looks, str) else sorted(looks or [], key=lambda e: e[0])
        cur_t, cur_s, since, ang, snap, seen = None, -9.0, 99, 0.0, 0, []
        for i, (f, ps) in enumerate(pos):
            t = f / fps; (hx, hy), base = track[c['name']][i]
            if c.get('die') is not None and t >= c['die']: break   # the dead stop looking (actions.die owns the head)
            forced = [e[1] for e in looks if e[0] <= t]
            if forced and forced[-1] is not None: best, bs = forced[-1], 99.0
            else:
                sc_ = {}
                for n, (x, y) in ps.items():   # only someone who talks or moves draws the eye; closer wins a tie
                    d = math.hypot(x - hx, y - hy)
                    mv_ = i and math.hypot(x - pos[i - 1][1][n][0], y - pos[i - 1][1][n][1]) > 0.05
                    act = 3 * any(a <= t <= b_ for a, b_ in talks.get(n, [])) + 2 * bool(mv_)
                    if d <= 45 and act: sc_[n] = act - d / 15
                best = max(sc_, key=sc_.get) if sc_ else cur_t   # nobody active: keep watching the last one
                bs = sc_.get(best, cur_s)
                if cur_t in ps and best != cur_t and (since < 12 or bs < sc_.get(cur_t, -9.0) + 0.75): best, bs = cur_t, sc_.get(cur_t, cur_s)   # no flicking
            if best != cur_t:
                since, snap = 0, (6 if best else 0)
                if best: seen.append(f'{t:.1f}s {best}')
            cur_t, cur_s = best, bs; since += step
            tgt = ps.get(best) or (bpy.data.objects[best].matrix_world.translation.xy / S if best and bpy.data.objects.get(best) else None)
            want = 0.0
            if tgt is not None:
                want = math.atan2(tgt[0] - hx, -(tgt[1] - hy)) - base
                want = max(-1.22, min(1.22, (want + math.pi) % (2 * math.pi) - math.pi))
            rate = math.radians(12 if snap > 0 else 4) * step; snap -= step
            ang += max(-rate, min(rate, want - ang))
            h.rotation_euler.z = ang; h.keyframe_insert('rotation_euler', frame=f, index=2)
        if seen: log.setdefault('notes', []).append(f"{c['name']} looks at: {', '.join(seen[:6])}")
