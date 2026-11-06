#!/usr/bin/env python3
"""Gera tex/planta.jpg a partir do TIF de implantacao (FyrStudio): apaga os rotulos e a rua de cima
(remodelada mais para fora, porque o terreno do Gaia avanca sobre ela). Uso: python3 tex_planta.py <tif>"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
Image.MAX_IMAGE_PIXELS = None
AQUI = os.path.dirname(os.path.abspath(__file__))
im = Image.open(sys.argv[1]).convert('RGB')

def remenda(x0, y0, x1, y1, dx, dy, fe=14):
    """cobre o retangulo com o trecho deslocado (dx,dy) da propria imagem, com borda suave"""
    w, h = x1 - x0 + 2 * fe, y1 - y0 + 2 * fe
    src = im.crop((x0 - fe + dx, y0 - fe + dy, x0 - fe + dx + w, y0 - fe + dy + h))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rectangle((fe, fe, w - fe, h - fe), fill=255)
    im.paste(src, (x0 - fe, y0 - fe), m.filter(ImageFilter.GaussianBlur(fe / 2)))

ROTULOS = [
    (1430, 4760, 1770, 4900, 0, 170),   # LOTE 02
    (1300, 5650, 1620, 5810, 0, 200),   # LOTE 01
    (5180, 830, 5500, 930, 0, 100),     # LOTE 03
    (5600, 690, 6335, 805, 0, 125),     # AREA INSTITUCIONAL 01 (cima)
    (6395, 690, 7125, 805, 0, 125),     # AREA INSTITUCIONAL 02 (cima)
    (5550, 2050, 6500, 2170, 0, 160),   # FUTUROS LANCAMENTOS
    (6220, 3510, 6920, 3625, -800, 0),  # SISTEMA DE LAZER
    (8210, 1920, 8700, 2020, 0, -120),  # AREA VERDE (Gaia)
    (6800, 5100, 7260, 5220, 0, 150),   # AREA VERDE (praca)
    (6630, 5860, 7400, 5945, 0, -90),   # AREA INSTITUCIONAL 01 (baixo)
    (6630, 6310, 7400, 6395, 0, 100),   # AREA INSTITUCIONAL 02 (baixo)
]
for r in ROTULOS:
    remenda(*r)

# apaga a rua de cima original: grama do proprio lote de Futuros Lancamentos, mascarada pelo traco da rua
grama = im.crop((5300, 1100, 6700, 2400)).resize((5000, 1600))
m = Image.new('L', (5000, 1600), 0)
RUA = [(5130, 620), (5300, 500), (5597, 461), (6983, 367), (8002, 257), (8777, 233), (9150, 300)]
ImageDraw.Draw(m).line([(x - 4900, y + 100) for x, y in RUA], fill=255, width=210, joint='curve')
im.paste(grama, (4900, -100), m.filter(ImageFilter.GaussianBlur(10)))

# borda desbota para a cor C (a mesma do anel) e copas escuras viram posicoes de arvore 3D
C = (92, 110, 60)
CONT = [(260, 3050), (1040, 3050), (1460, 3672), (4950, 3672), (4950, 700), (5120, 470), (5600, 290), (6820, 230), (8000, 210), (9100, 130), (9720, 130), (9720, 6700), (260, 6700)]
E = 4
m = Image.new('L', (im.size[0] // E, im.size[1] // E), 0)
ImageDraw.Draw(m).polygon([(x / E, y / E) for x, y in CONT], fill=255)
m = m.filter(ImageFilter.MinFilter(61)).filter(ImageFilter.GaussianBlur(28)).resize(im.size, Image.BILINEAR)
fundo = Image.new('RGB', im.size, C)
fundo.paste(im, (0, 0), m)
im = fundo

saida = im.resize((4096, round(im.size[1] * 4096 / im.size[0])), Image.LANCZOS)
saida.save(os.path.join(AQUI, 'tex', 'planta.jpg'), quality=78, optimize=True)
print(saida.size, os.path.getsize(os.path.join(AQUI, 'tex', 'planta.jpg')))

# arvores: pixels de copa (verde escuro saturado) na grade de 3 m, so nas areas do plano
import json, random
rnd = random.Random(3)
peq = im.resize((im.size[0] // 8, im.size[1] // 8), Image.BILINEAR)
pp = peq.load(); W, H = peq.size
ARV = []
for py in range(0, H, 5):
    for px in range(0, W, 5):
        x = px * 8; y = py * 8
        ix, iy = min(W - 1, px + rnd.randint(-2, 2)), min(H - 1, py + rnd.randint(-2, 2))
        r, g, b = pp[ix, iy]
        lum = (r + g + b) / 3
        roxo = r > 110 and b > 110 and g < r - 25
        amarelo = r > 150 and g > 130 and b < 90
        verde = g > r * 1.12 and g > b * 1.25 and lum < 68
        if not (roxo or amarelo or verde):
            continue
        # fora do lote do Gaia (modelo proprio)
        if 6800 < x < 8130 and 200 < y < 3430:
            continue
        ARV.append((x, y, 'r' if roxo else 'a' if amarelo else 'v'))
json.dump(ARV, open(os.path.join(AQUI, 'arvores_planta.json'), 'w'), separators=(',', ':'))
print('arvores planta', len(ARV))
