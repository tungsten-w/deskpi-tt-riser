#!/usr/bin/env python3
"""
3D-printed riser for a DeskPi RackMate TT lying HORIZONTALLY (10" 3U mode): +1U, +2U or +3U UNDER the chassis.

Each side (left / right) is an "O" frame seen from the side:
  - a front post and a rear post, drilled on the EIA pitch on their front face (like the TT rails)
  - a top rail screwed into the TT's 4 M4 foot holes (feet removed)
  - a bottom rail that takes the original rubber feet
The space between X = ±111.125 (standard 10" opening) stays free: 10" shelves mount as in the TT.

Equipment fixing on the riser rails (choose at print time):
  - "inserts": pockets for M5 heat-set brass inserts (Ø6.4, Ruthex / CNC Kitchen standard)
  - "nuts" (internal name "ecrous"): captive M5 nuts slid into a slot from the inside of the post

Coordinates (mm), rack on the desk, seen from the front:
  X: width, 0 = centre (left -, right +)
  Y: depth, 0 = middle, +100 = front face
  Z: height, 0 = underside of the riser (without feet)

Dimensions: official DeskPi drawing "DP-0054 TT Aluminum chassis" (drawn standing: 171 × 266 × 200;
lying down, the 266 × 200 side panel becomes the bottom, with its 4 M4 holes at 248.5 × 130).
Usage: python cad/riser.py  -> runs the checks, writes stl/sides, stl/test_fit.stl, stl/rear_brace_x2.stl
       and the numbered print sets in stl/print-sets/. Code comments are in French.
"""
import math
import os
import struct

import numpy as np
from manifold3d import CrossSection, Manifold

SEG = 48
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_STL = os.path.join(HERE, "..", "stl")
BUILD = os.path.join(HERE, "..", "build")                   # STL intermédiaires des rendus (non versionnés)
IMAGES = os.path.join(HERE, "..", "docs", "images")

# --------------------------------------------------------------------------------------
# PARAMÈTRES
# --------------------------------------------------------------------------------------
# --- Châssis TT à l'horizontale (DP-0054, tourné de 90°) ---
RACK_W = 266.0             # largeur hors-tout (= hauteur 266 du TT dessiné debout)
RACK_IN = 222.25           # largeur libre entre montants de la rehausse (10" standard ; le TT a 226 d'ouverture,
                           # mais à 226 il ne reste que 2 mm autour des inserts : on garde 222.25)
RACK_D = 200.0             # profondeur
TT_H = 171.0               # hauteur du TT couché (sans poignées)
TT_RAIL_Z0 = 18.75         # bas du 1er U du TT au-dessus de son dessous (1er trou à 25.1 mm, mesuré sur DP-0054)
FOOT_PITCH_X = 248.5       # entraxe des trous M4 du panneau du dessous, mesuré sur DP-0054 (8.45 / 9.05 des bords)
FOOT_PITCH_Y = 130.0       # 35 et 165 mm depuis la face avant -> centré
U = 44.45
EIA = (6.35, 22.225, 38.1)  # trous dans chaque U (pas 15.88 / 15.88 / 12.70)
RAIL_PITCH = 236.525        # entraxe horizontal des trous 10"

XO = RACK_W / 2             # 133     : face extérieure
XI = RACK_IN / 2            # 111.125 : face intérieure
YF = RACK_D / 2             # 100     : face avant
X_RAIL = RAIL_PITCH / 2     # 118.2625
X_FOOT = FOOT_PITCH_X / 2   # 124.25
Y_FOOT = FOOT_PITCH_Y / 2   # 65

# --- Rehausse ---
POST_D = 20.0               # profondeur des montants (Y)
TOP_T = 10.0                # épaisseur lisse haute
BOT_T = 12.0                # épaisseur lisse basse (recouvrement 6 + 6)
LAP_L = 20.0                # demi-longueur du recouvrement (de -20 à +20)
LAP_BOLTS_Y = (-10.0, 10.0)
X_MID = (XO + XI) / 2       # 122.06 : milieu de la lisse

# --- Visserie ---
M4_CLR = 4.5
M4_SLOT = 1.0               # le trou du haut est oblong de ±1 mm en X (incertitude sur l'entraxe)
M4_HEAD_D = 8.5             # tête de vis CHC / bombée M4
M4_HEAD_H = 4.0
M4_NUT_AF = 7.3             # écrou M4 (7 sur plat) + jeu
M4_NUT_H = 3.5
M5_CLR = 5.5
INSERT_D = 6.4              # insert M5 (Ruthex RX-M5x5.8 / CNC Kitchen M5 standard)
INSERT_L = 10.0
M5_NUT_AF = 8.3             # écrou M5 (8 sur plat) + jeu
M5_NUT_H = 4.4
M5_NUT_FROM_FACE = 5.0      # paroi devant l'écrou

# --- Traverse arrière (optionnelle, contreventement gauche/droite) ---
BR_W = 250.0
BR_H = 30.0
BR_T = 8.0
BR_LAP = 10.0               # demi-recouvrement au milieu
BR_BOLTS_Z = (8.0, 22.0)

BED = 180.0                 # plateau de référence pour le découpage « plateau_180 »


# --------------------------------------------------------------------------------------
# OUTILS
# --------------------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl_z(x, y, z0, z1, d, seg=SEG):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, seg).translate([x, y, z0])


def cyl_y(x, z, y0, y1, d, seg=SEG):
    # cylindre d'axe Y entre y0 et y1
    c = Manifold.cylinder(y1 - y0, d / 2, d / 2, seg).rotate([-90, 0, 0])
    return c.translate([x, y0, z])


def hex_z(x, y, z0, z1, af):
    # prisme hexagonal d'axe Z, un sommet dans l'axe X (toit autoportant une fois imprimé couché)
    r = af / math.sqrt(3)
    return CrossSection.circle(r, 6).extrude(z1 - z0).translate([x, y, z0])


def hex_y(x, z, y0, y1, af):
    # prisme hexagonal d'axe Y, sommets dans l'axe X, plats en haut/bas (Z)
    r = af / math.sqrt(3)
    h = CrossSection.circle(r, 6).extrude(y1 - y0).rotate([-90, 0, 0])
    return h.translate([x, y0, z])


def slot_x_z(xc, y, z0, z1, d, half):
    """trou oblong d'axe Z, allongé en X de ±half"""
    return (cyl_z(xc - half, y, z0, z1, d) + cyl_z(xc + half, y, z0, z1, d)
            + box(xc - half, xc + half, y - d / 2, y + d / 2, z0, z1))


def rail_z(n_u):
    return [k * U + e for k in range(n_u) for e in EIA]


def write_stl(m, path):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    t = np.asarray(mesh.tri_verts)
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    with open(path, "wb") as f:
        f.write(b"DeskPi RackMate TT riser".ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        data = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", 9), ("a", "<u2")])
        data["n"] = n
        data["v"] = tri.reshape(-1, 9)
        data.tofile(f)


def lay_on_outer_face(m, side):
    """côté gauche : face X = -133 sur le plateau ; côté droit : face X = +133"""
    m = m.rotate([0, -90 if side == "gauche" else 90, 0])
    b = m.bounding_box()
    return m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def footprint(m):
    b = m.bounding_box()
    return b[3] - b[0], b[4] - b[1], b[5] - b[2]


# --------------------------------------------------------------------------------------
# PIÈCES (construites pour le côté GAUCHE, le droit est le miroir en X)
# --------------------------------------------------------------------------------------
def rail_holes(n_u, y_face, inward, fixing):
    """trous de rail sur la face y_face (inward = -1 si la face regarde vers +Y)"""
    cut = Manifold()
    y_back = y_face + inward * POST_D
    for z in rail_z(n_u):
        y0, y1 = sorted([y_face - inward * 1, y_back + inward * 1])
        cut += cyl_y(-X_RAIL, z, y0, y1, M5_CLR)
        if fixing == "inserts":
            a, b = sorted([y_face - inward * 1, y_face + inward * INSERT_L])
            cut += cyl_y(-X_RAIL, z, a, b, INSERT_D)
        else:
            a, b = sorted([y_face + inward * M5_NUT_FROM_FACE,
                           y_face + inward * (M5_NUT_FROM_FACE + M5_NUT_H)])
            cut += hex_y(-X_RAIL, z, a, b, M5_NUT_AF)
            # fente d'introduction depuis la face intérieure du montant
            cut += box(-X_RAIL, -XI + 1, a, b, z - M5_NUT_AF / 2, z + M5_NUT_AF / 2)
    return cut


def half_side(n_u, fixing, lap):
    """
    moitié AVANT du côté gauche (Y de 0 à +100).
    lap : 'bas'  -> languette de recouvrement en bas de la lisse basse (Y de -20 à +20)
          'haut' -> languette en haut (sera retournée en Y pour faire la moitié arrière)
          None   -> pas de recouvrement (moitié d'un côté monobloc)
    """
    H = n_u * U
    xo, xi = -XO, -XI
    body = box(xo, xi, YF - POST_D, YF, 0, H)                 # montant
    body += box(xo, xi, 0, YF, H - TOP_T, H)                  # lisse haute
    if lap is None:
        body += box(xo, xi, 0, YF, 0, BOT_T)
    else:
        body += box(xo, xi, LAP_L, YF, 0, BOT_T)
        z0, z1 = (0, BOT_T / 2) if lap == "bas" else (BOT_T / 2, BOT_T)
        body += box(xo, xi, -LAP_L, LAP_L, z0, z1)

    cut = rail_holes(n_u, YF, -1, fixing)
    # lisse haute : vis M4 vers le trou du pied du TT, tête noyée par en dessous
    cut += slot_x_z(-X_FOOT, Y_FOOT, H - TOP_T - 1, H + 1, M4_CLR, M4_SLOT)
    cut += slot_x_z(-X_FOOT, Y_FOOT, H - TOP_T - 1, H - TOP_T + M4_HEAD_H, M4_HEAD_D, M4_SLOT)
    # lisse basse : pied caoutchouc d'origine, écrou M4 posé dessus (accessible par la fenêtre)
    cut += cyl_z(-X_FOOT, Y_FOOT, -1, BOT_T + 1, M4_CLR)
    cut += hex_z(-X_FOOT, Y_FOOT, BOT_T - M4_NUT_H, BOT_T + 1, M4_NUT_AF)
    # recouvrement : 2 vis M4 verticales, écrou noyé sous la languette basse
    if lap is not None:
        for y in LAP_BOLTS_Y:
            cut += cyl_z(-X_MID, y, -1, BOT_T + 1, M4_CLR)
            if lap == "bas":
                cut += hex_z(-X_MID, y, -1, M4_NUT_H, M4_NUT_AF)
    return body - cut


def side(n_u, fixing, part):
    """part : 'avant', 'arriere' (moitiés) ou 'monobloc' ; côté gauche"""
    if part == "avant":
        return half_side(n_u, fixing, "bas")
    if part == "arriere":
        return half_side(n_u, fixing, "haut").mirror([0, 1, 0])
    h = half_side(n_u, fixing, None)
    return h + h.mirror([0, 1, 0])


def brace_half():
    """
    demi-traverse arrière, vissée sur les 2 premiers trous des montants arrière.
    Pièce identique ×2 : la 2e est la même tournée de 180° autour de Z.
    Repère : plaque dans le plan XZ, Y de 0 (contre les montants) à BR_T.
    """
    body = box(-BR_W / 2, -BR_LAP, 0, BR_T, 0, BR_H)
    body += box(-BR_LAP, BR_LAP, BR_T / 2, BR_T, 0, BR_H)
    cut = Manifold()
    for z in EIA[:2]:
        cut += cyl_y(-X_RAIL, z, -1, BR_T + 1, M5_CLR)
    for z in BR_BOLTS_Z:
        cut += cyl_y(0, z, -1, BR_T + 1, M4_CLR)
    return body - cut


def test_piece():
    """bout de montant + bout de lisse : 1 insert M5, 1 écrou M5, trou M4 oblong + lamage + écrou M4"""
    xo, xi = -XO, -XI
    body = box(xo, xi, YF - POST_D, YF, 0, 30) + box(xo, xi, 55, YF - POST_D, 0, 10)
    cut = Manifold()
    cut += cyl_y(-X_RAIL, 8, YF - POST_D - 1, YF + 1, M5_CLR)
    cut += cyl_y(-X_RAIL, 8, YF - INSERT_L, YF + 1, INSERT_D)
    z = 22
    cut += cyl_y(-X_RAIL, z, YF - POST_D - 1, YF + 1, M5_CLR)
    a, b = YF - M5_NUT_FROM_FACE - M5_NUT_H, YF - M5_NUT_FROM_FACE
    cut += hex_y(-X_RAIL, z, a, b, M5_NUT_AF) + box(-X_RAIL, xi + 1, a, b, z - M5_NUT_AF / 2, z + M5_NUT_AF / 2)
    cut += slot_x_z(-X_FOOT, Y_FOOT, -1, 11, M4_CLR, M4_SLOT)
    cut += slot_x_z(-X_FOOT, Y_FOOT, -1, M4_HEAD_H, M4_HEAD_D, M4_SLOT)
    cut += hex_z(-X_FOOT, Y_FOOT, 10 - M4_NUT_H, 11, M4_NUT_AF)
    return body - cut


# --------------------------------------------------------------------------------------
# VÉRIFICATIONS
# --------------------------------------------------------------------------------------
def checks():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  ERREUR ") + msg)
        ok &= cond

    check(abs(X_RAIL - XI) - INSERT_D / 2 >= 3.0, f"paroi insert / face intérieure = {X_RAIL - XI - INSERT_D / 2:.1f} mm")
    check(XO - X_RAIL - INSERT_D / 2 >= 3.0, f"paroi insert / face extérieure = {XO - X_RAIL - INSERT_D / 2:.1f} mm")
    check(XO - X_RAIL - M5_NUT_AF / math.sqrt(3) >= 2.0,
          f"paroi écrou M5 / face extérieure = {XO - X_RAIL - M5_NUT_AF / math.sqrt(3):.1f} mm")
    check(min(EIA[1] - EIA[0], U + EIA[0] - EIA[2]) - M5_NUT_AF >= 3.0,
          f"matière entre 2 fentes d'écrou = {min(EIA[1] - EIA[0], U + EIA[0] - EIA[2]) - M5_NUT_AF:.1f} mm")
    check(XO - X_FOOT - M4_CLR / 2 - M4_SLOT >= 2.0, f"paroi trou M4 / face extérieure = {XO - X_FOOT - M4_CLR / 2 - M4_SLOT:.1f} mm")
    check(X_FOOT - XI - M4_HEAD_D / 2 - M4_SLOT >= 2.0, f"paroi lamage M4 / face intérieure = {X_FOOT - XI - M4_HEAD_D / 2 - M4_SLOT:.1f} mm")
    check(Y_FOOT + M4_NUT_AF < YF - POST_D, "écrou du pied dans la fenêtre (accessible)")
    win = U - TOP_T - BOT_T
    check(win >= 12 + M4_HEAD_H + 2, f"fenêtre 1U = {win:.1f} mm : une vis M4×12 + tête passe ({12 + M4_HEAD_H} mm)")
    check(TOP_T - M4_HEAD_H >= 5, f"matière sous la vis du haut = {TOP_T - M4_HEAD_H:.0f} mm")
    return ok


# --------------------------------------------------------------------------------------
# APERÇUS (STL en position dans le repère du rack, rendus par rendus_blender.py)
# --------------------------------------------------------------------------------------
def tt_mock(z0):
    """TT couché simplifié (DP-0054) : cadres avant/arrière 4 mm à bord de 20 mm percés de 3U de rails,
    panneaux dessus/dessous/côtés, poignées sur le dessus, pieds remis sous la rehausse"""
    H = TT_H
    frame_cut = box(-XO + 20, XO - 20, -1e3, 1e3, z0 + 20, z0 + H - 20)
    m = Manifold()
    for y0 in (YF - 4, -YF):
        f = box(-XO, XO, y0, y0 + 4, z0, z0 + H) - frame_cut
        for sx in (-1, 1):
            for k in range(3):
                for e in EIA:
                    f -= cyl_y(sx * X_RAIL, z0 + TT_RAIL_Z0 + k * U + e, y0 - 1, y0 + 5, 4.8)
        m += f
    m += box(-XO, XO, -YF + 4, YF - 4, z0, z0 + 2)                      # dessous (panneau latéral du TT debout)
    m += box(-XO, XO, -YF + 4, YF - 4, z0 + H - 2, z0 + H)              # dessus
    for sx in (-1, 1):                                                  # côtés ajourés (dessus/dessous du TT debout)
        x0, x1 = sorted([sx * XO, sx * (XO - 2)])
        m += box(x0, x1, -YF + 4, YF - 4, z0, z0 + H)
    for sx in (-1, 1):                                                  # poignées
        x = sx * X_FOOT
        m += box(x - 6, x + 6, -Y_FOOT - 6, -Y_FOOT + 6, z0 + H, z0 + H + 30)
        m += box(x - 6, x + 6, Y_FOOT - 6, Y_FOOT + 6, z0 + H, z0 + H + 30)
        m += box(x - 6, x + 6, -Y_FOOT - 6, Y_FOOT + 6, z0 + H + 30, z0 + H + 40)
    for sx in (-1, 1):                                                  # pieds remis sous la rehausse
        for sy in (-1, 1):
            m += cyl_z(sx * X_FOOT, sy * Y_FOOT, -8, 0, 16)
    return m


# --------------------------------------------------------------------------------------
# SORTIE
# --------------------------------------------------------------------------------------
FIXING_EN = {"inserts": "inserts", "ecrous": "nuts"}
SIDE_EN = {"gauche": "left", "droit": "right"}
PRINT_SET = os.path.join(OUT_STL, "print-sets", "centauri-carbon-2")   # bed 256 mm, M5 nuts


def print_brace():
    br = brace_half().rotate([-90, 0, 0])       # face Y = BR_T (côté languette) sur le plateau
    b = br.bounding_box()
    return br.translate([-b[0], -b[1], -b[2]])


def main():
    print("Checks:")
    if not checks():
        raise SystemExit("FAILED")

    os.makedirs(os.path.join(OUT_STL, "sides"), exist_ok=True)
    print("STL:")
    sides = {}
    for fixing in ("inserts", "ecrous"):
        for n_u in (1, 2, 3):
            left = side(n_u, fixing, "monobloc")
            for name, m in (("gauche", left), ("droit", left.mirror([1, 0, 0]))):
                p = lay_on_outer_face(m, name)
                sides[(n_u, fixing, name)] = p
                fname = f"{n_u}U_{FIXING_EN[fixing]}_{SIDE_EN[name]}.stl"
                write_stl(p, os.path.join(OUT_STL, "sides", fname))
                fx, fy, fz = footprint(p)
                print(f"  sides/{fname:24s} {fx:6.1f} x {fy:6.1f} x {fz:5.1f}")

    brace = print_brace()
    write_stl(brace, os.path.join(OUT_STL, "rear_brace_x2.stl"))
    test = lay_on_outer_face(test_piece(), "gauche")
    write_stl(test, os.path.join(OUT_STL, "test_fit.stl"))
    print(f"  rear_brace_x2.stl  {tuple(round(v, 1) for v in footprint(brace))}")
    print(f"  test_fit.stl       {tuple(round(v, 1) for v in footprint(test))}")

    # jeux numérotés dans l'ordre d'impression (docs/print-order.md)
    for n_u in (1, 2, 3):
        d = os.path.join(PRINT_SET, f"{n_u}U")
        os.makedirs(d, exist_ok=True)
        for fname, m in ((f"1_test_fit.stl", test),
                         (f"2_{n_u}U_nuts_left.stl", sides[(n_u, "ecrous", "gauche")]),
                         (f"3_{n_u}U_nuts_right.stl", sides[(n_u, "ecrous", "droit")]),
                         ("4_rear_brace_A.stl", brace),
                         ("5_rear_brace_B.stl", brace)):
            write_stl(m, os.path.join(d, fname))
    print(f"  print-sets/centauri-carbon-2/{{1U,2U,3U}}/1..5")
    print("OK")


if __name__ == "__main__":
    main()
