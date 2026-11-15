# jbo_patio.py -- chao do condominio: desenho lido na implantacao (tex/chao.json, de jbo_chao.py: grama, asfalto,
# paver, concreto e paver laranja em retangulos de 11 cm), guias da rua interna, vagas (piso drenante com trilhos de
# concreto, asfalto com faixas, motos, PcD com o simbolo e as zebras entre elas), faixas de pedestre, muros das divisas,
# gradil e portoes da entrada e o edificio-garagem (terreo coberto + cobertura com vagas e rampa).
# Executado por jbo_modelo.py.
import math

Z_CHAO = {'grama': 0.0, 'asfalto': 0.02, 'paver': 0.05, 'concreto': 0.06, 'paver_laranja': 0.055}
Z_VAGA, Z_LINHA = 0.03, 0.045
H_GAR = 3.0                      # piso da cobertura do edificio-garagem
H_PARAPEITO = 1.1


def materiais_patio():
    mat('grama', '#ffffff', 0.97, img='grama2.jpg', uv=6.0)
    mat('grama_garden', '#e9f0dc', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=4.0)
    mat('entorno', (0.62, 0.62, 0.50), 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=14.0)
    mat('asfalto', '#ffffff', 0.92, img='asfalto2.jpg', uv=8.0)
    mat('paver', '#a7a5a2', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('paver_laranja', '#c8805a', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('concreto', '#d3d0ca', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('piso_garagem', '#9c9ea1', 0.85, img='concreto.jpg', tint=True, uv=5.0)
    mat('vaga_drenante', '#ffffff', 0.92, img='drenante.jpg')
    mat('meio_fio', '#c8c5bc', 0.9)
    mat('faixa', '#f0f0ea', 0.75)
    mat('faixa_amarela', '#e3b62c', 0.75)
    mat('pcd_azul', '#2f63b0', 0.8)
    mat('marcas', '#ffffff', 0.8, img='piso_marcas.png', recorte=True)
    mat('sombra_contato', '#ffffff', 1.0, img='piso_marcas.png', blend_img=True)
    R = dict(img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('muro_bloco', '#c9c7c2', 0.93, img='bloco.jpg', tint=True, img_mean=0.8, uv=(1.6, 1.6))
    mat('muro_liso', '#d6d2ca', 0.93, **R)
    mat('muro_base', '#8d8a85', 0.93, **R)
    mat('parede_externa', '#d9d8d4', 0.93, **R)
    mat('garagem_parede', '#c5c4c0', 0.93, **R)
    mat('garagem_viga', '#d9d8d4', 0.93, **R)
    mat('telha_metalica', '#c7c9cb', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.9, 0.9), metal=0.2)
    mat('estrutura_escura', '#2c2e31', 0.55, metal=0.35)
    mat('rampa', '#8f9193', 0.85, img='concreto.jpg', tint=True, uv=3.0)
    mat('vao_escuro', '#2a2c2f', 0.95)
    mat('sebe', '#5f8a45', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.5)
    mat('gradil_branco', '#e8e8e6', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))


def P(p):
    return (X(p[0]), Y(p[1]))


def _quad_cima(g, cs, mat, uvs=None):
    """Quad horizontal garantindo a normal para cima (inverte a ordem e os uvs se preciso)."""
    if _normal(cs)[2] < 0:
        cs = cs[::-1]
        if uvs is not None:
            uvs = uvs[::-1]
    g.face(cs, mat, uvs=uvs)


def _frame(a, b, d):
    """Referencial local de uma fileira: origem em a, x de a para b; devolve (A, giro, L, prof com sinal)."""
    A, Bp, D = P(a), P(b), P(d)
    ux, uy = Bp[0] - A[0], Bp[1] - A[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    dx, dy = D[0] - A[0], D[1] - A[1]
    prof = -uy * dx + ux * dy
    return A, math.degrees(math.atan2(uy, ux)), L, prof


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def chao(g):
    """Desenho do chao lido por cor na implantacao (jbo_chao.py -> tex/chao.json)."""
    for nome, rs in CHAO['classes'].items():
        z = Z_CHAO[nome]
        for x0, y0, x1, y1 in rs:
            g.piso(X(x0), X(x1), Y(y1), Y(y0), z, nome)
    # faixas de pedestre
    for x0, y0, x1, y1, ori in PL.ZEBRAS:
        mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
        if ori == 'h':          # listras ao longo de x, empilhadas em y
            yy = my0 + 0.2
            while yy + 0.4 <= my1:
                g.piso(mx0, mx1, yy, yy + 0.4, Z_LINHA, 'faixa'); yy += 0.8
        else:
            xx = mx0 + 0.2
            while xx + 0.4 <= mx1:
                g.piso(xx, xx + 0.4, my0, my1, Z_LINHA, 'faixa'); xx += 0.8
    # faixa diagonal da avenida: listras de 0,4 m perpendiculares ao eixo
    (ax, ay), (bx, by), lp = PL.ZEBRA_AVENIDA
    A, Bp = P((ax, ay)), P((bx, by))
    L = math.hypot(Bp[0] - A[0], Bp[1] - A[1])
    ux, uy = (Bp[0] - A[0]) / L, (Bp[1] - A[1]) / L
    w = lp * S_PX / 2
    t = 0.2
    while t + 0.4 <= L:
        p0, p1 = (A[0] + ux * t, A[1] + uy * t), (A[0] + ux * (t + 0.4), A[1] + uy * (t + 0.4))
        _quad_cima(g, [(p0[0] - uy * w, p0[1] + ux * w, Z_LINHA), (p1[0] - uy * w, p1[1] + ux * w, Z_LINHA),
                       (p1[0] + uy * w, p1[1] - ux * w, Z_LINHA), (p0[0] + uy * w, p0[1] - ux * w, Z_LINHA)], 'faixa')
        t += 0.8
    # guias da rua interna (meio-fio de 12 cm nas duas bordas, da garagem ate a curva da entrada)
    for yy, s in ((PL.RUA_Y[0], 1), (PL.RUA_Y[1], -1)):
        y = Y(yy)
        g.caixa(X(1913), X(12440), min(y, y + s * 0.15), max(y, y + s * 0.15), 0.0, 0.12, 'meio_fio')


def _linhas(g, L, s, pr, n, z, mat='faixa', fundo=True):
    """Divisorias de uma fileira (referencial local): n+1 linhas e a linha do fundo."""
    for k in range(n + 1):
        xx = L * k / n
        g.piso(xx - 0.05, xx + 0.05, min(0, s * pr), max(0, s * pr), z, mat)
    if fundo:
        y = s * (pr - 0.05)
        g.piso(0, L, min(y - 0.05, y + 0.05), max(y - 0.05, y + 0.05), z, mat)


def _vaga_pcd(g, L, s, pr, z):
    """Simbolo PcD azul no meio da vaga."""
    r_ = MARCAS['pcd']
    xc, yc = L / 2, s * pr * 0.55
    g.piso(xc - 0.75, xc + 0.75, yc - 0.75, yc + 0.75, z, 'pcd_azul')
    g.tapete(xc - 0.7, xc + 0.7, yc - 0.7, yc + 0.7, z + 0.004, 'marcas', r_, gira=(s < 0))


def vagas(g):
    """Fileiras de vagas. Drenante: cada vaga com a textura dos trilhos de concreto e grama (uma repeticao por vaga);
    asfalto e cobertura da garagem so com as faixas brancas; motos com divisorias a cada ~1 m."""
    for cs, n, tipo in PL.VAGAS:
        a, b, c, d = cs
        A, giro, L, prof = _frame(a, b, d)
        s = 1 if prof > 0 else -1
        pr = abs(prof)
        with g.em(A[0], A[1], 0.0, giro):
            if tipo == 'dren':
                for k in range(n):
                    x0, x1 = L * k / n, L * (k + 1) / n
                    _quad_cima(g, [(x0, 0, Z_VAGA), (x1, 0, Z_VAGA), (x1, s * pr, Z_VAGA), (x0, s * pr, Z_VAGA)],
                               'vaga_drenante', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
                # meio-fio baixo no fundo (separa da grama/passeio)
                g.caixa(0, L, min(s * pr, s * (pr - 0.1)), max(s * pr, s * (pr - 0.1)), 0.0, 0.08, 'meio_fio')
            elif tipo == 'asf':
                _quad_cima(g, [(0, 0, Z_CHAO['asfalto']), (L, 0, Z_CHAO['asfalto']), (L, s * pr, Z_CHAO['asfalto']),
                               (0, s * pr, Z_CHAO['asfalto'])], 'asfalto')
                _linhas(g, L, s, pr, n, Z_LINHA)
            elif tipo == 'moto':
                _quad_cima(g, [(0, 0, Z_CHAO['asfalto']), (L, 0, Z_CHAO['asfalto']), (L, s * pr, Z_CHAO['asfalto']),
                               (0, s * pr, Z_CHAO['asfalto'])], 'asfalto')
                _linhas(g, L, s, pr, n, Z_LINHA, fundo=True)
            else:   # deck: cobertura da garagem
                _linhas(g, L, s, pr, n, H_GAR + 0.006, fundo=False)
    # PcD e vagas no asfalto junto as quadras, com as faixas zebradas amarelas entre elas
    for x0, x1, yf, yb, pcd in PL.VAGAS_PCD:
        a, b, d = (x0, yf), (x1, yf), (x0, yb)
        A, giro, L, prof = _frame(a, b, d)
        s = 1 if prof > 0 else -1
        pr = abs(prof)
        with g.em(A[0], A[1], 0.0, giro):
            _quad_cima(g, [(0, 0, Z_CHAO['asfalto']), (L, 0, Z_CHAO['asfalto']), (L, s * pr, Z_CHAO['asfalto']),
                           (0, s * pr, Z_CHAO['asfalto'])], 'asfalto')
            _linhas(g, L, s, pr, 1, Z_LINHA)
            if pcd:
                _vaga_pcd(g, L, s, pr, Z_LINHA - 0.004)
    for x0, x1 in PL.ZEBRAS_PCD:
        for yf, yb in ((1545, 1730), (1272, 1095)):
            mx0, mx1 = X(x0), X(x1)
            my0, my1 = sorted((Y(yf), Y(yb)))
            g.piso(mx0, mx1, my0, my1, Z_CHAO['asfalto'], 'asfalto')
            yy = my0 + 0.15
            while yy + 0.18 < my1:
                g.face([(mx0 + 0.08, yy, Z_LINHA), (mx1 - 0.08, yy + 0.35, Z_LINHA), (mx1 - 0.08, yy + 0.53, Z_LINHA),
                        (mx0 + 0.08, yy + 0.18, Z_LINHA)], 'faixa_amarela')
                yy += 0.5
            for xx in (mx0, mx1):
                g.piso(xx - 0.05, xx + 0.05, my0, my1, Z_LINHA, 'faixa_amarela')


def _muro_seg(g, a, b, h, e, mat='muro_liso', pilar=3.0, topo='pingadeira'):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -e / 2, e / 2, 0, h, mat, topo=topo, sem='ol')
        k = 0.0
        while k <= L:
            g.caixa(k - 0.12, k + 0.12, -e / 2 - 0.03, e / 2 + 0.03, 0, h + 0.04, mat, topo=topo)
            k += pilar


def _gradil(g, a, b, hm=0.5, hg=1.7, mat='gradil_preto'):
    """Mureta com gradil por cima (frente na avenida, perspectiva da portaria)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -0.1, 0.1, 0, hm, 'muro_base', topo='pingadeira')
        g.painel(0, 0.0, L, 0.0, hm, hm + hg, mat, (0, 0, L / 2.0, 1))
        g.painel(L, 0.0, 0, 0.0, hm, hm + hg, mat, (0, 0, L / 2.0, 1))
        g.caixa(0, L, -0.03, 0.03, hm + hg - 0.05, hm + hg, 'ferro_escuro')
        k = 0.0
        while k <= L:
            g.caixa(k - 0.05, k + 0.05, -0.05, 0.05, hm, hm + hg, 'ferro_escuro')
            k += 2.5


def _portao(g, a, b, h=2.2):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.painel(0, 0.0, L, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.painel(L, 0.0, 0, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.caixa(0, L, -0.04, 0.04, h - 0.08, h, 'ferro_escuro')
        for k in (0.0, L):
            g.caixa(k - 0.15, k + 0.15, -0.15, 0.15, 0, h + 0.15, 'muro_base', topo='pingadeira')


def muros_perimetro(g):
    """Muros de bloco nas divisas (fotomontagem: muro alto de bloco aparente), gradil na frente da avenida e os
    portoes de entrada e saida na linha da guarita."""
    # muro de cima (divisa norte), do edificio-garagem ate a avenida
    pts = [(PL.X_OESTE, PL.topo(PL.X_OESTE)), (13715, PL.topo(13715))]
    _muro_seg(g, P(pts[0]), P(pts[1]), 2.6, 0.16, 'muro_bloco', pilar=3.2)
    _muro_seg(g, P((PL.X_OESTE, PL.topo(PL.X_OESTE))), P((PL.X_OESTE, PL.Y_BAIXO)), 2.6, 0.16, 'muro_bloco', pilar=3.2)
    _muro_seg(g, P((PL.X_OESTE, PL.Y_BAIXO)), P((13160, PL.Y_BAIXO)), 2.6, 0.16, 'muro_bloco', pilar=3.2)
    # frente: gradil sobre mureta acompanhando a calcada, ate o portao de pedestres junto a guarita
    fr = PL.FRENTE
    for i in range(len(fr) - 1):
        _gradil(g, P(fr[i]), P(fr[i + 1]))
    se = PL.CANTO_SE
    for i in range(len(se) - 1):
        _gradil(g, P(se[i]), P(se[i + 1]))
    a, b = PL.PORTAO
    ym = (a[1] + b[1]) / 2
    _portao(g, P(a), P((a[0], ym - 6)))           # entrada e saida, com a ilha da guarita no meio
    _portao(g, P((a[0], ym + 6)), P(b))
    g.caixa(X(a[0]) - 0.6, X(a[0]) + 0.6, Y(ym + 6), Y(ym - 6), 0.0, 0.15, 'meio_fio', topo='concreto')


# ------------------------------------------------------------------ edificio-garagem
def garagem(g):
    """Edificio-garagem (17): terreo coberto aberto nas laterais (pilares e vigas de concreto) e cobertura com vagas,
    platibanda, a rampa (desce para o norte, ao longo do muro oeste) e o nucleo de escada/elevador com o bike sharing
    e a oficina de bike (18). As vagas da cobertura vem de VAGAS ('deck')."""
    x0, x1, y0, y1 = RM(PL.GARAGEM)
    rx0, rx1, ry0, ry1 = RM(PL.RAMPA_GARAGEM)
    e = 0.30
    # piso do terreo e laje da cobertura (com o furo da rampa)
    g.piso(x0, x1, y0, y1, 0.03, 'piso_garagem')
    for a0, a1, b0, b1 in ((x0, rx1, y0, ry0), (x0, rx1, ry1, y1), (rx1, x1, y0, y1)):
        g.caixa(a0, a1, b0, b1, H_GAR - e, H_GAR, 'piso_garagem', lados='garagem_viga', fundo='concreto', sem_fundo=False,
                sem=('o' if a0 == x0 else '') + ('l' if a1 < x1 - 0.1 else '') + ('s' if b0 > y0 + 0.1 else '') + ('n' if b1 < y1 - 0.1 else ''))
    # platibanda
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        ang = math.degrees(math.atan2(dy, dx))
        with g.em(a[0], a[1], H_GAR, ang):
            g.caixa(0, L, -0.15, 0.0, 0, H_PARAPEITO, 'garagem_parede', topo='pingadeira')
    # pilares do terreo (grade de ~8 m) e o fechamento baixo nas laterais
    nx = max(1, round((x1 - x0) / 8.0)); ny = max(1, round((y1 - y0) / 7.5))
    for i in range(nx + 1):
        for j in range(ny + 1):
            xx = x0 + 0.25 + (x1 - x0 - 0.5) * i / nx
            yy = y0 + 0.25 + (y1 - y0 - 0.5) * j / ny
            if rx0 - 0.3 < xx < rx1 + 0.3 and ry0 - 0.3 < yy < ry1 + 0.3:
                continue
            g.caixa(xx - 0.25, xx + 0.25, yy - 0.25, yy + 0.25, 0.03, H_GAR - e, 'garagem_viga')
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        ang = math.degrees(math.atan2(dy, dx))
        with g.em(a[0], a[1], 0, ang):
            g.caixa(0, L, -0.12, 0.0, 0, 1.1, 'garagem_parede', topo='pingadeira')
    # interior escuro do terreo visto pelas aberturas: forro ja e a laje; sombra no piso pela propria cena
    # rampa: desce da cobertura (ponta sul, onde comecam as vagas da coluna oeste) ate o terreo (ponta norte)
    _quad_cima(g, [(rx0, ry0, H_GAR), (rx1, ry0, H_GAR), (rx1, ry1, 0.03), (rx0, ry1, 0.03)], 'rampa')
    for xx in (rx0, rx1):
        g.face([(xx, ry1, 0.03), (xx, ry0, H_GAR), (xx, ry0, H_GAR + 1.1), (xx, ry1, 1.1)], 'garagem_parede')
        g.face([(xx, ry1, 1.1), (xx, ry0, H_GAR + 1.1), (xx, ry0, H_GAR), (xx, ry1, 0.03)], 'garagem_parede')
    # nucleo: escada e elevador, com o bike sharing e a oficina de bike na cobertura
    nx0, nx1, ny0, ny1 = RM(PL.NUCLEO_GARAGEM)
    g.caixa(nx0, nx1, ny0, ny1, H_GAR, H_GAR + 3.0, 'parede_externa', topo='cobertura')
    g.caixa(nx0 - 0.3, nx1 + 0.3, ny0 - 0.3, ny1 + 0.3, H_GAR + 3.0, H_GAR + 3.18, 'laje_borda', topo='cobertura',
            fundo='forro', sem_fundo=False)
    for k in range(3):
        u0 = nx0 + 0.5 + k * (nx1 - nx0 - 1.0) / 3
        g.face([(u0, ny0 - 0.012, H_GAR + 0.1), (u0 + (nx1 - nx0 - 1.0) / 3 - 0.3, ny0 - 0.012, H_GAR + 0.1),
                (u0 + (nx1 - nx0 - 1.0) / 3 - 0.3, ny0 - 0.012, H_GAR + 2.4), (u0, ny0 - 0.012, H_GAR + 2.4)], 'vidro_lazer')
