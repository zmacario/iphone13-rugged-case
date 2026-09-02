"""Plan view of the camera opening, seen from the BACK of the case.

Draws the four squares that matter and the three nut pockets nearest to them, to
show why the opening flares inward only. Dimensions are parsed out of
case_iphone13.py so this drawing cannot drift away from the model.

    python3 camera_plan.py     ->  camera_plan.png
"""
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

SRC = open("case_iphone13.py", encoding="utf-8").read()


def p(name):
    """Read a float parameter from the generator."""
    m = re.search(r"^%s\s*=\s*(-?[\d.]+)" % name, SRC, re.M)
    if not m:
        raise SystemExit("parameter %s not found in case_iphone13.py" % name)
    return float(m.group(1))


PL, PW, PR = p("PL"), p("PW"), p("PR")
BASE, ISL_R = p("CAM_ISL"), p("CAM_ISL_R")
CLR, FLARE = p("CAM_CLR"), p("CAM_FLARE")
FT, FS = p("CAM_FROM_TOP"), p("CAM_FROM_SIDE")
NUT_AF = p("NUT_AF")
PLATEAU = 30.0          # lens plateau: measured, not used by the model

# Island centre, from the two measured edge insets.
cx = PW / 2 - FS - BASE / 2
cy = PL / 2 - FT - BASE / 2
SLOT = BASE + 2 * CLR                 # opening against the phone
MOUTH = SLOT + 2 * FLARE              # opening at the outer face
mx, my = cx - FLARE, cy - FLARE       # mouth centre: offset inward on both axes

# Nut pockets, as reported by the generator (corner, mid-side, both top screws).
NUTS = [(39.25, 57.35, 30), (39.25, -8.5, 30), (-20.0, 76.85, 0), (20.0, 76.85, 0)]

GREEN, BLUE, RED = "#2f5d3f", "#1f4e79", "#a03030"


def rrect(w, h, r, x, y, **kw):
    ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r,
                                boxstyle="round,pad=%.3f" % r, **kw))


def dim(x0, y0, x1, y1, txt, off=(0, 0), lead=None, ha="center"):
    """Double arrow between two points, with the label offset from its midpoint.

    `lead` puts the label at an absolute position instead and draws a thin
    leader to the arrow — needed for the two 1.5 mm insets, which are far too
    small to letter in place.
    """
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.3))
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    if lead is None:
        ax.text(mid[0] + off[0], mid[1] + off[1], txt, fontsize=8.5, color=RED, ha=ha)
    else:
        ax.plot([mid[0], lead[0]], [mid[1], lead[1]], color=RED, lw=.7, ls=":")
        ax.text(lead[0] + off[0], lead[1] + off[1], txt, fontsize=8.5, color=RED, ha=ha)


fig, ax = plt.subplots(figsize=(9.5, 9.5), facecolor="white")

rrect(PW, PL, PR, 0, 0, fc="none", ec="#333", lw=2)
rrect(BASE, BASE, ISL_R, cx, cy, fc="#dde6dd", ec=GREEN, lw=2)
rrect(PLATEAU, PLATEAU, ISL_R - 1.3, cx, cy, fc="none", ec=GREEN, lw=1, ls="--")
rrect(SLOT, SLOT, ISL_R + CLR, cx, cy, fc="none", ec=BLUE, lw=1.6, ls="--")
rrect(MOUTH, MOUTH, ISL_R + CLR + FLARE, mx, my, fc="none", ec=BLUE, lw=2.2)

R = NUT_AF / np.sqrt(3)
for x, y, rot in NUTS:
    a = np.radians(np.arange(rot, rot + 360, 60))
    ax.add_patch(Polygon(np.c_[x + R * np.cos(a), y + R * np.sin(a)],
                         fc="#f3d9d9", ec=RED, lw=1.4))

ax.annotate("top screw kept —\nthe mouth opens inward only",
            xy=(20.0, 79.5), xytext=(11.0, 90.0), ha="center",
            fontsize=7.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=.8))

#  The two insets are 1.5 mm at a scale where the phone is 147 mm: label them
#  outside the outline, on a leader.
dim(cx, PL / 2, cx, cy + BASE / 2, "%.2f from the top" % FT,
    off=(0, 1.4), lead=(-8.0, 84.0))
dim(PW / 2, cy, cx + BASE / 2, cy, "%.2f from the side" % FS,
    off=(-1.5, -1.0), lead=(45.0, 18.0), ha="left")
dim(cx - BASE / 2, -PL / 2, cx - BASE / 2, cy - BASE / 2, "112.5 (measured)", (-9.5, 0))
dim(cx - BASE / 2, 30.0, cx + BASE / 2, 30.0, "%.1f (base)" % BASE, (0, -3.4))

for kw, lbl in (
    (dict(color=GREEN, lw=2), "island base %.1f — what the case must clear" % BASE),
    (dict(color=GREEN, lw=1, ls="--"), "island at the lens plateau %.1f" % PLATEAU),
    (dict(color=BLUE, lw=1.6, ls="--"), "opening against the phone %.1f" % SLOT),
    (dict(color=BLUE, lw=2.2), "mouth %.1f, offset %.1f on both axes" % (MOUTH, FLARE)),
    (dict(color=RED, lw=1.4), "nut pockets"),
):
    ax.plot([], [], label=lbl, **kw)
ax.legend(fontsize=8, loc="lower right")

# +X is the camera side; seen from the back it falls on the left.
ax.set_xlim(48, -42)
ax.set_ylim(-80, 97)
ax.set_aspect("equal")
ax.grid(alpha=.2, lw=.4)
ax.set_title("Camera opening in plan (seen from the BACK)\n"
             "the island is a truncated pyramid: %.1f at the base, %.1f at the plateau"
             % (BASE, PLATEAU), fontsize=10)
plt.tight_layout()
plt.savefig("camera_plan.png", dpi=120, facecolor="white")
print("camera_plan.png")
