# -*- coding: utf-8 -*-
"""Cross-sections of the assembly: the joint, a screw, and the camera opening.

Run inside FreeCAD's interpreter, after case_iphone13.py has written the STEP:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd sections.py
"""
import os, re, numpy as np, Part
from FreeCAD import Vector
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.dirname(os.path.abspath(__file__))
sh = Part.Shape(); sh.read(os.path.join(D, "capa_v8_conjunto.step"))
sol = sh.Solids
base, aro = (sol[0], sol[1]) if sol[0].BoundBox.ZLength < sol[1].BoundBox.ZLength else (sol[1], sol[0])

# Cut the camera panel through the centre of the island, read from the generator
# so this section cannot drift away from the model.
SRC = open(os.path.join(D, "case_iphone13.py"), encoding="utf-8").read()
def p(name):
    return float(re.search(r"^%s\s*=\s*(-?[\d.]+)" % name, SRC, re.M).group(1))
CAMY = p("PL")/2 - p("CAM_FROM_TOP") - p("CAM_ISL")/2


def draw(ax, peca, cor, n, d, a, b):
    for w in peca.slice(Vector(*n), d):
        for e in w.Edges:
            q = np.array([(v.x, v.y, v.z) for v in e.discretize(Number=60)])
            ax.plot(q[:, a], q[:, b], color=cor, lw=1.5)


CB, CA = "#2f5d3f", "#8a5a1f"
fig, axs = plt.subplots(1, 3, figsize=(17.5, 6.2), facecolor="white",
                        gridspec_kw=dict(width_ratios=[1, 1.15, 2.6]))

for ax, y, tit, xlim, ylim in (
    (axs[0], -20.0, "JOINT  (section at y = -20)\n"
                    "the frame's 1.4 x 1.6 tongue inside the plate's groove", (33, 41), (-0.5, 8)),
    (axs[1], -8.5,  "MID-SIDE SCREW  (section at y = -8.5)\n"
                    "nut captive in the plate, head on the front rim", (33, 45), (-0.5, 14.5)),
    (axs[2], CAMY,  "CAMERA  (section through the centre of the island)\n"
                    "flared opening, 4 mm back", (-45, 45), (-1, 14))):
    draw(ax, base, CB, (0, 1, 0), y, 0, 2)
    draw(ax, aro,  CA, (0, 1, 0), y, 0, 2)
    ax.axhline(4.0, color="#999", lw=0.7, ls="--")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal"); ax.grid(alpha=.25, lw=.4)
    ax.set_title(tit, fontsize=9)

axs[0].plot([], [], color=CB, lw=2, label="back plate")
axs[0].plot([], [], color=CA, lw=2, label="front frame")
axs[0].legend(fontsize=8, loc="upper left")
plt.tight_layout(); plt.savefig(os.path.join(D, "sections.png"), dpi=115, facecolor="white")
print("-> sections.png  (camera section at y = %.2f)" % CAMY)
