"""
STLs for the explanatory renders of the 2U riser <-> TT mounting (render_mounting.py).

Usage: python cad/mounting_models.py    (venv with manifold3d + numpy)
Writes build/mounting/<view>_<part>.stl for 3 views:
  exploded : front-left corner exploded (TT lifted, screws and foot pulled out, screw axes)
  section  : vertical section through the front-left screw axis
  key      : assembled, 3 mm hex key passed through the window up to the screw head
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riser import (BOT_T, BUILD, M4_NUT_AF, M4_NUT_H, TOP_T, TT_H, U, X_FOOT, XO,  # noqa: E402
                         Y_FOOT, YF, CrossSection, Manifold, box, brace_half, BR_T, cyl_z, side, tt_mock,
                         write_stl)
import math  # noqa: E402

N_U = 2
H = N_U * U
OUT = os.path.join(BUILD, "mounting")
FEET = [(sx * X_FOOT, sy * Y_FOOT) for sx in (-1, 1) for sy in (-1, 1)]
HEAD_D, HEAD_H, SCREW_D = 7.0, 4.0, 4.0
TT_WALL = 18.0           # bord plein du TT au-dessus des trous de pieds (plan DP-0054 : bande de 16-18 mm)
TT_HOLE_DEPTH = 10.0     # profondeur du trou taraudé du TT : inconnue, à vérifier en dévissant un pied


def hexagon_z(x, y, z0, z1, af):
    return CrossSection.circle(af / math.sqrt(3), 6).extrude(z1 - z0).translate([x, y, z0])


def screw(x, y, z_head_bottom, length):
    """vis CHC M4 tête en bas (vissée vers le haut)"""
    head = cyl_z(x, y, z_head_bottom, z_head_bottom + HEAD_H, HEAD_D)
    head -= hexagon_z(x, y, z_head_bottom - 1, z_head_bottom + 2.5, 3.0)       # empreinte 6 pans de 3
    return head + cyl_z(x, y, z_head_bottom + HEAD_H, z_head_bottom + HEAD_H + length, SCREW_D, seg=24)


def nut(x, y, z0):
    return hexagon_z(x, y, z0, z0 + M4_NUT_H - 0.3, M4_NUT_AF - 0.4) - cyl_z(x, y, z0 - 1, z0 + 4, SCREW_D)


def foot(x, y, z_top):
    """pied caoutchouc d'origine (simplifié) avec sa vis M4 qui dépasse vers le haut"""
    f = cyl_z(x, y, z_top - 8, z_top, 16) + cyl_z(x, y, z_top - 9, z_top - 8, 13)
    return f, cyl_z(x, y, z_top, z_top + 14, SCREW_D, seg=24)


def tt(z0):
    """TT couché + bords pleins percés M4 au droit des pieds"""
    m = tt_mock(z0) - box(-1e3, 1e3, -1e3, 1e3, -100, 0)        # sans les pieds du mock
    for sx in (-1, 1):
        x0, x1 = sorted([sx * XO, sx * (XO - TT_WALL)])
        m += box(x0, x1, -YF + 4, YF - 4, z0, z0 + 16)
    for x, y in FEET:
        m -= cyl_z(x, y, z0 - 1, z0 + TT_HOLE_DEPTH, 3.4)
    return m


def allen_key(x, y, z_tip):
    """clé Allen 3 mm coudée : petit bras vertical dans la tête, grand bras qui sort par la fenêtre (vers -X)"""
    af = 3.0
    short = hexagon_z(x, y, z_tip - 24, z_tip, af)
    r = af / math.sqrt(3)
    long_ = CrossSection.circle(r, 6).extrude(100).rotate([0, -90, 0]).translate([x + 1.5, y, z_tip - 24 + r])  # +Z -> -X : sort par la fenêtre
    return short + long_


def cut_keep_outer(m):
    """coupe par le plan X = -X_FOOT (axe des vis gauches), on garde l'extérieur (X < -X_FOOT)"""
    return m ^ box(-1e3, -X_FOOT, -1e3, 1e3, -1e3, 1e3)


def main():
    os.makedirs(OUT, exist_ok=True)
    left = side(N_U, "ecrous", "monobloc")
    right = left.mirror([1, 0, 0])
    br = brace_half()
    brace = br.rotate([0, 0, 180]).translate([0, -YF, 0]) + br.translate([0, -YF - BR_T, 0])
    z_head = H - TOP_T                       # dessous de la lisse haute = fond du lamage
    w = lambda name, m: write_stl(m, os.path.join(OUT, name + ".stl"))  # noqa: E731

    # --- 1. éclaté ---
    E_TT, E_SCREW, E_FOOT = 60.0, -38.0, -34.0
    w("exploded_riser", left + right + brace)
    w("exploded_tt", tt(H + E_TT))
    w("exploded_screws", sum((screw(x, y, z_head + E_SCREW, 12) for x, y in FEET), Manifold()))
    w("exploded_nuts", sum((nut(x, y, BOT_T + 22) for x, y in FEET), Manifold()))
    feet = [foot(x, y, E_FOOT) for x, y in FEET]
    w("exploded_feet", sum((f for f, _ in feet), Manifold()))
    w("exploded_foot_screws", sum((s for _, s in feet), Manifold()))
    axes = Manifold()
    for x, y in FEET:
        axes += cyl_z(x, y, E_FOOT - 4, H + E_TT + 14, 0.8, seg=12)
    w("exploded_axes", axes)

    # --- 2. coupe dans l'axe des vis gauches ---
    w("section_riser", cut_keep_outer(left))
    w("section_tt", cut_keep_outer(tt(H)))
    w("section_screws", sum((screw(x, y, z_head, 12) for x, y in FEET if x < 0), Manifold()))
    w("section_nuts", sum((nut(x, y, BOT_T - M4_NUT_H + 0.3) for x, y in FEET if x < 0), Manifold()))
    cf = [foot(x, y, 0) for x, y in FEET if x < 0]
    w("section_feet", sum((f for f, _ in cf), Manifold()))
    w("section_foot_screws", sum((s for _, s in cf), Manifold()))

    # --- 3. clé Allen par la fenêtre ---
    x, y = -X_FOOT, Y_FOOT
    w("key_riser", left + right + brace)
    w("key_tt", tt(H))
    w("key_screws", sum((screw(fx, fy, z_head, 12) for fx, fy in FEET), Manifold()))
    w("key_feet", sum((foot(fx, fy, 0)[0] for fx, fy in FEET), Manifold()))
    w("key_hexkey", allen_key(x, y, z_head + 2.5))
    print("OK", OUT)


if __name__ == "__main__":
    main()
