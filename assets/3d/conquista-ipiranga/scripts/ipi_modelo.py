# ipi_modelo.py -- reconstroi do zero a cena do Conquista Clube Ipiranga (maquete externa, etapa 1).
# Roda DENTRO do Blender (run_all.py ou Blender -b --factory-startup -P run_all.py). Metros, Z para cima,
# origem em ipi_planta.ORIGEM_PX. Modulos executados no mesmo namespace:
#   ipi_geo.py (geometria)  ipi_patio.py (chao, vagas, passeios, muros, rua)  ipi_lazer.py (lazer e apoio)
#   ipi_paisagem.py (ipes, arvores, palmeiras, carros)
# Medidas: ipi_planta.py (px da implantacao), plantas tipo e FAQ da ficha tecnica.
#
# Sem varandas: a cor de cada apartamento (malha "unidades") vai nas janelas da unidade (sala, dormitorio 2 e
# suite), com o mapa janela_unidade.png de detalhe. Decisao do usuario em 2026-11-14.
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/conquista-ipiranga/scripts
TEXDIR = SCR + '/tex'


def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())


_carrega('ipi_geo.py')          # Geo, X, Y, UVESC (usados ja na definicao das classes abaixo)

# ------------------------------------------------------------------ parametros da torre
# FAQ: pe-direito 2,50 m e laje de 10 cm -> 2,60 m piso a piso; terreo + 6 = 7 pavimentos nas 4 torres.
PD = 2.60
PARAPEITO = 1.10
TILE = PD

GRADE_TORRES = [1, 2, 3, 4]
GRADE_ANDARES, GRADE_FINAIS = 7, 12


def indice(torre, andar, final):   # = Maquete.indice
    return ((GRADE_TORRES.index(torre)) * GRADE_ANDARES + andar) * GRADE_FINAIS + (final - 1)


# ------------------------------------------------------------------ limpeza
def limpar():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras,
                 bpy.data.lights, bpy.data.worlds, bpy.data.node_groups, bpy.data.curves):
        for d in list(coll):
            try:
                coll.remove(d)
            except Exception:
                pass


# ------------------------------------------------------------------ materiais
MATS = {}
IMAGENS = {}


def srgb(hx):
    hx = hx.lstrip('#')
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def lin(v):
    return ((v + 0.055) / 1.055) ** 2.4


def tx(nome, dados=False):
    """Carrega (uma vez) uma textura de tex/ e embute no .blend."""
    if nome in IMAGENS:
        return IMAGENS[nome]
    im = bpy.data.images.load(TEXDIR + '/' + nome)
    if dados:
        im.colorspace_settings.name = 'Non-Color'
    im.pack()
    IMAGENS[nome] = im
    return im


def mat(name, cor='#ffffff', rough=0.85, img=None, tint=False, nrm=None, nrm_str=1.0, metal=0.0, double=False,
        img_mean=0.85, emit_img=None, recorte=False, blend=None, uv=None, blend_img=False):
    """cor sRGB (hex) ou rgb linear. tint=True: imagem cinza multiplicada pela cor (baseColorFactor no glTF), com
    compensacao pela media da imagem. recorte=True: alfa MASK. blend=a: transparente com alfa constante a."""
    assert name not in MATS, 'material repetido: ' + name
    rgb = srgb(cor) if isinstance(cor, str) else cor
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if p is None:      # Blender 5: material novo pode vir sem nos
        nt.nodes.clear()
        p = nt.nodes.new('ShaderNodeBsdfPrincipled')
        sai = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(p.outputs['BSDF'], sai.inputs['Surface'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if img is not None:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = tx(img); t.location = (-700, 250)
        if tint:
            k = lin(img_mean)
            fac = tuple(min(1.0, c / k) for c in rgb)
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
            mx.location = (-300, 250)
            mx.inputs['Factor'].default_value = 1.0
            nt.links.new(t.outputs['Color'], mx.inputs['A'])
            mx.inputs['B'].default_value = (*fac, 1)
            nt.links.new(mx.outputs['Result'], p.inputs['Base Color'])
        else:
            nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
        if recorte:
            rd = nt.nodes.new('ShaderNodeMath'); rd.operation = 'ROUND'; rd.location = (-300, -50)
            nt.links.new(t.outputs['Alpha'], rd.inputs[0])
            nt.links.new(rd.outputs[0], p.inputs['Alpha'])
            m.surface_render_method = 'DITHERED'
            double = True
        if blend_img:
            nt.links.new(t.outputs['Alpha'], p.inputs['Alpha'])
            m.surface_render_method = 'BLENDED'
    else:
        p.inputs['Base Color'].default_value = (*rgb, 1)
    if blend is not None:
        p.inputs['Alpha'].default_value = blend
        m.surface_render_method = 'BLENDED'
    if nrm is not None:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = tx(nrm, dados=True); tn.location = (-700, -300)
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (-300, -300)
        nm.inputs['Strength'].default_value = nrm_str
        nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    if emit_img is not None:
        te = nt.nodes.new('ShaderNodeTexImage'); te.image = tx(emit_img); te.location = (-700, -650)
        nt.links.new(te.outputs['Color'], p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value = 1.0
    m.use_backface_culling = not double
    MATS[name] = m
    if uv is not None:
        UVESC[name] = uv if isinstance(uv, tuple) else (uv, uv)
    return m


def materiais_torre():
    # cores da perspectiva da fachada (785 ITAJUBA_FACHADA): reboco bege claro nos blocos e pontas, fundo dos recuos
    # com faixas terracota entre as janelas e faixa bege na altura das janelas, terreo em taupe
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.6, img_mean=0.88, uv=TILE)
    mat('fachada_clara', '#e6e1d8', 0.93, **kw)
    mat('fachada_lateral', '#dcd6cc', 0.93, **kw)
    mat('fachada_base', '#8e847b', 0.93, **kw)
    mat('terracota', '#9d5a48', 0.92, **kw)
    mat('faixa_janela', '#e2dcd2', 0.92, **kw)
    mat('friso', '#cfc8bd', 0.92, **kw)
    mat('laje_borda', '#e6e1d7', 0.92, **kw)
    mat('cobertura', '#8a8781', 0.95, **kw)
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')   # acesos a noite (pedido do usuario)
    mat('unidade', '#ffffff', 0.25, img='janela_unidade.png')
    mat('caixilho', '#ece9e2', 0.45)
    mat('vidro_porta', '#3a4a58', 0.08, metal=0.2)
    mat('luz_forro', '#fff4dc', 0.5)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)
    mat('piso_hall', '#bdb3a6', 0.7, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('forro', '#ece7dd', 0.9)


def materiais_patio():
    mat('grama', '#ffffff', 0.97, img='grama2.jpg', uv=6.0)
    mat('entorno', (0.62, 0.62, 0.50), 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=14.0)
    mat('asfalto', '#ffffff', 0.92, img='asfalto2.jpg', uv=8.0)
    mat('concreto', '#cfccc4', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('paver', '#8f8d8a', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('vaga_drenante', '#ffffff', 0.92, img='vaga_drenante.jpg')
    mat('vaga_pcd', '#bdbab3', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('meio_fio', '#c8c5bc', 0.9)
    mat('faixa', '#f0f0ea', 0.75)
    mat('faixa_amarela', '#e3b62c', 0.75)
    mat('marcas', '#ffffff', 0.8, img='piso_marcas.png', recorte=True)
    mat('sombra_contato', '#ffffff', 1.0, img='piso_marcas.png', blend_img=True)
    mat('muro_liso', '#c9c3b9', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('muro_base', '#8e847b', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('pingadeira', '#d5d0c6', 0.9)
    mat('cisterna', '#2f62bf', 0.45)
    mat('telha', '#8f9195', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.0, 1.0))
    mat('parede_externa', '#d9d3c9', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('parede_taupe', '#8e847b', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('sebe', '#4b6f36', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.5)
    mat('sebe_flor', '#c9a43a', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.5)
    mat('alambrado_branco', '#f2f2ee', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))


# ------------------------------------------------------------------ planta da torre
def _q():
    """Medidas do quadrante +x +y em metros (ipi_planta.Q_PX)."""
    q = {k: v * S_PX for k, v in PL.Q_PX.items()}
    return q


def contorno_quadrante():
    """Contorno de 1/4 da torre (+x +y), do eixo (x = 0) ate o eixo maior (y = 0), sentido horario."""
    q = Q
    xn, yF, yS, yP, yN = q['nucleo'], q['y_fundo'], q['y_fachada'], q['y_ponta'], q['y_nucleo']
    xe, tr, yT = q['fim'], q['testa_recuo'], q['testa_y']
    return [(0.0, yN), (xn, yN), (xn, yF), (q['g06'], yF), (q['g06'], yS), (q['b06'], yS), (q['b06'], yF),
            (q['r'], yF), (q['r'], yS), (q['b05'], yS), (q['b05'], yF), (q['ponta'], yF), (q['ponta'], yP),
            (xe, yP), (xe, yT), (xe - tr, yT), (xe - tr, 0.0)]


def contorno_torre():
    """Contorno inteiro (4 quadrantes espelhados), anti-horario."""
    qe = contorno_quadrante()
    leste = qe + [(x, -y) for x, y in reversed(qe)][1:]
    cw = leste + [(-x, y) for x, y in reversed(leste)][1:-1]
    out = []
    for p in reversed(cw):
        if not out or abs(out[-1][0] - p[0]) + abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    if abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


# finais por quadrante (sx, sy) do nucleo para a ponta
FINAIS_Q = {(1, 1): (6, 5, 4), (-1, 1): (7, 8, 9), (1, -1): (1, 2, 3), (-1, -1): (12, 11, 10)}
JANELA = (1.00, 2.20)        # peitoril e verga dos dormitorios e da sala
BASCULANTE = (1.60, 2.20)


def aberturas_quadrante():
    """Aberturas do quadrante +x +y (finais 06, 05 e 04) lidas na implantacao e nas plantas tipo:
    (k = 0 nucleo .. 2 ponta | None = nao e da unidade, plano, coordenada, a0, a1, tipo).
    Sala no fundo do recuo do garden, dormitorio 2 na frente do bloco saliente (com o basculante do banho ao lado),
    suite no fundo do recuo entre os blocos; na ponta, dormitorio na frente e suite na testa."""
    q = Q
    yF, yS, yP, xe = q['y_fundo'], q['y_fachada'], q['y_ponta'], q['fim']
    c = lambda a, b: (a + b) / 2
    g06, b06, rr, b05, g04, pt = c(q['nucleo'], q['g06']), c(q['g06'], q['b06']), c(q['b06'], q['r']), \
        c(q['r'], q['b05']), c(q['b05'], q['g04']), c(q['ponta'], xe)
    g04b = c(q['g04'], q['ponta'])
    return [
        (0, 'y', yF, g06 - 0.75, g06 + 0.75, 'sala'),
        (0, 'y', yS, b06 - 1.05, b06 + 0.15, 'dorm'),
        (None, 'y', yS, b06 + 0.55, b06 + 1.05, 'basc'),
        (0, 'y', yF, rr - 1.55, rr - 0.45, 'dorm'),
        (1, 'y', yF, rr + 0.45, rr + 1.55, 'dorm'),
        (1, 'y', yS, b05 - 0.15, b05 + 1.05, 'dorm'),
        (None, 'y', yS, b05 - 1.05, b05 - 0.55, 'basc'),
        (1, 'y', yF, g04 - 0.75, g04 + 0.75, 'sala'),
        (2, 'y', yF, g04b - 0.75, g04b + 0.75, 'sala'),
        (2, 'y', yP, pt - 0.95, pt + 0.25, 'dorm'),
        (None, 'y', yP, pt + 0.75, pt + 1.25, 'basc'),
        (2, 'x', xe, 4.05, 5.25, 'dorm'),
        (None, 'x', xe, 3.25, 3.75, 'basc'),
    ]


class GeoUn(Geo):
    """Geo que guarda o indice da unidade de cada vertice (atributo _unit)."""

    def __init__(self, nome):
        super().__init__(nome, ao=False)
        self.un = []
        self.idx_un = 0.0

    def face(self, cos, mat, **kw):
        super().face(cos, mat, **kw)
        self.un += [self.idx_un] * len(cos)

    def objeto(self):
        ob = super().objeto()
        at = ob.data.attributes.new('_unit', 'FLOAT', 'POINT')
        at.data.foreach_set('value', self.un)
        return ob


def _parede(g, a, b, z0, z1, m):
    """Parede vertical de a a b (planta, anti-horario do contorno), voltada para fora (direita do sentido)."""
    g.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m)


def _abertura(g, gu, plano, c, a0, a1, z0, z1, m, sx, sy, unidade=None):
    """Janela no quadrante (sx, sy): quad com a textura (na malha da unidade quando `unidade` for o indice) +
    caixilho em relevo e peitoril. plano 'y': fachada y = c (a0..a1 em x); plano 'x': testa x = c (a0..a1 em y)."""
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    e, f = 0.05, 0.045
    alvo = g
    if unidade is not None:
        gu.idx_un = float(unidade)
        alvo = gu
    if plano == 'y':
        ya = sy * (c + 0.03)
        x0, x1 = sorted((sx * a0, sx * a1))
        cs = [(x1, ya, z0), (x0, ya, z0), (x0, ya, z1), (x1, ya, z1)]
        alvo.face(cs if sy > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)

        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * b0, sx * b1, sy * c, sy * (c + ee), zz0, zz1, 'caixilho')
    else:
        xa = sx * (c + 0.03)
        y0, y1 = sorted((sy * a0, sy * a1))
        cs = [(xa, y0, z0), (xa, y1, z0), (xa, y1, z1), (xa, y0, z1)]
        alvo.face(cs if sx > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)

        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * c, sx * (c + ee), sy * b0, sy * b1, zz0, zz1, 'caixilho')
    bx(a0 - f, a1 + f, z0 - 0.03, z0 + f - 0.03, ee=0.09)
    bx(a0 - f, a1 + f, z1, z1 + f)
    bx(a0 - f, a0, z0, z1)
    bx(a1, a1 + f, z0, z1)


def _sala_terreo(g, sx, sy):
    """Espaco de uso comum no lugar do final 12 (terreo, quadrante -x -y): vitrine na linha do guarda-corpo dos
    gardens, piso, forro e a parede do recuo com uma porta de vidro."""
    q = Q
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    x0, x1 = q['nucleo'], q['g06']
    y0, y1 = q['y_fundo'], q['y_fachada']
    g.piso(min(X_(x0), X_(x1)), max(X_(x0), X_(x1)), min(Y_(y0), Y_(y1)), max(Y_(y0), Y_(y1)), 0.13, 'piso_hall')
    # vitrine (vidro + montantes) na frente e nas laterais
    yy = y1 - 0.06
    g.caixa(X_(x0), X_(x1), Y_(yy), Y_(yy + 0.03), 0.13, PD - 0.12, 'vidro_porta')
    n = 4
    for k in range(n + 1):
        xx = x0 + (x1 - x0) * k / n
        g.caixa(X_(xx - 0.03), X_(xx + 0.03), Y_(yy - 0.02), Y_(yy + 0.05), 0.13, PD - 0.12, 'ferragem')
    g.caixa(X_(x0), X_(x1), Y_(yy - 0.02), Y_(yy + 0.05), 2.30, 2.36, 'ferragem')
    for xx in (x0, x1):
        g.caixa(X_(xx - 0.02), X_(xx + 0.02), Y_(y0), Y_(yy), 0.13, PD - 0.12, 'vidro_porta')
    # laje sobre a sala (forro) e platibanda baixa na linha da fachada
    g.caixa(X_(x0), X_(x1), Y_(y0), Y_(y1), PD - 0.12, PD, 'laje_borda', fundo='forro', sem_fundo=False)


def _hall(g):
    """Entrada do hall no nucleo, face -y: porta de vidro recuada e marquise."""
    q = Q
    yN, xn = q['y_nucleo'], q['nucleo']
    g.caixa(-xn + 0.15, xn - 0.15, -yN - 0.02, -yN + 0.01, 0.0, 2.45, 'vidro_porta')
    for xx in (-0.02, -xn + 0.15, xn - 0.15):
        g.caixa(xx - 0.03, xx + 0.03, -yN - 0.05, -yN, 0.0, 2.45, 'ferragem')
    g.caixa(-xn - 0.6, xn + 0.6, -yN - 2.0, -yN, 2.65, 2.85, 'laje_borda', fundo='forro', sem_fundo=False)
    g.cil(0, -yN - 1.0, 0.1, 2.635, 2.65, 'luz_forro', seg=8, tampa=False, base=True)
    g.tapete(-2.6, 2.6, -yN - 3.8, -yN + 1.4, 0.14, 'luz_chao', (0, 0, 1, 1))     # poca de luz da marquise (noite)
    g.piso(-xn, xn, -yN - 2.0, -yN, 0.08, 'piso_hall')


def _cobertura(g, Hp):
    """Caixa d'agua e casa de maquinas do elevador sobre o nucleo; condensadoras soltas na laje."""
    q = Q
    yN = q['y_nucleo']
    g.caixa(-3.2, 3.2, -2.6, 2.6, Hp - 0.6, Hp + 2.6, 'fachada_clara', topo='cobertura')
    g.caixa(-1.4, 1.4, -yN + 0.8, -2.6, Hp - 0.6, Hp + 1.6, 'fachada_clara', topo='cobertura')
    g.caixa(-3.3, 3.3, -2.7, 2.7, Hp + 2.6, Hp + 2.72, 'laje_borda', topo='cobertura')
    for xx, yy in ((9.0, 2.2), (-9.0, 2.2), (17.5, -2.2), (-17.5, -2.2), (24.0, 2.0), (-24.0, -2.0)):
        g.caixa(xx - 0.45, xx + 0.45, yy - 0.3, yy + 0.3, Hp - 1.1, Hp - 0.45, 'parede_externa', topo='telha')


def torre(n, cx, cy, giro, npav, gu):
    """Torre n em (cx, cy) metros com giro em graus (Blender). Corpo e detalhes em 'torre-n'; janelas das
    unidades em gu (malha 'unidades')."""
    g = Geo('torre-%d' % n, ao=False)
    q = Q
    H = npav * PD
    Hp = H + PARAPEITO
    poly = contorno_torre()
    yF, yS = q['y_fundo'], q['y_fachada']
    with g.em(cx, cy, 0.0, giro), gu.em(cx, cy, 0.0, giro):
        # paredes externas: terreo em taupe, resto bege; fundo dos recuos em terracota com a faixa das janelas
        m_ = len(poly)
        for i in range(m_):
            a, b = poly[i], poly[(i + 1) % m_]
            no_fundo = abs(a[1] - b[1]) < 1e-6 and abs(abs(a[1]) - yF) < 1e-6
            lateral = abs(a[0] - b[0]) < 1e-6 and abs(a[0]) < q['fim'] - 0.5
            corpo = 'terracota' if no_fundo else ('fachada_lateral' if lateral else 'fachada_clara')
            _parede(g, a, b, 0.0, PD, 'fachada_base')
            _parede(g, a, b, PD, Hp, corpo)
            # faixa bege na altura das janelas e friso de laje, andar a andar
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            if L < 0.05:
                continue
            nx, ny = dy / L, -dx / L
            for andar in range(1, npav):
                z = andar * PD
                if no_fundo:
                    o = 0.012
                    g.face([(a[0] + nx * o, a[1] + ny * o, z + 0.85), (b[0] + nx * o, b[1] + ny * o, z + 0.85),
                            (b[0] + nx * o, b[1] + ny * o, z + 2.35), (a[0] + nx * o, a[1] + ny * o, z + 2.35)], 'faixa_janela')
                else:
                    o = 0.02
                    q4 = [(a[0] + nx * o, a[1] + ny * o, z - 0.03), (b[0] + nx * o, b[1] + ny * o, z - 0.03),
                          (b[0] + nx * o, b[1] + ny * o, z + 0.03), (a[0] + nx * o, a[1] + ny * o, z + 0.03)]
                    g.face(q4, 'friso')
            # cimalha no topo
            o = 0.04
            g.face([(a[0] + nx * o, a[1] + ny * o, Hp - 0.14), (b[0] + nx * o, b[1] + ny * o, Hp - 0.14),
                    (b[0] + nx * o, b[1] + ny * o, Hp), (a[0] + nx * o, a[1] + ny * o, Hp)], 'laje_borda')
        g.poligono(poly, Hp, 'cobertura')
        # janelas e unidades
        ab = aberturas_quadrante()
        for (sx, sy), finais in FINAIS_Q.items():
            for andar in range(npav):
                z = andar * PD
                sala_comum = (andar == 0 and (sx, sy) == (-1, -1))
                for k, plano, c, a0, a1, tipo in ab:
                    if sala_comum and k == 0:
                        continue
                    zz = BASCULANTE if tipo == 'basc' else JANELA
                    if k is None:
                        _abertura(g, gu, plano, c, a0, a1, z + zz[0], z + zz[1], 'janela_banheiro', sx, sy)
                    else:
                        _abertura(g, gu, plano, c, a0, a1, z + zz[0], z + zz[1], 'unidade', sx, sy,
                                  unidade=indice(n, andar, finais[k]))
            if (sx, sy) == (-1, -1):
                _sala_terreo(g, sx, sy)
        _hall(g)
        _cobertura(g, Hp)
    return g.objeto()


def gardens(g):
    """Gardens do terreo nos recuos dos finais 1 a 11: mureta de 1,00 m + alambrado de 0,80 m (planta garden) na
    linha da fachada saliente e divisa entre os gardens do 05 e do 04."""
    q = Q
    yF, yS = q['y_fundo'], q['y_fachada']
    e = 0.12
    trechos = [(q['nucleo'], q['g06']), (q['b05'], q['ponta'])]
    for t, (cxp, cyp, ang) in sorted(PL.TORRES.items()):
        with g.em(X(cxp), Y(cyp), 0.0, -ang):
            for (sx, sy) in FINAIS_Q:
                for x0, x1 in trechos:
                    if (sx, sy) == (-1, -1) and x0 == q['nucleo']:
                        continue            # espaco comum no lugar do final 12
                    xa, xb = sorted((sx * x0, sx * x1))
                    ya, yb = sorted((sy * (yS - e), sy * yS))
                    g.caixa(xa, xb, ya, yb, 0.0, 1.0, 'parede_externa', topo='pingadeira')
                    g.painel(xa, sy * yS, xb, sy * yS, 1.0, 1.8, 'alambrado_branco', (0, 0, (xb - xa) / 0.5 / 4, 0.4))
                    g.painel(xb, sy * yS, xa, sy * yS, 1.0, 1.8, 'alambrado_branco', (0, 0, (xb - xa) / 0.5 / 4, 0.4))
                    # piso de grama do garden
                    y0_, y1_ = sorted((sy * yF, sy * (yS - e)))
                    g.piso(xa, xb, y0_, y1_, 0.03, 'grama')
                xd = q['g04']
                ya, yb = sorted((sy * yF, sy * yS))
                g.caixa(sx * xd - e / 2, sx * xd + e / 2, ya, yb, 0.0, 1.8, 'parede_externa', topo='pingadeira')


# ------------------------------------------------------------------ contorno da unidade selecionada
def _trecho_fachada(k):
    """Trecho do contorno do quadrante +x +y que e fachada da unidade k (0 nucleo .. 2 ponta), como polilinha:
    meio = entre as divisas (com as paredes laterais dos recuos); ponta = da divisa 05|04 ate o eixo maior,
    contornando a testa."""
    q = Q
    pts = contorno_quadrante()
    x0, x1 = {0: (q['nucleo'], q['div06']), 1: (q['div06'], q['div05']), 2: (q['div05'], 1e9)}[k]
    out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if k == 2 and a[0] >= x0 - 1e-6 and (b[0] >= x0 - 1e-6):
            seg = [a, b]                     # ponta: tudo depois da divisa, inclusive a testa
        else:
            lo, hi = sorted((a[0], b[0]))
            if hi < x0 - 1e-6 or lo > x1 + 1e-6:
                continue
            if abs(a[1] - b[1]) < 1e-6:      # trecho horizontal: corta nas divisas
                ca = (min(max(a[0], x0), x1), a[1])
                cb = (min(max(b[0], x0), x1), b[1])
                if abs(ca[0] - cb[0]) < 1e-6:
                    continue
                seg = [ca, cb]
            else:                            # parede vertical dentro da faixa
                if not (x0 - 1e-6 <= a[0] <= x1 + 1e-6):
                    continue
                if k == 0 and abs(a[0] - x0) < 1e-6 and min(a[1], b[1]) < q['y_fundo'] - 1e-6:
                    continue
                seg = [a, b]
        for p in seg:
            if not out or abs(out[-1][0] - p[0]) + abs(out[-1][1] - p[1]) > 1e-6:
                out.append(p)
    return out


def _afasta(pts, d):
    """Polilinha deslocada d m para a esquerda do percurso (para fora no contorno horario), juntas em esquadria."""
    out = []
    n = len(pts)
    for i in range(n):
        ns = []
        if i > 0:
            ns.append((pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        if i < n - 1:
            ns.append((pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
        nrm = []
        for dx, dy in ns:
            L = math.hypot(dx, dy) or 1
            nrm.append((-dy / L, dx / L))
        mx, my = sum(v[0] for v in nrm), sum(v[1] for v in nrm)
        Lm = math.hypot(mx, my) or 1
        mx, my = mx / Lm, my / Lm
        kk = d / max(0.5, mx * nrm[0][0] + my * nrm[0][1])
        out.append((pts[i][0] + mx * kk, pts[i][1] + my * kk))
    return out


def exportar_contornos():
    """ipiranga-contornos.json: por torre e final, a fachada da unidade em planta (x, z do Three, 6 cm para fora da
    parede). A cena desenha o contorno da unidade selecionada rente a torre: base no piso do andar, topo no teto."""
    trechos = {k: _afasta(_trecho_fachada(k), 0.06) for k in (0, 1, 2)}
    out = {'schema': 'contornos-unidade/1', 'pe_direito': PD, 'torres': {}}
    for t, (cxp, cyp, ang) in sorted(PL.TORRES.items()):
        cx, cy, a = X(cxp), Y(cyp), math.radians(-ang)
        ca, sa = math.cos(a), math.sin(a)
        fin = {}
        for (sx, sy), finais in FINAIS_Q.items():
            for k, f in enumerate(finais):
                pts = []
                for x, y in trechos[k]:
                    lx, ly = x * sx, y * sy
                    bx, by = cx + lx * ca - ly * sa, cy + lx * sa + ly * ca
                    pts.append([round(bx, 3), round(-by, 3)])           # Three: (x, z) = (x, -y)
                fin[str(f)] = pts
        out['torres'][str(t)] = fin
    with open(os.path.join(SCR, '..', 'ipiranga-contornos.json'), 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))


# ------------------------------------------------------------------ layout para conferencia
def layout_unidades():
    out = {
        'schema': 'ipi-unidades-layout/1',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': {str(k): v for k, v in PL.PAVIMENTOS.items()},
        'janelas': 'cada unidade = as janelas dela (sala, dormitorio 2, suite), z = andar*PD + %s' % list(JANELA),
        'sem_unidade_no_terreo': [12],
        'torres': {'torre-%d' % t: {'centro': [round(X(cx), 3), round(Y(cy), 3), 0.0], 'rotacao_z_graus': -ang,
                                    'finais_por_quadrante': {'%+d%+d' % k: v for k, v in FINAIS_Q.items()}}
                   for t, (cx, cy, ang) in sorted(PL.TORRES.items())},
    }
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ modulos (mesmo namespace)
_pl = {}
exec(compile(open(SCR + '/ipi_planta.py').read(), SCR + '/ipi_planta.py', 'exec'), _pl)


class _Plano:
    pass


PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper():
        setattr(PL, _k, _v)
assert abs(PL.S_PX - S_PX) < 1e-9 and PL.ORIGEM_PX == ORIGEM_PX, 'ipi_geo.X/Y fora de sincronia com ipi_planta'
Q = _q()
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
_carrega('ipi_patio.py')
_carrega('ipi_paisagem.py')
_carrega('ipi_lazer.py')
_carrega('ipi_luzes.py')
ATL = json.load(open(TEXDIR + '/atlas_lazer.json'))
_carrega('ipi_moveis.py')
_carrega('ipi_ambientes.py')

# ------------------------------------------------------------------ main
OBJETOS_EXPORTADOS = []


def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer(); materiais_luzes(); materiais_moveis()
    gu = GeoUn('unidades')
    nomes = ['unidades', 'entorno', 'entorno-rua', 'terreno', 'lazer', 'moveis', 'vegetacao', 'carros']
    for t, (cxp, cyp, ang) in sorted(PL.TORRES.items()):
        torre(t, X(cxp), Y(cyp), -ang, PL.PAVIMENTOS[t], gu)
        nomes.append('torre-%d' % t)
    gu.objeto()
    nun = len(set(gu.un))
    t = Geo('terreno', ao=False)
    chao(t)
    vagas(t)
    gardens(t)
    muros_perimetro(t)
    t.objeto()
    e = Geo('entorno', ao=False)
    e.piso(-4000, 4000, -4000, 4000, -0.04, 'entorno')
    e.objeto()
    r = Geo('entorno-rua', ao=False)     # separado: nao entra no enquadramento da sombra
    ruas(r)
    r.objeto()
    lz = Geo('lazer')
    lazer(lz)
    luzes(lz)
    lz.objeto()
    mv = Geo('moveis')
    moveis(mv)
    mv.objeto()
    vg = Geo('vegetacao', ao=False)
    paisagem(vg)
    vg.objeto()
    cr = Geo('carros', ao=False)
    carros(cr)
    cr.objeto()
    layout_unidades()
    exportar_contornos()
    OBJETOS_EXPORTADOS[:] = nomes
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun, 'materiais': len(bpy.data.materials)}


result['build'] = build()
