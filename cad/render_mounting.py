"""
Explanatory renders of the 2U riser <-> TT mounting.

Usage: blender -b -P cad/render_mounting.py   (after cad/mounting_models.py)
       python cad/annotate_mounting.py         (adds the labels -> docs/images/mounting/)
Writes build/mounting/<view>_raw.png + <view>.json (screen position of the labelled points)
"""
import json
import math
import os

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "build", "mounting")
STL = OUT

U = 44.45
H = 2 * U
X_FOOT, Y_FOOT = 124.25, 65.0
TOP_T, BOT_T = 10.0, 12.0
ZH = H - TOP_T                       # dessous de la lisse haute

COUL = {
    "riser": ((0.05, 0.22, 0.48), 0.45, 0.0),
    "tt": ((0.12, 0.12, 0.13), 0.35, 0.6),
    "screws": ((0.75, 0.04, 0.04), 0.3, 0.3),
    "foot_screws": ((0.75, 0.04, 0.04), 0.3, 0.3),
    "nuts": ((0.95, 0.70, 0.08), 0.3, 0.5),
    "feet": ((0.02, 0.02, 0.02), 0.8, 0.0),
    "axes": ((0.85, 0.05, 0.05), 0.5, 0.0),
    "hexkey": ((0.95, 0.45, 0.02), 0.3, 0.4),
}


def reset(res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.95, 0.96, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    return sc


def mat(name, rgb, rough, metal):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def load_view(prefix):
    for f in sorted(os.listdir(STL)):
        if not f.startswith(prefix + "_"):
            continue
        part = f[len(prefix) + 1:-4]
        bpy.ops.wm.stl_import(filepath=os.path.join(STL, f))
        o = bpy.context.selected_objects[0]
        o.data.materials.append(mat(part, *COUL[part]))
        bpy.ops.object.shade_auto_smooth(angle=math.radians(30))


def floor(z):
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, z))
    bpy.context.object.data.materials.append(mat("sol", (0.88, 0.89, 0.9), 0.9, 0.0))


def lights(target, scale=1.0):
    for loc, e, s in [((-500, 500, 700), 6e6, 500), ((600, 200, 400), 2.5e6, 400), ((-300, -600, 300), 2e6, 400),
                      ((-700, 100, 50), 1.5e6, 300)]:
        loc = Vector(loc) * scale + Vector(target)
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy, l.data.size = e * scale * scale, s * scale
        l.rotation_euler = (Vector(target) - loc).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50, ortho=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.data.clip_end = 10000
    if ortho:
        c.data.type = "ORTHO"
        c.data.ortho_scale = ortho
    else:
        c.data.lens = lens
    bpy.context.scene.camera = c
    return c


def render(name, cam, anchors):
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(OUT, name + "_raw.png")
    bpy.ops.render.render(write_still=True)
    W, Hh = sc.render.resolution_x, sc.render.resolution_y
    pts = {}
    for key, p in anchors.items():
        v = world_to_camera_view(sc, cam, Vector(p))
        pts[key] = [v.x * W, (1 - v.y) * Hh]
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump({"size": [W, Hh], "points": pts}, f, indent=1)
    print("->", name)


x, y = -X_FOOT, Y_FOOT
VUES = os.environ.get("VUES", "123")   # ex. VUES=3 pour ne refaire que la 3e vue

# 1. éclaté du coin avant gauche
if "1" in VUES:
  reset((1800, 1500))
  load_view("exploded")
  floor(-50)
  lights((-120, 60, 60))
  cam = camera((-700, 640, 380), (-70, 10, 85), lens=55)
  render("1_exploded", cam, {
      "trou_tt": (x, y, H + 60),
      "vis": (x, y, ZH - 38 + 10),
      "lamage": (x, y, ZH + 1),
      "fenetre": (-133, 0, 45),
      "ecrou": (x, y, BOT_T + 22 + 3),
      "pied": (x, y, -34 - 4),
  })

# 2. coupe dans l'axe de la vis avant gauche (vue depuis l'intérieur du rack)
if "2" in VUES:
  reset((1500, 1500))
  load_view("section")
  lights((-124, 50, 50))
  cam = camera((150, 52, 62), (-124, 52, 62), ortho=170)
  render("2_section", cam, {
      "tt": (x, 5, H + 25),
      "trou_tt": (x, y, H + 5),
      "vis": (x, y, ZH + 8),
      "tete": (x, y, ZH + 2),
      "lisse_haute": (x, 20, H - 5),
      "fenetre": (x, 25, 45),
      "montant": (x, 90, 45),
      "ecrou": (x, y, BOT_T - 2),
      "pied": (x, y, -4),
  })

# 3. la clé Allen passée par la fenêtre, vue de l'extérieur
if "3" in VUES:
  reset((1800, 1400))
  load_view("key")
  floor(-8.05)
  lights((-130, 40, 60))
  cam = camera((-470, 470, 115), (-150, 55, 58), lens=55)
  render("3_hex_key_through_window", cam, {
      "cle": (x - 85, y, ZH + 2.5 - 24 + 1),
      "tete": (x, y, ZH + 1),
      "fenetre": (-133, -20, 40),
      "tt": (-100, -40, H + 120),
  })
