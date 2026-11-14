#!/usr/bin/env python3
"""ipi_ver.py -- desenha as medidas de ipi_planta.py por cima da implantacao, para conferir antes de gerar.
Fora do Blender, num venv com pillow:  python ipi_ver.py implantacao.png saida.jpg [escala]
implantacao.png: DIRECIONAL_785 ITAJUBA_IMPLANTACAO 01_R04.png do Drive (4000 x 2037 px)."""
import math, os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipi_planta as P

Image.MAX_IMAGE_PIXELS = None
im = Image.open(sys.argv[1]).convert('RGB')
k = im.size[0] / 4000.0
esc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
d = ImageDraw.Draw(im, 'RGBA')
q = lambda p: (p[0] * k, p[1] * k)


def ret(r, cor, w=3, fill=None):
    d.rectangle([q(r[:2]), q(r[2:4])], outline=cor, width=w, fill=fill)


def pol(pts, cor, w=3, fill=None):
    d.polygon([q(p) for p in pts], outline=cor, fill=fill)
    d.line([q(p) for p in list(pts) + [pts[0]]], fill=cor, width=w)


pol(P.TERRENO, (255, 0, 0), 5)
for p in P.ASFALTO:
    pol(p, (0, 0, 0, 255), 2, (0, 0, 0, 50))
for p in P.PASSEIOS:
    pol(p, (255, 140, 0), 2, (255, 140, 0, 50))
for p in P.PRACAS:
    pol(p, (255, 200, 0), 2, (255, 200, 0, 50))
for cs, n, tipo in P.VAGAS:
    cor = {'carro': (255, 0, 255), 'pcd': (0, 120, 255), 'moto': (0, 200, 200)}[tipo]
    pol(cs, cor, 2)
    a, b, c, dd = cs
    for i in range(1, n):
        t = i / n
        p0 = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        p1 = (dd[0] + (c[0] - dd[0]) * t, dd[1] + (c[1] - dd[1]) * t)
        d.line([q(p0), q(p1)], fill=cor, width=1)
for r in P.ILHAS:
    ret(r, (0, 160, 0), 2)
for x0, y0, x1, y1, _ in P.ZEBRAS:
    ret((x0, y0, x1, y1), (255, 255, 255), 2)
# torres: contorno do quadrante espelhado e girado
Q = P.Q_PX
qe = [(0, Q['y_nucleo']), (Q['nucleo'], Q['y_nucleo']), (Q['nucleo'], Q['y_fundo']), (Q['g06'], Q['y_fundo']),
      (Q['g06'], Q['y_fachada']), (Q['b06'], Q['y_fachada']), (Q['b06'], Q['y_fundo']), (Q['r'], Q['y_fundo']),
      (Q['r'], Q['y_fachada']), (Q['b05'], Q['y_fachada']), (Q['b05'], Q['y_fundo']), (Q['ponta'], Q['y_fundo']),
      (Q['ponta'], Q['y_ponta']), (Q['fim'], Q['y_ponta']), (Q['fim'], Q['testa_y']),
      (Q['fim'] - Q['testa_recuo'], Q['testa_y']), (Q['fim'] - Q['testa_recuo'], 0)]
leste = qe + [(x, -y) for x, y in reversed(qe)][1:]
cheio = leste + [(-x, y) for x, y in reversed(leste)][1:-1]
for t, (cx, cy, ang) in P.TORRES.items():
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    # local +y = para cima na imagem (-y px); giro na imagem (y para baixo)
    pts = [(cx + x * ca + y * sa, cy + x * sa - y * ca) for x, y in cheio]
    d.line([q(p) for p in pts + pts[:1]], fill=(0, 255, 255), width=3)
for nome in ('SOLARIUM', 'PISCINA', 'PISCINA_INFANTIL', 'VESTIARIO', 'FITNESS', 'PLAYGROUND', 'GOURMET', 'PERGOLADO',
             'APOIO', 'PET', 'GUARITA', 'CASA_BOMBAS', 'LIXO'):
    ret(getattr(P, nome), (255, 255, 0), 3)
for cx, cy in P.RESERVATORIOS:
    rr = P.RAIO_RESERVATORIO_PX
    d.ellipse([q((cx - rr, cy - rr)), q((cx + rr, cy + rr))], outline=(0, 0, 255), width=3)
for x, y in P.IPES:
    d.ellipse([q((x - 12, y - 12)), q((x + 12, y + 12))], fill=(200, 0, 160, 200))
for x, y, _ in P.ARVORES:
    d.ellipse([q((x - 12, y - 12)), q((x + 12, y + 12))], fill=(0, 120, 0, 200))
for x, y in P.PALMEIRAS:
    d.ellipse([q((x - 9, y - 9)), q((x + 9, y + 9))], fill=(230, 140, 0, 220))
for x, y, g in P.CARROS:
    a = math.radians(-g)
    pts = [(x + u * math.cos(a) - v * math.sin(a), y + u * math.sin(a) + v * math.cos(a))
           for u, v in ((-48, -20), (48, -20), (48, 20), (-48, 20))]
    pol(pts, (255, 60, 60), 2)
for x, y in P.POSTES_RUA:
    d.ellipse([q((x - 14, y - 14)), q((x + 14, y + 14))], fill=(255, 255, 0, 255), outline=(0, 0, 0))
for x, y in P.POSTES_JARDIM:
    d.ellipse([q((x - 10, y - 10)), q((x + 10, y + 10))], fill=(255, 160, 0, 255), outline=(0, 0, 0))
for x, y in P.BALIZADORES:
    d.ellipse([q((x - 6, y - 6)), q((x + 6, y + 6))], fill=(255, 255, 255, 255), outline=(0, 0, 0))
im = im.resize((int(im.size[0] * esc), int(im.size[1] * esc)), Image.LANCZOS)
im.save(sys.argv[2], quality=88)
