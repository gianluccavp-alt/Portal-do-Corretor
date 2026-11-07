# gaia_patio.py -- chao do condominio em vetores limpos, a partir das medidas de gaia_planta.py:
# grama, asfalto com guia, passeios levantados, vagas, PCD, faixas, rua de acesso, muros e jardins das torres.
# Executado por gaia_modelo.py dentro do Blender.
import numpy as np, json, math

Z_GRAMA, Z_ASF, Z_LINHA, Z_PASSEIO = 0.0, 0.02, 0.05, 0.14
L_LINHA = 0.10
W_GRADE, H_GRADE = 2600, 1500


def _mascara(rects):
    m = np.zeros((H_GRADE, W_GRADE), bool)
    for r in rects:
        m[int(r[1]):int(r[3]), int(r[0]):int(r[2])] = True
    return m


def _mascara_poligono(pts):
    """Rasteriza um poligono simples por varredura (grade de 1 px)."""
    m = np.zeros((H_GRADE, W_GRADE), bool)
    n = len(pts)
    for y in range(H_GRADE):
        yc = y + 0.5
        xs = []
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[0::2], xs[1::2]):
            m[y, int(round(a)):int(round(b))] = True
    return m


def _decompor(m):
    """Uniao de retangulos -> poucos retangulos sem sobreposicao (corridas por linha fundidas na vertical)."""
    abertos, saida = {}, []
    for y in range(m.shape[0] + 1):
        corridas = set()
        if y < m.shape[0] and m[y].any():
            lin = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            ini, fim = np.nonzero(lin == 1)[0], np.nonzero(lin == -1)[0]
            corridas = set(zip(ini.tolist(), fim.tolist()))
        for c in list(abertos):
            if c not in corridas:
                saida.append((c[0], abertos.pop(c), c[1], y))
        for c in corridas:
            abertos.setdefault(c, y)
    return saida


def _bordas(m):
    """Segmentos da divisa de m: (x0, y0, x1, y1, lado) em px; lado = direcao do lado de FORA."""
    seg = []
    h, w = m.shape
    dif = m[1:, :] != m[:-1, :]
    for y in np.nonzero(dif.any(1))[0]:
        lin = dif[y]
        d = np.diff(np.concatenate([[0], lin.astype(np.int8), [0]]))
        for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            # pode haver troca de lado no meio do trecho: separa por quem esta dentro
            k = a
            while k < b:
                dentro_cima = bool(m[y, k])
                j = k
                while j < b and bool(m[y, j]) == dentro_cima:
                    j += 1
                seg.append((k, y + 1, j, y + 1, 's' if dentro_cima else 'n'))
                k = j
    dif = m[:, 1:] != m[:, :-1]
    for x in np.nonzero(dif.any(0))[0]:
        lin = dif[:, x]
        d = np.diff(np.concatenate([[0], lin.astype(np.int8), [0]]))
        for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            k = a
            while k < b:
                dentro_esq = bool(m[k, x])
                j = k
                while j < b and bool(m[j, x]) == dentro_esq:
                    j += 1
                seg.append((x + 1, k, x + 1, j, 'l' if dentro_esq else 'o'))
                k = j
    return seg


def _ret_px(g, r, z, mat):
    g.piso(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), z, mat)


def linha_h(g, x0, x1, y, mat='faixa', z=Z_LINHA, w=L_LINHA):
    g.piso(X(x0), X(x1), y - w / 2, y + w / 2, z, mat)


def linha_v(g, x, y0, y1, mat='faixa', z=Z_LINHA, w=L_LINHA):
    g.piso(x - w / 2, x + w / 2, min(y0, y1), max(y0, y1), z, mat)


def segmento(g, a, b, w, z, mat='faixa'):
    """Faixa de a a b em metros, largura w."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    g.face([(a[0] - nx, a[1] - ny, z), (b[0] - nx, b[1] - ny, z), (b[0] + nx, b[1] + ny, z), (a[0] + nx, a[1] + ny, z)], mat)


def chao_vagas(g):
    dados = json.load(open(SCR + '/patio_vagas.json'))
    for v in dados['vagas']:
        x0, y0, x1, y1 = v['r']
        linhas = [p for p in v['linhas'] if (y0 - 0.5 <= p <= y1 + 0.5 if v['s'] == 'v' else x0 - 0.5 <= p <= x1 + 0.5)]
        if v['s'] == 'v':
            for p in linhas:
                linha_h(g, x0, x1, Y(p))
            linha_v(g, X(x0), Y(linhas[0]), Y(linhas[-1]))
            linha_v(g, X(x1), Y(linhas[0]), Y(linhas[-1]))
        else:
            for p in linhas:
                linha_v(g, X(p), Y(y0), Y(y1))
            linha_h(g, linhas[0], linhas[-1], Y(y0))
            linha_h(g, linhas[0], linhas[-1], Y(y1))
    for v in dados['motos']:
        x0, y0, x1, y1 = v['r']
        ln = v['linhas']
        for k, p in enumerate(ln):
            if v['s'] == 'v':
                linha_h(g, x0, x1, Y(p), w=0.07)
            else:
                linha_v(g, X(p), Y(y0), Y(y1), w=0.07)
            if k + 1 < len(ln):
                q = ln[k + 1]
                if v['s'] == 'v':
                    a, b = X(x0) + 0.3, X(x1) - 0.3
                    cy = Y((p + q) / 2)
                    g.tapete(a, b, cy - 0.28, cy + 0.28, Z_LINHA, 'marcas', MARCAS['moto'], gira=True)
                else:
                    a, b = Y(y1) + 0.3, Y(y0) - 0.3
                    cx = X((p + q) / 2)
                    g.tapete(cx - 0.28, cx + 0.28, a, b, Z_LINHA, 'marcas', MARCAS['moto'])
    # PCD: hachura diagonal + simbolo azul
    for xc in PL.COLUNAS_PCD:
        x0, x1 = X(xc), X(xc + 41)
        for ya, yb in PL.PCD_HACHURA_Y:
            yy0, yy1 = Y(yb), Y(ya)
            n = 9
            passo = (x1 - x0) / n
            for k in range(n):
                xa = x0 + k * passo
                g.face([(xa, yy0, Z_LINHA), (xa + passo * 0.5, yy0, Z_LINHA), (xa + passo * 1.2, yy1, Z_LINHA), (xa + passo * 0.7, yy1, Z_LINHA)], 'faixa')
            linha_h(g, xc, xc + 41, yy0, w=0.07); linha_h(g, xc, xc + 41, yy1, w=0.07)
        for py in PL.PCD_SIMBOLO_Y:
            cx, cy = X(xc + 39), Y(py)
            g.tapete(cx - 0.55, cx + 0.55, cy - 0.55, cy + 0.55, Z_LINHA + 0.002, 'marcas', MARCAS['pcd'], gira=True)
    # faixas de pedestre do passeio transversal
    for x0, y0, x1, y1, _s in PL.ZEBRAS:
        n = max(3, round((x1 - x0) / 12))
        p = (X(x1) - X(x0)) / n
        for k in range(n):
            g.piso(X(x0) + k * p + p * 0.2, X(x0) + k * p + p * 0.8, Y(y1), Y(y0), Z_LINHA, 'faixa')


def rua_lateral(g):
    """Rua de acesso, calcada, vagas de visitante, faixa de pedestre e apron da entrada."""
    def xrua(py):
        return PL.RUA_X0 + (py - 640) * PL.RUA_INCL
    y_a, y_b = -900, 2600
    for y0, y1 in ((y_a, y_b),):
        a0, a1 = xrua(y0), xrua(y1)
        L = PL.RUA_MEIA * 2
        g.poligono([(X(a0), Y(y0)), (X(a1), Y(y1)), (X(a1 + L), Y(y1)), (X(a0 + L), Y(y0))], Z_ASF, 'asfalto')
        # guias
        for off in (0, L):
            segmento(g, (X(a0 + off), Y(y0)), (X(a1 + off), Y(y1)), 0.18, Z_PASSEIO, 'meio_fio')
    # eixo tracejado e calcadas dos dois lados
    py = y_a
    while py < y_b:
        c = xrua(py) + PL.RUA_MEIA
        c2 = xrua(py + 30) + PL.RUA_MEIA
        segmento(g, (X(c), Y(py)), (X(c2), Y(py + 30)), 0.14, Z_LINHA)
        py += 75
    for off0, off1, ya, yb in ((-22, 0, y_a, 1125), (PL.RUA_MEIA * 2, PL.RUA_MEIA * 2 + 28, y_a, y_b), (-22, 0, 1320, y_b)):
        a, b = xrua(ya), xrua(yb)
        g.poligono([(X(a + off0), Y(ya)), (X(b + off0), Y(yb)), (X(b + off1), Y(yb)), (X(a + off1), Y(ya))], Z_PASSEIO, 'concreto')
    # vagas de visitante (blocos de concregrama/concreto, inclinados com a rua)
    for cantos, n in PL.VISITANTES:
        q = [(X(p[0]), Y(p[1])) for p in cantos]
        g.poligono(q, Z_ASF + 0.015, 'paver_rua')
        for i in range(4):
            segmento(g, q[i], q[(i + 1) % 4], L_LINHA, Z_LINHA)
        for k in range(1, n):
            t = k / n
            a = (q[0][0] + (q[3][0] - q[0][0]) * t, q[0][1] + (q[3][1] - q[0][1]) * t)
            b = (q[1][0] + (q[2][0] - q[1][0]) * t, q[1][1] + (q[2][1] - q[1][1]) * t)
            segmento(g, a, b, L_LINHA, Z_LINHA)
    # faixa de pedestre na rua (junto da entrada) e na entrada de veiculos
    for py0, py1, x0, w_ in ((1142, 1293, 2371, 27), (1200, 1277, 2168, 30)):
        n = int((py1 - py0) / 15)
        for k in range(n):
            py = py0 + k * (py1 - py0) / n
            dx = (py - py0) * 0.107
            a = (X(x0 + dx), Y(py)); b = (X(x0 + dx + w_), Y(py))
            segmento(g, a, b, 0.62, Z_LINHA + 0.004)
    # apron da entrada
    pts = [(X(p[0]), Y(p[1])) for p in PL.ASFALTO_ENTRADA]
    g.poligono(pts, Z_ASF + 0.002, 'asfalto')


def chao(g):
    # grama do terreno, com recorte sob o deck (a piscina tem profundidade real)
    m_gr = _mascara_poligono(PL.TERRENO)
    x0, y0, x1, y1 = PL.DECK
    m_gr[y0:y1, x0:x1] = False
    for r in _decompor(m_gr):
        _ret_px(g, r, Z_GRAMA, 'grama')
    m_asf = _mascara(PL.ASFALTO)
    for r in _decompor(m_asf):
        _ret_px(g, r, Z_ASF, 'asfalto')
    m_pas = _mascara(PL.PASSEIO)
    m_pav = _mascara(PL.PAVER_PATIO) & ~m_pas
    for r in _decompor(m_pas):
        _ret_px(g, r, Z_PASSEIO, 'concreto')
    for r in _decompor(m_pav):
        _ret_px(g, r, Z_PASSEIO, 'paver')
    # lateral dos passeios (a borda pega luz e sombra)
    for x0, y0, x1, y1, lado in _bordas(m_pas | m_pav):
        if lado in 'ns':
            # 'n' = fora ao norte da planta (y menor): y0 == y1
            yy = Y(y0)
            if lado == 'n':
                g.face([(X(x1), yy, 0), (X(x0), yy, 0), (X(x0), yy, Z_PASSEIO), (X(x1), yy, Z_PASSEIO)], 'meio_fio')
            else:
                g.face([(X(x0), yy, 0), (X(x1), yy, 0), (X(x1), yy, Z_PASSEIO), (X(x0), yy, Z_PASSEIO)], 'meio_fio')
        else:
            xx = X(x0)
            if lado == 'l':
                g.face([(xx, Y(y1), 0), (xx, Y(y0), 0), (xx, Y(y0), Z_PASSEIO), (xx, Y(y1), Z_PASSEIO)], 'meio_fio')
            else:
                g.face([(xx, Y(y0), 0), (xx, Y(y1), 0), (xx, Y(y1), Z_PASSEIO), (xx, Y(y0), Z_PASSEIO)], 'meio_fio')
    # guia entre asfalto e grama
    livre = ~(m_pas | m_pav | _mascara([(2103, 1180, 2400, 1300), (2033, 1281, 2323, 1292), PL.CHARGE]))
    for x0, y0, x1, y1, lado in _bordas(m_asf):
        if y0 == y1:
            # trecho horizontal: 'n' fora para y menor (px)
            fora_y = y0 - 1 if lado == 'n' else y0
            for a, b in _trechos(livre[fora_y, x0:x1], x0):
                yy = Y(y0)
                yy0, yy1 = (yy, yy + 0.12) if lado == 'n' else (yy - 0.12, yy)
                g.caixa(X(a), X(b), yy0, yy1, 0, Z_PASSEIO, 'meio_fio')
        else:
            fora_x = x0 if lado == 'l' else x0 - 1
            for a, b in _trechos(livre[y0:y1, fora_x], y0):
                xx = X(x0)
                xx0, xx1 = (xx, xx + 0.12) if lado == 'l' else (xx - 0.12, xx)
                g.caixa(xx0, xx1, Y(b), Y(a), 0, Z_PASSEIO, 'meio_fio')
    # narizes de concreto no fim dos canteiros
    for x0, y0, x1, y1 in PL.NARIZ:
        r = min(abs(X(x1) - X(x0)), abs(Y(y0) - Y(y1))) * 0.49
        g.caixa_red(X(x0), X(x1), Y(y1), Y(y0), 0, Z_PASSEIO, r, 'meio_fio', topo='concreto')
    chao_vagas(g)
    # carga e descarga, patios tecnicos, carro eletrico
    for r in PL.LAJE_TECNICA + PL.LAJE_CISTERNA:
        g.caixa(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), 0, 0.06, 'concreto')
    for x0, y0, x1, y1 in PL.CARGA:
        g.tapete(X(x0) + 0.25, X(x1) - 0.25, Y(y1) + 0.2, Y(y0) - 0.2, 0.07, 'marcas', MARCAS['carga'])
        linha_v(g, X(x0), Y(y0), Y(y1), z=0.07); linha_v(g, X(x1), Y(y0), Y(y1), z=0.07)
        linha_h(g, x0, x1, Y(y0), z=0.07)
    x0, y0, x1, y1 = PL.CHARGE
    g.tapete(X(x0), X(x1), Y(y1), Y(y0), Z_LINHA, 'marcas', MARCAS['charge'])



def _trechos(lin, ini):
    d = np.diff(np.concatenate([[0], lin.astype(np.int8), [0]]))
    return [(ini + a, ini + b) for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0])]


def jardim_torre(g, cx_px):
    """Garden: muro externo em bloco, divisorias entre quintais, passeio em volta da torre."""
    mx, my = PL.MURO_GARDEN
    x0, x1 = X(cx_px - mx), X(cx_px + mx)
    y0, y1 = Y(PL.TORRE_Y + my), Y(PL.TORRE_Y - my)
    cx, cy = X(cx_px), Y(PL.TORRE_Y)
    E, H_M = 0.14, 1.8
    M_ = 'muro_bloco'
    def muro(a, b, c, d):
        g.caixa(a, b, c, d, 0, H_M, M_, topo='pingadeira')
    muro(x0, x1, y0, y0 + E)
    muro(x0, x1, y1 - E, y1)
    muro(x0, x0 + E, y0, y1)
    # lado da entrada (+x) aberto no meio
    ab0, ab1 = Y(PL.TORRE_Y + 108), Y(PL.TORRE_Y - 108)
    muro(x1 - E, x1, y0, ab0)
    muro(x1 - E, x1, ab1, y1)
    # divisorias dos quintais
    for dy in (-10.0, 10.0):
        muro(x0, cx - 7.0, cy + dy - E / 2, cy + dy + E / 2)
    muro(x0, cx - 7.0, cy - E / 2, cy + E / 2)
    for dy0, dy1 in ((19.5, 20.9), (-20.9, -19.5)):
        muro(cx - E / 2, cx + E / 2, cy + dy0, cy + dy1)
    # passeio cinza em volta da torre (quintais continuam grama)
    for rect in ((cx - 6.6, cx + 6.6, cy + 10.5, cy + 19.9), (cx - 6.6, cx + 6.6, cy - 19.9, cy - 10.5),
                 (cx - 8.0, cx + 8.55, cy - 10.5, cy + 10.5)):
        g.caixa(rect[0], rect[1], rect[2], rect[3], 0, 0.12, 'paver', lados='meio_fio')
    # hall aberto ate o passeio
    g.caixa(cx + 8.0, x1, cy - 1.4, cy + 1.4, 0, 0.12, 'concreto', lados='meio_fio')


def muros_perimetro(g):
    """Muro de bloco em volta do terreno e gradil escuro na frente do lazer."""
    H_M, E = 2.6, 0.16
    pts = [(355, 1360), (330, 1310), (300, 1265), (260, 1205), (200, 1150), (110, 1090), (41, 1050), (41, 398), (1877, 398), (1877, 642), (GX_FIM, 642)]
    for a, b in zip(pts[:-1], pts[1:]):
        _muro_seg(g, (X(a[0]), Y(a[1])), (X(b[0]), Y(b[1])), H_M, E)
    _muro_seg(g, (X(355), Y(1360)), (X(2323), Y(1360)), H_M, E)
    _muro_seg(g, (X(2323), Y(1360)), (X(2323), Y(1328)), H_M, E)


GX_FIM = 2272


def _muro_seg(g, a, b, h, e, mat='muro_bloco'):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -e / 2, e / 2, 0, h, mat, topo='pingadeira', sem='ol')
        # pilaretes a cada 3 m
        k = 0.0
        while k <= L:
            g.caixa(k - 0.1, k + 0.1, -e / 2 - 0.03, e / 2 + 0.03, 0, h + 0.03, mat, topo='pingadeira')
            k += 3.2


def cisternas_e_bombas(g):
    for cx, cy in PL.CISTERNAS:
        g.cil(X(cx), Y(cy), 1.75, 0.06, 2.6, 'cisterna', seg=24)
        g.elipsoide(X(cx), Y(cy), 2.6, 1.75, 1.75, 0.55, 'cisterna', seg=24, aneis=4, zmin=0.0)
    cx, cy = PL.CISTERNA_SE
    g.cil(X(cx), Y(cy), 1.5, 0.06, 2.4, 'cisterna', seg=24)
    g.elipsoide(X(cx), Y(cy), 2.4, 1.5, 1.5, 0.5, 'cisterna', seg=24, aneis=4, zmin=0.0)
    for r in (PL.BOMBAS_NO, PL.BOMBAS_SE, PL.LIXO):
        x0, y0, x1, y1 = X(r[0]), Y(r[3]), X(r[2]), Y(r[1])
        g.caixa(x0, x1, y0, y1, 0.06, 2.5, 'parede_externa', topo='telha')
        g.caixa(x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, 2.5, 2.72, 'pingadeira', topo='telha')
        g.painel(x0 + 0.5, y0 - 0.01, x0 + 1.5, y0 - 0.01, 0.1, 2.2, 'porta_servico', (0, 0, 1, 1))
