# avm_modelo.py -- reconstroi do zero a cena do Alta Vista Mangara (maquete externa, etapa 1).
# Roda DENTRO do Blender (run_all.py ou Blender -b --factory-startup -P run_all.py). Metros, Z para cima,
# origem no centro do terreno (avm_planta.ORIGEM_PX). Modulos executados no mesmo namespace:
#   avm_geo.py (geometria)  avm_patio.py (chao, vagas, deck da garagem, muros, ruas)  avm_lazer.py (lazer e apoio)
#   avm_paisagem.py (arvores, palmeiras, carros)
# Medidas: avm_planta.py (px da implantacao), plantas tipo e FAQ da ficha tecnica.
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/alta-vista-mangara/scripts
TEXDIR = SCR + '/tex'

# ------------------------------------------------------------------ parametros da torre
# Paredes de concreto: pe-direito 2,50 m e laje de 10 cm -> 2,60 m piso a piso (o FAQ da o hall com 2,52 m).
# Terreo ao 18o pavimento = 19 pavimentos nas duas torres.
PD = 2.60
PARAPEITO = 1.2
TILE = PD           # reboco: 1 repeticao por pavimento (junta sempre na laje)

# Planta local da torre (m), quadrante x >= 0, y >= 0 (finais 4 e 3); o resto e espelhado. Eixo maior em x.
# Medida na implantacao (18,91 px/m) e nas plantas tipo (ponta 46 m2: 137,7 px/m; meio 48 m2: 142,3 px/m).
L2 = 18.85          # meio comprimento (fachada de ponta a ponta 37,70 m)
Y_FACE = 5.82       # fachada longa (pontas e meio)
X_C = 3.12          # fim da faixa central (lajes tecnicas das suites do meio, coluna escura da fachada)
X_B1 = 5.30         # saliencia do dormitorio 2 do meio: de X_C a X_B1, ate Y_BUMP
Y_BUMP = 6.80
X_V0, X_DIV0, X_DIV1, X_V1 = 5.30, 9.38, 9.63, 13.66   # varandas do meio (X_V0..X_DIV0) e da ponta (X_DIV1..X_V1)
Y_VAR = 4.82        # fundo das varandas (1,00 m de profundidade)
X_NOTCH = 16.58     # recorte da testa (laje tecnica + janela do dormitorio 2 da ponta)
Y_NOTCH = 2.38
Y_LT = 6.42         # laje tecnica das suites do meio (0,60 m a frente da fachada)

GRADE_TORRES = [1, 2]
GRADE_ANDARES, GRADE_FINAIS = 19, 8


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
    # cores da perspectiva da fachada (782-...-FAC): pontas em cinza quente, molduras das varandas em branco
    # gelo, faixa central azul acinzentada com a coluna grafite das lajes tecnicas, paineis laranja e marrom
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.6, img_mean=0.88, uv=TILE)
    mat('fachada_clara', '#e4ded3', 0.93, **kw)
    mat('fachada_media', '#857c73', 0.93, **kw)
    mat('fachada_azul', '#7e8996', 0.93, **kw)
    mat('fachada_grafite', '#4a505a', 0.93, **kw)
    mat('prumada_escura', '#3c424c', 0.93, **kw)
    mat('painel_laranja', '#c8702e', 0.9, **kw)
    mat('painel_marrom', '#6f4c37', 0.9, **kw)
    mat('laje_borda', '#e6e1d7', 0.92, **kw)
    mat('cobertura', '#77757a', 0.95, **kw)
    mat('varanda_forro', '#ece7dd', 0.9)
    mat('varanda_parede', '#d8d2c8', 0.9)
    mat('varanda_piso', '#b9ab98', 0.8, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('janela_veneziana', '#ffffff', 0.4, img='veneziana2.png', emit_img='veneziana2_luz.jpg')
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')
    mat('guarda_corpo', '#ffffff', 0.45, img='guarda_corpo2.png', recorte=True)
    mat('unidade', '#2b3440', 0.2, img='porta_unidade2.png', tint=True, img_mean=0.7)
    mat('caixilho', '#ece9e2', 0.45)
    mat('vidro_porta', '#3a4a58', 0.08, metal=0.2)
    mat('luz_forro', '#fff4dc', 0.5)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)
    mat('ripado_claro', '#c79a6b', 0.7, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.0, 1.0))
    mat('brise', '#5d6672', 0.6, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))


def materiais_patio():
    mat('grama', '#ffffff', 0.97, img='grama2.jpg', uv=6.0)
    mat('entorno', (0.62, 0.62, 0.50), 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=14.0)
    mat('asfalto', '#ffffff', 0.92, img='asfalto2.jpg', uv=8.0)
    mat('asfalto_deck', '#b9b6b0', 0.9, img='concreto.jpg', tint=True, uv=4.0)
    mat('concreto', '#cfccc4', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('paver', '#918f8c', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('meio_fio', '#c8c5bc', 0.9)
    mat('faixa', '#f0f0ea', 0.75)
    mat('faixa_amarela', '#e3b62c', 0.75)
    mat('pcd_azul', '#2f63b0', 0.8)
    mat('marcas', '#ffffff', 0.8, img='piso_marcas.png', recorte=True)
    mat('sombra_contato', '#ffffff', 1.0, img='piso_marcas.png', blend_img=True)
    mat('muro_bloco', '#8e8f92', 0.95, img='bloco.jpg', tint=True, img_mean=0.6, uv=3.2)
    mat('muro_liso', '#b3aea6', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('pingadeira', '#c9c5bc', 0.9)
    mat('cisterna', '#2f78bf', 0.45)
    mat('telha', '#8f9195', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.0, 1.0))
    mat('parede_externa', '#a7a4a0', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('garagem_parede', '#9b958d', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('garagem_teto', '#cfcbc3', 0.95)
    mat('porta_servico', '#d9d9d4', 0.6)
    mat('sebe', '#4b6f36', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.5)


# ------------------------------------------------------------------ torre
def _face_x(g, x, y0, y1, z0, z1, m, s):
    """Parede no plano x, voltada para +x (s=1) ou -x (s=-1)."""
    y0, y1 = min(y0, y1), max(y0, y1)
    cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    g.face(cs if s > 0 else cs[::-1], m)


def _face_y(g, y, x0, x1, z0, z1, m, s):
    """Parede no plano y, voltada para +y (s=1) ou -y (s=-1)."""
    x0, x1 = min(x0, x1), max(x0, x1)
    cs = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)]
    g.face(cs if s > 0 else cs[::-1], m)


def _janela(g, plano, c, a0, a1, z0, z1, m, sx, sy):
    """Janela (quad com a textura inteira) + caixilho em relevo e peitoril, no quadrante (sx, sy).
    plano 'y': na fachada y = c (a0, a1 em x); plano 'x': na parede x = c (a0, a1 em y)."""
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    e, f = 0.05, 0.045
    if plano == 'y':
        ya = sy * (c + 0.012)
        x0, x1 = sorted((sx * a0, sx * a1))
        cs = [(x1, ya, z0), (x0, ya, z0), (x0, ya, z1), (x1, ya, z1)]
        g.face(cs if sy > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)
        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * b0, sx * b1, sy * c, sy * (c + ee), zz0, zz1, 'caixilho')
    else:
        xa = sx * (c + 0.012)
        y0, y1 = sorted((sy * a0, sy * a1))
        cs = [(xa, y0, z0), (xa, y1, z0), (xa, y1, z1), (xa, y0, z1)]
        g.face(cs if sx > 0 else [cs[1], cs[0], cs[3], cs[2]], m, uvs=uvs, cor=1.0)
        def bx(b0, b1, zz0, zz1, ee=e):
            g.caixa(sx * c, sx * (c + ee), sy * b0, sy * b1, zz0, zz1, 'caixilho')
    bx(a0 - f, a1 + f, z0 - 0.03, z0 + f - 0.03, ee=0.09)
    bx(a0 - f, a1 + f, z1, z1 + f)
    bx(a0 - f, a0, z0, z1)
    bx(a1, a1 + f, z0, z1)


# aberturas do quadrante +x/+y (local), lidas nas plantas tipo e repetidas por espelhamento
JANELA_DORM = (1.00, 2.20)    # peitoril e verga (z relativo ao piso do andar)
JANELA_BANHO = (1.55, 2.15)
JANELAS = [
    ('y', Y_FACE, (16.96, 18.12), 'janela_veneziana'),      # ponta: suite
    ('y', Y_FACE, (15.40, 15.95), 'janela_banheiro'),       # ponta: banho da suite
    ('y', Y_FACE, (14.02, 14.57), 'janela_banheiro'),       # ponta: banho social
    ('x', X_NOTCH, (0.70, 1.60), 'janela_veneziana'),       # ponta: dormitorio 2 (no recorte da testa)
    ('y', Y_BUMP, (3.65, 4.80), 'janela_veneziana'),        # meio: dormitorio 2 (saliencia)
    ('y', Y_FACE, (1.23, 2.39), 'janela_veneziana'),        # meio: suite (atras da laje tecnica)
]
# paineis coloridos no fundo lateral das varandas (como na perspectiva: laranja e marrom alternados)
PAINEIS = {0: 'painel_laranja', 1: None, 2: 'painel_marrom', 3: None, 4: 'painel_laranja', 5: None}


def quadrante(g, gc, sx, sy, npav, terreo_loja):
    """1/4 do corpo da torre em coordenadas locais. g = corpo e detalhes, gc = guarda-corpos.
    terreo_loja: no terreo este quadrante tem o hall e os espacos de uso comum no lugar do final do meio."""
    H = npav * PD
    Hp = H + PARAPEITO
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    # paredes externas: (eixo, coordenada, a0, a1, material, lado de fora: +1 = sentido do quadrante, -1 = para o eixo)
    paredes = [
        ('y', Y_FACE, 0.0, X_C, 'fachada_azul', 1),               # faixa central (atras das lajes tecnicas)
        ('x', X_C, Y_FACE, Y_BUMP, 'fachada_azul', -1),           # saliencia do dormitorio do meio
        ('y', Y_BUMP, X_C, X_B1, 'fachada_azul', 1),
        ('x', X_B1, Y_VAR, Y_BUMP, 'fachada_clara', 1),           # moldura branca das varandas (lado do meio)
        ('y', Y_FACE, X_V1, L2, 'fachada_media', 1),              # fachada da ponta
        ('x', L2, Y_NOTCH, Y_FACE, 'fachada_media', 1),           # testa
        ('y', Y_NOTCH, X_NOTCH, L2, 'fachada_media', -1),         # recorte da testa
        ('x', X_NOTCH, 0.0, Y_NOTCH, 'fachada_grafite', 1),
        ('x', X_V1, Y_VAR, Y_FACE, 'fachada_clara', -1),          # moldura branca (lado da ponta)
    ]
    for k, (ax, c, a0, a1, m, d) in enumerate(paredes):
        z0 = PD if (terreo_loja and k < 3) else 0.0      # terreo aberto em vitrine na faixa central e na saliencia
        if ax == 'x':
            _face_x(g, X_(c), Y_(a0), Y_(a1), z0, Hp, m, sx * d)
        else:
            _face_y(g, Y_(c), X_(a0), X_(a1), z0, Hp, m, sy * d)
    # cobertura (laje da platibanda) em retangulos que cobrem o quadrante
    tampa = [(0, X_C, 0, Y_FACE), (X_C, X_B1, 0, Y_BUMP), (X_B1, X_V1, 0, Y_VAR), (X_V1, X_NOTCH, 0, Y_FACE),
             (X_NOTCH, L2, Y_NOTCH, Y_FACE)]
    for x0, x1, y0, y1 in tampa:
        g.piso(min(X_(x0), X_(x1)), max(X_(x0), X_(x1)), min(Y_(y0), Y_(y1)), max(Y_(y0), Y_(y1)), Hp, 'cobertura')
    # varandas (meio e ponta): fundo, divisoria, laje e guarda-corpo, pavimento a pavimento
    varandas = ((X_V0, X_DIV0), (X_DIV1, X_V1))
    for i in range(npav):
        z = i * PD
        loja = (i == 0 and terreo_loja)
        if loja:
            _terreo_loja(g, sx, sy)
        for k, (xa, xb) in enumerate(varandas):
            if loja and k == 0:
                continue
            _face_y(g, Y_(Y_VAR), X_(xa), X_(xb), z, z + PD, 'varanda_parede', sy)
            # laje: piso, borda branca e forro
            g.caixa(X_(xa), X_(xb), Y_(Y_VAR), Y_(Y_FACE + 0.04), z - (0.18 if i else 0), z + 0.12, 'laje_borda',
                    topo='varanda_piso', fundo='varanda_forro', sem_fundo=(i == 0))
            if i > 0:
                g.cil(X_((xa + xb) / 2), Y_(Y_VAR + 0.5), 0.09, z - 0.2, z - 0.185, 'luz_forro', seg=8, tampa=False, base=True)
                gq = [(X_(xa + 0.05), Y_(Y_FACE), z + 0.12), (X_(xb - 0.05), Y_(Y_FACE), z + 0.12),
                      (X_(xb - 0.05), Y_(Y_FACE), z + 1.22), (X_(xa + 0.05), Y_(Y_FACE), z + 1.22)]
                if sx * sy < 0:
                    gq = [gq[1], gq[0], gq[3], gq[2]]
                gc.face(gq, 'guarda_corpo', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)] if sx * sy > 0 else [(1, 0), (0, 0), (0, 1), (1, 1)], cor=1.0)
        # divisoria entre a varanda do meio e a da ponta (parede cheia branca)
        if True:
            g.caixa(X_(X_DIV0), X_(X_DIV1), Y_(Y_VAR), Y_(Y_FACE), z, z + PD, 'fachada_clara')
        # painel colorido na parede lateral da varanda da ponta (alternando com os andares)
        pn = PAINEIS[(i + (0 if sx > 0 else 3) + (0 if sy > 0 else 1)) % 6]
        if pn and i > 0:
            _face_y(g, Y_(Y_VAR + 0.012), X_(X_V1 - 1.25), X_(X_V1), z + 0.12, z + PD - 0.18, pn, sy)
        # laje tecnica da suite do meio (faixa central) e do dormitorio 2 da ponta (recorte da testa)
        if i > 0 or not loja:
            g.caixa(X_(0.0), X_(X_C), Y_(Y_FACE), Y_(Y_LT), z + 0.30, z + 0.42, 'prumada_escura')
            g.painel(X_(0.55), Y_(Y_LT), X_(X_C), Y_(Y_LT), z + 0.42, z + PD + 0.30, 'brise', (0, 0, X_C / 0.5, PD / 0.5))
        if i == 0:
            g.caixa(X_(0.0), X_(0.55), Y_(Y_FACE), Y_(Y_LT + 0.02), PD if loja else 0.0, Hp, 'prumada_escura', topo='cobertura')
        if i > 0:
            g.caixa(X_(X_NOTCH), X_(X_NOTCH + 0.62), Y_(0.0), Y_(Y_NOTCH), z, z + 0.10, 'laje_borda')
        # janelas
        for plano, c, (a0, a1), m in JANELAS:
            zz = JANELA_BANHO if m == 'janela_banheiro' else JANELA_DORM
            if loja and (c == Y_BUMP or a1 <= X_C):
                continue
            _janela(g, plano, c, a0, a1, z + zz[0], z + zz[1], m, sx, sy)
        # friso de laje na ponta e na faixa azul
        if i > 0:
            g.caixa(X_(X_V1), X_(L2), Y_(Y_FACE), Y_(Y_FACE + 0.025), z - 0.02, z + 0.02, 'laje_borda')
            g.caixa(X_(X_C), X_(X_B1), Y_(Y_BUMP), Y_(Y_BUMP + 0.025), z - 0.02, z + 0.02, 'fachada_grafite')
    # forro e platibanda sobre o vao das varandas
    for xa, xb in varandas:
        g.piso(min(X_(xa), X_(xb)), max(X_(xa), X_(xb)), min(Y_(Y_VAR), Y_(Y_FACE)), max(Y_(Y_VAR), Y_(Y_FACE)), H, 'varanda_forro')
        g.caixa(X_(xa), X_(xb), Y_(Y_VAR), Y_(Y_FACE + 0.04), H, Hp, 'fachada_clara', topo='cobertura')
    g.caixa(X_(X_DIV0), X_(X_DIV1), Y_(Y_VAR), Y_(Y_FACE), H, Hp, 'fachada_clara', topo='cobertura')
    # moldura branca: pilares de frente nas pontas das varandas, de cima a baixo
    for xx in (X_B1, X_V1):
        g.caixa(X_(xx - 0.12), X_(xx + 0.12), Y_(Y_FACE - 0.02), Y_(Y_FACE + 0.10), 0.0, Hp, 'fachada_clara', topo='cobertura')


def _terreo_loja(g, sx, sy):
    """Terreo do lado -y no lugar do final do meio: vitrine dos espacos comuns (brinquedoteca e mini market na
    T1, coworking e pilates na T2) e, no quadrante -x, a porta do hall com marquise na faixa central."""
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    yv = Y_FACE - 0.3

    def vitrine(xa, xb, yy, n):
        g.caixa(X_(xa), X_(xb), Y_(yy), Y_(yy + 0.03), 0.12, PD - 0.14, 'vidro_porta')
        for k in range(n + 1):
            xx = xa + (xb - xa) * k / n
            g.caixa(X_(xx - 0.03), X_(xx + 0.03), Y_(yy), Y_(yy + 0.06), 0.12, PD - 0.14, 'ferragem')
        g.caixa(X_(xa), X_(xb), Y_(yy), Y_(yy + 0.06), 2.30, 2.36, 'ferragem')

    vitrine(0.0, X_B1, yv, 4)
    vitrine(X_V0, X_DIV0, Y_VAR, 3)
    g.caixa(X_(0.0), X_(X_B1), Y_(yv), Y_(Y_BUMP), PD - 0.14, PD, 'laje_borda', fundo='varanda_forro', sem_fundo=False)
    g.piso(min(X_(0.0), X_(X_B1)), max(X_(0.0), X_(X_B1)), min(Y_(yv), Y_(Y_BUMP)), max(Y_(yv), Y_(Y_BUMP)), 0.125, 'varanda_piso')
    g.piso(min(X_(X_V0), X_(X_DIV1)), max(X_(X_V0), X_(X_DIV1)), min(Y_(Y_VAR), Y_(Y_FACE)), max(Y_(Y_VAR), Y_(Y_FACE)), 0.125, 'varanda_piso')
    if sx < 0:
        g.caixa(X_(0.5), X_(2.7), Y_(Y_BUMP - 0.98), Y_(Y_FACE + 2.2), PD - 0.02, PD + 0.12, 'laje_borda', fundo='varanda_forro', sem_fundo=False)
        for xx in (1.0, 2.2):
            g.caixa(X_(xx - 0.04), X_(xx + 0.04), Y_(yv - 0.01), Y_(yv + 0.07), 0.12, PD - 0.14, 'ferragem')


def _cobertura(g, npav):
    """Caixa d'agua, casa de maquinas dos elevadores e barrilete sobre o nucleo."""
    Hp = npav * PD + PARAPEITO
    g.caixa(-3.4, 3.4, -2.0, 2.0, Hp - 0.6, Hp + 3.4, 'fachada_clara', topo='cobertura')
    g.caixa(-1.4, 1.4, -2.9, -2.0, Hp - 0.6, Hp + 2.3, 'fachada_grafite', topo='cobertura')
    g.caixa(-3.5, 3.5, -2.1, 2.1, Hp + 3.4, Hp + 3.55, 'laje_borda', topo='cobertura')
    for xx in (-2.8, 2.8):
        g.caixa(xx - 0.03, xx + 0.03, -2.1, -2.04, Hp + 3.55, Hp + 4.3, 'ferragem')
        g.caixa(xx - 0.03, xx + 0.03, 2.04, 2.1, Hp + 3.55, Hp + 4.3, 'ferragem')
    # condensadoras e antenas soltas na laje (quebram a cobertura lisa)
    for xx, yy in ((9.0, 3.0), (-9.0, 3.0), (9.0, -3.0), (-9.0, -3.0), (14.5, 0.8), (-14.5, -0.8)):
        g.caixa(xx - 0.5, xx + 0.5, yy - 0.35, yy + 0.35, Hp - 0.6, Hp - 0.0, 'parede_externa', topo='telha')


def torre(n, cx, cy, npav, gc):
    """Torre n em (cx, cy) metros. Corpo + detalhes num objeto so ('torre-n'); guarda-corpos acumulados em gc."""
    g = Geo('torre-%d' % n, ao=False)
    with g.em(cx, cy, 0.0, 0.0):
        with gc.em(cx, cy, 0.0, 0.0):
            for sx in (1, -1):
                for sy in (1, -1):
                    quadrante(g, gc, sx, sy, npav, terreo_loja=(sy < 0))
        _cobertura(g, npav)
    return g.objeto()


# ------------------------------------------------------------------ malha "unidades" (contrato com a pagina)
FINAIS = {   # face local (+1 = +y, -1 = -y) e faixa em x (local) da varanda de cada final
    '06': (1, -X_V1, -X_DIV1), '05': (1, -X_DIV0, -X_V0), '04': (1, X_V0, X_DIV0), '03': (1, X_DIV1, X_V1),
    '07': (-1, -X_V1, -X_DIV1), '08': (-1, -X_DIV0, -X_V0), '01': (-1, X_V0, X_DIV0), '02': (-1, X_DIV1, X_V1),
}
UN_OFF = 0.04          # quad 4 cm a frente do fundo da varanda
SEM_UNIDADE_TERREO = ('01', '08')   # FAQ: terreo com 6 gardens; no lugar dos finais 1 e 8 ficam o hall e o lazer
Z_UN = (0.14, -0.16)


def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for t, (cxp, cyp) in sorted(PL.TORRES.items()):
        cx, cy = X(cxp), Y(cyp)
        for fin, (s, xa, xb) in FINAIS.items():
            y = s * (Y_VAR + UN_OFF)
            x0, x1 = min(xa, xb) + 0.08, max(xa, xb) - 0.08
            for andar in range(PL.PAVIMENTOS[t]):
                if andar == 0 and fin in SEM_UNIDADE_TERREO:
                    continue
                z0 = andar * PD + Z_UN[0]
                z1 = (andar + 1) * PD + Z_UN[1]
                loc = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)] if s > 0 else [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
                k = len(verts)
                verts += [(cx + p[0], cy + p[1], p[2]) for p in loc]
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
        'schema': 'avm-unidades-layout/1',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': {str(k): v for k, v in PL.PAVIMENTOS.items()},
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]',
        'z_rel': list(Z_UN),
        'plano': 'fundo da varanda: y_local = face*(%.2f + %.2f); a fachada fica %.2f m a frente' % (Y_VAR, UN_OFF, Y_FACE - Y_VAR),
        'sem_unidade_no_terreo': list(SEM_UNIDADE_TERREO),
        'torres': {},
    }
    for t, (cxp, cyp) in sorted(PL.TORRES.items()):
        out['torres']['torre-%d' % t] = {'centro': [round(X(cxp), 3), round(Y(cyp), 3), 0.0], 'rotacao_z_graus': 0.0,
                                         'finais': {f: {'face_local': '+y' if s > 0 else '-y', 'x_local': [xa, xb]}
                                                    for f, (s, xa, xb) in FINAIS.items()}}
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ modulos (mesmo namespace)
def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())


_carrega('avm_geo.py')
_pl = {}
exec(compile(open(SCR + '/avm_planta.py').read(), SCR + '/avm_planta.py', 'exec'), _pl)


class _Plano:
    pass


PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper():
        setattr(PL, _k, _v)
assert abs(PL.S_PX - S_PX) < 1e-9 and PL.ORIGEM_PX == ORIGEM_PX, 'avm_geo.X/Y fora de sincronia com avm_planta'
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
_carrega('avm_patio.py')
_carrega('avm_paisagem.py')
_carrega('avm_lazer.py')

# ------------------------------------------------------------------ main
OBJETOS_EXPORTADOS = []


def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer()
    gc = Geo('guarda-corpo', ao=False)
    nomes = ['unidades', 'guarda-corpo', 'entorno', 'entorno-rua', 'terreno', 'garagem', 'lazer', 'vegetacao', 'carros']
    for t, (cxp, cyp) in sorted(PL.TORRES.items()):
        torre(t, X(cxp), Y(cyp), PL.PAVIMENTOS[t], gc)
        nomes.append('torre-%d' % t)
    gc.objeto()
    _, nun = unidades()
    t = Geo('terreno', ao=False)
    chao(t)
    muros_perimetro(t)
    jardins_torres(t)
    t.objeto()
    gg = Geo('garagem', ao=False)
    garagem(gg)
    gg.objeto()
    e = Geo('entorno', ao=False)
    e.piso(-4000, 4000, -4000, 4000, -0.04, 'entorno')
    e.objeto()
    r = Geo('entorno-rua', ao=False)     # separado: nao entra no enquadramento da sombra
    ruas(r)
    r.objeto()
    lz = Geo('lazer')
    lazer(lz)
    lz.objeto()
    vg = Geo('vegetacao', ao=False)
    paisagem(vg)
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
