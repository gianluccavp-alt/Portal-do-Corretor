#!/usr/bin/env python3
"""park_mapa.py -- monta o chao do Village Park e grava park_chao.json, lido pelo gerador no Blender.

Fora do Blender, num venv com numpy, pillow e shapely:  python park_mapa.py [pasta_de_conferencia]

O chao e desenhado a mao em park_chao_mao.py (poligonos em px da implantacao,
assets/img/village-park/plantas/implantacao.jpg, 2600 x 2870 px, 0,079 m/px). Daqui sai, tudo em px da imagem
(x para a direita, y para baixo):
  tri_asfalto / tri_grama / tri_passeio : triangulos [x0, y0, x1, y1, x2, y2] sem sobreposicao
  guias          : trechos da divisa asfalto-grama [x0, y0, x1, y1, nx, ny], (nx, ny) apontando para a grama
  bordas_passeio : trechos da borda da calcada levantada [x0, y0, x1, y1, nx, ny], normal para fora
  tri_faixas     : triangulos das faixas pintadas (vagas e faixas de pedestre), recortadas pelo asfalto
  grama          : retangulos (x0, y0, x1, y1) do gramado, numa grade de 2 px (postes procuram o gramado aqui)
  arvores        : (tipo, x, y) pelas copas coloridas da implantacao
  carros         : (x, y, giro) da lista a mao em park_planta.py
As faixas das vagas nao sao copiadas pixel a pixel: em cada fileira o passo e a fase das divisorias sao medidos
no desenho e as linhas cobrem a fileira inteira (o desenho tem carros e copas por cima).
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
from shapely.prepared import prep

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import park_planta as P
import park_chao_mao as M

IMG = os.path.join(AQUI, '..', '..', '..', 'img', 'village-park', 'plantas', 'implantacao.jpg')
im = Image.open(IMG).convert('RGB')
a = np.asarray(im).astype(np.int16)
H, W = a.shape[:2]
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
mn = a.mean(2)
sat = a.max(2) - a.min(2)
branco = (sat < 30) & (mn >= 200)
DESC, ASF, GRAMA, CLARO = 0, 1, 2, 3


def caixa(m, r):
    """Soma numa janela (2r+1)^2 por imagem integral."""
    c = np.pad(m.astype(np.int32), ((r + 1, r), (r + 1, r))).cumsum(0).cumsum(1)
    return c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:] - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1]


def desvio(v, r):
    n = (2 * r + 1) ** 2
    m1 = caixa(v, r) / n
    m2 = caixa(v * v, r) / n
    return np.sqrt(np.maximum(m2 - m1 * m1, 0))


def retangulos(rs):
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in rs:
        m[int(y0):int(y1), int(x0):int(x1)] = True
    return m


# ------------------------------------------------------------------ geometria do chao (park_chao_mao.py)
def _no_ref(ref, g):
    if ref == 'img':
        return g
    return shapely.transform(g, lambda c: np.array([M.L(u, v) for u, v in c]))


def _ret_redondo(x0, y0, x1, y1, rr):
    rr = min(rr, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return box(x0 + rr, y0 + rr, x1 - rr, y1 - rr).buffer(rr, quad_segs=6)


def forma(ref, f):
    t = f[0]
    if t == 'r':
        g = box(*f[1:5])
    elif t == 'rr':
        g = _ret_redondo(*f[1:])
    elif t == 'q':
        x0, y0, x1, y1, cx, cy, rr = f[1:]
        g = box(x0, y0, x1, y1).intersection(Point(cx, cy).buffer(rr, quad_segs=16))
    elif t == 'arco':
        cx, cy, r0, r1, poli = f[1:]
        g = Point(cx, cy).buffer(r1, quad_segs=24)
        if r0:
            g = g.difference(Point(cx, cy).buffer(r0, quad_segs=24))
        g = g.intersection(Polygon(poli))
    else:
        g = Polygon(f[1])
    return _no_ref(ref, g)


def uniao(lista):
    return unary_union([forma(ref, f) for ref, f in lista])


def _limpa(g):
    g = shapely.set_precision(g.buffer(0), 0.05)
    g = g.buffer(0.3, join_style=2).buffer(-0.6, join_style=2).buffer(0.3, join_style=2)   # tira lascas < 0,6 px
    return g


def calcadas_torres():
    out = []
    for (cx, cy), giro in P.TORRES.values():
        mx_, my_ = (98, 278) if giro in (0.0, 180.0) else (278, 98)
        out.append(box(cx - mx_, cy - my_, cx + mx_, cy + my_))
    return unary_union(out)


terreno = Polygon(P.TERRENO)
regiao = unary_union([terreno, box(*P.AVENIDA)]).difference(unary_union([box(*r) for r in P.ZONAS_A_MAO]))
arcos = unary_union([Point(c).buffer(M.R_ARCO[1], quad_segs=24).intersection(Polygon(bx)) for c, bx in M.ARCOS])
# limpa cada classe uma vez e so depois recorta (as divisas ficam com os mesmos vertices dos dois lados)
G_PAS = _limpa(uniao(M.PASSEIO).union(calcadas_torres()).intersection(regiao))
G_ASF = _limpa(uniao(M.ASFALTO).difference(uniao(M.CANTEIROS)).difference(arcos).intersection(regiao))
G_ASF = G_ASF.difference(G_PAS)


def raster(g, val, cl):
    """Pinta o poligono (ou multipoligono, com furos) no mapa de classes."""
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty:
            continue
        d.polygon([tuple(c) for c in p.exterior.coords], fill=1)
        for it in p.interiors:
            d.polygon([tuple(c) for c in it.coords], fill=0)
    cl[np.asarray(m).astype(bool)] = val


area = np.zeros((H, W), np.uint8)
raster(regiao, 1, area)
area = area.astype(bool)
cl = np.zeros((H, W), np.uint8)
cl[area] = GRAMA
raster(G_ASF, ASF, cl)
raster(G_PAS, CLARO, cl)
cl[~area] = DESC

# ------------------------------------------------------------------ copas (cores do paisagismo da implantacao)
lum = mn.astype(np.float64)
textura = desvio(lum, 3)
COPAS = {
    'rosa': (r_ > 160) & (b_ > 120) & (g_ < r_ - 40),
    'roxa': (r_ > g_ + 22) & (b_ > g_ + 12) & (mn < 175),
    'amarela': (r_ > 185) & (g_ > 150) & (b_ < 110) & (r_ - b_ > 95),
    'oliva': (r_ > g_ - 8) & (r_ < g_ + 22) & (b_ < g_ - 42) & (mn > 105) & (mn < 185),
    'verde': (g_ >= r_) & (g_ > b_) & (lum < 62) & (sat > 12),
    'branca': (mn > 165) & (sat < 36) & (textura > 16),
}


# ------------------------------------------------------------------ faixas pintadas
def _amostra(ref, aa, bb, eixo):
    """Mascara de branco amostrada numa grade (aa ao longo da fileira, bb na profundidade) -> [len(bb), len(aa)]."""
    A_, B_ = np.meshgrid(aa, bb)
    if eixo == 'v':
        U, V = A_, B_
    else:
        U, V = B_, A_
    if ref == 'L':
        X_ = M.ORIGEM_L[0] + U * M._C - V * M._S
        Y_ = M.ORIGEM_L[1] + U * M._S + V * M._C
    else:
        X_, Y_ = U, V
    xi = np.clip(np.round(X_).astype(int), 0, W - 1)
    yi = np.clip(np.round(Y_).astype(int), 0, H - 1)
    return branco[yi, xi]


def _passo_fase(perfil, aa, pmin, pmax):
    """Melhor (passo, fase) para divisorias regulares: soma do perfil nas posicoes fase + k * passo."""
    melhor = (-1, None, None)
    da = aa[1] - aa[0]
    suave = np.convolve(perfil, np.ones(3) / 3, 'same')
    for p in np.arange(pmin, pmax + 0.01, 0.1):
        for f in np.arange(0, p, 0.5):
            pos = np.arange(aa[0] + f, aa[-1] + 0.01, p)
            idx = np.clip(np.round((pos - aa[0]) / da).astype(int), 0, len(aa) - 1)
            sc = suave[idx].mean()
            if sc > melhor[0]:
                melhor = (sc, p, f)
    return melhor


LARG = 1.6     # largura da faixa pintada, px (~13 cm)


def _quad(ref, eixo, a0, a1, b0, b1):
    """Retangulo no referencial da fileira -> 4 cantos na imagem (anti-horario na imagem)."""
    if eixo == 'v':
        cs = [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]
    else:
        cs = [(b0, a0), (b1, a0), (b1, a1), (b0, a1)]
    if ref == 'L':
        cs = [M.L(u, v) for u, v in cs]
    return [round(c, 2) for p in cs for c in p]


def fileira(ref, ret, eixo, pmin, pmax):
    x0, y0, x1, y1 = ret
    a0, a1, b0, b1 = (x0, x1, y0, y1) if eixo == 'v' else (y0, y1, x0, x1)
    aa = np.arange(a0, a1 + 0.01, 0.5)
    prof = b1 - b0
    bb = np.arange(b0 + prof * 0.2, b1 - prof * 0.2, 1.0)
    perfil = _amostra(ref, aa, bb, eixo).mean(0)
    sc, p, f = _passo_fase(perfil, aa, pmin, pmax)
    out = []
    if sc < (0.05 if pmax < 20 else 0.15):          # fileira sem divisorias legiveis no desenho
        return out, (round(p, 1), round(sc, 2), 'descartada')
    for pos in np.arange(a0 + f, a1 + 0.01, p):
        if pos < a0 - 0.5 or pos > a1 + 0.5:
            continue
        out.append(_quad(ref, eixo, pos - LARG / 2, pos + LARG / 2, b0, b1))
    # linhas paralelas (fundo, meio e frente): fracao de branco ao longo da fileira, fora das divisorias
    bb2 = np.arange(b0 - 3, b1 + 3.01, 0.5)
    q = _amostra(ref, aa, bb2, eixo).mean(1)
    linhas = []
    i = 0
    while i < len(bb2):
        if q[i] > 0.4:
            j = i
            while j < len(bb2) and q[j] > 0.4:
                j += 1
            linhas.append((bb2[i] + bb2[j - 1]) / 2)
            i = j
        else:
            i += 1
    for bpos in linhas:
        out.append(_quad(ref, eixo, a0, a1, bpos - LARG / 2, bpos + LARG / 2))
    return out, (round(p, 1), round(sc, 2), [round(v, 1) for v in linhas])


def zebra(ref, ret, dirc, larg=4.0):
    x0, y0, x1, y1 = ret
    out = []
    if dirc == 'x':
        k = x0
        while k + larg <= x1 + 0.1:
            out.append(_quad(ref, 'v', k, k + larg, y0, y1))
            k += 2 * larg
    else:
        k = y0
        while k + larg <= y1 + 0.1:
            out.append(_quad(ref, 'v', x0, x1, k, k + larg))
            k += 2 * larg
    return out


faixas, relatorio = [], []
for fl in M.FILEIRAS:
    q, info = fileira(*fl)
    faixas += q
    relatorio.append((fl[0], fl[1], info))
for ref, ret, dirc in M.ZEBRAS:
    faixas += zebra(ref, ret, dirc)
# so dentro do asfalto (nada de faixa boiando sobre canteiro ou calcada)
G_FAIXAS = unary_union([Polygon([(q[i], q[i + 1]) for i in range(0, 8, 2)]) for q in faixas]).intersection(G_ASF)

# ------------------------------------------------------------------ arvores (copas)
saida = {'escala_m_px': P.S_PX}
C = 2


def reduz(m):
    hh, ww = H // C, W // C
    return m[:hh * C, :ww * C].reshape(hh, C, ww, C).mean((1, 3)) > 0.5


def decompor(m):
    abertos, out = {}, []
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                out.append([c[0] * C, abertos.pop(c) * C, c[1] * C, y * C])
        for c in corr:
            abertos.setdefault(c, y)
    return out


dq = Image.new('L', (W, H), 0)
for q in faixas:
    ImageDraw.Draw(dq).polygon([(q[i], q[i + 1]) for i in range(0, 8, 2)], fill=1)
lin = np.asarray(dq).astype(bool)

cel = 12
cand = []
for tipo, m in COPAS.items():
    m = m & area & ~retangulos(P.SEM_ARVORE_AUTO)
    if tipo == 'branca':
        m &= ~(caixa(lin | branco & (cl == ASF), 8) > 0)
    hh, ww = H // cel, W // cel
    fr = m[:hh * cel, :ww * cel].reshape(hh, cel, ww, cel).mean((1, 3))
    lim = 0.6 if tipo == 'branca' else 0.5 if tipo == 'oliva' else 0.36
    for cy, cx in zip(*np.nonzero(fr > lim)):
        cand.append((float(fr[cy, cx]), tipo, int((cx + 0.5) * cel), int((cy + 0.5) * cel)))
cand.sort(key=lambda t: -t[0])
ocupado = reduz(cl == ASF)       # o tronco fica na grama ou na calcada, nunca no asfalto
arv = []
for sc, tipo, px, py in cand:
    if ocupado[min(py // C, ocupado.shape[0] - 1), min(px // C, ocupado.shape[1] - 1)]:
        ok = None
        for rr in range(3, 16, 3):          # copa na borda do canteiro: o tronco vai para a grama ao lado
            for dx, dy in ((rr, 0), (-rr, 0), (0, rr), (0, -rr)):
                qx, qy = px + dx, py + dy
                if 0 <= qy < H and 0 <= qx < W and not ocupado[qy // C, qx // C] and area[qy, qx]:
                    ok = (qx, qy)
                    break
            if ok:
                break
        if not ok:
            continue                        # copa no meio do asfalto (carro, sombra): sem arvore
        px, py = ok
    if any((px - q[1]) ** 2 + (py - q[2]) ** 2 < 30 ** 2 for q in arv):
        continue
    arv.append((tipo, px, py))
G_GRA = regiao.difference(G_ASF).difference(G_PAS)
G_GRA = MultiPolygon([p for p in getattr(G_GRA, 'geoms', [G_GRA]) if p.geom_type == 'Polygon' and p.area > 2])


# ------------------------------------------------------------------ triangulos, guias e bordas
def triangulos(g):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.area < 0.05:
            continue
        for t in shapely.constrained_delaunay_triangles(p).geoms:
            cs = list(t.exterior.coords)[:3]
            out.append([round(v, 2) for c in cs for v in c])
    return out


def _segmentos(linhas):
    for ln in getattr(linhas, 'geoms', [linhas]):
        if ln.geom_type == 'LineString':
            cs = list(ln.coords)
            for i in range(len(cs) - 1):
                yield cs[i], cs[i + 1]
        elif hasattr(ln, 'geoms'):
            yield from _segmentos(ln)


def divisa(g_dentro, g_lado=None):
    """Trechos da borda de g_dentro que encostam em g_lado; normal apontando para g_lado (ou para fora)."""
    linhas = g_dentro.boundary.intersection(g_lado.boundary) if g_lado is not None else g_dentro.boundary
    pd = prep(g_dentro)
    out = []
    for (x0, y0), (x1, y1) in _segmentos(linhas):
        L_ = math.hypot(x1 - x0, y1 - y0)
        if L_ < 0.2:
            continue
        nx, ny = -(y1 - y0) / L_, (x1 - x0) / L_
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if pd.contains(Point(mx + nx * 0.3, my + ny * 0.3)):
            nx, ny = -nx, -ny
        out.append([round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2), round(nx, 4), round(ny, 4)])
    return out


saida.update({
    'tri_asfalto': triangulos(G_ASF),
    'tri_grama': triangulos(G_GRA),
    'tri_passeio': triangulos(G_PAS),
    'guias': divisa(G_ASF, G_GRA),
    'bordas_passeio': divisa(G_PAS),
    'tri_faixas': triangulos(G_FAIXAS),
    'grama': decompor(reduz((cl == GRAMA) & area)),
    'arvores': arv,
    'carros': [list(c) for c in P.CARROS],
})

json.dump(saida, open(os.path.join(AQUI, 'park_chao.json'), 'w'), separators=(',', ':'))
print({k: len(v) for k, v in saida.items() if isinstance(v, list)})

# ------------------------------------------------------------------ conferencia visual
if len(sys.argv) > 1:
    pasta = sys.argv[1]
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, 'fileiras.txt'), 'w') as fo:
        for ref, ret, info in relatorio:
            fo.write(f'{ref} {ret} passo/score/paralelas {info}\n')
    base = im.copy()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for g, cor in ((G_GRA, (40, 200, 40, 70)), (G_ASF, (40, 40, 60, 90)), (G_PAS, (255, 160, 0, 110))):
        for p in getattr(g, 'geoms', [g]):
            if p.is_empty:
                continue
            d.polygon([tuple(c) for c in p.exterior.coords], fill=cor, outline=(255, 0, 255, 255))
            for it in p.interiors:
                d.polygon([tuple(c) for c in it.coords], outline=(255, 0, 255, 255))
    for q in faixas:
        d.polygon([(q[i], q[i + 1]) for i in range(0, 8, 2)], fill=(255, 0, 0, 230))
    for t, x, y in arv:
        d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=(0, 0, 255, 255), width=2)
    Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB').save(os.path.join(pasta, 'sobreposto.png'))
    pal = np.array([[255, 255, 255], [70, 70, 76], [70, 150, 60], [205, 203, 195]], np.uint8)
    vis = Image.fromarray(pal[cl])
    dv = ImageDraw.Draw(vis)
    for q in faixas:
        dv.polygon([(q[i], q[i + 1]) for i in range(0, 8, 2)], fill=(255, 255, 255))
    for x0, y0, x1, y1, nx, ny in saida['guias']:
        dv.line((x0, y0, x1, y1), fill=(255, 200, 0), width=1)
    vis.save(os.path.join(pasta, 'chao.png'))
