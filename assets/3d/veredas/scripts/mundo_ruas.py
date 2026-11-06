# mundo_ruas.py -- chao da planta, ruas, rotatorias, guias e sinalizacao
SOLO_Z, ASF_Z, GUIA_Z = -0.32, -0.14, 0.02
# ---- eixos em px da planta: (pontos, largura em metros, marcacao)
RUAS = {
  'av-norte':  ([(1250, 3790), (8110, 3790)], 9.0, None),
  'av-sul':    ([(1270, 4110), (1500, 4092), (8020, 4100)], 10.0, 'amarela'),
  'ligacao':   ([(5050, 3790), (5050, 4100)], 14.0, None),
  'rua-gaia':  ([(5050, 3790), (5050, 1800), (5050, 950), (5110, 680), (5280, 520), (5620, 430), (6200, 300), (6819, 186),
                 (7500, 165), (8200, 150), (8800, 165), (9150, 250), (9290, 430), (9310, 800), (9290, 1630), (9245, 2242),
                 (9143, 2650), (8940, 3017), (8613, 3384), (8440, 3660)], 9.2, 'branca'),
  'rua-01':    ([(8530, 4400), (8536, 4732), (8478, 4963), (8200, 5263), (7993, 5517), (7762, 5748), (7647, 6025), (7605, 6395), (7623, 6800)], 10.0, 'amarela'),
  'prolong-o': ([(530, 4340), (508, 4863), (470, 5500), (416, 6250), (345, 6800)], 12.0, None),
  'prolong-l': ([(860, 4300), (859, 4863), (815, 5600), (774, 6250), (720, 6800)], 12.0, None),
  'alca':      ([(1480, 4150), (1250, 4310), (1060, 4520), (930, 4760), (860, 4960)], 9.0, None),
  'rua-baixo': ([(790, 6480), (3500, 6725), (5000, 6825), (7600, 6930)], 7.5, None),
}
ROTAT = [((739, 3777), 497, 617), ((8448, 4044), 328, 439)]  # centro, raio ilha, raio externo (px)

def montar_ruas(M, extras=None):
    ras = dict(RUAS)
    if extras:
        ras.update(extras)
    cz = []  # (pts array, meia-largura) para cortar guias nas juncoes
    eixos = {}
    for k, (pp, w, _) in ras.items():
        pts = suaviza(Ps(pp), 5.0)
        eixos[k] = pts
        cz.append((k, np.array(pts), w / 2))
    rot_m = [(np.array(P(*c)), ri / PXM, re / PXM) for c, ri, re in ROTAT]
    def sobre_outra(p, eu):
        for k, a, h in cz:
            if k == eu:
                continue
            if ((a - p) ** 2).sum(axis=1).min() < (h - 0.15) ** 2:
                return True
        for j, (c, ri, re) in enumerate(rot_m):
            if eu == 'rot%d' % j:
                continue
            d = np.linalg.norm(p - c)
            if ri + 0.1 < d < re - 0.1:
                return True
        return False
    for k, (pp, w, marca) in ras.items():
        pts = eixos[k]
        pular = lambda p, k=k: sobre_outra(p, k)
        fita(M['asfalto'], pts, w, ASF_Z, uv_esc=0.09)
        guia(M['guia'], pts, w / 2, ASF_Z, GUIA_Z, pular=pular)
        guia(M['guia'], pts, -w / 2, ASF_Z, GUIA_Z, pular=pular)
        if marca:
            a = np.array(pts)
            seg = [tuple(q) for q in a if not any(np.linalg.norm(q - c) < re + 3 for c, _, re in rot_m)]
            if len(seg) > 2:
                tracejado(M['faixa_amarela' if marca == 'amarela' else 'faixa_branca'], seg, 0.16, ASF_Z + 0.03)
    # rotatorias
    for j, (c, ri, re) in enumerate(rot_m):
        n = 96
        an = [2 * math.pi * i / n for i in range(n + 1)]
        ci = [tuple(c + ri * np.array([math.cos(t), math.sin(t)])) for t in an]
        ce = [tuple(c + re * np.array([math.cos(t), math.sin(t)])) for t in an]
        for i in range(n):
            cos = [(*ci[i], ASF_Z), (*ce[i], ASF_Z), (*ce[i + 1], ASF_Z), (*ci[i + 1], ASF_Z)]
            M['asfalto'].face(cos, [(q[0] * 0.09, q[1] * 0.09) for q in cos])
        p = lambda q, j=j: sobre_outra(q, 'rot%d' % j)
        # eixo no sentido anti-horario: normal aponta para dentro
        guia(M['guia'], ci, 0.0, ASF_Z, GUIA_Z + 0.1, pular=None, larg=0.3)
        guia(M['guia'], ce, -0.001, ASF_Z, GUIA_Z, pular=p)
    # calcadas da rua remodelada (a planta original foi apagada ali)
    a = suaviza(Ps(RUAS['rua-gaia'][0][4:17]), 5.0)
    pular = lambda q: sobre_outra(q, 'rua-gaia')
    fita(M['passeio'], a, 3.0, GUIA_Z, desloc=9.2 / 2 + 1.5, uv_esc=0.25, pular=pular)
    fita(M['passeio'], a, 3.0, GUIA_Z, desloc=-9.2 / 2 - 1.5, uv_esc=0.25, pular=pular)
    # faixas de pedestre sobre a avenida (x em px da planta)
    for px, y0, y1 in ((1750, 4040, 4170), (4700, 4040, 4170), (5945, 4040, 4170), (7831, 4040, 4170), (1750, 3730, 3850), (4700, 3730, 3850), (5945, 3730, 3850), (7831, 3730, 3850)):
        (xa, ya), (xb, yb) = P(px, y0), P(px, y1)
        for i in range(int(abs(xa - xb) / 1.1)):
            x = max(xa, xb) - 0.55 - i * 1.1
            cos = [(x - 0.25, ya + 1.6, ASF_Z + 0.03), (x + 0.25, ya + 1.6, ASF_Z + 0.03), (x + 0.25, ya - 1.6, ASF_Z + 0.03), (x - 0.25, ya - 1.6, ASF_Z + 0.03)]
            M['faixa_branca'].face(cos, [(0, 0), (1, 0), (1, 1), (0, 1)])
    return eixos

CONTORNO = [(260, 3050), (1040, 3050), (1460, 3672), (4950, 3672), (4950, 700), (5120, 470), (5600, 290), (6820, 230), (8000, 210), (9100, 130), (9720, 130), (9720, 6700), (260, 6700)]
def montar_solo_planta(mat):
    m = Malha('mundo-solo-planta', mat)
    cos = [(*P(*c), SOLO_Z) for c in CONTORNO]
    uvs = [(c[0] / 10000, 1 - c[1] / 7039) for c in CONTORNO]
    # poligono em sentido anti-horario visto de cima (normal +z)
    area = sum(cos[i][0] * cos[(i + 1) % len(cos)][1] - cos[(i + 1) % len(cos)][0] * cos[i][1] for i in range(len(cos)))
    if area < 0:
        cos, uvs = cos[::-1], uvs[::-1]
    m.face(cos, uvs)
    return m.objeto()
