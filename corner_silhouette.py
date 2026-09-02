"""Corner silhouette in plan, for five values of PAD_R.

PAD_R is the outer radius of the six reinforcement pads. Smaller is squarer. The
value the model was generated with is drawn heavier. Dimensions are parsed out of
case_iphone13.py so this drawing cannot drift away from the model.

    python3 corner_silhouette.py     ->  corner_silhouette.png
"""
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = open("case_iphone13.py", encoding="utf-8").read()


def p(name):
    m = re.search(r"^%s\s*=\s*(-?[\d.]+)" % name, SRC, re.M)
    if not m:
        raise SystemExit("parameter %s not found in case_iphone13.py" % name)
    return float(m.group(1))


PW, PL, PR = p("PW"), p("PL"), p("PR")
CLR, WALL, BUMP, BUMP_R = p("CLR_XY"), p("WALL"), p("BUMP"), p("BUMP_R")
CURRENT = p("PAD_R")

IW, IL = PW + 2 * CLR, PL + 2 * CLR          # phone cavity
OW, OL = IW + 2 * WALL, IL + 2 * WALL        # body
IR = PR + CLR
ORR = IR + WALL
ccx, ccy = OW / 2 - ORR, OL / 2 - ORR        # centre of the corner arc

# Before PAD_R became a parameter of its own, the pads inherited their radius
# from the offset body: ORR + BUMP, which is where the soft lobed corners came from.
INHERITED = round(ORR + BUMP, 2)
VARIANTS = [(INHERITED, "#bbbbbb", "inherited from the body"),
            (14.0, "#7aa37a", None),
            (CURRENT, "#2f5d3f", "as generated"),
            (11.0, "#8a5a1f", None),
            (9.0, "#a03030", None)]


def in_rr(X, Y, w, l, r):
    """True where (X, Y) is inside a rounded rectangle centred on the origin."""
    ax_, ay_ = np.abs(X), np.abs(Y)
    cx, cy = w / 2 - r, l / 2 - r
    inside = (ax_ <= w / 2) & (ay_ <= l / 2)
    corner = (ax_ > cx) & (ay_ > cy)
    d = np.hypot(np.clip(ax_ - cx, 0, None), np.clip(ay_ - cy, 0, None))
    return inside & (~corner | (d <= r))


x = np.linspace(20, 46, 700)
y = np.linspace(45, 85, 900)
X, Y = np.meshgrid(x, y)
body = in_rr(X, Y, OW, OL, ORR)

fig, ax = plt.subplots(figsize=(7.5, 8), facecolor="white")

for pr, colour, note in VARIANTS:
    pad = in_rr(X, Y, OW + 2 * BUMP, OL + 2 * BUMP, pr) & (np.hypot(X - ccx, Y - ccy) <= BUMP_R)
    lw = 2.6 if pr == CURRENT else 1.5
    ax.contour(X, Y, (body | pad).astype(float), levels=[0.5], colors=[colour], linewidths=lw)
    lbl = "PAD_R = %.2f" % pr if pr > 16 else "PAD_R = %.1f" % pr
    ax.plot([], [], color=colour, lw=lw, label=lbl + ("  (%s)" % note if note else ""))

ax.contour(X, Y, in_rr(X, Y, IW, IL, IR).astype(float), levels=[0.5],
           colors=["#888"], linestyles=":")
ax.plot([], [], color="#888", ls=":", label="cavity (the phone)")

ax.plot([39.25], [57.35], "ko", ms=5)
ax.annotate("corner screw", (39.25, 57.35), textcoords="offset points",
            xytext=(-88, -4), fontsize=8)
ax.plot([30.0], [76.85], "ko", ms=5)
ax.annotate("bottom screw\n(mirrored here)", (30.0, 76.85), textcoords="offset points",
            xytext=(-58, 10), fontsize=8)

ax.set_aspect("equal")
ax.grid(alpha=.25, lw=.4)
ax.legend(fontsize=8, loc="lower left")
ax.set_title("Top-right corner silhouette in plan\n"
             "the smaller the radius, the squarer the pad", fontsize=10)
plt.tight_layout()
plt.savefig("corner_silhouette.png", dpi=120, facecolor="white")
print("corner_silhouette.png")
