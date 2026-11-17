"""creatures.py - big creatures and custom models in a story (scene key `creatures`): a dragon, a monster, a robot, a car...
Kinds (SKILL.md "New assets": Claude tries 1, then 2):
  'rbx:<slug>'  1) a Creator Store model fetched ONCE through Roblox Studio into assets/rbxsets/<id>_<slug> (the same import as Roblox
                   sets: tools/fetch_library.py model <id> <slug>), reused by every later story
  'dragon'      2) a part-built blocky model made here (dragon.py), no Studio needed
A creature is registered like a prop: shots `on: ["Dragon"]`, `look: "Dragon"`, walks away from it all work by its name.
  {"name": "Dragon", "kind": "dragon", "at": [0, 0], "yaw": 180, "scale": 1, "color": "#3FA34D",
   "path": [{"t": 0, "at": [0, 40], "z": 30}, {"t": 2.0, "at": [0, 0], "z": 0}],    # flies / walks between points (studs, seconds)
   "flap": [0, 3.0], "hover": [2.0, 6.0], "roar": [[2.4, 3.2]]}                     # [from, to] seconds; flap/roar only on part-built kinds
"""
import math
import bpy

S = 0.5
KINDS = ('dragon',)   # part-built kinds (dragon.py); everything else is 'rbx:<slug>'


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
    elif kind.startswith('rbx:'):
        import sets
        r = sets.rbx_set(kind[4:], at=(0, 0), rot=0, scale=k)['root']
        root = bpy.data.objects.new(f'{name} root', None); bpy.context.scene.collection.objects.link(root)
        r.parent = root
    else: raise KeyError(f"creature kind '{kind}' -> 'dragon' or 'rbx:<slug>' (a Creator Store model in assets/rbxsets)")
    root.location = (at[0] * S, at[1] * S, z * S); root.rotation_euler = (0, 0, math.radians(yaw))
    root.keyframe_insert('location', frame=0); root.keyframe_insert('rotation_euler', frame=0)
    bpy.context.view_layer.update()
    subj = _subject(root); subj['creature_root'] = root.name   # camera.py frames the whole creature
    return root, subj


def animate(root, c, fps, notes):
    """Key the story motion: path (fly/walk with the nose along the travel), flap, hover, roar. Seconds -> frames."""
    F = lambda t: round(t * fps)
    part_built = str(c.get('kind', 'dragon')) in KINDS
    pts = c.get('path') or []
    if pts:
        keys, yaw = [], c.get('yaw', 0)
        for i, p in enumerate(pts):
            nx = pts[min(i + 1, len(pts) - 1)]; pv = pts[max(i - 1, 0)]
            dx, dy = (nx['at'][0] - p['at'][0], nx['at'][1] - p['at'][1]) if i + 1 < len(pts) else (p['at'][0] - pv['at'][0], p['at'][1] - pv['at'][1])
            if abs(dx) + abs(dy) > 0.5: yaw = math.degrees(math.atan2(dx, -dy))   # face = local -Y: nose along the travel
            keys.append((F(p['t']), (p['at'][0], p['at'][1], p.get('z', 0)), p.get('yaw', yaw)))
        if part_built:
            import dragon; dragon.fly(root, keys)
        else:
            for f, (x, y, z), yw in keys:
                root.location = (x * S, y * S, z * S); root.rotation_euler = (0, 0, math.radians(yw))
                root.keyframe_insert('location', frame=f); root.keyframe_insert('rotation_euler', frame=f)
    if part_built:
        import dragon
        if c.get('flap'): dragon.flap(root, F(c['flap'][0]), F(c['flap'][1]))
        if c.get('hover'): dragon.hover(root, F(c['hover'][0]), F(c['hover'][1]))
        for a, b in c.get('roar', []): dragon.roar(root, F(a), F(b))
    elif c.get('flap') or c.get('roar'):
        notes.append(f"{c['name']}: flap/roar need a part-built kind (a Creator Store model moves as one piece)")
    if not part_built and c.get('hover'):   # a whole-model bob for Creator Store models
        a, b = F(c['hover'][0]), F(c['hover'][1]); z0 = root.location.z
        for f in range(a, b + 1, 6):
            root.location.z = z0 + 0.2 * S * math.sin(2 * math.pi * (f - a) / 24); root.keyframe_insert('location', index=2, frame=f)
