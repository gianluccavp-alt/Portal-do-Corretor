#!/usr/bin/env python3
"""jbo_ver.py -- sobrepoe as medidas de jbo_planta.py e o contorno das torres (jbo_torre.py) na implantacao, para
conferir antes de gerar. Fora do Blender, num venv com pillow:
    python -I jbo_ver.py <GUI_M01_Implantacao_REV_05_00a.jpg> saida.jpg [x0 y0 x1 y1]  (recorte opcional, px)"""
import os, sys
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
PL, TR = {}, {}
exec(open(os.path.join(AQUI, 'jbo_planta.py')).read(), PL)
exec(open(os.path.join(AQUI, 'jbo_torre.py')).read(), TR)
Image.MAX_IMAGE_PIXELS = None
im = Image.open(sys.argv[1]).convert('RGB')
d = ImageDraw.Draw(im, 'RGBA')
S = PL['S_PX']


def poly(pts, cor, w=2):
    d.line([tuple(p) for p in pts] + [tuple(pts[0])], fill=cor, width=w)


def ret(r, cor, w=2):
    d.rectangle(r[:4], outline=cor, width=w)


for t, (cx, cy) in PL['TORRES'].items():
    tw = lambda p: (cx + p[0] / S, cy - p[1] / S)
    poly([tw(p) for p in TR['contorno']()], (255, 0, 0, 255), 2)
    for f in range(1, 9):
        var, jan = TR['aberturas'](f)
        for j in jan:
            a, b = ((j[2], j[1]), (j[3], j[1])) if j[0] == 'y' else ((j[1], j[2]), (j[1], j[3]))
            d.line([tw(a), tw(b)], fill=(0, 200, 255, 255), width=4)
        pl, c, a0, a1 = var['face']
        fz = var['fundo']
        a, b = ((fz, a0), (fz, a1)) if pl == 'x' else ((a0, fz), (a1, fz))
        d.line([tw(a), tw(b)], fill=(0, 255, 0, 255), width=4)
xs = range(int(PL['X_OESTE']), 13716, 50)
d.line([(x, PL['topo'](x)) for x in xs], fill=(255, 0, 0, 255), width=3)
d.line([(PL['X_OESTE'], PL['Y_BAIXO']), (13160, PL['Y_BAIXO'])], fill=(255, 0, 0, 255), width=3)
d.line([tuple(p) for p in PL['FRENTE']], fill=(255, 0, 0, 255), width=3)
d.line([tuple(p) for p in PL['CANTO_SE']], fill=(255, 0, 0, 255), width=3)
for cs, n, tipo in PL['VAGAS']:
    poly(cs, (255, 255, 0, 255), 2)
    a, b, c, dd = cs
    for i in range(1, n):
        t = i / n
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        q = (dd[0] + (c[0] - dd[0]) * t, dd[1] + (c[1] - dd[1]) * t)
        d.line([p, q], fill=(255, 255, 0, 200), width=1)
for x0, x1, yf, yb, pcd in PL['VAGAS_PCD']:
    ret((x0, min(yf, yb), x1, max(yf, yb)), (0, 80, 255, 255), 2)
for k in ('GARAGEM', 'RAMPA_GARAGEM', 'NUCLEO_GARAGEM', 'ACADEMIA', 'FITNESS', 'PET', 'DECK_PISCINA', 'PISCINA',
          'PISCINA_INFANTIL', 'PLAYGROUND', 'HAPPY_HOUR', 'SALAO', 'QUADRA', 'CHURRASQUEIRA', 'BEACH', 'PRACA',
          'PERGOLA_PRACA', 'GUARITA', 'LIXO', 'MEDIDORES', 'COBERTURA_SE'):
    ret(PL[k], (255, 0, 255, 255), 2)
for r in PL['CABANAS'] + PL['CASA_MAQ']:
    ret(r, (255, 0, 255, 255), 1)
for x, y in PL['IPES']:
    d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(160, 0, 220, 255), width=3)
for x, y in PL['FLORIDAS']:
    d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(255, 200, 0, 255), width=3)
for x, y, _ in PL['ARVORES']:
    d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(0, 90, 0, 255), width=3)
for x, y in PL['PALMEIRAS']:
    d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 255, 255, 255), width=3)
if len(sys.argv) > 6:
    im = im.crop(tuple(int(v) for v in sys.argv[3:7]))
im.save(sys.argv[2], quality=88)
print('ok', sys.argv[2])
