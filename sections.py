# -*- coding: utf-8 -*-
"""Cortes 2D da v2: encaixe macho/femea, parafuso e camera."""
import os, numpy as np, Part
from FreeCAD import Vector
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.dirname(os.path.abspath(__file__))
sh = Part.Shape(); sh.read(os.path.join(D, "capa_v6_conjunto.step"))
sol = sh.Solids
base, aro = (sol[0], sol[1]) if sol[0].BoundBox.ZLength < sol[1].BoundBox.ZLength else (sol[1], sol[0])
CAMY = 146.7/2 - 6.0 - 30.2/2

def draw(ax, peca, cor, n, d, a, b):
    for w in peca.slice(Vector(*n), d):
        for e in w.Edges:
            p = np.array([(q[a], q[b]) for q in
                          [(v.x, v.y, v.z) for v in e.discretize(Number=60)]])
            ax.plot(p[:,0], p[:,1], color=cor, lw=1.5)

CB, CA = "#2f5d3f", "#8a5a1f"
fig, axs = plt.subplots(1, 3, figsize=(16.5, 6.2), facecolor="white")

for ax, y, tit, xlim, ylim in (
    (axs[0], -20.0, u"ENCAIXE  (corte em y=-20)\nmacho do aro 1,4×1,6 dentro da fêmea da base", (33, 41), (-0.5, 8)),
    (axs[1], -8.5, u"PARAFUSO DO MEIO  (corte em y=-8,5)\nv5: porca embutida na base, cabeca na borda frontal", (33, 45), (-0.5, 14.5)),
    (axs[2], CAMY, u"CÂMERA  (corte no centro da ilha)\nrasgo abocardado, costas de 4 mm", (-45, 45), (-1, 14))):
    draw(ax, base, CB, (0,1,0), y, 0, 2)
    draw(ax, aro,  CA, (0,1,0), y, 0, 2)
    ax.axhline(4.0, color="#999", lw=0.7, ls="--")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal"); ax.grid(alpha=.25, lw=.4)
    ax.set_title(tit, fontsize=9)
axs[0].plot([], [], color=CB, lw=2, label="base traseira")
axs[0].plot([], [], color=CA, lw=2, label="aro frontal")
axs[0].legend(fontsize=8, loc="upper left")
plt.tight_layout(); plt.savefig(os.path.join(D, "cortes.png"), dpi=115, facecolor="white")
print("-> cortes.png")
