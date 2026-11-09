"""
Adds titles, labels and arrows to the mounting renders (build/mounting/*_raw.png -> docs/images/mounting/).
Usage: python cad/annotate_mounting.py      (Pillow; DejaVu Sans font)
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "build", "mounting")
OUT = os.path.join(ROOT, "docs", "images", "mounting")
FONT = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
INK = (25, 28, 35)
RED = (200, 20, 20)

# view -> (title, bottom caption, [(no., anchor key or (x, y) in px, label top-left corner, text)])
VIEWS = {
    "1_exploded": (
        "Riser 2U <-> TT mounting: exploded view",
        "Same at all 4 corners. The red lines show the axis of each screw.",
        [
            (1, "trou_tt", (1270, 470), "Threaded M4 hole under\nthe TT (foot location)"),
            (2, "lamage", (1270, 650), "Hole in the top rail, screw\nhead recessed underneath"),
            (4, "fenetre", (1270, 830), "Window: the hex key\ngoes in through here"),
            (3, "vis", (1270, 1010), "M4 x 12 screw inserted\nFROM BELOW, into the TT"),
            (5, "ecrou", (60, 1130), "M4 nut sitting in\nthe bottom rail"),
            (6, "pied", (60, 1290), "Original foot screwed\nunder the bottom rail"),
        ],
    ),
    "2_section": (
        "Section through the front-left screw axis",
        "Seen from inside the rack. The screw clamps the top rail against the underside of the TT.",
        [
            (1, "tt", (60, 140), "TT (underside, solid edge\nabove the foot)"),
            (2, "trou_tt", (1190, 330), "TT M4 hole\n(6 mm of thread)"),
            (3, "vis", (1190, 500), "M4 x 12 screw"),
            (4, "tete", (1190, 610), "Recessed head\n(4 mm)"),
            (5, "lisse_haute", (60, 690), "Top rail (10 mm)\npressed under the TT"),
            (6, "fenetre", (60, 870), "Window: access\nto the screw head"),
            (7, "montant", (1190, 960), "Front\npost"),
            (8, "ecrou", (60, 1080), "Foot M4 nut, sitting\nin the bottom rail"),
            (9, "pied", (60, 1330), "Original foot"),
        ],
    ),
    "3_hex_key_through_window": (
        "Tightening: the hex key goes through the window",
        "3 mm L-shaped hex key. Tighten firmly without forcing (steel screw in aluminium).",
        [
            (1, "tete", (1270, 250), "Short arm of the key in the\nM4 screw socket, right\nunder the top rail"),
            (2, "cle", (1270, 470), "Long arm sticking out of\nthe window: turn from here"),
            (3, (985, 830), (1270, 1000), "Riser window\n(66 mm tall in 2U)"),
        ],
    ),
}


def box_size(draw, text, font):
    l, t, r, b = draw.multiline_textbbox((0, 0), text, font=font, spacing=6)
    return r - l, b - t


def annotate(name, title, caption, labels):
    im = Image.open(os.path.join(D, name + "_raw.png")).convert("RGB")
    pts = json.load(open(os.path.join(D, name + ".json")))["points"]
    W, H = im.size
    dr = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, int(W / 62))
    fb = ImageFont.truetype(FONT_B, int(W / 62))
    ft = ImageFont.truetype(FONT_B, int(W / 42))
    fc = ImageFont.truetype(FONT, int(W / 66))

    for n, anchor, (bx, by), text in labels:
        ax, ay = pts[anchor] if isinstance(anchor, str) else anchor
        tw, th = box_size(dr, text, f)
        pad, badge = 14, int(W / 40)
        bw, bh = tw + badge + 3 * pad, max(th, badge) + 2 * pad
        # point d'attache de la flèche : bord de l'étiquette le plus proche
        ex = bx if ax < bx else (bx + bw if ax > bx + bw else ax)
        ey = by + bh / 2
        dr.line([(ex, ey), (ax, ay)], fill=RED + (255,), width=4)
        dr.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=RED + (255,), outline=(255, 255, 255, 255), width=3)
        dr.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(255, 255, 255, 235),
                             outline=RED + (255,), width=3)
        cx, cy = bx + pad + badge / 2, by + bh / 2
        dr.ellipse([cx - badge / 2, cy - badge / 2, cx + badge / 2, cy + badge / 2], fill=RED + (255,))
        dr.text((cx, cy), str(n), font=fb, fill=(255, 255, 255), anchor="mm")
        dr.multiline_text((bx + 2 * pad + badge, by + pad), text, font=f, fill=INK, spacing=6)

    # titre et légende
    tw, th = box_size(dr, title, ft)
    dr.rectangle([0, 0, W, th + 44], fill=(255, 255, 255, 225))
    dr.text((40, 22), title, font=ft, fill=INK)
    cw, ch = box_size(dr, caption, fc)
    dr.rectangle([0, H - ch - 40, W, H], fill=(255, 255, 255, 225))
    dr.text((40, H - ch - 20), caption, font=fc, fill=INK)
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, name + ".png")
    im.save(out)
    print("->", out)


for name, (title, caption, labels) in VIEWS.items():
    annotate(name, title, caption, labels)
