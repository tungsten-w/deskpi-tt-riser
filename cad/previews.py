"""
Preview STLs for each height (1U, 2U, 3U), M5-nut version, one-piece sides (256 mm bed).
Rendered afterwards by render_previews.py (Blender).

Usage: python cad/previews.py   (venv with manifold3d + numpy)
Writes build/previews/<n>U/:
  sides.stl, brace.stl, tt.stl          -> assembled riser in rack coordinates
  bed_night_*.stl, bed_next_*.stl       -> parts laid out on the 256 mm bed (night plate, and 2nd plate for 3U)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riser import (BR_T, BUILD, U, YF, brace_half, lay_on_outer_face, side,  # noqa: E402
                         tt_mock, write_stl)

PLATE = 256.0
GAP = 8.0
MARGIN = 6.0


def at(m, x, y, rot90=False):
    """pose la pièce m (déjà orientée pour l'impression) avec son coin mini en (x, y)"""
    if rot90:
        m = m.rotate([0, 0, 90])
    b = m.bounding_box()
    return m.translate([x - b[0], y - b[1], -b[2]])


def size(m, rot90=False):
    b = m.bounding_box()
    w, d = b[3] - b[0], b[4] - b[1]
    return (d, w) if rot90 else (w, d)


def check_plate(parts, label):
    tot = None
    for m in parts:
        tot = m if tot is None else tot + m
    b = tot.bounding_box()
    w, d = b[3] - b[0], b[4] - b[1]
    ok = w <= PLATE - 2 * MARGIN + 1e-6 and d <= PLATE - 2 * MARGIN + 1e-6
    inter = sum((parts[i] ^ parts[j]).volume() for i in range(len(parts)) for j in range(i + 1, len(parts)))
    print(f"  {label:22s} {w:6.1f} × {d:6.1f} mm (max {PLATE - 2 * MARGIN:.0f})  chevauchement {inter:.3f} mm³"
          f"  {'OK' if ok and inter < 1e-3 else '!! NE RENTRE PAS'}")
    assert ok and inter < 1e-3, label
    # centre sur le plateau (origine = coin du plateau)
    return [m.translate([PLATE / 2 - (b[0] + b[3]) / 2, PLATE / 2 - (b[1] + b[4]) / 2, 0]) for m in parts]


def main():
    br = brace_half()
    br_print = br.rotate([-90, 0, 0])
    for n_u in (1, 2, 3):
        d = os.path.join(BUILD, "previews", f"{n_u}U")
        os.makedirs(d, exist_ok=True)
        H = n_u * U
        left = side(n_u, "ecrous", "monobloc")
        write_stl(left + left.mirror([1, 0, 0]), os.path.join(d, "sides.stl"))
        write_stl(br.rotate([0, 0, 180]).translate([0, -YF, 0]) + br.translate([0, -YF - BR_T, 0]),
                  os.path.join(d, "brace.stl"))
        write_stl(tt_mock(H), os.path.join(d, "tt.stl"))

        g = lay_on_outer_face(left, "gauche")
        r = lay_on_outer_face(left.mirror([1, 0, 0]), "droit")
        gw, gd = size(g)
        tw, td = size(br_print, rot90=True)          # traverse debout dans le sens Y : 30 × 135
        if n_u == 1:
            # n°2 | n°3 | n°4 | n°5 côte à côte
            xs = [0, gw + GAP, 2 * (gw + GAP), 2 * (gw + GAP) + tw + GAP]
            night = {"2_left": at(g, xs[0], 0), "3_right": at(r, xs[1], 0),
                     "4_brace_A": at(br_print, xs[2], 0, True), "5_brace_B": at(br_print, xs[3], 0, True)}
            second = None
        elif n_u == 2:
            # n°2 | n°3 | n°4 debout, n°5 couchée sous les côtés
            night = {"2_left": at(g, 0, 0), "3_right": at(r, gw + GAP, 0),
                     "4_brace_A": at(br_print, 2 * (gw + GAP), 0, True),
                     "5_brace_B": at(br_print, 0, gd + GAP)}
            second = None
        else:
            # nuit : n°2 + n°4 + n°5 ; plateau suivant : n°3
            night = {"2_left": at(g, 0, 0), "4_brace_A": at(br_print, gw + GAP, 0, True),
                     "5_brace_B": at(br_print, gw + GAP + tw + GAP, 0, True)}
            second = {"3_right": at(r, 0, 0)}

        for label, plate in (("bed_night", night), ("bed_next", second)):
            if not plate:
                continue
            placed = check_plate(list(plate.values()), f"{n_u}U {label}")
            for (name, _), m in zip(plate.items(), placed):
                write_stl(m, os.path.join(d, f"{label}_{name}.stl"))
    print("OK")


if __name__ == "__main__":
    main()
