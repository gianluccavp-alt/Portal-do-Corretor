#!/usr/bin/env python3
"""jbo_chao.py -- desenho do chao do condominio (grama, asfalto, paver, concreto, paver laranja) lido por cor na
implantacao, em celulas de 4 px (11 cm), e gravado como retangulos em tex/chao.json. Roda fora do Blender, num venv
com numpy, pillow e scipy:
    python -I jbo_chao.py <GUI_M01_Implantacao_REV_05_00a.jpg> [previa.png]
O que tem geometria propria (vagas, edificio-garagem, lazer, cobertura da churrasqueira) fica fora do raster. Arvores
e carros desenhados na imagem viram o chao em volta (filtro de moda e preenchimento pelo vizinho mais proximo)."""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

AQUI = os.path.dirname(os.path.abspath(__file__))
PL = {}
exec(open(os.path.join(AQUI, 'jbo_planta.py')).read(), PL)
Image.MAX_IMAGE_PIXELS = None
B = 4
NOMES = {1: 'grama', 2: 'asfalto', 3: 'paver', 4: 'concreto', 5: 'paver_laranja'}

im = Image.open(sys.argv[1]).convert('RGB')
a = np.asarray(im).astype(np.int16)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx, mn = a.max(2), a.min(2)
C = np.zeros(r.shape, np.uint8)
C[(g > r + 4) & (g > b + 4)] = 1
C[(r > g + 28) & (r > 150) & (r > b + 40)] = 5
C[((r - b) >= 5) & (r >= 100) & (r <= 152) & ((mx - mn) < 26) & (C == 0)] = 2
C[(abs(r - b) < 5) & (r >= 118) & (r <= 182) & ((mx - mn) < 14) & (C == 0)] = 3
C[(mn >= 183) & (mn < 236) & ((mx - mn) < 20)] = 4
C[mn >= 236] = 6
H, W = C.shape
H2, W2 = H // B, W // B
cc = C[:H2 * B, :W2 * B].reshape(H2, B, W2, B).transpose(0, 2, 1, 3).reshape(H2, W2, B * B)
lab = np.stack([(cc == k).sum(2) for k in range(7)], -1).argmax(-1).astype(np.uint8)


def moda(l, k=5):
    best = np.zeros(l.shape, np.float32)
    out = l.copy()
    for c in (1, 2, 3, 4, 5, 6):
        s = nd.uniform_filter((l == c).astype(np.float32), k)
        m = s > best
        out[m] = c
        best = np.where(m, s, best)
    return out


lab = moda(moda(lab, 5), 5)
# manchas pequenas (copas, carros, sombras) viram o vizinho
for c in (1, 2, 3, 4, 5):
    rot, n = nd.label(lab == c)
    if n:
        tam = nd.sum(np.ones_like(rot), rot, np.arange(1, n + 1))
        peq = np.isin(rot, np.nonzero(tam < 40)[0] + 1)
        lab[peq] = 0
fora = lab == 6
desc = lab == 0
if desc.any():
    _, (iy, ix) = nd.distance_transform_edt(desc, return_indices=True)
    lab = lab[iy, ix]
lab[fora] = 6


# entrada e avenida: faixas de pedestre e carros desenhados viram asfalto (a faixa da avenida e geometria propria)
lab[:, 12880 // B:][lab[:, 12880 // B:] == 4] = 2

# areas com geometria propria (ficam fora do raster)
def corta(x0, y0, x1, y1, folga=0):
    lab[max(0, int(y0 - folga) // B):int(np.ceil((y1 + folga) / B)), max(0, int(x0 - folga) // B):int(np.ceil((x1 + folga) / B))] = 7


corta(*PL['GARAGEM'])
for cs, n, tipo in PL['VAGAS']:
    xs, ys = [p[0] for p in cs], [p[1] for p in cs]
    corta(min(xs), min(ys), max(xs), max(ys))
for x0, x1, yf, yb, _ in PL['VAGAS_PCD']:
    corta(x0, min(yf, yb), x1, max(yf, yb))
for x0, x1 in PL['ZEBRAS_PCD']:
    corta(x0, 1095, x1, 1272)
    corta(x0, 1545, x1, 1730)
for k in ('ACADEMIA', 'FITNESS', 'PET', 'DECK_PISCINA', 'PLAYGROUND', 'HAPPY_HOUR', 'SALAO', 'QUADRA', 'BEACH',
          'PRACA', 'GUARITA', 'LIXO', 'MEDIDORES'):
    corta(*PL[k])
cx, cy, rr = PL['RESERVATORIO']
corta(cx - rr, cy - rr, cx + rr, cy + rr)
# fora do lote a oeste e no alto (branco da prancha) e o resto da prancha branca
lab[:, :int(PL['X_OESTE']) // B] = 6
# acima do muro de cima e abaixo do muro de baixo (ate a calcada da avenida) e fora do lote
for cxl in range(W2):
    x = cxl * B + B / 2
    lab[:int(PL['topo'](x)) // B, cxl] = 6
    if x < 13150:
        lab[int(PL['Y_BAIXO'] + 3) // B + 1:, cxl] = 6


def retangulos(m):
    """Mascara booleana -> retangulos (x0, y0, x1, y1) em celulas, juntando corridas iguais de linhas seguidas."""
    out, abertos = [], {}
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                out.append((c[0], abertos.pop(c), c[1], y))
        for c in corr:
            abertos.setdefault(c, y)
    return out


saida = {'schema': 'jbo-chao/1', 'celula_px': B, 'classes': {}}
tot = 0
for k, nome in NOMES.items():
    rs = retangulos(lab == k)
    saida['classes'][nome] = [[x0 * B, y0 * B, x1 * B, y1 * B] for x0, y0, x1, y1 in rs]
    tot += len(rs)
    print(nome, len(rs))
with open(os.path.join(AQUI, 'tex', 'chao.json'), 'w') as fh:
    json.dump(saida, fh, separators=(',', ':'))
print('total', tot)
if len(sys.argv) > 2:
    pal = np.array([[255, 0, 255], [90, 150, 60], [60, 60, 60], [150, 150, 175], [235, 235, 235], [230, 140, 60],
                    [255, 255, 255], [255, 220, 0]], np.uint8)
    Image.fromarray(pal[lab]).resize((W2 // 2, H2 // 2)).save(sys.argv[2])
