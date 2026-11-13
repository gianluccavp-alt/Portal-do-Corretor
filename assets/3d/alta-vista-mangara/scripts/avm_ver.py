#!/usr/bin/env python3
"""avm_ver.py -- desenha as medidas de avm_planta.py por cima da implantacao, para conferir antes de gerar.
Fora do Blender, num venv com pillow:  python avm_ver.py implantacao.png saida.jpg [escala]
implantacao.png: o adesivo de 4724 px do Drive (ou a do repo, 3840 px: o script reescala)."""
import os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import avm_planta as P

Image.MAX_IMAGE_PIXELS = None
im = Image.open(sys.argv[1]).convert('RGB')
k = im.size[0] / 4724.0
esc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
d = ImageDraw.Draw(im, 'RGBA')
q = lambda p: (p[0] * k, p[1] * k)


def ret(r, cor, w=3, fill=None):
    d.rectangle([q(r[:2]), q(r[2:4])], outline=cor, width=w, fill=fill)


d.line([q(p) for p in P.TERRENO + P.TERRENO[:1]], fill=(255, 0, 0), width=5)
d.line([q(p) for p in P.MEIO_FIO], fill=(255, 140, 0), width=4)
for r in P.ASFALTO:
    ret(r, (0, 0, 0, 255), 2, (0, 0, 0, 40))
ret(P.DECK, (0, 160, 255), 5)
ret(P.RAMPA_DECK, (0, 160, 255), 3)
for r in P.JARDIM_TORRE.values():
    ret(r, (0, 200, 0), 3)
for x0, y0, x1, y1, ori, lw, _ in P.VAGAS:
    ret((x0, y0, x1, y1), (255, 0, 255), 2)
    passo = lw / P.S_PX
    if ori == 'h':
        x = x0
        while x <= x1 + 1:
            d.line([q((x, y0)), q((x, y1))], fill=(255, 0, 255), width=1); x += passo
    else:
        y = y0
        while y <= y1 + 1:
            d.line([q((x0, y)), q((x1, y))], fill=(255, 0, 255), width=1); y += passo
m = 1 / P.S_PX
for t, (cx, cy) in P.TORRES.items():
    pts = [(x, y) for x, y in P.TORRE_Q]
    full = pts + [(x, -y) for x, y in reversed(pts)]
    full = full + [(-x, y) for x, y in reversed(full)]
    d.line([q((cx + x * m, cy - y * m)) for x, y in full + full[:1]], fill=(0, 255, 255), width=3)
for nome in ('PISCINA_DECK', 'EDIF_SALAO', 'DECK_GOURMET', 'PLAYGROUND', 'QUADRA_AREIA', 'CHURRASQUEIRA',
             'LOUNGE_CHURRASQUEIRA', 'PIQUENIQUE', 'PRACA', 'PORTARIA', 'LIXO', 'PET', 'CASA_BOMBAS', 'BIKE',
             'PISCINA_INFANTIL', 'ESCADA_DECK', 'DECK_MOLHADO'):
    ret(getattr(P, nome), (255, 255, 0), 3)
for r in P.PISCINA:
    ret(r, (0, 0, 255), 3)
for cx, cy in P.RESERVATORIOS:
    rr = P.RAIO_RESERVATORIO_PX
    d.ellipse([q((cx - rr, cy - rr)), q((cx + rr, cy + rr))], outline=(0, 0, 255), width=3)
for x, y, _ in P.ARVORES:
    d.ellipse([q((x - 14, y - 14)), q((x + 14, y + 14))], fill=(0, 120, 0, 200))
for x, y in P.PALMEIRAS:
    d.ellipse([q((x - 10, y - 10)), q((x + 10, y + 10))], fill=(200, 120, 0, 220))
for x, y, g in P.CARROS:
    w, h = (45, 18) if g == 0 else (18, 45)
    ret((x - w, y - h, x + w, y + h), (255, 60, 60), 2)
im = im.resize((int(im.size[0] * esc), int(im.size[1] * esc)), Image.LANCZOS)
im.save(sys.argv[2], quality=88)
