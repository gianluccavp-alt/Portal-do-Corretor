# park_modelo.py -- reconstroi do zero a cena do Village Park (maquete externa).
# Roda DENTRO do Blender (run_all.py ou Blender -b --factory-startup -P run_all.py). Metros, Z para cima,
# origem no centro do terreno (park_planta.ORIGEM_PX). Modulos executados no mesmo namespace:
#   park_geo.py (geometria)  park_patio.py (chao, vagas, muros)  park_lazer.py (lazer e apoio)
#   park_paisagem.py (arvores, canteiros, carros)  park_moveis.py (pecas de mobiliario, vindas do Gaia)
#   park_ambientes.py (posicao dos moveis por ambiente e palmeiras do lazer)
# Medidas: park_planta.py (px da implantacao), park_chao.json (park_mapa.py) e FAQ da ficha tecnica.
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/village-park/scripts
TEXDIR = SCR + '/tex'

# ------------------------------------------------------------------ parametros da torre
# FAQ: pe-direito 2,70 m e laje de 12 cm -> 2,82 m piso a piso. T1 e T2 com 20 pavimentos, T3 com 19.
PD = 2.82
PARAPEITO = 1.2
TILE = PD           # reboco: 1 repeticao por pavimento (junta sempre na laje)

# Planta local da torre (m), quadrante x >= 0, y >= 0; o resto e espelhado. Medida no contorno da torre na
# implantacao em alta (78,7 px/m) e conferida com as plantas tipo (140,7 px/m): 42,02 x 13,98 m, saliencia
# dos dormitorios do meio ate 14,84 m. Eixo maior em y; face +x tem os finais 3 a 6, a -x os finais 7, 8, 1 e 2.
L2 = 21.0           # meio comprimento (fachada de ponta a ponta 42,02 m)
X_PONTA = 6.99      # face lateral da ponta (dormitorios)
X_FACE = 6.51       # face lateral do meio (varandas, banheiros)
X_BUMP = 7.42       # saliencia do dormitorio de meio
X_NOTCH = 4.12      # recorte central entre os aptos de meio
X_VAR = 5.18        # fundo das varandas (1,33 m de profundidade)
Y_PONTA0 = 15.02    # inicio do bloco da ponta
Y_VAR1, Y_DIV, Y_VAR0 = 14.90, 10.905, 6.66   # varanda da ponta (14,90 a 10,905) e do meio (10,905 a 6,66)
Y_BUMP0, Y_BUMP1 = 2.64, 5.44
Y_NOTCH = 1.42
# testa: recorte central e degrau junto da ponta
X_NE0, Y_NE0 = 1.245, 17.82
X_NE1, Y_NE1 = 2.516, 20.24

GRADE_TORRES = [1, 2, 3]
GRADE_ANDARES, GRADE_FINAIS = 20, 8


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
    # cores tiradas da perspectiva da fachada (FACHADA04) e da aerea: ponta cinza medio, saliencias e
    # molduras brancas, grafite nas prumadas das varandas e no recorte central
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.6, img_mean=0.88, uv=TILE)
    mat('fachada_clara', '#d6d4d2', 0.93, **kw)
    mat('fachada_media', '#a7a5ab', 0.93, **kw)
    mat('fachada_grafite', '#5a5b62', 0.93, **kw)
    mat('prumada_escura', '#4b4c53', 0.93, **kw)
    mat('laje_borda', '#d2cfcb', 0.92, **kw)
    mat('cobertura', '#7c7a7d', 0.95, **kw)
    mat('varanda_forro', '#e2ddd3', 0.9)
    mat('varanda_parede', '#d4cfc6', 0.9)
    mat('varanda_piso', '#b9ab98', 0.8, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('janela_veneziana', '#ffffff', 0.4, img='veneziana2.png', emit_img='veneziana2_luz.jpg')
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')
    mat('guarda_corpo', '#ffffff', 0.45, img='guarda_corpo2.png', recorte=True)
    mat('unidade', '#2b3440', 0.2, img='porta_unidade2.png', tint=True, img_mean=0.7)
    mat('caixilho', '#ece9e2', 0.45)
    mat('vidro_porta', '#3a4a58', 0.08, metal=0.2)
    mat('luz_forro', '#fff4dc', 0.5)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)
    mat('ripado_hall', '#b88a5e', 0.7, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.0, 1.0))


def materiais_patio():
    mat('grama', '#ffffff', 0.97, img='grama2.jpg', uv=6.0)
    mat('entorno', (0.62, 0.62, 0.50), 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=14.0)
    mat('asfalto', '#ffffff', 0.92, img='asfalto2.jpg', uv=8.0)
    mat('concreto', '#cfccc4', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('paver', '#918f8c', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('paver_rua', '#a9a7a2', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('meio_fio', '#c8c5bc', 0.9)
    mat('faixa', '#f0f0ea', 0.75)
    mat('marcas', '#ffffff', 0.8, img='piso_marcas.png', recorte=True)
    mat('sombra_contato', '#ffffff', 1.0, img='piso_marcas.png', blend_img=True)
    mat('muro_bloco', '#8e8f92', 0.95, img='bloco.jpg', tint=True, img_mean=0.6, uv=3.2)
    mat('pingadeira', '#b9b6ae', 0.9)
    mat('cisterna', '#2f78bf', 0.45)
    mat('telha', '#8f9195', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.0, 1.0))
    mat('parede_externa', '#a7a4a0', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('porta_servico', '#d9d9d4', 0.6)


# ------------------------------------------------------------------ torre
def _face_x(g, x, y0, y1, z0, z1, m, s):
    """Parede no plano x, voltada para +x (s=1) ou -x (s=-1)."""
    y0, y1 = min(y0, y1), max(y0, y1)
    cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    g.face(cs if s > 0 else cs[::-1], m)


def _face_y(g, y, x0, x1, z0, z1, m, s):
    x0, x1 = min(x0, x1), max(x0, x1)
    cs = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)]
    g.face(cs if s > 0 else cs[::-1], m)


def _janela(g, plano, c, a0, a1, z0, z1, m, sx, sy):
    """Janela (quad com a textura inteira) + caixilho em relevo e peitoril, no quadrante (sx, sy)."""
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    e, f = 0.05, 0.045
    if plano == 'x':
        xa = sx * (c + 0.012)
        y0, y1 = sorted((sy * a0, sy * a1))
        cs = [(xa, y0, z0), (xa, y1, z0), (xa, y1, z1), (xa, y0, z1)]
        g.face(cs if sx > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)
        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * c, sx * (c + ee), sy * b0, sy * b1, zz0, zz1, 'caixilho')
    else:
        ya = sy * (c + 0.012)
        x0, x1 = sorted((sx * a0, sx * a1))
        cs = [(x1, ya, z0), (x0, ya, z0), (x0, ya, z1), (x1, ya, z1)]
        g.face(cs if sy > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)
        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * b0, sx * b1, sy * c, sy * (c + ee), zz0, zz1, 'caixilho')
    bx(a0 - f, a1 + f, z0 - 0.03, z0 + f - 0.03, ee=0.09)
    bx(a0 - f, a1 + f, z1, z1 + f)
    bx(a0 - f, a0, z0, z1)
    bx(a1, a1 + f, z0, z1)


# aberturas do quadrante +x/+y (local), lidas nas plantas tipo e repetidas por espelhamento
JANELA_DORM = (0.95, 2.25)    # peitoril e verga (z relativo ao piso do andar)
JANELA_BANHO = (1.60, 2.20)
JANELAS = [
    ('x', X_PONTA, (18.79, 19.99), 'janela_veneziana'),     # ponta: suite
    ('x', X_PONTA, (15.74, 16.94), 'janela_veneziana'),     # ponta: dormitorio 2
    ('y', L2, (3.33, 3.90), 'janela_banheiro'),             # ponta: banho da suite (testa)
    ('y', Y_NE1, (1.80, 2.37), 'janela_banheiro'),          # ponta: banho social (degrau da testa)
    ('y', Y_NE0, (0.13, 1.16), 'janela_veneziana'),         # ponta: dormitorio 3 (recorte da testa)
    ('x', X_FACE, (5.48, 6.05), 'janela_banheiro'),         # meio: banho social
    ('x', X_BUMP, (3.38, 4.55), 'janela_veneziana'),        # meio: dormitorio 2 (saliencia)
    ('x', X_FACE, (1.92, 2.49), 'janela_banheiro'),         # meio: banho da suite
    ('x', X_NOTCH, (0.06, 1.20), 'janela_veneziana'),       # meio: suite (recorte central)
]


def quadrante(g, gc, sx, sy, npav, hall):
    """1/4 do corpo da torre em coordenadas locais. g = corpo e detalhes, gc = guarda-corpos.
    hall: este quadrante tem o hall de entrada no terreo (final 1)."""
    H = npav * PD
    Hp = H + PARAPEITO
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    # face de cada parede externa: (eixo, coordenada, a0, a1, material)
    # paredes externas: (eixo, coordenada, a0, a1, material, lado de fora: +1 = sentido do quadrante, -1 = para o eixo)
    paredes = [
        ('y', L2, X_NE1, X_PONTA, 'fachada_clara', 1),               # testa da ponta
        ('x', X_NE1, Y_NE1, L2, 'prumada_escura', -1),               # degrau da testa
        ('y', Y_NE1, X_NE0, X_NE1, 'fachada_grafite', 1),
        ('x', X_NE0, Y_NE0, Y_NE1, 'prumada_escura', -1),
        ('y', Y_NE0, 0.0, X_NE0, 'prumada_escura', 1),               # recorte central da testa
        ('x', X_PONTA, Y_PONTA0, L2, 'fachada_media', 1),            # lateral da ponta
        ('y', Y_PONTA0, X_FACE, X_PONTA, 'fachada_grafite', -1),     # moldura grafite da varanda da ponta
        ('x', X_FACE, Y_VAR1, Y_PONTA0, 'fachada_grafite', 1),
        ('x', X_FACE, Y_BUMP1, Y_VAR0, 'fachada_grafite', 1),        # banho social do meio
        ('y', Y_BUMP1, X_FACE, X_BUMP, 'fachada_clara', 1),
        ('x', X_BUMP, Y_BUMP0, Y_BUMP1, 'fachada_clara', 1),         # saliencia do dormitorio
        ('y', Y_BUMP0, X_FACE, X_BUMP, 'fachada_clara', -1),
        ('x', X_FACE, Y_NOTCH, Y_BUMP0, 'fachada_clara', 1),
        ('y', Y_NOTCH, X_NOTCH, X_FACE, 'prumada_escura', -1),
        ('x', X_NOTCH, 0.0, Y_NOTCH, 'prumada_escura', 1),           # recorte central
    ]
    for ax, c, a0, a1, m, d in paredes:
        if ax == 'x':
            _face_x(g, X_(c), Y_(a0), Y_(a1), 0.0, Hp, m, sx * d)
        else:
            _face_y(g, Y_(c), X_(a0), X_(a1), 0.0, Hp, m, sy * d)
    # cobertura (laje da platibanda) em retangulos que cobrem o quadrante
    tampa = [(0, X_NE0, 0, Y_NE0), (X_NE0, X_NE1, 0, Y_NE1), (X_NE1, X_NOTCH, 0, L2), (X_NOTCH, X_FACE, Y_NOTCH, Y_PONTA0),
             (X_NOTCH, X_PONTA, Y_PONTA0, L2), (X_FACE, X_BUMP, Y_BUMP0, Y_BUMP1)]
    for x0, x1, y0, y1 in tampa:
        g.piso(min(X_(x0), X_(x1)), max(X_(x0), X_(x1)), min(Y_(y0), Y_(y1)), max(Y_(y0), Y_(y1)), Hp, 'cobertura')
    # varandas: o vao entre o fundo (X_VAR) e a face (X_FACE), de Y_VAR0 a Y_VAR1
    for i in range(npav):
        z = i * PD
        sem_varanda = (i == 0 and hall)          # terreo do final 1: hall de entrada
        # fundo, laterais e divisoria
        for ya, yb in ((Y_VAR0, Y_DIV), (Y_DIV, Y_VAR1)):
            if sem_varanda and ya == Y_VAR0:
                continue
            _face_x(g, X_(X_VAR), Y_(ya), Y_(yb), z, z + PD, 'varanda_parede', sx)
        _face_y(g, Y_(Y_VAR0), X_(X_VAR), X_(X_FACE), z, z + PD, 'varanda_parede', sy)
        _face_y(g, Y_(Y_VAR1), X_(X_VAR), X_(X_FACE), z, z + PD, 'varanda_parede', -sy)
        g.caixa(X_(X_VAR), X_(X_FACE), Y_(Y_DIV - 0.06), Y_(Y_DIV + 0.06), z, z + PD, 'varanda_parede', topo='varanda_parede')
        # laje: piso, borda e forro (a cada 3 pavimentos a borda e grafite, como na perspectiva)
        borda = 'fachada_grafite' if (i % 3 == 0 and i > 0) else 'laje_borda'
        eb = 0.30 if borda == 'fachada_grafite' else 0.16
        g.caixa(X_(X_VAR), X_(X_FACE + 0.02), Y_(Y_VAR0), Y_(Y_VAR1), z - (eb - 0.12 if i else 0), z + 0.12, borda,
                topo='varanda_piso', fundo='varanda_forro', sem_fundo=(i == 0))
        if not (i == 0):
            g.cil(X_(X_VAR + 0.75), Y_((Y_VAR0 + Y_DIV) / 2), 0.09, z - 0.02, z - 0.005, 'luz_forro', seg=8, tampa=False, base=True)
            g.cil(X_(X_VAR + 0.75), Y_((Y_DIV + Y_VAR1) / 2), 0.09, z - 0.02, z - 0.005, 'luz_forro', seg=8, tampa=False, base=True)
            for ya, yb in ((Y_VAR0, Y_DIV), (Y_DIV, Y_VAR1)):
                gc_q = [(X_(X_FACE), Y_(ya + 0.07), z + 0.12), (X_(X_FACE), Y_(yb - 0.07), z + 0.12),
                        (X_(X_FACE), Y_(yb - 0.07), z + 1.12), (X_(X_FACE), Y_(ya + 0.07), z + 1.12)]
                if sx * sy < 0:
                    gc_q = [gc_q[1], gc_q[0], gc_q[3], gc_q[2]]
                gc.face(gc_q, 'guarda_corpo', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)] if sx * sy > 0 else [(1, 0), (0, 0), (0, 1), (1, 1)], cor=1.0)
        # janelas
        for plano, c, (a0, a1), m in JANELAS:
            zz = JANELA_BANHO if m == 'janela_banheiro' else JANELA_DORM
            if i == 0 and hall and plano == 'x' and c in (X_FACE, X_BUMP):
                continue
            if i == 0 and plano == 'x' and c == X_NOTCH and sx < 0:
                continue                                  # porta do hall no recorte central (os dois lados de y)
            _janela(g, plano, c, a0, a1, z + zz[0], z + zz[1], m, sx, sy)
        # junta de laje na fachada (friso fino) em toda a volta da ponta e do meio
        if i > 0:
            g.caixa(X_(X_PONTA), X_(X_PONTA + 0.025), Y_(Y_PONTA0), Y_(L2), z - 0.02, z + 0.02, 'laje_borda')
    # forro da varanda do ultimo pavimento
    g.piso(min(X_(X_VAR), X_(X_FACE)), max(X_(X_VAR), X_(X_FACE)), min(Y_(Y_VAR0), Y_(Y_VAR1)), max(Y_(Y_VAR0), Y_(Y_VAR1)),
           H, 'varanda_forro')
    # platibanda sobre o vao da varanda
    g.caixa(X_(X_VAR), X_(X_FACE + 0.02), Y_(Y_VAR0), Y_(Y_VAR1), H, Hp, 'fachada_grafite', topo='cobertura')
    if hall:
        _hall(g, sx, sy)
    elif sx < 0:
        _porta_hall(g, sx, sy)


def _hall(g, sx, sy):
    """Hall de entrada no terreo: porta de vidro de 2 folhas no recorte central da face -x, com marquise.
    No lugar do final 1 (sem unidade no terreo) o fundo da varanda vira vidro do hall."""
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    xf = X_NOTCH
    for yy0, yy1 in ((0.0, Y_NOTCH - 0.12),):
        g.caixa(X_(xf), X_(xf + 0.03), Y_(yy0), Y_(yy1), 0.12, 2.6, 'vidro_porta')
        for yy in (yy0 + 0.04, yy1):
            g.caixa(X_(xf), X_(xf + 0.06), Y_(yy - 0.04), Y_(yy + 0.04), 0.12, 2.6, 'ferragem')
        g.caixa(X_(xf), X_(xf + 0.06), Y_(yy0), Y_(yy1 + 0.04), 2.56, 2.66, 'ferragem')
    g.caixa(X_(X_NOTCH), X_(X_FACE + 1.6), Y_(0.0), Y_(Y_NOTCH + 0.35), 2.80, 2.92, 'laje_borda', fundo='varanda_forro')
    g.piso(min(X_(X_NOTCH), X_(X_FACE + 1.6)), max(X_(X_NOTCH), X_(X_FACE + 1.6)), min(Y_(0.0), Y_(Y_NOTCH)),
           max(Y_(0.0), Y_(Y_NOTCH)), 0.125, 'varanda_piso')
    # fundo da varanda do final 1 no terreo: vidro do hall com montantes
    ya, yb = Y_VAR0, Y_DIV
    g.caixa(X_(X_VAR), X_(X_VAR + 0.03), Y_(ya), Y_(yb), 0.12, 2.7, 'vidro_porta')
    n = 4
    for k in range(n + 1):
        yy = ya + (yb - ya) * k / n
        g.caixa(X_(X_VAR), X_(X_VAR + 0.06), Y_(yy - 0.03), Y_(yy + 0.03), 0.12, 2.7, 'ferragem')
    g.caixa(X_(X_VAR), X_(X_VAR + 0.02), Y_(Y_DIV + 0.4), Y_(Y_VAR1 - 0.4), 0.12, 2.7, 'ripado_hall')


def _porta_hall(g, sx, sy):
    """Metade +y da porta e da marquise do hall (a outra metade vem com _hall)."""
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    xf = X_NOTCH
    g.caixa(X_(xf), X_(xf + 0.03), Y_(0.0), Y_(Y_NOTCH - 0.12), 0.12, 2.6, 'vidro_porta')
    g.caixa(X_(xf), X_(xf + 0.06), Y_(Y_NOTCH - 0.16), Y_(Y_NOTCH - 0.08), 0.12, 2.6, 'ferragem')
    g.caixa(X_(xf), X_(xf + 0.06), Y_(0.0), Y_(Y_NOTCH - 0.08), 2.56, 2.66, 'ferragem')
    g.caixa(X_(X_NOTCH), X_(X_FACE + 1.6), Y_(0.0), Y_(Y_NOTCH + 0.35), 2.80, 2.92, 'laje_borda', fundo='varanda_forro')
    g.piso(min(X_(X_NOTCH), X_(X_FACE + 1.6)), max(X_(X_NOTCH), X_(X_FACE + 1.6)), min(Y_(0.0), Y_(Y_NOTCH)),
           max(Y_(0.0), Y_(Y_NOTCH)), 0.125, 'varanda_piso')


def _cobertura(g, npav):
    """Caixa d'agua, casa de maquinas dos 3 elevadores e barrilete sobre o nucleo."""
    Hp = npav * PD + PARAPEITO
    g.caixa(-2.4, 2.4, -3.6, 3.6, Hp - 0.6, Hp + 3.4, 'fachada_clara', topo='cobertura')
    g.caixa(-1.7, 1.7, 3.6, 6.4, Hp - 0.6, Hp + 2.2, 'fachada_grafite', topo='cobertura')
    g.caixa(-2.5, 2.5, -3.7, 3.7, Hp + 3.4, Hp + 3.55, 'laje_borda', topo='cobertura')
    for xx in (-1.9, 0.0, 1.9):
        g.caixa(xx - 0.03, xx + 0.03, -3.7, -3.64, Hp + 3.55, Hp + 4.3, 'ferragem')
        g.caixa(xx - 0.03, xx + 0.03, 3.64, 3.7, Hp + 3.55, Hp + 4.3, 'ferragem')
    for yy in (-3.67, 3.67):
        g.caixa(-1.95, 1.95, yy - 0.03, yy + 0.03, Hp + 4.25, Hp + 4.32, 'ferragem')
    # condensadoras e antenas soltas na laje (quebram a cobertura lisa)
    for xx, yy in ((4.2, 12.0), (-4.2, 12.0), (4.2, -12.0), (-4.2, -12.0)):
        g.caixa(xx - 0.5, xx + 0.5, yy - 0.35, yy + 0.35, Hp - 0.6, Hp - 0.0, 'parede_externa', topo='telha')


def torre(n, cx, cy, giro, npav, gc):
    """Torre n em (cx, cy) metros. Corpo + detalhes num objeto so ('torre-n'); guarda-corpos acumulados em gc."""
    g = Geo('torre-%d' % n, ao=False)
    with g.em(cx, cy, 0.0, giro):
        with gc.em(cx, cy, 0.0, giro):
            for sx in (1, -1):
                for sy in (1, -1):
                    quadrante(g, gc, sx, sy, npav, hall=(sx < 0 and sy < 0))
        _cobertura(g, npav)
    return g.objeto()


# ------------------------------------------------------------------ malha "unidades" (contrato com a pagina)
FINAIS = {   # face local e faixa em y (local) da varanda de cada final
    '06': (1, Y_DIV, Y_VAR1), '05': (1, Y_VAR0, Y_DIV), '04': (1, -Y_DIV, -Y_VAR0), '03': (1, -Y_VAR1, -Y_DIV),
    '07': (-1, Y_DIV, Y_VAR1), '08': (-1, Y_VAR0, Y_DIV), '01': (-1, -Y_DIV, -Y_VAR0), '02': (-1, -Y_VAR1, -Y_DIV),
}
UN_OFF = 0.04          # quad 4 cm a frente do fundo da varanda
SEM_UNIDADE_TERREO = ('01',)   # FAQ: terreo com 7 gardens; no lugar do final 1 fica o hall
Z_UN = (0.14, -0.14)


def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for t, ((cxp, cyp), giro) in sorted(PL.TORRES.items()):
        cx, cy = X(cxp), Y(cyp)
        a = math.radians(giro)
        ca, sa = math.cos(a), math.sin(a)
        rot = lambda x, y: (cx + ca * x - sa * y, cy + sa * x + ca * y)
        for fin, (s, ya, yb) in FINAIS.items():
            x = s * (X_VAR + UN_OFF)
            y0, y1 = min(ya, yb) + 0.08, max(ya, yb) - 0.08
            for andar in range(PL.PAVIMENTOS[t]):
                if andar == 0 and fin in SEM_UNIDADE_TERREO:
                    continue
                z0 = andar * PD + Z_UN[0]
                z1 = (andar + 1) * PD + Z_UN[1]
                loc = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)] if s > 0 else [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
                k = len(verts)
                verts += [(*rot(p[0], p[1]), p[2]) for p in loc]
                faces.append((k, k + 1, k + 2, k + 3))
                uvs += [(0, 0), (1, 0), (1, 1), (0, 1)]
                unit += [float(indice(t, andar, int(fin)))] * 4
    me = bpy.data.meshes.new('unidades')
    me.from_pydata(verts, [], faces)
    me.update()
    uvl = me.uv_layers.new(name='UVMap')
    for li, loop in enumerate(me.loops):
        uvl.data[li].uv = uvs[loop.vertex_index]
    at = me.attributes.new('_unit', 'FLOAT', 'POINT')
    at.data.foreach_set('value', unit)
    me.materials.append(MATS['unidade'])
    ob = bpy.data.objects.new('unidades', me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, len(set(unit))


def layout_unidades():
    out = {
        'schema': 'park-unidades-layout/1',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': {str(k): v for k, v in PL.PAVIMENTOS.items()},
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]',
        'z_rel': list(Z_UN),
        'plano': 'fundo da varanda: x_local = normal*(%.2f + %.2f); a fachada fica %.2f m a frente' % (X_VAR, UN_OFF, X_FACE - X_VAR),
        'sem_unidade_no_terreo': list(SEM_UNIDADE_TERREO),
        'torres': {},
    }
    for t, ((cxp, cyp), giro) in sorted(PL.TORRES.items()):
        out['torres']['torre-%d' % t] = {'centro': [round(X(cxp), 3), round(Y(cyp), 3), 0.0], 'rotacao_z_graus': giro,
                                         'finais': {f: {'face_local': '+x' if s > 0 else '-x', 'y_local': [ya, yb]}
                                                    for f, (s, ya, yb) in FINAIS.items()}}
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ modulos (mesmo namespace)
def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())


_carrega('park_geo.py')
_pl = {}
exec(compile(open(SCR + '/park_planta.py').read(), SCR + '/park_planta.py', 'exec'), _pl)


class _Plano:
    pass


PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper():
        setattr(PL, _k, _v)
assert abs(PL.S_PX - S_PX) < 1e-9 and PL.ORIGEM_PX == (1296.0, 1486.0), 'park_geo.X/Y fora de sincronia com park_planta'
CHAO = json.load(open(SCR + '/park_chao.json'))
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
ATL = json.load(open(TEXDIR + '/atlas_lazer.json'))
_carrega('park_patio.py')
_carrega('park_paisagem.py')
_carrega('park_lazer.py')
_carrega('park_moveis.py')
_carrega('park_ambientes.py')

# ------------------------------------------------------------------ main
OBJETOS_EXPORTADOS = []


def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer(); materiais_moveis()
    gc = Geo('guarda-corpo', ao=False)
    nomes = ['unidades', 'guarda-corpo', 'entorno', 'entorno-rua', 'terreno', 'lazer', 'moveis', 'vegetacao', 'carros']
    for t, ((cxp, cyp), giro) in sorted(PL.TORRES.items()):
        torre(t, X(cxp), Y(cyp), giro, PL.PAVIMENTOS[t], gc)
        nomes.append('torre-%d' % t)
    gc.objeto()
    _, nun = unidades()
    t = Geo('terreno', ao=False)
    chao(t)
    muros_perimetro(t)
    jardins_torres(t)
    t.objeto()
    e = Geo('entorno', ao=False)
    e.piso(-4000, 4000, -4000, 4000, -0.04, 'entorno')
    e.objeto()
    r = Geo('entorno-rua', ao=False)     # separado: nao entra no enquadramento da sombra
    avenida(r)
    r.objeto()
    lz = Geo('lazer')
    lazer(lz)
    lz.objeto()
    mv = Geo('moveis')
    moveis(mv)
    mv.objeto()
    vg = Geo('vegetacao', ao=False)
    paisagem(vg)
    paisagem_lazer(vg)
    vg.objeto()
    cr = Geo('carros', ao=False)
    carros(cr)
    cr.objeto()
    layout_unidades()
    OBJETOS_EXPORTADOS[:] = nomes
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun, 'materiais': len(bpy.data.materials)}


result['build'] = build()
