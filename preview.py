# -*- coding: utf-8 -*-
"""View sheet of the two parts.

Run inside FreeCAD's interpreter, after case_iphone13.py has written the STEP:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd preview.py
"""
import os, numpy as np, Part
from FreeCAD import Vector
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

D = os.path.dirname(os.path.abspath(__file__))
sh = Part.Shape(); sh.read(os.path.join(D, "capa_v8_conjunto.step"))
sol = sh.Solids
base, aro = (sol[0], sol[1]) if sol[0].BoundBox.ZLength < sol[1].BoundBox.ZLength else (sol[1], sol[0])

def tri(s, dz=0.0):
    p, f = s.tessellate(0.05)
    V = np.array([[q.x, q.y, q.z + dz] for q in p]); F = np.array(f)
    T = V[F]
    N = np.cross(T[:,1]-T[:,0], T[:,2]-T[:,0])
    N /= (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)
    return T, N

COR = {"base": np.array([0.33, 0.37, 0.27]), "aro": np.array([0.45, 0.44, 0.36])}
def render(ax, peças, d, up, title):
    d = np.array(d, float); d /= np.linalg.norm(d)
    rx = np.cross(up, d); rx /= np.linalg.norm(rx); ry = np.cross(d, rx)
    P, C = [], []
    for nome, T, N in peças:
        v = N @ d > 0.001; t, n = T[v], N[v]
        # Light relative to the camera (upper left of the frame). Without this the
        # honeycomb recesses invert into an illusion of bumps.
        L = -0.45*rx + 0.55*ry + 0.70*d; L /= np.linalg.norm(L)
        inten = 0.30 + 0.70*np.clip(n @ L, 0, 1)
        P.append(t); C.append(np.clip(COR[nome][None,:]*inten[:,None]*1.65, 0, 1))
    t = np.concatenate(P); c = np.concatenate(C)
    o = np.argsort(t.mean(axis=1) @ d); t, c = t[o], c[o]
    poly = np.stack([t @ rx, t @ ry], axis=-1)
    ax.add_collection(PolyCollection(poly, facecolors=c, edgecolors=c, linewidths=0.1))
    ax.set_xlim(poly[...,0].min()-3, poly[...,0].max()+3)
    ax.set_ylim(poly[...,1].min()-3, poly[...,1].max()+3)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=9, color="#333")

Tb, Nb = tri(base); Ta, Na = tri(aro)
Tae, Nae = tri(aro, dz=26.0)                      # exploded view
mont = [("base", Tb, Nb), ("aro", Ta, Na)]
expl = [("base", Tb, Nb), ("aro", Tae, Nae)]

fig, axs = plt.subplots(2, 3, figsize=(15.5, 11), facecolor="white")
render(axs[0,0], mont, (0.55,0.4,-1), (0,1,0), "assembled - back 3/4")
render(axs[0,1], expl, (0.8,0.35,-0.75), (0,1,0), "exploded (frame lifted 26 mm)")
render(axs[0,2], mont, (-0.5,-0.35,1), (0,1,0), "assembled - front 3/4")
render(axs[1,0], [("base", Tb, Nb)], (0.2,0.15,1), (0,1,0), "PLATE - inner face (groove + through holes)")
render(axs[1,1], [("aro", Ta, Na)], (0.2,0.15,-1), (0,1,0), "FRAME - joint face (tongue + screw channels)")
render(axs[1,2], [("base", Tb, Nb)], (0,0,-1), (0,1,0), "PLATE - outer face: the 10 nut pockets")
plt.tight_layout()
plt.savefig(os.path.join(D, "preview.png"), dpi=105, facecolor="white")
print("-> preview.png")
