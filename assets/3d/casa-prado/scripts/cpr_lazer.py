# cpr_lazer.py -- lazer e apoio do Casa Prado em volumes (etapa 1): deck de madeira com a piscina adulto
# 18,78 x 3,78, a infantil 4,28 x 2,28, deck molhado e ofuro (FAQ), casa de maquinas, espaco gourmet com o apoio dos
# funcionarios e a varanda com pergolado, playground, miniquadra de areia com alambrado, praca de chegada, guarita,
# delivery, abrigo de lixo, pet place, o grande pergolado metalico do acesso e as passarelas cobertas ate a torre e a
# garagem. Sem moveis (etapa 2). Medidas: cpr_planta.py (px). Executado por cpr_modelo.py.

Z_DECK = 0.25          # deck da piscina acima do passeio
H_EDIF = 3.0
H_PASSARELA = 2.85
H_PERGOLA_PORTARIA = 5.2


def materiais_lazer():
    mat('deck_madeira', '#b98a5e', 0.75, img='madeira_piso.jpg', tint=True, img_mean=0.6, uv=(2.0, 2.0))
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#d8d3c6', 0.6)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_azul', '#3d7fc4', 0.85, **E_)
    mat('ep_azul_claro', '#8fc0e6', 0.85, **E_)
    mat('ep_cinza', '#9aa1a8', 0.85, **E_)
    mat('areia', '#e2cfaa', 0.98, img='concreto.jpg', tint=True, uv=2.0)
    mat('alambrado', '#2f5d3a', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('rede', '#f2f2ee', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('ferro_verde', '#2b5e36', 0.55, metal=0.3)
    mat('vidro_cobertura', '#9fb6bf', 0.05, blend=0.45, double=True)
    mat('ripado_madeira', '#8a5f3e', 0.7, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.2, 1.2))
    mat('pergola_escura', '#2b2c2e', 0.6, metal=0.3)
    mat('telhado_laje', '#9a9893', 0.95)
    mat('piso_lazer', '#d8d2c6', 0.5, img='porcelanato.jpg', tint=True, img_mean=0.87, uv=3.0)
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)
    mat('brinquedo_azul', '#2f5fae', 0.5)
    mat('brinquedo_madeira', '#9a6a42', 0.7)
    mat('jardineira', '#3a5f2b', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.2)


def _menos(r, buracos):
    """Retangulo px menos buracos px -> retangulos px (grade de 1 px)."""
    x0, y0, x1, y1 = r
    m = np.ones((y1 - y0, x1 - x0), bool)
    for b in buracos:
        m[max(0, b[1] - y0):max(0, b[3] - y0), max(0, b[0] - x0):max(0, b[2] - x0)] = False
    out, abertos = [], {}
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                out.append((x0 + c[0], y0 + abertos.pop(c), x0 + c[1], y0 + y))
        for c in corr:
            abertos.setdefault(c, y)
    return out


def _cerca(g, x0, x1, y0, y1, h, mat='gradil_preto', passo=2.4, z0=0.0, poste='ferro_escuro', lados='snlo'):
    trechos = {'s': ((x0, y0), (x1, y0)), 'l': ((x1, y0), (x1, y1)), 'n': ((x1, y1), (x0, y1)), 'o': ((x0, y1), (x0, y0))}
    for a, b in (trechos[c] for c in lados):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        g.painel(a[0], a[1], b[0], b[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        g.painel(b[0], b[1], a[0], a[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        n = max(1, round(L / passo))
        for k in range(n + 1):
            t = k / n
            g.cil(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.035, z0, z0 + h + 0.05, poste, seg=6)


def _tanque(g, r, z_agua, fundo=0.04, borda=True):
    x0, x1, y0, y1 = RM(r)
    g.piso(x0, x1, y0, y1, fundo, 'pastilha')
    g.piso(x0, x1, y0, y1, z_agua, 'agua')
    for q in ([(x0, y1, fundo), (x0, y0, fundo), (x0, y0, Z_DECK), (x0, y1, Z_DECK)],
              [(x1, y0, fundo), (x1, y1, fundo), (x1, y1, Z_DECK), (x1, y0, Z_DECK)],
              [(x1, y1, fundo), (x0, y1, fundo), (x0, y1, Z_DECK), (x1, y1, Z_DECK)],
              [(x0, y0, fundo), (x1, y0, fundo), (x1, y0, Z_DECK), (x0, y0, Z_DECK)]):
        g.face(q[::-1], 'pastilha')
    if borda:
        e = 0.22
        g.caixa(x0 - e, x1 + e, y1, y1 + e, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x0, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x1, x1 + e, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')


def _piscinas(g):
    """Deck de madeira com os tanques recortados (fundo de pastilha, agua 6 cm abaixo do deck). O deck molhado e o
    ofuro ficam na borda sul da piscina adulto, como na implantacao e na perspectiva 057."""
    tanques = [PL.PISCINA, PL.PISCINA_INFANTIL, PL.DECK_MOLHADO, PL.OFURO]
    for r in _menos(PL.DECK_PISCINA, tanques):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, Z_DECK, 'deck_madeira', lados='meio_fio')
    _tanque(g, PL.PISCINA, Z_DECK - 0.06)
    _tanque(g, PL.PISCINA_INFANTIL, Z_DECK - 0.06)
    _tanque(g, PL.DECK_MOLHADO, Z_DECK - 0.04, fundo=Z_DECK - 0.22, borda=False)
    _tanque(g, PL.OFURO, Z_DECK - 0.06, borda=True)
    # casa de maquinas da piscina (caixa branca na implantacao)
    x0, x1, y0, y1 = RM(PL.CASA_MAQ)
    g.caixa(x0, x1, y0, y1, 0, 2.4, 'parede_externa', topo='telhado_laje')


def _edificio(g, r_px, h=H_EDIF, m='parede_externa', vidros=('s',), beiral=0.35):
    """Volume do lazer com laje plana e beiral; faces com vidro do piso a 2,4 m (pano a cada 3 m)."""
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0, h, m, topo='telhado_laje')
    g.caixa(x0 - beiral, x1 + beiral, y0 - beiral, y1 + beiral, h, h + 0.18, 'laje_borda', topo='telhado_laje', fundo='forro', sem_fundo=False)
    for lado in vidros:
        if lado in 'sn':
            yy = y0 - 0.012 if lado == 's' else y1 + 0.012
            a, b = (x0, x1) if lado == 's' else (x1, x0)
        else:
            xx = x1 + 0.012 if lado == 'l' else x0 - 0.012
            a, b = (y0, y1) if lado == 'l' else (y1, y0)
        L = abs(b - a)
        n = max(1, int(L / 3.0))
        for k in range(n):
            u0 = a + (b - a) * (k + 0.08) / n
            u1 = a + (b - a) * (k + 0.92) / n
            if lado in 'sn':
                g.painel(u0, yy, u1, yy, 0.1, 2.4, 'vidro_lazer', (0, 0, 1, 1))
            else:
                g.painel(xx, u0, xx, u1, 0.1, 2.4, 'vidro_lazer', (0, 0, 1, 1))


def _pergolado(g, r_px, h, passo=0.45, ao_longo_x=True, m='pergola_escura', pilares=True, vidro=False):
    """Pergolado de vigas: pilares nos cantos (e a cada ~4 m), vigas de borda e ripas paralelas."""
    x0, x1, y0, y1 = RM(r_px)
    if pilares:
        nx = max(1, round((x1 - x0) / 4.0)); ny = max(1, round((y1 - y0) / 4.0))
        for i in range(nx + 1):
            for j in (0, ny):
                xx, yy = x0 + 0.1 + (x1 - x0 - 0.2) * i / nx, y0 + 0.1 + (y1 - y0 - 0.2) * j / max(1, ny)
                g.caixa(xx - 0.07, xx + 0.07, yy - 0.07, yy + 0.07, 0.05, h, m)
        for j in range(1, ny):
            for xx in (x0 + 0.1, x1 - 0.1):
                yy = y0 + 0.1 + (y1 - y0 - 0.2) * j / ny
                g.caixa(xx - 0.07, xx + 0.07, yy - 0.07, yy + 0.07, 0.05, h, m)
    e = 0.12
    g.caixa(x0, x1, y0, y0 + e, h, h + 0.22, m)
    g.caixa(x0, x1, y1 - e, y1, h, h + 0.22, m)
    g.caixa(x0, x0 + e, y0, y1, h, h + 0.22, m)
    g.caixa(x1 - e, x1, y0, y1, h, h + 0.22, m)
    if vidro:
        g.piso(x0, x1, y0, y1, h + 0.24, 'vidro_cobertura')
        g.face([(x0, y1, h + 0.235), (x1, y1, h + 0.235), (x1, y0, h + 0.235), (x0, y0, h + 0.235)], 'vidro_cobertura')
    if ao_longo_x:
        yy = y0 + passo
        while yy < y1 - 0.05:
            g.caixa(x0, x1, yy - 0.03, yy + 0.03, h + 0.04, h + 0.22, m); yy += passo
    else:
        xx = x0 + passo
        while xx < x1 - 0.05:
            g.caixa(xx - 0.03, xx + 0.03, y0, y1, h + 0.04, h + 0.22, m); xx += passo


def _guarita(g):
    """Guarita (perspectiva 022): volume revestido de ripado de madeira com o vidro voltado para o acesso, laje com
    beiral e o grande pergolado metalico escuro sobre a entrada de veiculos, ate o abrigo de lixo."""
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0, x1, y0, y1, 0, 2.9, 'ripado_madeira', topo='telhado_laje')
    g.face([(x0 - 0.012, y1 - 0.4, 1.0), (x0 - 0.012, y0 + 0.4, 1.0), (x0 - 0.012, y0 + 0.4, 2.4), (x0 - 0.012, y1 - 0.4, 2.4)],
           'vidro_lazer')
    g.face([(x1 - 0.5, y0 - 0.012, 1.0), (x0 + 0.5, y0 - 0.012, 1.0), (x0 + 0.5, y0 - 0.012, 2.4), (x1 - 0.5, y0 - 0.012, 2.4)],
           'vidro_lazer')
    g.caixa(x0 - 0.6, x1 + 0.6, y0 - 0.8, y1 + 0.6, 2.9, 3.15, 'laje_borda', topo='telhado_laje', fundo='forro', sem_fundo=False)
    _pergolado(g, PL.PERGOLA_PORTARIA, H_PERGOLA_PORTARIA, passo=0.9, ao_longo_x=False)


def _apoio(g):
    _guarita(g)
    # delivery (02): pergolado com jardineiras (implantacao: canteiro florido sob a grelha)
    x0, x1, y0, y1 = RM(PL.DELIVERY)
    g.caixa(x0 + 0.3, x1 - 0.3, y0 + 0.3, y1 - 0.3, 0, 0.45, 'meio_fio', topo='jardineira')
    _pergolado(g, PL.DELIVERY, 2.8, passo=0.8)
    # abrigo de lixo
    x0, x1, y0, y1 = RM(PL.LIXO)
    g.caixa(x0, x1, y0, y1, 0, 2.6, 'ripado_madeira', topo='telhado_laje')
    g.caixa(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 2.6, 2.78, 'laje_borda', topo='telhado_laje')
    # pet place: grama cercada (gradil preto, perspectiva 012)
    x0, x1, y0, y1 = RM(PL.PET)
    g.piso(x0, x1, y0, y1, 0.07, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.2, 'gradil_preto', 2.0)
    # passarelas cobertas: pilares e vigas escuras com cobertura de vidro (perspectivas 058 e 051)
    for r in PL.PASSARELAS:
        _pergolado(g, r, H_PASSARELA, passo=1.5, ao_longo_x=(r[2] - r[0]) < (r[3] - r[1]), vidro=True)
    for x0p, y0p, x1p, y1p in PL.SEBES:
        mx0, mx1, my0, my1 = X(x0p), X(x1p), Y(y1p), Y(y0p)
        g.caixa(mx0, mx1, my0, my1, 0.0, 0.9, 'sebe')


def lazer(g):
    _piscinas(g)
    # espaco gourmet e apoio dos funcionarios (fechado; varanda com pergolado a oeste)
    _edificio(g, PL.GOURMET, vidros=('s', 'o'))
    x0, x1, y0, y1 = RM(PL.GOURMET_DECK)
    g.caixa(x0, x1, y0, y1, 0, 0.12, 'deck_madeira', lados='meio_fio')
    _pergolado(g, PL.GOURMET_DECK, 2.9, passo=0.35, ao_longo_x=True)
    # playground: piso emborrachado azul com os desenhos e um brinquedo com escorregador (perspectiva 016)
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, 0.08, 'ep_azul_claro', lados='meio_fio')
    for cx, cy, r in ((0.3, 0.35, 0.22), (0.7, 0.6, 0.25), (0.45, 0.78, 0.18)):
        xc, yc = x0 + (x1 - x0) * cx, y0 + (y1 - y0) * cy
        g.cil(xc, yc, r * (x1 - x0) * 0.5, 0.08, 0.085, 'ep_azul', seg=20)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    for dx, dy in ((-1.0, -0.8), (1.0, 0.8)):
        tx_, ty_ = xm + dx * 1.6, ym + dy * 1.4
        for sx, sy in ((-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.6, 0.6)):
            g.caixa(tx_ + sx - 0.05, tx_ + sx + 0.05, ty_ + sy - 0.05, ty_ + sy + 0.05, 0.08, 2.6, 'brinquedo_madeira')
        g.caixa(tx_ - 0.7, tx_ + 0.7, ty_ - 0.7, ty_ + 0.7, 1.2, 1.3, 'brinquedo_madeira')
        g.prisma([(tx_ - 0.8, ty_ - 0.8), (tx_ + 0.8, ty_ - 0.8), (tx_ + 0.8, ty_ + 0.8), (tx_ - 0.8, ty_ + 0.8)], 2.6, 2.7, 'brinquedo_azul')
        g.prisma([(tx_ - 0.8, ty_ - 0.8), (tx_ + 0.8, ty_ - 0.8), (tx_, ty_)], 2.7, 3.1, 'brinquedo_azul')
    g.tubo([(xm - 1.6, ym - 0.1, 1.25), (xm, ym, 1.0), (xm + 1.6, ym + 0.1, 1.25)], 0.32, 'brinquedo_azul', seg=10)
    g.tubo([(xm - 2.3, ym - 0.8, 1.25), (xm - 3.4, ym - 0.9, 0.4)], 0.3, 'brinquedo_azul', seg=8)
    # miniquadra de areia com alambrado e rede (perspectiva 018)
    x0, x1, y0, y1 = RM(PL.QUADRA)
    g.caixa(x0, x1, y0, y1, 0, 0.10, 'areia', lados='meio_fio')
    for xx in (x0 + 0.3, x1 - 0.3):
        g.piso(xx - 0.04, xx + 0.04, y0 + 0.3, y1 - 0.3, 0.105, 'pcd_azul')
    for yy in (y0 + 0.3, y1 - 0.3, (y0 + y1) / 2):
        g.piso(x0 + 0.3, x1 - 0.3, yy - 0.04, yy + 0.04, 0.105, 'pcd_azul')
    _cerca(g, x0, x1, y0, y1, 3.2, 'alambrado', 2.5, poste='ferro_verde')
    ym = (y0 + y1) / 2
    g.painel(x0, ym, x1, ym, 1.4, 2.4, 'rede', (0, 0, (x1 - x0) / 0.25, 4))
    g.painel(x1, ym, x0, ym, 1.4, 2.4, 'rede', (0, 0, (x1 - x0) / 0.25, 4))
    # praca de chegada: deck de madeira (perspectiva 017)
    x0, x1, y0, y1 = RM(PL.PRACA_CHEGADA)
    g.caixa(x0, x1, y0, y1, 0, 0.12, 'deck_madeira', lados='meio_fio')
    _apoio(g)
