#!/usr/bin/env python3
"""cpr_ver.py -- sobrepoe as medidas de cpr_planta.py e o contorno da torre (cpr_torre.py) na implantacao, para
conferir antes de gerar. Fora do Blender, num venv com pillow:
    python cpr_ver.py <implantacao.png> saida.jpg [escala_de_saida]
A implantacao e a imagem embutida na pagina 8 do book de mesa (2671 x 1083 px)."""
import os, sys
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
PL, TR = {}, {}
exec(open(os.path.join(AQUI, 'cpr_planta.py')).read(), PL)
exec(open(os.path.join(AQUI, 'cpr_torre.py')).read(), TR)

im = Image.open(sys.argv[1]).convert('RGB')
k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
d = ImageDraw.Draw(im, 'RGBA')
S, (cx, cy) = PL['S_PX'], PL['TORRE']


def tw(p):          # torre (x, v) em metros -> px
    return (cx + p[0] / S, cy + p[1] / S)


def poly(pts, cor, w=2, fill=None):
    d.polygon([tuple(p) for p in pts], outline=cor, fill=fill)
    d.line([tuple(p) for p in pts] + [tuple(pts[0])], fill=cor, width=w)


def ret(r, cor, w=2):
    d.rectangle(r, outline=cor, width=w)


poly(PL['TERRENO'], (255, 0, 0, 255), 3)
for p in PL['ASFALTO']:
    poly(p, (40, 40, 40, 255), 2, (0, 0, 0, 40))
poly(PL['DECK'], (0, 0, 255, 255), 2)
poly(PL['ALCA'], (60, 60, 60, 255), 2)
poly(PL['ILHA'], (0, 160, 0, 255), 2)
for cs, n, tipo in PL['VAGAS']:
    poly(cs, (255, 255, 0, 255), 1)
    a, b = cs[0], cs[1]
    for i in range(1, n):
        t = i / n
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        q = (cs[3][0] + (cs[2][0] - cs[3][0]) * t, cs[3][1] + (cs[2][1] - cs[3][1]) * t)
        d.line([p, q], fill=(255, 255, 0, 255), width=1)
for p in PL['PASSEIOS']:
    poly(p, (255, 140, 0, 255), 1)
for p in PL['PRACAS']:
    poly(p, (255, 0, 255, 255), 1)
for r in PL['COBERTURAS']:
    ret(r, (0, 255, 255, 255), 1)
poly(PL['RAMPA'], (255, 0, 255, 255), 2)
for nome in ('PLAYGROUND', 'GOURMET', 'GOURMET_DECK', 'DECK_PISCINA', 'PISCINA', 'PISCINA_INFANTIL', 'DECK_MOLHADO',
             'OFURO', 'CASA_MAQ', 'QUADRA', 'PRACA_CHEGADA', 'GUARITA', 'DELIVERY', 'LIXO', 'PET', 'NUCLEO_GARAGEM'):
    ret(PL[nome], (255, 0, 0, 255), 2)
for r in PL['SEBES']:
    ret(r, (0, 120, 0, 255), 1)
for r in PL['PASSARELAS']:
    ret(r, (120, 0, 200, 255), 1)
# torre
poly([tw(p) for p in TR['contorno_tipo']()], (255, 0, 0, 255), 2)
poly([tw(p) for p in TR['contorno_cobertura']()], (0, 0, 255, 255), 1)
for f in range(1, 7):
    var, jan, bri = TR['aberturas'](f)
    for j in jan:
        if j[0] == 'v':
            d.line([tw((j[2], j[1])), tw((j[3], j[1]))], fill=(0, 200, 255, 255), width=3)
        else:
            d.line([tw((j[1], j[2])), tw((j[1], j[3]))], fill=(0, 200, 255, 255), width=3)
    for fu in var['fundos']:
        if fu[0] == 'v':
            d.line([tw((fu[2], fu[1])), tw((fu[3], fu[1]))], fill=(0, 255, 0, 255), width=3)
        else:
            d.line([tw((fu[1], fu[2])), tw((fu[1], fu[3]))], fill=(0, 255, 0, 255), width=3)
for x, y in PL['IPES'] + PL['FLORIDAS']:
    d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(200, 0, 200, 255), width=2)
for x, y, _ in PL['ARVORES']:
    d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(0, 120, 0, 255), width=2)
for x, y in PL['PALMEIRAS']:
    d.ellipse((x - 4, y - 4, x + 4, y + 4), outline=(255, 255, 255, 255), width=2)
for x, y, g in PL['CARROS']:
    d.rectangle((x - 5, y - 5, x + 5, y + 5), outline=(255, 0, 0, 255))
if k != 1.0:
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
im.save(sys.argv[2], quality=88)
print('ok', sys.argv[2])
