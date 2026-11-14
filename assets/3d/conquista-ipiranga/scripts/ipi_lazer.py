# ipi_lazer.py -- lazer e apoio do Conquista Clube Ipiranga: solarium com piscina adulto 15,00 x 5,90 e infantil
# 4,75 x 3,20, vestiarios, fitness externo, playground, varanda gourmet com pergolado e o apoio administrativo, pet
# place, bicicletario, e o apoio (guarita com delivery, casa de bombas, deposito de lixo e os 4 reservatorios).
# Etapa 2: varanda gourmet SEM TETO (paredes cortadas a 3 m, para ver os moveis de cima), pergolado em grade como na
# implantacao, gradil claro em volta do solarium, piso do playground com os circulos coloridos, gradil verde no
# playground e no pet place (perspectivas) e a guarita com a placa do logo oficial e as luzes da marquise.
# Medidas: ipi_planta.py (px). Moveis: ipi_moveis.py (pecas) e ipi_ambientes.py (posicoes). Luzes: ipi_luzes.py.
# Executado por ipi_modelo.py.

Z_DECK = 0.30          # solarium acima do passeio
Z_PISO = 0.12          # piso do playground e do fitness
Z_GOURMET = 0.15       # piso da varanda gourmet
Z_PERGOLADO = 0.17     # deck de madeira sob o pergolado
H_EDIF = 3.0
H_CORTE = 3.0          # paredes da gourmet sem teto


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#d9d3c8', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#cfcabc', 0.6)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_grafite', '#3e4247', 0.85, **E_)
    mat('ep_azul', '#2f6fb8', 0.85, **E_)
    mat('ep_verde', '#4f9a52', 0.85, **E_)
    mat('ep_amarelo', '#e4b42c', 0.85, **E_)
    mat('ep_vermelho', '#c2453a', 0.85, **E_)
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('vidro_lazer', '#4a5d68', 0.06, metal=0.15)
    mat('reboco_grafite', '#55565c', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('pergola_madeira', '#7a5236', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.6, uv=1.5)
    mat('deck_grafite', '#6b6a68', 0.8, img=P_, tint=True, img_mean=0.87, uv=1.2)
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)
    mat('telhado_ripado', '#c9c6bf', 0.8, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.6, 0.6))
    # etapa 2
    mat('gradil_claro', '#e6e5e1', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('gradil_verde', '#2f6b3c', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_claro', '#d9d8d3', 0.5, metal=0.3)
    mat('ferro_verde', '#2b5e36', 0.55, metal=0.3)
    mat('ep_marinho', '#24427a', 0.85, **E_)
    mat('ep_azul_claro', '#4b8fd0', 0.85, **E_)
    mat('piso_gourmet', '#dcd8d0', 0.4, img=P_, tint=True, img_mean=0.87, uv=3.0)      # piso_: aceso a noite
    mat('piso_cinza', '#b9b6af', 0.4, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('deck_madeira', '#8a5a3a', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.2, 1.2))
    mat('int_taupe', '#6f6760', 0.85)          # parede da cozinha gourmet (perspectiva); int_: acesa a noite
    mat('int_branco', '#ece7dd', 0.85)
    mat('parede_corte', '#d9d6cf', 0.9)
    mat('atlas', '#ffffff', 0.5, img='atlas_lazer.jpg')
    mat('tela', '#ffffff', 0.25, img='atlas_lazer.jpg')
    mat('placa_conquista', '#ffffff', 0.45, img='placa_conquista.jpg')    # placa da guarita (logo oficial)
    mat('janela_guarita', '#ffffff', 0.12, img='vidro_guarita.jpg', emit_img='vidro_guarita_luz.jpg')   # acesa a noite


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


def _piscinas(g):
    """Solarium em deck com os tanques recortados: fundo de pastilha, paredes internas e agua 6 cm abaixo."""
    tanques = [PL.PISCINA, PL.PISCINA_INFANTIL]
    for r in _menos(PL.SOLARIUM, tanques):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, Z_DECK, 'deck', lados='meio_fio')
    for r in tanques:
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, 0.04, 'pastilha')
        g.piso(x0, x1, y0, y1, Z_DECK - 0.06, 'agua')
        for q in ([(x0, y1, 0.04), (x0, y0, 0.04), (x0, y0, Z_DECK), (x0, y1, Z_DECK)],
                  [(x1, y0, 0.04), (x1, y1, 0.04), (x1, y1, Z_DECK), (x1, y0, Z_DECK)],
                  [(x1, y1, 0.04), (x0, y1, 0.04), (x0, y1, Z_DECK), (x1, y1, Z_DECK)],
                  [(x0, y0, 0.04), (x1, y0, 0.04), (x1, y0, Z_DECK), (x0, y0, Z_DECK)]):
            g.face(q[::-1], 'pastilha')
        e = 0.25
        g.caixa(x0 - e, x1 + e, y1, y1 + e, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x0, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x1, x1 + e, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
    # gradil claro em volta do solarium (perspectiva 02); a entrada fica no lado oeste, junto do vestiario
    x0, x1, y0, y1 = RM(PL.SOLARIUM)
    _cerca(g, x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, 1.2, 'gradil_claro', 2.0, Z_DECK, 'ferro_claro', 'snl')


def _edificio(g, r_px, h=H_EDIF, mat_='parede_externa', vidro=True, beiral=0.3, telhado='telhado_ripado'):
    """Volume fechado com cobertura de telha metalica (ripado claro, como na implantacao) e beiral."""
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0, h, mat_, topo=telhado)
    g.caixa(x0 - beiral, x1 + beiral, y0 - beiral, y1 + beiral, h, h + 0.16, 'laje_borda', topo=telhado, fundo='forro')
    if vidro:
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y1), (x0, y1))):
            L = abs(b[0] - a[0])
            n = max(1, int(L / 3.0))
            for k in range(n):
                u0 = a[0] + (b[0] - a[0]) * (k + 0.15) / n
                u1 = a[0] + (b[0] - a[0]) * (k + 0.85) / n
                yy = a[1] + (-0.012 if a[1] == y0 else 0.012)
                g.painel(u0, yy, u1, yy, 0.3, 2.4, 'vidro_lazer', (0, 0, 1, 1))


def _disco(cx, cy, r, ret, n=28):
    """Circulo (m) recortado no retangulo ret = (x0, x1, y0, y1): pontos presos ao retangulo."""
    x0, x1, y0, y1 = ret
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        p = (min(max(cx + r * math.cos(a), x0), x1), min(max(cy + r * math.sin(a), y0), y1))
        if not pts or abs(p[0] - pts[-1][0]) + abs(p[1] - pts[-1][1]) > 1e-4:
            pts.append(p)
    return pts


def _playground(g):
    """Piso emborrachado azul-marinho com os circulos verdes e azuis da implantacao, cerca verde (perspectiva 04)."""
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'ep_marinho', lados='meio_fio')
    ret = (x0, x1, y0, y1)
    for px, py, r, mt, dz in ((1875, 1592, 45, 'ep_verde', 0.004), (1912, 1732, 42, 'ep_verde', 0.004),
                              (1966, 1576, 42, 'ep_azul_claro', 0.004), (1962, 1572, 20, 'ep_verde', 0.008),
                              (1868, 1705, 34, 'ep_azul_claro', 0.004)):
        pts = _disco(X(px), Y(py), r * S_PX, ret)
        if len(pts) >= 3:
            g.poligono(pts, Z_PISO + dz, mt)
    _cerca(g, x0, x1, y0, y1, 1.2, 'gradil_verde', 2.4, Z_PISO, 'ferro_verde')


def _fitness(g):
    """Piso de concreto desempenado (perspectiva 03); os aparelhos ficam em ipi_ambientes.py."""
    x0, x1, y0, y1 = RM(PL.FITNESS)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'concreto', lados='meio_fio')


def _parede_corte(g, a, b, z0, z1, e=0.15, mt='parede_externa', topo='parede_corte'):
    """Parede reta de a a b (m) com espessura e, cortada no topo (ambiente sem teto)."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -e / 2, e / 2, z0, z1, mt, topo=topo)


def _gourmet(g):
    """Varanda gourmet SEM TETO: piso claro, trechos de parede cortados a 3 m, a parede da cozinha em taupe
    (perspectiva 06) e o pergolado em grade a oeste, sobre deck de madeira (implantacao). O apoio fica a leste."""
    x0, x1, y0, y1 = RM(PL.GOURMET)
    g.caixa(x0, x1, y0, y1, 0, Z_GOURMET, 'piso_gourmet', lados='meio_fio')
    zt = Z_GOURMET + H_CORTE
    for (pa, pb) in (((1610, 1537), (1636, 1537)), ((1660, 1537), (1690, 1537)), ((1610, 1713), (1646, 1713))):
        _parede_corte(g, (X(pa[0]), Y(pa[1])), (X(pb[0]), Y(pb[1])), Z_GOURMET, zt)
    for px, py in ((1547, 1537), (1547, 1713)):
        g.caixa(X(px) - 0.15, X(px) + 0.15, Y(py) - 0.15, Y(py) + 0.15, Z_GOURMET, zt, 'parede_externa', topo='parede_corte')
    # parede da cozinha: a face oeste do apoio pintada de taupe ate o corte
    g.face([(x1 - 0.01, y0, Z_GOURMET), (x1 - 0.01, y1, Z_GOURMET), (x1 - 0.01, y1, zt), (x1 - 0.01, y0, zt)][::-1], 'int_taupe')
    # pergolado: deck de madeira e grade de vigas nos dois sentidos, pilares nos cantos e no meio
    px0, px1, py0, py1 = RM(PL.PERGOLADO)
    g.caixa(px0, px1, py0, py1, 0, Z_PERGOLADO, 'deck_madeira', lados='meio_fio')
    zp = Z_PERGOLADO + 2.6
    passo = 1.1
    nx = max(1, round((px1 - px0) / passo))
    ny = max(1, round((py1 - py0) / passo))
    for k in range(nx + 1):
        xx = px0 + 0.1 + (px1 - px0 - 0.2) * k / nx
        g.caixa(xx - 0.05, xx + 0.05, py0 + 0.05, py1 - 0.05, zp, zp + 0.16, 'pergola_madeira')
    for k in range(ny + 1):
        yy = py0 + 0.1 + (py1 - py0 - 0.2) * k / ny
        g.caixa(px0 + 0.05, px1 - 0.05, yy - 0.04, yy + 0.04, zp + 0.16, zp + 0.28, 'pergola_madeira')
    for xx in (px0 + 0.15, px1 - 0.15):
        for yy in (py0 + 0.15, (py0 + py1) / 2, py1 - 0.15):
            g.caixa(xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, Z_PERGOLADO, zp, 'pergola_madeira')
    _edificio(g, PL.APOIO, h=3.0)


def _pet(g):
    x0, x1, y0, y1 = RM(PL.PET)
    g.caixa(x0, x1, y0, y1, 0, 0.05, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.2, 'gradil_verde', 2.4, 0.05, 'ferro_verde')


def _bicicletario(g):
    """Piso do bicicletario ja vem da praca (ipi_patio); os paraciclos de inox ficam em ipi_ambientes.py."""
    return


Z_PASSEIO_LZ = 0.06


def _guarita(g):
    """Guarita com delivery (perspectiva 01-guarita): caixa taupe, janela de 3 folhas voltada para o acesso (leste),
    a placa branca com o logo oficial do Conquista Clube Ipiranga logo abaixo, laje plana com beiral largo e as
    luzes embutidas no beiral (acesas a noite, com poca de luz no acesso)."""
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0, x1, y0, y1, 0, 2.8, 'parede_taupe')
    # janela de 3 folhas na face leste
    wa, wb = y0 + 1.3, y0 + 4.4
    g.caixa(x1 - 0.02, x1 + 0.02, wa, wb, 1.05, 2.3, 'parede_taupe')
    g.face([(x1 + 0.021, wa, 1.05), (x1 + 0.021, wb, 1.05), (x1 + 0.021, wb, 2.3), (x1 + 0.021, wa, 2.3)], 'janela_guarita',
           uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=[(1, 0, 0)] * 4, cor=1.0)
    for k in range(4):
        yy = wa + (wb - wa) * k / 3
        g.caixa(x1 - 0.01, x1 + 0.05, yy - 0.03, yy + 0.03, 1.02, 2.33, 'ferro_escuro')
    for zz in (1.02, 2.3):
        g.caixa(x1 - 0.01, x1 + 0.05, wa - 0.03, wb + 0.03, zz - 0.02, zz + 0.03, 'ferro_escuro')
    g.caixa(x1 - 0.01, x1 + 0.09, wa - 0.08, wb + 0.08, 0.96, 1.0, 'laje_borda')
    # placa com o logo (1,20 x 0,52 m) sob a janela, como na perspectiva
    yc = (wa + wb) / 2 + 0.5
    g.caixa(x1, x1 + 0.025, yc - 0.6, yc + 0.6, 0.32, 0.84, 'ferro_claro')
    g.face([(x1 + 0.026, yc - 0.6, 0.32), (x1 + 0.026, yc + 0.6, 0.32), (x1 + 0.026, yc + 0.6, 0.84), (x1 + 0.026, yc - 0.6, 0.84)],
           'placa_conquista', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=[(1, 0, 0)] * 4, cor=1.0)
    # laje com beiral largo e luzes embutidas
    bx0, bx1, by0, by1 = x0 - 0.6, x1 + 1.0, y0 - 0.6, y1 + 0.6
    g.caixa(bx0, bx1, by0, by1, 2.8, 3.1, 'parede_externa', topo='cobertura', fundo='forro', sem_fundo=False)
    for yy in (y0 + 0.9, (y0 + y1) / 2, y1 - 0.9):
        g.cil(x1 + 0.5, yy, 0.09, 2.785, 2.8, 'luz_poste', seg=10, tampa=False, base=True)
    poca(g, x1 + 1.2, (y0 + y1) / 2, 3.6)


def _apoio(g):
    _guarita(g)
    _edificio(g, PL.CASA_BOMBAS, h=2.6, vidro=False)
    _edificio(g, PL.LIXO, h=2.6, vidro=False)
    for cx, cy in PL.RESERVATORIOS:
        rr = PL.RAIO_RESERVATORIO_PX * S_PX
        g.cil(X(cx), Y(cy), rr, 0.06, 2.4, 'cisterna', seg=24, topo='cisterna', r2=rr * 0.96)
        g.cil(X(cx), Y(cy), rr * 0.3, 2.4, 2.75, 'cisterna', seg=12, r2=rr * 0.12)
    for x0p, y0p, x1p, y1p in PL.SEBES:
        mx0, mx1, my0, my1 = X(x0p), X(x1p), Y(y1p), Y(y0p)
        g.caixa(mx0, mx1, my0, my1, 0.0, 0.7, 'sebe_flor' if x0p > 3000 else 'sebe')


def lazer(g):
    _piscinas(g)
    x0, x1, y0, y1 = RM(PL.SOLARIUM)
    _edificio(g, PL.VESTIARIO, h=2.8, vidro=False)
    _fitness(g)
    _playground(g)
    _gourmet(g)
    _pet(g)
    _bicicletario(g)
    _apoio(g)
