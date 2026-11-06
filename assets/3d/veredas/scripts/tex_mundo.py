#!/usr/bin/env python3
"""Texturas procedurais do bairro. Uso: python3 tex_mundo.py"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
Image.MAX_IMAGE_PIXELS = None
AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'tex')
rnd = random.Random(7); np.random.seed(7)

# ---------- fachadas: casas (8 linhas: 4 cores x 2 pavimentos) e predios (4 colunas de cor)
def fachada(nome, celulas, cores, por_coluna, aceso=0.32):
    S = 1024; c = S // celulas
    base = Image.new('RGB', (S, S)); luz = Image.new('RGB', (S, S), (0, 0, 0))
    db, dl = ImageDraw.Draw(base), ImageDraw.Draw(luz)
    for j in range(celulas):
        for i in range(celulas):
            cor = cores[(i * len(cores)) // celulas] if por_coluna else cores[(j * len(cores)) // celulas]
            x, y = i * c, j * c
            db.rectangle((x, y, x + c, y + c), fill=cor)
            db.rectangle((x, y, x + c, y + c // 14), fill=tuple(int(v * 0.8) for v in cor))
            mx, my = c // 5, c // 4
            db.rectangle((x + mx, y + my, x + c - mx, y + c - my), fill=(52, 62, 72))
            if rnd.random() < aceso:
                q = rnd.choice([(255, 196, 110), (255, 214, 150), (255, 176, 90), (230, 225, 200)])
                dl.rectangle((x + mx, y + my, x + c - mx, y + c - my), fill=q)
    base.save(os.path.join(T, nome + '.jpg'), quality=82)
    luz.save(os.path.join(T, nome + '_luz.jpg'), quality=82)
fachada('casas', 8, [(232, 226, 212), (222, 205, 175), (240, 238, 232), (200, 190, 172)], False, 0.42)
fachada('predios', 16, [(226, 224, 218), (196, 186, 170), (150, 152, 158), (178, 134, 112)], True, 0.30)

# ---------- paleta de telhados (8 celulas)
tel = Image.new('RGB', (64, 8)); dt = ImageDraw.Draw(tel)
for i, c in enumerate([(170, 124, 98), (150, 96, 72), (196, 160, 130), (128, 124, 120), (214, 210, 202), (92, 90, 90), (196, 178, 156), (168, 166, 160)]):
    dt.rectangle((i * 8, 0, i * 8 + 8, 8), fill=c)
tel.save(os.path.join(T, 'telhados.png'))

# ---------- copas: U = especie, V = sombra (embaixo escuro -> topo claro), com leve ruido
W, H = 64, 64
c = np.zeros((H, W, 3), float)
CORES = [(54, 78, 38), (44, 68, 36), (68, 88, 42), (38, 58, 32), (62, 84, 48), (80, 96, 46), (146, 78, 124), (186, 152, 48)]
for i, cor in enumerate(CORES):
    for j in range(H):
        k = 0.42 + 0.62 * (1 - j / (H - 1))
        c[j, i * 8:i * 8 + 8] = np.array(cor) * k
c += np.random.normal(0, 4, c.shape)
Image.fromarray(np.clip(c, 0, 255).astype('uint8')).save(os.path.join(T, 'copas.png'))

# ---------- luz no chao / halo (radial)
S = 128
y, x = np.mgrid[0:S, 0:S]
r = np.hypot(x - S / 2 + .5, y - S / 2 + .5) / (S / 2)
a = np.clip(1 - r, 0, 1) ** 2.2
rgba = np.zeros((S, S, 4), 'uint8')
rgba[..., 0], rgba[..., 1], rgba[..., 2] = 255, 200, 130
rgba[..., 3] = (a * 255).astype('uint8')
Image.fromarray(rgba, 'RGBA').save(os.path.join(T, 'luz_radial.png'))
Image.new('RGB', (4, 4), (255, 226, 170)).save(os.path.join(T, 'lampada.png'))

# ---------- anel: chao de ~8,4 km x 8,4 km (dia + mapa de luz noturna), pintado do OSM
L = 4200; N = 4096; K = N / (2 * L)
def px(p): return ((p[0] + L) * K, (L - p[1]) * K)
def ruido(oit, amp):
    img = np.random.rand(oit, oit)
    return np.array(Image.fromarray((img * 255).astype('uint8')).resize((N, N), Image.BICUBIC), float) / 255 * amp
camp = (ruido(40, 1.0) + ruido(180, 0.5) + ruido(700, 0.25)) / 1.75
s = np.zeros((N, N, 3), float)
seca, verde, terra = np.array((150, 138, 88.)), np.array((102, 118, 62.)), np.array((146, 100, 72.))
m1 = np.clip((camp - 0.42) * 7, 0, 1)[..., None]
m2 = np.clip((ruido(70, 1.0) - 0.68) * 8, 0, 1)[..., None]
s = seca * (1 - m1) + verde * m1
s = s * (1 - m2) + terra * m2
s += (ruido(1400, 22) - 11)[..., None]
img = Image.fromarray(np.clip(s, 0, 255).astype('uint8'))
d = ImageDraw.Draw(img)
luz = Image.new('RGB', (N, N), (0, 0, 0)); dl = ImageDraw.Draw(luz)
o = json.load(open(os.path.join(AQUI, 'osm_cena.json')))
COR = {'res': (146, 136, 120), 'campo': (138, 134, 78), 'verde': (92, 118, 60), 'mata': (54, 84, 44), 'ind': (140, 136, 130), 'obra': (150, 108, 80), 'agua': (66, 96, 110)}
for u in ('campo', 'res', 'ind', 'obra', 'verde', 'mata', 'agua'):
    for e in o['solo']:
        if e['u'] == u and len(e['p']) > 2:
            d.polygon([px(q) for q in e['p']], fill=COR[u])
LARG = {'motorway': 16, 'trunk': 14, 'motorway_link': 7, 'trunk_link': 7, 'primary': 12, 'primary_link': 7, 'secondary': 12, 'secondary_link': 7, 'tertiary': 10, 'tertiary_link': 6, 'residential': 7, 'unclassified': 7, 'living_street': 6, 'service': 4}
ORD = ['service', 'living_street', 'unclassified', 'residential', 'tertiary_link', 'tertiary', 'secondary_link', 'secondary', 'primary_link', 'primary', 'trunk_link', 'motorway_link', 'trunk', 'motorway']
# telhadinhos (de longe viram a textura de bairro)
for e in o['ruas']:
    if e['c'] in ('residential', 'living_street', 'unclassified', 'service'):
        pts = e['p']
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]; L2 = math.hypot(dx, dy)
            if not L2: continue
            nx, ny = -dy / L2, dx / L2
            for t in np.arange(0, L2, 13):
                for lado in (-1, 1):
                    if rnd.random() < 0.15: continue
                    cx, cy = a[0] + dx * t / L2 + nx * lado * 13, a[1] + dy * t / L2 + ny * lado * 13
                    qx, qy = px((cx, cy))
                    cor = rnd.choice([(170, 124, 98), (196, 160, 130), (196, 178, 156), (214, 210, 202), (168, 166, 160)])
                    d.rectangle((qx - 2.5, qy - 2.5, qx + 2.5, qy + 2.5), fill=cor)
                    if rnd.random() < 0.38:
                        dl.rectangle((qx - 1, qy - 1, qx + 1, qy + 1), fill=rnd.choice([(255, 190, 110), (255, 210, 150)]))
for cl in ORD:
    for e in o['ruas']:
        if e['c'] == cl:
            pts = [px(q) for q in e['p']]
            w = max(1, round(LARG[cl] * K))
            d.line(pts, fill=(86, 86, 88) if LARG[cl] >= 10 else (112, 110, 106), width=w)
            if cl != 'service':
                dl.line(pts, fill=(120, 84, 44) if LARG[cl] < 10 else (200, 140, 70), width=max(1, w - 1))
for e in o['predios']:
    if len(e['p']) > 2:
        dl.polygon([px(q) for q in e['p']], fill=(120, 90, 60))
# transicao com a planta: mesma cor C dos dois lados da borda
def P(x, y): return (31.9 - (y - 1510) / 13.04, 19.7 - (x - 7187) / 13.04)
CONT = [(260, 3050), (1040, 3050), (1460, 3672), (4950, 3672), (4950, 700), (5120, 470), (5600, 290), (6820, 230), (8000, 210), (9100, 130), (9720, 130), (9720, 6700), (260, 6700)]
C = (92, 110, 60)
m = Image.new('L', (N, N), 0)
ImageDraw.Draw(m).polygon([px(P(*q)) for q in CONT], fill=255)
m = m.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(26))
img.paste(Image.new('RGB', (N, N), C), (0, 0), m)
luz.paste(Image.new('RGB', (N, N), (0, 0, 0)), (0, 0), m)
img.save(os.path.join(T, 'anel.jpg'), quality=62, optimize=True)
luz.resize((2048, 2048), Image.BILINEAR).save(os.path.join(T, 'anel_luz.jpg'), quality=70, optimize=True)
for n in ('anel.jpg', 'anel_luz.jpg', 'casas.jpg', 'predios.jpg'):
    print(n, os.path.getsize(os.path.join(T, n)))
