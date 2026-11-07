#!/usr/bin/env python3
"""Calcula as linhas das vagas (patio_vagas.json) medindo a implantacao e sobrepoe o layout na imagem,
para conferir as medidas antes do 3D. Precisa de numpy e pillow, fora do Blender.
Uso: python ver_planta.py saida.jpg"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import gaia_planta as P

IMG = os.path.join(AQUI, '..', '..', '..', 'img', 'village-gaia', 'plantas', 'implantacao.jpg')
im = Image.open(IMG).convert('RGB')
a = np.asarray(im).astype(np.float32)
branco = (a.min(2) > 188) & ((a.max(2) - a.min(2)) < 26)


def linhas(x0, y0, x1, y1, sentido, pmin, pmax):
    """Posicoes das divisorias ao longo da fileira: acha o passo e a fase que melhor explicam os picos."""
    if sentido == 'v':
        faixa = branco[y0:y1, x0 + 6:x1 - 6].mean(1)
        ini, fim = y0, y1
    else:
        faixa = branco[y0 + 6:y1 - 6, x0:x1].mean(0)
        ini, fim = x0, x1
    melhor = (-1, None, None)
    n = len(faixa)
    for passo in np.arange(pmin, pmax, 0.05):
        for fase in np.arange(0, passo, 0.5):
            idx = np.arange(fase, n, passo).astype(int)
            idx = idx[idx < n]
            nota = faixa[idx].sum() + 0.6 * (np.roll(faixa, -1)[idx].sum())
            nota /= len(idx) ** 0.5
            if nota > melhor[0]:
                melhor = (nota, passo, fase)
    _, passo, fase = melhor
    pos = [round(float(ini + p), 1) for p in np.arange(fase, n + 0.01, passo)]
    return pos, round(float(passo), 2)


res = []
for x0, y0, x1, y1, s in P.VAGAS:
    pos, passo = linhas(x0, y0, x1, y1, s, 22.0, 25.5)
    res.append({'r': [x0, y0, x1, y1], 's': s, 'linhas': pos, 'passo': passo})
motos = []
for x0, y0, x1, y1, s in P.MOTOS:
    n = (y1 - y0 if s == 'v' else x1 - x0)
    k = max(1, round(n / 11.0))
    ini = y0 if s == 'v' else x0
    motos.append({'r': [x0, y0, x1, y1], 's': s, 'linhas': [round(ini + i * n / k, 1) for i in range(k + 1)]})
json.dump({'vagas': res, 'motos': motos}, open(os.path.join(AQUI, 'patio_vagas.json'), 'w'), indent=0)
print('passos', sorted(set(r['passo'] for r in res)))

# ------------------------------------------------------------------ arvores do patio (lazer e a mao)
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
lum = a.mean(2)
fora = (a.min(2) > 240)
rosa = (r_ > 165) & (b_ > 125) & (g_ < r_ - 40)
amarela = (r_ > 190) & (g_ > 155) & (b_ < 110) & (r_ - b_ > 100)
escura = (g_ >= r_) & (g_ > b_) & (lum < 58) & ~fora
H_, W_ = lum.shape
cel = 12
cand = []
for tipo, m in (('rosa', rosa), ('amarela', amarela), ('verde', escura)):
    hh, ww = H_ // cel, W_ // cel
    fr = m[:hh * cel, :ww * cel].reshape(hh, cel, ww, cel).mean((1, 3))
    for cy, cx in zip(*np.nonzero(fr > 0.34)):
        cand.append((float(fr[cy, cx]), tipo, (cx + 0.5) * cel, (cy + 0.5) * cel))
cand.sort(key=lambda t: -t[0])
asf = np.zeros((H_, W_), bool)
for x0, y0, x1, y1 in P.ASFALTO:
    asf[y0:y1, x0:x1] = True
pas = np.zeros((H_, W_), bool)
for x0, y0, x1, y1 in P.PASSEIO:
    pas[y0:y1, x0:x1] = True
ocupado = asf | pas
arv = []
for sc, tipo, px, py in cand:
    px_, py_ = int(px), int(py)
    if py_ < 400 or px_ < 45 or px_ > 2300:
        continue
    if 1845 < px_ < 2300 and 660 < py_ < 1200:     # lazer: posicionado a mao
        continue
    if any(abs(px_ - t) < 100 and abs(py_ - P.TORRE_Y) < 215 for t in P.TORRES_PX.values()):
        continue
    if ocupado[py_, px_]:                          # copa sobre a vaga: tronco vai para o canteiro mais proximo
        ok = None
        for r in range(4, 46, 3):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                q = (px_ + dx, py_ + dy)
                if 0 <= q[1] < H_ and 0 <= q[0] < W_ and not ocupado[q[1], q[0]]:
                    ok = q
                    break
            if ok:
                break
        if not ok:
            continue
        px_, py_ = ok
    if any((px_ - q[1]) ** 2 + (py_ - q[2]) ** 2 < 34 ** 2 for q in arv):
        continue
    arv.append((tipo, px_, py_))
json.dump(arv, open(os.path.join(AQUI, 'patio_arvores.json'), 'w'))
print('arvores', len(arv))

if len(sys.argv) > 1:
    d = ImageDraw.Draw(im, 'RGBA')
    def ret(rs, cor, borda=None):
        for r in rs:
            d.rectangle(r[:4], fill=cor, outline=borda)
    ret(P.ASFALTO, (255, 0, 0, 45), (255, 0, 0, 150))
    ret(P.PASSEIO, (0, 255, 255, 110))
    ret(P.PAVER_PATIO, (255, 0, 255, 90))
    ret(P.NARIZ, (255, 255, 0, 130))
    d.polygon(P.TERRENO, outline=(255, 255, 0, 255))
    d.polygon(P.ASFALTO_ENTRADA, outline=(255, 120, 0, 255))
    for v in res + motos:
        x0, y0, x1, y1 = v['r']
        for p in v['linhas']:
            if v['s'] == 'v':
                d.line((x0, p, x1, p), fill=(0, 255, 0, 255), width=1)
            else:
                d.line((p, y0, p, y1), fill=(0, 255, 0, 255), width=1)
    laz = [P.DECK, P.PISCINA, P.PISCINA_MOLHADO, P.PISCINA_INFANTIL, P.VESTIARIOS, P.QUADRA_LAJE, P.QUADRA, P.CHURRASCO,
           P.PERGOLA_CHURRASCO, (P.BLOCO_X[0], P.ACADEMIA_Y[0], P.BLOCO_X[1], P.ACADEMIA_Y[1]),
           (P.BLOCO_X[0], P.PUB_Y[0], P.BLOCO_X[1], P.PUB_Y[1]), (P.BLOCO_X[0], P.BRINQ_Y[0], P.BLOCO_X[1], P.BRINQ_Y[1]),
           (P.BLOCO_X[0], P.SALAO_Y[0], P.BLOCO_X[1], P.SALAO_Y[1]), P.SERVICO, P.PLAYGROUND, P.GOURMET, P.PRACA_JOGOS,
           P.PIQUENIQUE, P.BICICLETARIO, P.PRACA14, P.CROSSFIT, P.PERGOLA_CROSSFIT, P.LOUNGE_TEEN, P.APOIO, P.GUARITA,
           P.PERGOLA_GUARITA_N, P.PERGOLA_GUARITA_S, P.PORTICO, P.FOODTRUCK, P.PET, P.BOMBAS_SE, P.LIXO, P.BOMBAS_NO, P.CHARGE]
    for r in laz:
        d.rectangle(r[:4], outline=(255, 255, 0, 255), width=1)
    for r in P.CIRCULACAO:
        d.rectangle(r, outline=(255, 0, 255, 200))
    for q, _n in P.VISITANTES:
        d.polygon(q, outline=(0, 255, 0, 255))
    k = 2
    im.crop((30, 395, 1250, 1370)).resize((1220 * 2 // 2 * k // 2, 975), Image.LANCZOS).save(sys.argv[1] + '_a.jpg', quality=88)
    im.crop((1180, 395, 2460, 1400)).resize((1280, 1005), Image.LANCZOS).save(sys.argv[1] + '_b.jpg', quality=88)
    im.crop((1820, 670, 2400, 1350)).resize((1450, 1700), Image.LANCZOS).save(sys.argv[1] + '_c.jpg', quality=90)
