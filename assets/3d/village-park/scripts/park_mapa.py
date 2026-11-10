#!/usr/bin/env python3
"""park_mapa.py -- mede o chao do Village Park direto da implantacao (assets/img/village-park/plantas/implantacao.jpg,
2600 x 2870 px, 0,079 m/px) e grava park_chao.json, lido pelo gerador no Blender.

Fora do Blender, num venv com numpy e pillow:  python park_mapa.py [saida_conferencia.jpg]

O que sai (tudo em px da imagem; x para a direita, y para baixo):
  asfalto / grama / passeio : retangulos (x0, y0, x1, y1) sem sobreposicao, da segmentacao por cor
  guias                     : trechos da divisa asfalto-grama (x0, y0, x1, y1, lado de fora)
  bordas_passeio            : trechos da divisa do passeio levantado
  linhas                    : retangulos das faixas brancas pintadas no asfalto (vagas, zebras)
  arvores                   : (tipo, x, y) pelas copas coloridas
  carros                    : (x, y, giro) da lista a mao em park_planta.py (o chao embaixo e reconstruido)
Zonas tratadas a mao (torres e lazer, em park_planta.py) ficam fora da segmentacao.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import park_planta as P

IMG = os.path.join(AQUI, '..', '..', '..', 'img', 'village-park', 'plantas', 'implantacao.jpg')
im = Image.open(IMG).convert('RGB')
a = np.asarray(im).astype(np.int16)
H, W = a.shape[:2]
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
mn = a.mean(2)
sat = a.max(2) - a.min(2)

# ------------------------------------------------------------------ classes por cor
DESC, ASF, GRAMA, CLARO = 0, 1, 2, 3
branco = (sat < 28) & (mn >= 205)
cl = np.zeros((H, W), np.uint8)
cl[(sat < 16) & (mn > 98) & (mn < 146)] = ASF
cl[(sat < 22) & (mn >= 146) & (mn < 205)] = CLARO
cl[(g_ > r_ + 6) & (g_ > b_ + 12)] = GRAMA


def poligono(pts):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=1)
    return np.asarray(m).astype(bool)


def retangulos(rs):
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in rs:
        m[int(y0):int(y1), int(x0):int(x1)] = True
    return m


area = poligono(P.TERRENO) | retangulos([P.AVENIDA])
mao = retangulos(P.ZONAS_A_MAO)          # lazer modelado a mao (vazio na etapa 1)
cl[~area] = DESC


def caixa(m, r):
    """Soma numa janela (2r+1)^2 por imagem integral."""
    c = np.pad(m.astype(np.int32), ((r + 1, r), (r + 1, r))).cumsum(0).cumsum(1)
    return c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:] - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1]


def desvio(v, r):
    n = (2 * r + 1) ** 2
    m1 = caixa(v, r) / n
    m2 = caixa(v * v, r) / n
    return np.sqrt(np.maximum(m2 - m1 * m1, 0))


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
copa = np.zeros((H, W), bool)
for m in COPAS.values():
    copa |= m
copa &= caixa(copa, 4) > 45          # so manchas cheias: tira faixa pintada e borda de guia
copa = caixa(copa, 4) > 3             # e a franja de sombra/brilho em volta da copa
cl[copa] = DESC

# ------------------------------------------------------------------ carros: manchas de cor ou brilho sobre o asfalto
def corridas(mask, eixo, minimo):
    """Pixels que pertencem a corridas retas de pelo menos `minimo` px ao longo do eixo."""
    m = mask if eixo == 1 else mask.T
    out = np.zeros_like(m)
    for i in range(m.shape[0]):
        d = np.diff(np.concatenate([[0], m[i].astype(np.int8), [0]]))
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            if e - s >= minimo:
                out[i, s:e] = True
    return out if eixo == 1 else out.T


linha0 = corridas(branco, 1, 12) | corridas(branco, 0, 12)
linha0 &= caixa(linha0, 3) < 30          # faixas finas (carro branco e cheio)
linha0 = caixa(linha0, 2) > 0
carros, mancha_carro = [list(c) for c in P.CARROS], np.zeros((H, W), bool)
for x, y, giro in carros:
    w2, h2 = (32, 15) if giro == 0 else (15, 32)
    mancha_carro[y - h2:y + h2, x - w2:x + w2] = True
cl[mancha_carro & (cl != GRAMA)] = DESC


def preencher(cl, alvo):
    """Pixels desconhecidos herdam a classe da vizinhanca (dilatacoes sucessivas: copas, carros, textos, faixas)."""
    cl = cl.copy()
    for _ in range(120):
        falta = (cl == DESC) & alvo
        if not falta.any():
            break
        cont = np.stack([caixa(cl == k, 2) for k in (ASF, GRAMA, CLARO)])
        melhor = cont.argmax(0) + 1
        tem = cont.max(0) > 0
        cl[falta & tem] = melhor[falta & tem]
    return cl


def _ultimo(cl, eixo, rev):
    """Para cada pixel: classe e distancia do ultimo pixel conhecido ao longo do eixo (rev = do fim para o inicio)."""
    c = cl if eixo == 1 else cl.T
    if rev:
        c = c[:, ::-1]
    hh, ww = c.shape
    idx = np.where(c != DESC, np.arange(ww)[None, :], -1)
    idx = np.maximum.accumulate(idx, axis=1)
    cls = np.take_along_axis(c, np.maximum(idx, 0), 1)
    cls[idx < 0] = DESC
    dist = np.where(idx < 0, 10 ** 6, np.arange(ww)[None, :] - idx)
    if rev:
        cls, dist = cls[:, ::-1], dist[:, ::-1]
    return (cls, dist) if eixo == 1 else (cls.T, dist.T)


def preencher_cruz(cl, alvo, alcance=24):
    """Copa sobre calcada reta: se os dois lados na horizontal (ou na vertical) concordam, a classe atravessa
    a copa em linha reta. Reconstroi bordas retilineas melhor que a dilatacao."""
    cl = cl.copy()
    falta = (cl == DESC) & alvo
    (le, dle), (ri, dri) = _ultimo(cl, 1, False), _ultimo(cl, 1, True)
    (up, dup), (dn, ddn) = _ultimo(cl, 0, False), _ultimo(cl, 0, True)
    h_ok = (le == ri) & (le != DESC) & (dle + dri < 2 * alcance)
    v_ok = (up == dn) & (up != DESC) & (dup + ddn < 2 * alcance)
    # quando os dois eixos concordam com classes diferentes, vale o vao mais curto
    usa_h = h_ok & (~v_ok | (dle + dri <= dup + ddn))
    usa_v = v_ok & ~usa_h
    cl[falta & usa_h] = le[falta & usa_h]
    cl[falta & usa_v] = up[falta & usa_v]
    return cl


def moda(cl, r, alvo):
    cont = np.stack([caixa(cl == k, r) for k in (ASF, GRAMA, CLARO)])
    out = cl.copy()
    out[alvo] = (cont.argmax(0) + 1)[alvo]
    return out


def componentes_pequenos(m, minimo, k=4):
    """Mascara (resolucao cheia) das manchas de m com menos de `minimo` px (rotulagem numa grade de k px)."""
    hh, ww = H // k, W // k
    g = m[:hh * k, :ww * k].reshape(hh, k, ww, k).mean((1, 3)) > 0.5
    rot = np.zeros((hh, ww), np.int32)
    peq = np.zeros((hh, ww), bool)
    n = 0
    for y0, x0 in zip(*np.nonzero(g)):
        if rot[y0, x0]:
            continue
        n += 1
        pilha, cel_ = [(y0, x0)], []
        rot[y0, x0] = n
        while pilha:
            y, x = pilha.pop()
            cel_.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < hh and 0 <= xx < ww and g[yy, xx] and not rot[yy, xx]:
                    rot[yy, xx] = n
                    pilha.append((yy, xx))
        if len(cel_) * k * k < minimo:
            for y, x in cel_:
                peq[y, x] = True
    out = np.zeros((H, W), bool)
    out[:hh * k, :ww * k] = np.repeat(np.repeat(peq, k, 0), k, 1)
    return out & m


cl = preencher_cruz(cl, area)
cl = preencher(cl, area)
for k_, minimo in ((ASF, 2500), (CLARO, 2500), (GRAMA, 500)):     # sombra de copa, carro claro, gramadinho perdido
    cl[componentes_pequenos(cl == k_, minimo)] = DESC
cl = preencher_cruz(cl, area)
cl = preencher(cl, area)
cl = moda(cl, 5, area)          # 0,9 m: tira guia pintada, sombra, carro esquecido e serrilhado da imagem
cl = moda(cl, 2, area)
# calcada em volta das torres (a faixa escura da implantacao e a sombra da platibanda)
for (cx, cy), giro in P.TORRES.values():
    mx_, my_ = (98, 278) if giro in (0.0, 180.0) else (278, 98)
    cl[int(cy - my_):int(cy + my_), int(cx - mx_):int(cx + mx_)] = CLARO
cl[~area] = DESC

# ------------------------------------------------------------------ retangulos e divisas (grade de 2 px)
C = 2


def reduz(m):
    hh, ww = H // C, W // C
    return m[:hh * C, :ww * C].reshape(hh, C, ww, C).mean((1, 3)) > 0.5


def decompor(m):
    abertos, saida = {}, []
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                saida.append([c[0] * C, abertos.pop(c) * C, c[1] * C, y * C])
        for c in corr:
            abertos.setdefault(c, y)
    return saida


def bordas(m, viz=None):
    """Divisa de m em trechos (x0, y0, x1, y1, lado de fora). viz: so onde o lado de fora pertence a viz."""
    seg = []
    hh, ww = m.shape
    pm = np.pad(m, 1)
    pv = np.pad(viz if viz is not None else np.ones_like(m), 1)
    # horizontais: entre linha y-1 e y
    for y in range(hh + 1):
        cima, baixo = pm[y, 1:-1], pm[y + 1, 1:-1]
        for lado, ok in (('n', baixo & ~cima & pv[y, 1:-1]), ('s', cima & ~baixo & pv[y + 1, 1:-1])):
            d = np.diff(np.concatenate([[0], ok.astype(np.int8), [0]]))
            for i0, i1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
                seg.append([int(i0) * C, y * C, int(i1) * C, y * C, lado])
    for x in range(ww + 1):
        esq, dir_ = pm[1:-1, x], pm[1:-1, x + 1]
        for lado, ok in (('o', dir_ & ~esq & pv[1:-1, x]), ('l', esq & ~dir_ & pv[1:-1, x + 1])):
            d = np.diff(np.concatenate([[0], ok.astype(np.int8), [0]]))
            for i0, i1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
                seg.append([x * C, int(i0) * C, x * C, int(i1) * C, lado])
    return seg


livre = area & ~mao
saida = {'escala_m_px': P.S_PX, 'grade_px': C}

# ------------------------------------------------------------------ faixas brancas no asfalto
asf_viz = caixa(cl == ASF, 4) > 30


bw = branco & asf_viz & livre & ~copa & ~retangulos([P.AVENIDA])
lin = corridas(bw, 1, 12) | corridas(bw, 0, 12)
# linhas pintadas sao finas: a espessura na direcao transversal nao passa de 4 px
fino = caixa(lin, 3) < 30
lin &= fino | corridas(bw, 1, 40) | corridas(bw, 0, 40)
C1 = C
C = 1
saida['linhas'] = decompor(lin)
C = C1

# ------------------------------------------------------------------ arvores (copas)
cel = 12
cand = []
for tipo, m in COPAS.items():
    m = m & area & ~retangulos(P.SEM_ARVORE_AUTO)
    if tipo == 'branca':
        m &= ~(caixa(lin, 8) > 0)
    hh, ww = H // cel, W // cel
    fr = m[:hh * cel, :ww * cel].reshape(hh, cel, ww, cel).mean((1, 3))
    lim = 0.6 if tipo == 'branca' else 0.5 if tipo == 'oliva' else 0.36
    for cy, cx in zip(*np.nonzero(fr > lim)):
        cand.append((float(fr[cy, cx]), tipo, int((cx + 0.5) * cel), int((cy + 0.5) * cel)))
cand.sort(key=lambda t: -t[0])
ocupado = reduz(cl == ASF)
arv, covas = [], []
for sc, tipo, px, py in cand:
    if ocupado[min(py // C, ocupado.shape[0] - 1), min(px // C, ocupado.shape[1] - 1)]:
        ok = None
        for rr in range(3, 13, 3):          # copa na borda do canteiro: o tronco vai para a grama ao lado
            for dx, dy in ((rr, 0), (-rr, 0), (0, rr), (0, -rr)):
                qx, qy = px + dx, py + dy
                if 0 <= qy < H and 0 <= qx < W and not ocupado[qy // C, qx // C] and area[qy, qx]:
                    ok = (qx, qy)
                    break
            if ok:
                break
        if ok:
            px, py = ok
        else:
            covas.append((px, py))          # canteiro estreito sumiu sob as copas: devolve a grama
    if any((px - q[1]) ** 2 + (py - q[2]) ** 2 < 30 ** 2 for q in arv):
        continue
    arv.append((tipo, px, py))
for px, py in covas:
    r = 13
    y0, y1, x0, x1 = max(0, py - r), min(H, py + r + 1), max(0, px - r), min(W, px + r + 1)
    gy, gx = np.ogrid[y0:y1, x0:x1]
    disco = (gy - py) ** 2 + (gx - px) ** 2 <= r * r
    sub = cl[y0:y1, x0:x1]
    sub[disco & (sub == ASF)] = GRAMA
livre = area & ~mao
m_asf, m_gr, m_pas = reduz((cl == ASF) & livre), reduz((cl == GRAMA) & livre), reduz((cl == CLARO) & livre)
m_mao = reduz(mao & area)
saida.update({
    'asfalto': decompor(m_asf), 'grama': decompor(m_gr), 'passeio': decompor(m_pas),
    'guias': bordas(m_asf, m_gr | m_mao),
    'bordas_passeio': bordas(m_pas, m_asf | m_gr | m_mao),
})

saida['arvores'] = arv
saida['carros'] = carros

json.dump(saida, open(os.path.join(AQUI, 'park_chao.json'), 'w'), separators=(',', ':'))
print({k: len(v) for k, v in saida.items() if isinstance(v, list)})

# ------------------------------------------------------------------ conferencia visual
if len(sys.argv) > 1:
    pal = np.array([[255, 255, 255], [70, 70, 76], [70, 150, 60], [205, 203, 195]], np.uint8)
    vis_ = Image.fromarray(pal[cl])
    d = ImageDraw.Draw(vis_, 'RGBA')
    for x0, y0, x1, y1 in saida['linhas']:
        d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(255, 255, 255, 255))
    for x0, y0, x1, y1, _l in saida['guias']:
        d.line((x0, y0, x1, y1), fill=(255, 200, 0, 255), width=1)
    for r in P.ZONAS_A_MAO:
        d.rectangle(r, outline=(255, 0, 255, 255), width=3)
    for t, x, y in arv:
        c = {'rosa': (230, 80, 170), 'amarela': (250, 220, 0), 'verde': (0, 90, 0), 'branca': (240, 240, 255),
             'roxa': (140, 70, 160), 'oliva': (160, 160, 60)}[t]
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=c + (255,), outline=(0, 0, 0, 255))
    for x, y, gr in carros:
        w2, h2 = (28, 13) if gr == 0 else (13, 28)
        d.rectangle((x - w2, y - h2, x + w2, y + h2), outline=(255, 0, 0, 255), width=2)
    vis_.save(sys.argv[1], quality=88)
