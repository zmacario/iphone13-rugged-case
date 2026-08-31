# -*- coding: utf-8 -*-
"""
Capa robusta / anti-queda, estilo militar, para iPhone 13 (6.1", modelo padrao).
v4: DUAS PECAS aparafusadas com 10 parafusos (para impressao em PLA, que nao estica).
Gera STEP (solido BRep, para remodelar no Autodesk Fusion) e STL (para fatiar/imprimir).

Executar:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd case_iphone13.py

Sistema de coordenadas:
  X = largura   (+X = lado DIREITO do aparelho visto de FRENTE = lado do botao power/camera)
  Y = comprimento (+Y = topo do aparelho)
  Z = espessura (z=0 = face externa das costas = mesa da impressora; +Z aponta para a tela)
"""
import os, math
import FreeCAD as App
import Part
from FreeCAD import Vector

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# 1) PARAMETROS  -- tudo que voce pode querer ajustar esta aqui
# ============================================================================
# --- Aparelho (especificacao oficial Apple: 146.7 x 71.5 x 7.65 mm) ---------
PL   = 146.7   # comprimento do iPhone 13
PW   = 71.5    # largura
PT   = 7.65    # espessura
PR   = 9.0     # raio dos cantos do corpo do aparelho (estimado)

# --- Folgas (aumente para material rigido, diminua para TPU macio) ----------
CLR_XY = 0.45  # folga por lado em X/Y (PLA nao estica: um pouco mais de folga)
CLR_Z  = 0.30  # folga na espessura

# --- Paredes ---------------------------------------------------------------
WALL   = 3.4   # parede lateral
BACK   = 4.0   # costas (engrossado: e o que recua as lentes em relacao a mesa)
LIP_H  = 1.8   # quanto a borda sobe acima da tela (protecao ao cair de face)
LIP_IN = 1.5   # quanto a borda avanca sobre o bezel (retencao do aparelho)

# --- Reforco dos 4 cantos (o "anti-queda") ---------------------------------
BUMP    = 4.0   # material extra para fora, nos cantos (tambem abriga os parafusos)
CHAM_BOT= 0.5   # chanfro da aresta inferior externa (1a camada limpa)
BUMP_R  = 19.0  # raio do disco que define o alcance do reforco em cada canto
MIDPAD_R= 17.0  # idem para o reforco no meio de cada lateral longa (v3)
MIDPAD_Y= -8.5  # centro do reforco/parafuso do meio. Nao pode subir: acima disso
                # o reforco invade a janela do volume e o botao vira um poco fundo
BUMP_FIL= 1.4   # arredondamento da transicao reforco -> corpo
POCKET  = 1.6   # bolsa de ar interna no canto (zona de deformacao). 0 = desliga

# --- Recortes da camera (VERIFICAR COM PAQUIMETRO - ver README) -------------
CAM_ISL      = 30.2   # lado da ilha de cameras (quadrada) - ESTIMADO
CAM_ISL_R    = 8.4    # raio dos cantos da ilha
CAM_FROM_TOP = 6.0    # da borda superior do aparelho ate a borda da ILHA
CAM_FROM_SIDE= 6.2    # da borda lateral (+X) do aparelho ate a borda da ILHA
CAM_CLR      = 0.9    # folga em volta da ilha
CAM_FLARE    = 2.2    # abocardamento do rasgo por lado (evita vinheta na ultra-wide)
CAM_BUMP_H   = 1.9    # saliencia da camera acima das costas do aparelho (so p/ relatorio)

# --- Botoes e portas: centro medido a partir do TOPO do aparelho ------------
MUTE_Y,  MUTE_LEN  = 28.5, 12.0   # chave silencioso  (lado -X)
VOL_Y,   VOL_LEN   = 54.0, 31.0   # janela unica cobrindo volume + e -  (lado -X)
PWR_Y,   PWR_LEN   = 46.5, 26.0   # power / lateral   (lado +X)
PORT_W             = 17.0         # rasgo do Lightning (base)
SPK_W, SPK_X       = 14.0, 18.0   # rasgos alto-falante/microfone (base)

# --- Textura e pegada ------------------------------------------------------
HEX_AF, HEX_PITCH, HEX_DEPTH = 6.4, 8.6, 1.20  # favo nas costas (alivia peso das costas grossas)
GRIP_Y0, GRIP_Y1, GRIP_STEP = -49.0, -25.0, 6.0  # faixa dos frisos (entre os dois reforcos)
GRIP_W, GRIP_DEPTH, GRIP_ANG = 2.4, 1.0, 25.0

MIRROR = False   # True = espelha a capa em X (se a camera sair no lado errado)

# --- v2: divisao em duas pecas + parafusos ---------------------------------
TWO_PIECE  = True    # False = volta a peca unica da v1 (para TPU)
TONGUE_OFF = 1.0     # macho: afastamento a partir da parede da cavidade
TONGUE_W   = 1.4     # macho: largura
TONGUE_H   = 1.6     # macho: altura (desce do aro para dentro da base)
JOINT_GAP  = 0.15    # folga do encaixe macho/femea
JOINT_BREAK= 7.0     # interrupcao do macho em volta de cada parafuso
SEAM_CHAM  = 0.4     # chanfro nas duas bordas da juncao (forma um V de 0,8 mm)

# Parafusos: M3 x 10 mm cabeca ABAULADA (ISO 7380), 4 un., auto-atarraxantes no PLA.
# Cabeca abaulada em rebaixo de fundo plano, e nao escareada: cabeca conica faz
# forca de cunha ao apertar e racha PLA em parede fina.
SCREW_N     = "M3 x 10 cabeca abaulada (ISO 7380)"
SCREW_CLEAR = 3.4    # furo passante na base
SCREW_HEAD  = 6.2    # diametro do rebaixo da cabeca
SCREW_CB    = 2.0    # profundidade do rebaixo (cabeca tem 1,65 mm: fica 0,35 afundada)
SCREW_PILOT = 2.6    # furo-guia no aro
SCREW_DEPTH = 9.2    # profundidade do furo-guia
SCREW_D     = 9.0    # posicao ao longo da parede longa, a partir do centro do arco de canto
# v4: mais 2 parafusos no topo e 2 no fundo, aproveitando os ressaltos dos cantos.
# O do fundo nao pode ser central: os rasgos do alto-falante ocupam x de 11 a 25 mm.
SHORT_EDGE_SCREWS = True   # False = volta aos 6 parafusos da v3 (so laterais)
SCREW_TOP_X = 18.5   # parafusos da aresta do topo
SCREW_BOT_X = 30.0   # parafusos da aresta do fundo (empurrados pelo alto-falante)

# ---- Derivados ------------------------------------------------------------
IL = PL + 2*CLR_XY          # cavidade
IW = PW + 2*CLR_XY
IR = PR + CLR_XY
IT = PT + CLR_Z
OL = IL + 2*WALL            # corpo externo
OW = IW + 2*WALL
ORR= IR + WALL
OH = BACK + IT + LIP_H      # altura total
CAM_W = CAM_ISL + 2*CAM_CLR # rasgo junto ao aparelho
CAM_R = CAM_ISL_R + CAM_CLR

# ============================================================================
# 2) HELPERS
# ============================================================================
def rrect(w, l, h, r, cx=0.0, cy=0.0, z0=0.0):
    """Prisma de base retangular com cantos arredondados. w=X, l=Y, h=Z."""
    b = Part.makeBox(w, l, h, Vector(cx - w/2.0, cy - l/2.0, z0))
    if r > 1e-6:
        ve = []
        for e in b.Edges:
            d = e.Vertexes[1].Point.sub(e.Vertexes[0].Point)
            if abs(d.x) < 1e-6 and abs(d.y) < 1e-6:
                ve.append(e)
        b = b.makeFillet(r, ve)
    return b

def rrect_wire(w, l, r, cx, cy, z):
    """Fio (wire) de retangulo arredondado no plano z."""
    s = rrect(w, l, 1.0, r, cx, cy, z)
    return min(s.Faces, key=lambda f: f.CenterOfMass.z).OuterWire

def hexprism(af, h, cx, cy, z0):
    R = af / math.sqrt(3.0)
    pts = [Vector(cx + R*math.cos(math.radians(60*i + 30)),
                  cy + R*math.sin(math.radians(60*i + 30)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.Wire(Part.makePolygon(pts))).extrude(Vector(0, 0, h))

def inside_rrect(x, y, w, l, r):
    """Ponto dentro de um retangulo arredondado centrado na origem?"""
    ax, ay = abs(x), abs(y)
    if ax > w/2.0 or ay > l/2.0:
        return False
    cx, cy = w/2.0 - r, l/2.0 - r
    if ax <= cx or ay <= cy:
        return True
    return math.hypot(ax - cx, ay - cy) <= r

def safe(op, label, shape):
    """Executa uma operacao opcional (fillet/chamfer); se falhar, segue o baile."""
    try:
        out = op()
        if out.isValid():
            print("   [ok]   %s" % label)
            return out
        print("   [skip] %s (resultado invalido)" % label)
    except Exception as e:
        print("   [skip] %s (%s)" % (label, str(e).splitlines()[0][:60]))
    return shape

# ============================================================================
# 3) CORPO EXTERNO + REFORCO DOS CANTOS
# ============================================================================
print("-> corpo externo e reforcos de canto")
body = rrect(OW, OL, OH, ORR)

# Reforcos: perfil externo inflado, recortado por um disco em cada canto.
big = rrect(OW + 2*BUMP, OL + 2*BUMP, OH, ORR + BUMP)
ccx, ccy = OW/2.0 - ORR, OL/2.0 - ORR          # centros dos raios de canto
# (x, y, raio) de cada disco de reforco: 4 cantos + 2 no meio das laterais longas
PADS = [(sx*ccx, sy*ccy, BUMP_R) for sx in (-1, 1) for sy in (-1, 1)] + \
       [(sx*ccx, MIDPAD_Y, MIDPAD_R) for sx in (-1, 1)]
def pad_half_y(R):
    """Meia-extensao do reforco ao longo da parede."""
    return math.sqrt(max(R*R - ORR*ORR, 0.0))
for px, py, R in PADS:
    body = body.fuse(big.common(Part.makeCylinder(R, OH, Vector(px, py, 0.0))))
body = body.removeSplitter()

# Suaviza a transicao reforco -> corpo (arestas verticais criadas pela uniao)
junc = []
for e in body.Edges:
    p0, p1 = e.Vertexes[0].Point, e.Vertexes[-1].Point
    if abs(p0.x - p1.x) < 1e-6 and abs(p0.y - p1.y) < 1e-6 and abs(p1.z - p0.z) > OH*0.8:
        for px, py, R in PADS:
            if abs(math.hypot(p0.x - px, p0.y - py) - R) < 0.15:
                junc.append(e)
if junc:
    body = safe(lambda: body.makeFillet(BUMP_FIL, junc), "fillet transicao dos reforcos", body)

# Chanfros no perimetro inferior (1a camada limpa) e superior
def perimeter_edges(shape, z, tol=1e-4):
    out = []
    for e in shape.Edges:
        if all(abs(v.Point.z - z) < tol for v in e.Vertexes):
            out.append(e)
    return out
body = safe(lambda: body.makeChamfer(CHAM_BOT, perimeter_edges(body, 0.0)), "chanfro inferior", body)
body = safe(lambda: body.makeChamfer(0.6, perimeter_edges(body, OH)),   "chanfro superior", body)

# ============================================================================
# 4) CAVIDADE + BORDA FRONTAL (LIP)
# ============================================================================
print("-> cavidade interna e borda frontal")
cav  = rrect(IW, IL, IT + 0.001, IR, z0=BACK)                       # onde o aparelho encaixa
open_= rrect(IW - 2*LIP_IN, IL - 2*LIP_IN, LIP_H + 2.0,
             max(IR - LIP_IN, 0.5), z0=BACK + IT)                   # abertura da tela
case = body.cut(cav.fuse(open_))

# ============================================================================
# 5) RECORTES FUNCIONAIS
# ============================================================================
print("-> recortes (camera, botoes, portas)")
cuts = []

# Camera: rasgo abocardado - estreito junto ao aparelho, largo na face externa.
# A ilha fica AFUNDADA no rasgo; as lentes recuam BACK - CAM_BUMP_H em relacao a mesa.
cam_cx = PW/2.0 - CAM_FROM_SIDE - CAM_ISL/2.0
cam_cy = PL/2.0 - CAM_FROM_TOP  - CAM_ISL/2.0
CAM_OUT_W = CAM_W + 2*CAM_FLARE
CAM_OUT_R = CAM_R + CAM_FLARE
flare = Part.makeLoft([rrect_wire(CAM_OUT_W, CAM_OUT_W, CAM_OUT_R, cam_cx, cam_cy, 0.0),
                       rrect_wire(CAM_W,     CAM_W,     CAM_R,     cam_cx, cam_cy, BACK)],
                      True, True)
flare = flare.fuse(rrect(CAM_OUT_W, CAM_OUT_W, 1.5, CAM_OUT_R, cam_cx, cam_cy, -1.5))
flare = flare.fuse(rrect(CAM_W, CAM_W, 1.5, CAM_R, cam_cx, cam_cy, BACK))
cuts.append(flare.removeSplitter())

# Janelas laterais dos botoes: da base da cavidade ate o plano da tela
zb, zt = BACK + 0.9, BACK + IT
def side_slot(sign_x, y_from_top, length):
    y = PL/2.0 - y_from_top
    return Part.makeBox(WALL + BUMP + 6.0, length, zt - zb,
                        Vector(sign_x*(IW/2.0 - 1.0) if sign_x > 0
                               else -(IW/2.0 - 1.0) - (WALL + BUMP + 6.0),
                               y - length/2.0, zb))
cuts += [side_slot(-1, MUTE_Y, MUTE_LEN),
         side_slot(-1, VOL_Y,  VOL_LEN),
         side_slot(+1, PWR_Y,  PWR_LEN)]

# Base: Lightning + alto-falante/microfone
def bottom_slot(cx, w):
    depth = WALL + BUMP + 6.0
    return Part.makeBox(w, depth, zt - zb, Vector(cx - w/2.0, -(IL/2.0 - 1.0) - depth, zb))
cuts += [bottom_slot(0.0, PORT_W), bottom_slot(+SPK_X, SPK_W), bottom_slot(-SPK_X, SPK_W)]

case = case.cut(Part.makeCompound(cuts))

# ============================================================================
# 6) BOLSAS DE AR NOS CANTOS (zona de deformacao)
# ============================================================================
if POCKET > 1e-6:
    print("-> bolsas de ar nos cantos")
    icx, icy = IW/2.0 - IR, IL/2.0 - IR
    # comeca 0,05 mm acima do plano de corte: encostar exatamente nele cria
    # arestas degeneradas na face de juncao da base e impede o chanfro
    pk = [Part.makeCylinder(IR + POCKET, IT - 0.05, Vector(sx*icx, sy*icy, BACK + 0.05))
          for sx in (-1, 1) for sy in (-1, 1)]
    case = case.cut(Part.makeCompound(pk))

# ============================================================================
# 7) TEXTURA (favo de mel nas costas) + FRISOS DE PEGADA
# ============================================================================
print("-> textura e frisos")
tex = []
cam_x0, cam_x1 = cam_cx - CAM_OUT_W/2.0 - 3.5, cam_cx + CAM_OUT_W/2.0 + 3.5
cam_y0, cam_y1 = cam_cy - CAM_OUT_W/2.0 - 3.5, cam_cy + CAM_OUT_W/2.0 + 3.5
nx = int((OW + 2*BUMP) / (HEX_PITCH * math.sqrt(3)/2.0)) + 2
ny = int((OL + 2*BUMP) / HEX_PITCH) + 2
for i in range(-nx, nx + 1):
    for j in range(-ny, ny + 1):
        x = i * HEX_PITCH * math.sqrt(3) / 2.0
        y = j * HEX_PITCH + (HEX_PITCH/2.0 if i % 2 else 0.0)
        if cam_x0 < x < cam_x1 and cam_y0 < y < cam_y1:
            continue
        if not inside_rrect(x, y, OW - 6.0, OL - 6.0, ORR):
            continue
        tex.append(hexprism(HEX_AF, HEX_DEPTH, x, y, -0.001))
if tex:
    case = case.cut(Part.makeCompound(tex))

grip = []
ygrip = [GRIP_Y0 + k*GRIP_STEP for k in range(int((GRIP_Y1 - GRIP_Y0)/GRIP_STEP) + 1)]
for y in ygrip:
    if any(abs(y - py) < pad_half_y(R) + GRIP_W for _px, py, R in PADS):
        continue          # friso sobre um reforco viraria uma vala de 4 mm
    for sx in (-1, 1):
        b = Part.makeBox(GRIP_DEPTH + 3.0, GRIP_W, 34.0,
                         Vector(sx*(OW/2.0 - GRIP_DEPTH) if sx > 0
                                else -(OW/2.0 - GRIP_DEPTH) - (GRIP_DEPTH + 3.0),
                                y - GRIP_W/2.0, OH/2.0 - 17.0))
        b.rotate(Vector(sx*OW/2.0, y, OH/2.0), Vector(1, 0, 0), GRIP_ANG)
        grip.append(b)
if grip:
    case = case.cut(Part.makeCompound(grip))

case = case.removeSplitter()
if MIRROR:
    m = App.Matrix(); m.scale(-1, 1, 1)
    case = case.transformGeometry(m)

# ============================================================================
# 8) DIVISAO EM DUAS PECAS + PARAFUSOS
# ============================================================================
def face_at_z(sh, z):
    c = [f for f in sh.Faces if all(abs(v.Point.z - z) < 1e-6 for v in f.Vertexes)]
    return max(c, key=lambda f: f.Area) if c else None

def joint_ring(off0, off1, z0, h):
    o = rrect(IW + 2*off1, IL + 2*off1, h, IR + off1, 0, 0, z0)
    i = rrect(IW + 2*off0, IL + 2*off0, h + 0.4, IR + off0, 0, 0, z0 - 0.2)
    return o.cut(i)

parts = [("CapaIPhone13", case)]
if TWO_PIECE:
    print("-> divisao em duas pecas")
    SPLIT_Z = BACK                      # plano de corte = costas do aparelho
    # Parafuso posicionado para equilibrar as duas margens criticas:
    # (furo-guia -> parede da cavidade) e (escareado -> superficie externa).
    # O chanfro inferior come material exatamente onde o rebaixo e mais largo,
    # entao ele entra na conta da margem externa.
    sxp = 0.5*((IW/2.0 + SCREW_PILOT/2.0) + (OW/2.0 + BUMP - CHAM_BOT - SCREW_HEAD/2.0))
    syp = (IL/2.0 - IR) - SCREW_D
    # Parafusos das arestas curtas: mesma regra de equilibrio das margens, no eixo Y.
    syp_t = 0.5*((IL/2.0 + SCREW_PILOT/2.0) + (OL/2.0 + BUMP - CHAM_BOT - SCREW_HEAD/2.0))
    screws = [(gx*sxp, gy*syp) for gx in (-1, 1) for gy in (-1, 1)] + \
             [(gx*sxp, MIDPAD_Y) for gx in (-1, 1)]
    if SHORT_EDGE_SCREWS:
        screws += [(gx*SCREW_TOP_X,  syp_t) for gx in (-1, 1)] + \
                  [(gx*SCREW_BOT_X, -syp_t) for gx in (-1, 1)]
    # Ao longo da aresta curta o ressalto so tem espessura cheia nesta faixa em X:
    _full_x = math.sqrt(max(BUMP_R**2 - (OL/2.0 + BUMP - ccy)**2, 0.0))
    _cam_gap = (syp_t - SCREW_HEAD/2.0) - (cam_cy + CAM_OUT_W/2.0)
    _spk_gap = (SCREW_BOT_X - SCREW_HEAD/2.0) - (SPK_X + SPK_W/2.0)
    VAO = max(syp - MIDPAD_Y, MIDPAD_Y + syp)
    _jan = PL/2.0 - VOL_Y - VOL_LEN/2.0
    _top = MIDPAD_Y + pad_half_y(MIDPAD_R)
    MARG_IN  = sxp - SCREW_PILOT/2.0 - IW/2.0
    MARG_OUT = (OW/2.0 + BUMP - CHAM_BOT) - sxp - SCREW_HEAD/2.0

    B = 600.0
    base = case.common(Part.makeBox(B, B, B, Vector(-B/2, -B/2, SPLIT_Z - B))).removeSplitter()
    aro  = case.common(Part.makeBox(B, B, B, Vector(-B/2, -B/2, SPLIT_Z))).removeSplitter()
    # removeSplitter acima e obrigatorio: sem ele a face de juncao sai partida em
    # varias faces coplanares e o chanfro da juncao falha silenciosamente.
    for _n, _sh in (("base", base), ("aro", aro)):
        _c = [f for f in _sh.Faces if all(abs(v.Point.z - SPLIT_Z) < 1e-6 for v in f.Vertexes)]
        if len(_c) != 1:
            print("   [aviso] face de juncao da %s partida em %d faces" % (_n, len(_c)))

    # chanfro nas duas bordas externas da juncao (vira um V discreto na montagem)
    for nome, obj in (("base", "base"), ("aro", "aro")):
        sh = base if obj == "base" else aro
        f = face_at_z(sh, SPLIT_Z)
        if f:
            sh = safe(lambda sh=sh, f=f: sh.makeChamfer(SEAM_CHAM, f.OuterWire.Edges),
                      "chanfro da juncao (%s)" % nome, sh)
        if obj == "base": base = sh
        else:             aro = sh

    # Macho no ARO (desce para dentro da base), femea na BASE.
    # De proposito nesta ordem: assim a face de juncao do aro fica inteira, e o
    # rasgo cai numa chapa macica de 4 mm, que sobra material de sobra.
    tongue = joint_ring(TONGUE_OFF, TONGUE_OFF + TONGUE_W, SPLIT_Z - TONGUE_H, TONGUE_H)
    tongue = tongue.cut(Part.makeCompound(
        [Part.makeCylinder(JOINT_BREAK/2.0, TONGUE_H + 1.0, Vector(x, y, SPLIT_Z - TONGUE_H - 0.5))
         for x, y in screws]))
    aro = aro.fuse(tongue).removeSplitter()
    base = base.cut(joint_ring(TONGUE_OFF - JOINT_GAP, TONGUE_OFF + TONGUE_W + JOINT_GAP,
                               SPLIT_Z - TONGUE_H - JOINT_GAP, TONGUE_H + JOINT_GAP + 0.2))

    # furos: passante + escareado na base, furo-guia no aro
    bc, ac = [], []
    for x, y in screws:
        bc.append(Part.makeCylinder(SCREW_CLEAR/2.0, SPLIT_Z + 1.0, Vector(x, y, -0.5)))
        bc.append(Part.makeCylinder(SCREW_HEAD/2.0, SCREW_CB + 0.8, Vector(x, y, -0.8)))
        ac.append(Part.makeCylinder(SCREW_PILOT/2.0, SCREW_DEPTH, Vector(x, y, SPLIT_Z - 0.2)))
    base = base.cut(Part.makeCompound(bc)).removeSplitter()
    aro  = aro.cut(Part.makeCompound(ac)).removeSplitter()
    parts = [("Base_traseira", base), ("Aro_frontal", aro)]

# ============================================================================
# 9) VERIFICACAO E EXPORTACAO
# ============================================================================
print("\n== RELATORIO ==")
tot = 0.0
for nome, sh in parts:
    bb = sh.BoundBox; tot += sh.Volume
    print("%-14s: valido=%s solidos=%d | %.2f x %.2f x %.2f mm | %.1f cm3 | %.0f g PLA"
          % (nome, sh.isValid(), len(sh.Solids), bb.XLength, bb.YLength, bb.ZLength,
             sh.Volume/1000.0, sh.Volume/1000.0*1.24))
print("conjunto      : %.1f cm3 | %.0f g em PLA" % (tot/1000.0, tot/1000.0*1.24))
if len(parts) == 2:
    # A checagem que importa numa peca dividida: as duas metades nao podem
    # ocupar o mesmo espaco, ou nao fecham.
    _int = parts[0][1].common(parts[1][1]).Volume
    print("interferencia : %.4f mm3  %s"
          % (_int, "OK" if _int < 1e-3 else "<< AS PECAS SE SOBREPOEM"))
print("parede %.2f mm | costas %.2f mm | recuo da lente %.2f mm"
      % (WALL, BACK, BACK - CAM_BUMP_H))
print("rasgo camera  : %.1f -> %.1f mm" % (CAM_W, CAM_OUT_W))
if TWO_PIECE:
    print("parafusos     : %d x %s" % (len(screws), SCREW_N))
    print("  cantos: (x=+-%.2f, y=+-%.2f) | meio das laterais: (x=+-%.2f, y=%.2f)"
          % (sxp, syp, sxp, MIDPAD_Y))
    print("  topo: (x=+-%.2f, y=%.2f) | fundo: (x=+-%.2f, y=%.2f)"
          % (SCREW_TOP_X, syp_t, SCREW_BOT_X, -syp_t))
    print("  vao maximo nas laterais: %.2f mm (era %.2f mm com 4 parafusos)" % (VAO, 2*syp))
    print("  vao no topo: %.2f mm | no fundo: %.2f mm" % (2*SCREW_TOP_X, 2*SCREW_BOT_X))
    for _l, _x in (("topo ", SCREW_TOP_X), ("fundo", SCREW_BOT_X)):
        print("  %s: ressalto com espessura cheia? %s  (x cheio de %.2f a %.2f)"
              % (_l, "sim" if abs(_x - ccx) <= _full_x else "NAO",
                 ccx - _full_x, ccx + _full_x))
    print("  folga rebaixo do topo -> rasgo da camera : %.2f mm %s" % (_cam_gap, "OK" if _cam_gap > 1.0 else "<< FINO"))
    print("  folga rebaixo do fundo -> alto-falante   : %.2f mm %s" % (_spk_gap, "OK" if _spk_gap > 1.0 else "<< FINO"))
    print("  topo do reforco do meio em y=%.2f, janela do volume comeca em y=%.2f  %s"
          % (_top, _jan, "OK" if _top < _jan - 0.5 else "<< INVADE A JANELA"))
    print("  margem furo-guia -> cavidade : %.2f mm %s" % (MARG_IN,  "OK" if MARG_IN  > 1.0 else "<< FINO"))
    print("  margem rebaixo   -> externa  : %.2f mm %s" % (MARG_OUT, "OK" if MARG_OUT > 1.0 else "<< FINO"))
    print("encaixe macho/femea: %.1f x %.1f mm, folga %.2f mm" % (TONGUE_W, TONGUE_H, JOINT_GAP))
    print("  rebaixo %.1f mm fundo: sobra %.2f mm de chapa sob a cabeca" % (SCREW_CB, BACK - SCREW_CB))
    print("  rosca no aro: de z=%.1f a z=%.1f (%.1f mm de pega, %.2f mm ate o topo)"
          % (SPLIT_Z, SPLIT_Z + 8.0, 8.0, OH - (SPLIT_Z - 0.2 + SCREW_DEPTH)))

doc = App.newDocument("case")
objs = []
for nome, sh in parts:
    o = doc.addObject("Part::Feature", nome); o.Shape = sh; objs.append(o)
doc.recompute()

pref = "capa_v4" if TWO_PIECE else "capa_iphone13_militar"
step = os.path.join(OUT_DIR, pref + ("_conjunto.step" if TWO_PIECE else ".step"))
Part.export(objs, step)
print("\nSTEP -> %s  (%d corpos)" % (step, len(objs)))

import Mesh, MeshPart
def to_stl(sh, path):
    MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.04,
                           AngularDeflection=0.15, Relative=False).write(path)
    return path

for nome, sh in parts:
    f = os.path.join(OUT_DIR, "%s_%s.stl" % (pref, nome.lower()) if TWO_PIECE else pref + ".stl")
    to_stl(sh, f); print("STL  -> %s" % f)

doc.saveAs(os.path.join(OUT_DIR, pref + ".FCStd"))
print("FCStd-> %s" % os.path.join(OUT_DIR, pref + ".FCStd"))

# Cupons de teste: o canto da camera de cada peca, para validar encaixe,
# parafuso e recorte da camera antes de imprimir tudo.
bb = parts[0][1].BoundBox
for nome, sh in parts:
    try:
        cx1, cy1 = case.BoundBox.XMax, case.BoundBox.YMax
        cp = sh.common(Part.makeBox(64, 64, OH + 4, Vector(cx1 - 64, cy1 - 64, -2)))
        f = os.path.join(OUT_DIR, "teste_canto_%s.stl" % nome.split("_")[0].lower())
        to_stl(cp, f); print("CUPOM-> %s" % f)
    except Exception as e:
        print("cupom %s falhou: %s" % (nome, e))
