"""
PNG renders for each height (1U, 2U, 3U), M5-nut version.

Usage: blender -b -P cad/render_previews.py   (after cad/previews.py)
Writes docs/images/<n>U/*.png
"""
import glob
import math
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
U = 44.45
TT_H = 171.0   # TT couché
PLATE = 256.0

BLEU = (0.05, 0.22, 0.48)
VERT = (0.12, 0.42, 0.18)
ALU = (0.12, 0.12, 0.13)
COULEURS_PLATEAU = {"2_": BLEU, "3_": (0.75, 0.32, 0.05), "4_": VERT, "5_": (0.20, 0.55, 0.30)}


def reset(res=(1600, 1200)):
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
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.93, 0.95, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6


def mat(name, rgb, rough=0.45, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def load(path, material):
    bpy.ops.wm.stl_import(filepath=path)
    o = bpy.context.selected_objects[0]
    o.data.materials.append(material)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    return o


def plane(size, loc, rgb, rough=0.9):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    bpy.context.object.data.materials.append(mat("p", rgb, rough=rough))


def lights(target):
    for loc, e, s in [((-500, 500, 700), 7e6, 500), ((600, 200, 400), 3e6, 400), ((0, -600, 500), 2.5e6, 400)]:
        loc = Vector(loc) + Vector((target[0], target[1], 0))
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy, l.data.size = e, s
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


def render(out_dir, fname):
    bpy.context.scene.render.filepath = os.path.join(out_dir, fname)
    bpy.ops.render.render(write_still=True)
    print("->", os.path.join(os.path.basename(out_dir), fname))


def assembly(stl, with_tt=True):
    load(os.path.join(stl, "sides.stl"), mat("cotes", BLEU))
    load(os.path.join(stl, "brace.stl"), mat("traverse", VERT))
    if with_tt:
        load(os.path.join(stl, "tt.stl"), mat("tt", ALU, rough=0.35, metal=0.6))
    plane(3000, (0, 0, -8.05), (0.85, 0.86, 0.88))


def plate_view(stl, prefix, out, fname):
    """vue de dessus d'un plateau 256 × 256 avec les pièces placées"""
    reset(res=(1400, 1400))
    plane(5000, (PLATE / 2, PLATE / 2, -1.05), (0.85, 0.86, 0.88))
    plane(PLATE, (PLATE / 2, PLATE / 2, -0.05), (0.18, 0.18, 0.2), rough=0.6)   # plateau
    for p in sorted(glob.glob(os.path.join(stl, prefix + "_*.stl"))):
        num = os.path.basename(p)[len(prefix) + 1:][:2]
        load(p, mat(num, COULEURS_PLATEAU.get(num, BLEU)))
    lights((PLATE / 2, PLATE / 2, 0))
    camera((PLATE / 2 - 160, PLATE / 2 - 260, 420), (PLATE / 2, PLATE / 2, 0), lens=45)
    render(out, fname)


for n_u in (1, 2, 3):
    out = os.path.join(ROOT, "docs", "images", f"{n_u}U")
    stl = os.path.join(ROOT, "build", "previews", f"{n_u}U")
    H = n_u * U
    total = f"{3 + n_u}U"

    # 1. TT posé sur la rehausse, 3/4 avant
    reset()
    assembly(stl)
    zc = (H + TT_H) / 2
    lights((0, 0, zc))
    camera((-620, 820, 380 + H), (0, 0, zc), lens=50)
    render(out, f"01_tt_on_riser_{n_u}U_total_{total}.png")

    # 2. rehausse seule, 3/4 arrière (traverse)
    reset()
    assembly(stl, with_tt=False)
    lights((0, 0, H / 2))
    camera((520, -620, 300 + H), (0, 0, H / 2), lens=50)
    render(out, f"02_riser_{n_u}U_rear.png")

    # 3. façade orthographique : trous de rail au pas EIA sous ceux du TT
    reset(res=(1200, 1400))
    assembly(stl)
    lights((0, 0, zc))
    camera((0, 900, zc), (0, 0, zc), ortho=max(380, H + TT_H + 100))
    render(out, f"03_front_{n_u}U.png")

    # 4. plateau de la nuit (et 2e plateau en 3U)
    plate_view(stl, "bed_night", out, f"04_bed_night_{n_u}U.png")
    if glob.glob(os.path.join(stl, "bed_next_*.stl")):
        plate_view(stl, "bed_next", out, f"05_bed_next_{n_u}U.png")
