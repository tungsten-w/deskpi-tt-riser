# Print order: RackMate TT riser, 256 mm bed, M5-nut version

Files: `stl/print-sets/centauri-carbon-2/<1U|2U|3U>/`. Each folder has everything for that height, and the number is the print order.

Settings for all parts: PETG, 4 walls, 30 % gyroid, 0.2 mm layers, **no supports**. Print as is: the parts are already oriented.

## First: one minute with a ruler

The foot hole spacing comes from the official drawing (DP-0054), not from a real TT. Measure centre to centre between the foot screws:

- [ ] left ↔ right: **248.5 mm** (the riser slot tolerates ±1 mm)
- [ ] front ↔ rear: **130 mm** (no tolerance)
- [ ] the feet are screwed into the bottom panel of the lying TT, not into the front/rear frames

If anything differs, don't print anything yet: fix `cad/riser.py` first.

## #1 alone, before the long print

`1_test_fit.stl`, ~30 min. Check:

- [ ] an M5 nut slides into its slot
- [ ] held under the TT in place of a foot, the M4 screw goes into the foot hole
- [ ] an M4 nut fits in the foot pocket

## Then, by height

| Height | TT total | First plate (overnight) | Next plate | Filament |
|---|---|---|---|---|
| **1U** | 4U | #2 + 3 + 4 + 5 together | (none) | ~185 g |
| **2U** | 5U | #2 + 3 + 4 + 5 together ¹ | (none) | ~225 g |
| **3U** | 6U | #2 + 4 + 5 | #3 | ~270 g |

¹ The 2U plate is a tight fit: 224 × 238 mm on 256, checked by the script. If the slicer's auto-arrange can't place everything, copy `docs/images/2U/04_bed_night_2U.png`: both sides and #4 standing side by side, and #5 lying across above the sides.

For 3U, the two sides together are 267 mm wide, which is more than the bed, so you need two plates.

#4 and #5 (rear brace A and B) are the same file twice. You need 2 identical pieces: one is flipped at assembly.

## Images

`docs/images/<1U|2U|3U>/`:

| Image | Shows |
|---|---|
| `01_tt_on_riser_…_total_…U.png` | TT on the riser, 3/4 front view |
| `02_riser_…_rear.png` | riser alone, rear view with the brace |
| `03_front_….png` | front view: the riser rail holes line up under the TT's |
| `04_bed_night_….png` | layout on the 256 mm bed |
| `05_bed_next_3U.png` | 3U only: the second plate (#3) |

Bed views: blue = #2, orange = #3, dark green = #4, light green = #5.
