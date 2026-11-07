# gaia_modelo.py -- reconstroi do zero a cena do Village Gaia em alta fidelidade.
# Roda DENTRO do Blender (execute: __file__ = <este arquivo>; exec). Unidades em metros, Z para cima,
# origem no centro do terreno. Modulos executados no mesmo namespace:
#   gaia_geo.py (geometria)  gaia_patio.py (chao, vagas, muros)  gaia_lazer.py (edificios e areas externas)
#   gaia_moveis.py (mobiliario)  gaia_paisagem.py (arvores, palmeiras, canteiros, carros)
# Medidas: gaia_planta.py (px da implantacao) e FAQ do book. Texturas: gaia_tex.py (fora do Blender).
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/village-gaia/scripts
TEXDIR = SCR + '/tex'

# ------------------------------------------------------------------ parametros da torre
PD = 2.9            # pe-direito piso a piso
NPAV = 20           # andar 0 (terreo/garden) + 19 tipo
H = PD * NPAV       # 58.0 topo da ultima laje
PARAPEITO = 1.6     # platibanda
L = 39.0            # fachada de ponta a ponta (book, FAQ 1)
HW = 6.0            # meia largura do corpo (planta-chave: 12,0 m)
BUMP = 7.0          # saliencia dos dormitorios dos aptos de meio (+1,0 m)
LAJE_TEC = 5.4      # parede atras da laje tecnica central (-0,6 m)
VAR_FUNDO = 4.9     # fundo das varandas (loggia de 1,1 m)
Y_BUMP0, Y_BUMP1 = 2.9, 5.7
Y_VAR0, Y_DIV, Y_VAR1 = 5.95, 9.9, 14.0
Y_GRAF1 = 16.6
NOTCH_X, NOTCH_D = 2.5, 2.0
TILE = 2.9          # reboco: 1 repeticao por pavimento (junta sempre na laje)

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
    # cores medidas em 02-torre.jpg, sem o azul do ceu
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.9, img_mean=0.88, uv=TILE)
    mat('fachada_clara', '#94918f', 0.93, **kw)
    mat('fachada_grafite', '#59575a', 0.93, **kw)
    mat('prumada_escura', '#423f44', 0.93, **kw)
    mat('laje_borda', '#aaa6a2', 0.92, **kw)
    mat('cobertura', '#7c7a7d', 0.95, **kw)
    mat('varanda_forro', '#e0d4bf', 0.9)
    mat('varanda_parede', '#cfc4b3', 0.9)
    mat('janela_veneziana', '#ffffff', 0.4, img='veneziana2.png', emit_img='veneziana2_luz.jpg')
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')
    mat('guarda_corpo', '#ffffff', 0.45, img='guarda_corpo2.png', recorte=True)
    mat('unidade', '#2b3440', 0.2, img='porta_unidade2.png', tint=True, img_mean=0.7)
    mat('caixilho', '#ece9e2', 0.45)
    mat('vidro_porta', '#3a4a58', 0.08, metal=0.2)
    mat('luz_forro', '#fff4dc', 0.5)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)

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

# ------------------------------------------------------------------ torre (Builder em bmesh: malha de picking)
class Builder:
    """Acumula caixas/quads num bmesh com material por face e UV de projecao por eixo."""
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.mats = []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _uv(self, f, scale):
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            co = l.vert.co
            if ax == 2:
                u, v = co.x / scale[0], co.y / scale[0]
            elif ax == 0:
                u, v = co.y / scale[0], co.z / scale[1]
            else:
                u, v = co.x / scale[0], co.z / scale[1]
            l[self.uv].uv = (u, v)

    def box(self, x0, x1, y0, y1, z0, z1, m, mside=None, mtop=None, mbot=None, scale=(TILE, TILE)):
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        bm = self.bm
        v = [bm.verts.new(c) for c in (
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
        faces = [((0, 3, 2, 1), mbot or m), ((4, 5, 6, 7), mtop or m),
                 ((0, 1, 5, 4), mside or m), ((1, 2, 6, 5), m),
                 ((2, 3, 7, 6), mside or m), ((3, 0, 4, 7), m)]
        for idx, mm in faces:
            f = bm.faces.new([v[i] for i in idx])
            f.material_index = self.mi(mm)
            f.normal_update()
            self._uv(f, scale)

    def quad_x(self, x, y0, y1, z0, z1, m, outward=1, uvfit=False):
        bm = self.bm
        y0, y1 = min(y0, y1), max(y0, y1)
        cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)] if outward > 0 else [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        f.material_index = self.mi(m)
        f.normal_update()
        if uvfit:
            for l, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                l[self.uv].uv = uv
        else:
            self._uv(f, (TILE, TILE))
        return f

    def quad_y(self, y, x0, x1, z0, z1, m, outward=1, uvfit=False):
        bm = self.bm
        x0, x1 = min(x0, x1), max(x0, x1)
        cs = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)] if outward > 0 else [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        f.material_index = self.mi(m)
        f.normal_update()
        if uvfit:
            for l, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                l[self.uv].uv = uv
        else:
            self._uv(f, (TILE, TILE))
        return f

    def to_object(self, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.name, me)
        ob.location = loc
        bpy.context.scene.collection.objects.link(ob)
        return ob

# aberturas pelas plantas (quadrante +x/+y local; o resto e espelhado). Escala das plantas: 129,3 px/m.
# Banheiros dos aptos de meio ventilam por shaft (sem janela na fachada).
JANELA_DORM = (0.85, 2.20)    # peitoril e verga (z relativo ao piso do andar), dormitorios
JANELA_BANHO = (1.55, 2.15)   # basculante alto dos banheiros
JANELAS = [
    ('face', 'x', HW, (17.50, 18.69), 'janela_veneziana', 'ponta: dormitorio 1 (casal)'),
    ('face', 'x', HW, (15.87, 16.48), 'janela_banheiro', 'ponta: banheiro 1'),
    ('face', 'x', HW, (14.47, 15.09), 'janela_banheiro', 'ponta: banheiro 2'),
    ('recorte', 'y', L / 2 - NOTCH_D, (0.82, 1.98), 'janela_veneziana', 'ponta: dormitorio 2 (no recorte)'),
    ('saliencia', 'x', BUMP, (3.92, 5.12), 'janela_veneziana', 'meio: dormitorio 2 (saliencia)'),
    ('laje_tec', 'x', LAJE_TEC, (1.29, 2.45), 'janela_veneziana', 'meio: dormitorio 1 (sobre a laje tecnica)'),
]
# ambientes de lazer no terreo, no quadrante +x/-y (planta: 23 a 29). Local: distancia aos eixos.
SALA1 = dict(x=(1.4, 5.4), y=(0.15, 3.0))     # 11 m2: spa, mini market, cinema
SALA2 = dict(x=(0.9, 4.9), y=(5.95, 9.6))     # 15 m2: beauty, lavanderia, coworking

def _moldura(ge, plano, c, sx, sy, a0, a1, z0, z1):
    """Caixilho em relevo em volta da janela + peitoril: da sombra e tira o aspecto de adesivo."""
    e, f = 0.05, 0.045
    S_ = (sx if plano == 'x' else sy)
    if plano == 'x':
        def bx(y0, y1, zz0, zz1, ee=e, mat='caixilho'):
            xa, xb = sx * c, sx * (c + ee)
            ge.caixa(xa, xb, sy * y0, sy * y1, zz0, zz1, mat)
    else:
        def bx(x0, x1, zz0, zz1, ee=e, mat='caixilho'):
            ya, yb = sy * c, sy * (c + ee)
            ge.caixa(sx * x0, sx * x1, ya, yb, zz0, zz1, mat)
    bx(a0 - f, a1 + f, z0 - 0.03, z0 + f - 0.03, ee=0.09)    # peitoril
    bx(a0 - f, a1 + f, z1, z1 + f)
    bx(a0 - f, a0, z0, z1)
    bx(a1, a1 + f, z0, z1)

def quadrante(b, g, ge, sx, sy, comercial):
    """1/4 da torre. b = corpo (picking), g = guarda-corpos, ge = detalhes (coordenadas locais da torre).
    comercial: quadrante +x/-y, com os ambientes de lazer no terreo."""
    M = MATS
    X_ = lambda v: v * sx
    Y_ = lambda v: v * sy
    Hp = H + PARAPEITO
    z_sala1 = PD if comercial else 0
    z_sala2 = PD if comercial else 0
    z_hall = 0
    forro = M['varanda_forro']
    b.box(0, X_(LAJE_TEC), 0, Y_(Y_BUMP0), z_sala1, H + 0.6, M['prumada_escura'], mtop=M['cobertura'], mbot=forro)
    b.box(X_(LAJE_TEC), X_(BUMP), Y_(Y_BUMP0), Y_(Y_BUMP0 + 0.45), 0, Hp + 0.8, M['fachada_grafite'], mtop=M['cobertura'])
    b.box(X_(LAJE_TEC), X_(BUMP), Y_(Y_BUMP0 + 0.45), Y_(Y_BUMP1), 0, Hp + 0.8, M['fachada_clara'], mtop=M['cobertura'])
    # miolo atras das varandas: no quadrante comercial o terreo da final 08 vira sala
    b.box(0, X_(VAR_FUNDO), Y_(Y_BUMP0), Y_(Y_VAR0), 0, H, M['varanda_parede'], mtop=M['cobertura'])
    b.box(0, X_(VAR_FUNDO), Y_(Y_VAR0), Y_(Y_DIV), z_sala2, H, M['varanda_parede'], mtop=M['cobertura'], mbot=forro)
    b.box(0, X_(VAR_FUNDO), Y_(Y_DIV), Y_(Y_VAR1), 0, H, M['varanda_parede'], mtop=M['cobertura'])
    b.box(0, X_(LAJE_TEC), Y_(Y_BUMP1), Y_(Y_VAR0), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(X_(LAJE_TEC - 0.01), X_(HW), Y_(Y_BUMP1), Y_(Y_VAR0), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(X_(VAR_FUNDO), X_(HW), Y_(Y_VAR0), Y_(Y_VAR1), H, Hp, M['laje_borda'], mtop=M['cobertura'])
    b.box(0, X_(VAR_FUNDO), Y_(Y_VAR0), Y_(Y_VAR1), H, Hp - 0.4, M['cobertura'])
    b.box(0, X_(HW), Y_(Y_VAR1), Y_(Y_GRAF1), 0, Hp, M['fachada_grafite'], mtop=M['cobertura'])
    b.box(X_(NOTCH_X), X_(HW), Y_(Y_GRAF1), Y_(L / 2), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(0, X_(NOTCH_X), Y_(Y_GRAF1), Y_(L / 2 - NOTCH_D), 0, Hp, M['fachada_grafite'], mtop=M['cobertura'])

    # sem final 1 e 8 no terreo (planilha e implantacao): face +x so tem unidade garden nas pontas
    for i in range(NPAV):
        z = i * PD
        for k, (ya, yb) in enumerate(((Y_VAR0, Y_DIV), (Y_DIV, Y_VAR1))):
            sem_garden = (i == 0 and sx > 0 and k == 0)
            if i > 0:
                b.box(X_(VAR_FUNDO), X_(HW + 0.03), Y_(ya), Y_(yb), z - 0.15, z + 0.35, M['laje_borda'], mbot=forro)
            elif not sem_garden:
                b.box(X_(VAR_FUNDO), X_(HW + 0.03), Y_(ya), Y_(yb), z, z + 0.35, M['laje_borda'])
            if not sem_garden:
                g.quad_x(X_(HW), Y_(ya + 0.05), Y_(yb - 0.05), z + 0.35, z + 1.10, M['guarda_corpo'], outward=sx, uvfit=True)
                # plafon de LED no forro da varanda (aceso a noite)
                ym = (ya + yb) / 2
                ge.cil(X_(5.45), Y_(ym), 0.09, z + PD - 0.17, z + PD - 0.155, 'luz_forro', seg=8, tampa=False, base=True)
        if not (i == 0 and sx > 0):
            b.box(X_(VAR_FUNDO), X_(HW), Y_(Y_DIV - 0.08), Y_(Y_DIV + 0.08), z, z + PD, M['laje_borda'])
        else:
            b.box(X_(VAR_FUNDO), X_(HW), Y_(Y_DIV - 0.15), Y_(Y_DIV + 0.15), z, z + PD, M['fachada_clara'])
        b.box(X_(LAJE_TEC), X_(HW), 0, Y_(Y_BUMP0), z + PD - 0.18, z + PD, M['prumada_escura'], mbot=forro)
        for _t, plano, c, (a0, a1), mn, _d in JANELAS:
            if sx > 0 and i == 0 and _t == 'laje_tec':
                continue                                # terreo: vitrine da sala 1 e hall de entrada
            zz = JANELA_BANHO if mn == 'janela_banheiro' else JANELA_DORM
            if plano == 'x':
                b.quad_x(X_(c + 0.01), Y_(a0), Y_(a1), z + zz[0], z + zz[1], M[mn], outward=sx, uvfit=True)
            else:
                b.quad_y(Y_(c + 0.01), X_(a0), X_(a1), z + zz[0], z + zz[1], M[mn], outward=sy, uvfit=True)
            _moldura(ge, plano, c + 0.01, sx, sy, a0, a1, z + zz[0], z + zz[1])
        b.box(0, X_(NOTCH_X), Y_(L / 2 - NOTCH_D), Y_(L / 2 - 1.4), z + PD - 0.15, z + PD, M['prumada_escura'])
    if sy > 0:
        b.box(X_(LAJE_TEC), X_(HW - 0.05), -0.08, 0.08, 0, H, M['prumada_escura'])
    if sx > 0 and sy > 0:
        # caixa d'agua, casa de maquinas e guarda de cobertura
        b.box(-3.2, 3.2, -4.0, 4.0, Hp - 0.4, Hp + 3.6, M['fachada_clara'], mtop=M['cobertura'])
        b.box(-1.6, 1.6, 4.0, 6.6, Hp - 0.4, Hp + 2.2, M['fachada_grafite'], mtop=M['cobertura'])
        for yy in (-4.0, 4.0):
            ge.caixa(-3.25, 3.25, yy - 0.03, yy + 0.03, Hp + 3.6, Hp + 3.7, 'ferragem')
        for xx in (-2.8, 0, 2.8):
            ge.caixa(xx - 0.03, xx + 0.03, -4.0, 4.0, Hp + 3.6, Hp + 3.7, 'ferragem')
            ge.caixa(xx - 0.03, xx + 0.03, -3.9, -3.84, Hp + 3.6, Hp + 4.4, 'ferragem')
            ge.caixa(xx - 0.03, xx + 0.03, 3.84, 3.9, Hp + 3.6, Hp + 4.4, 'ferragem')
        for yy in (-3.87, 3.87):
            ge.caixa(-2.83, 2.83, yy - 0.03, yy + 0.03, Hp + 4.35, Hp + 4.42, 'ferragem')

def torre(nome, cx, cy, g):
    b = Builder(nome)
    gl = Builder('_tmp')
    ge = Geo(nome + '-det', ao=False)
    with ge.em(cx, cy):
        for sx in (1, -1):
            for sy in (1, -1):
                quadrante(b, gl, ge, sx, sy, sx > 0 and sy < 0)
        # hall de entrada na laje tecnica do lado +y: porta de vidro de 2 folhas com marquise
        ge.caixa(LAJE_TEC, LAJE_TEC + 0.03, 0.35, 2.55, 0.12, 2.5, 'vidro_porta')
        for yy in (0.33, 1.45, 2.57):
            ge.caixa(LAJE_TEC, LAJE_TEC + 0.06, yy - 0.04, yy + 0.04, 0.12, 2.5, 'ferragem')
        ge.caixa(LAJE_TEC, LAJE_TEC + 0.06, 0.29, 2.61, 2.46, 2.56, 'ferragem')
        for yy in (1.3, 1.6):
            ge.caixa(LAJE_TEC + 0.06, LAJE_TEC + 0.09, yy - 0.015, yy + 0.015, 0.95, 1.55, 'cromo')
        ge.caixa(LAJE_TEC, HW + 0.9, 0.0, 2.85, 2.62, 2.72, 'laje_borda', fundo='varanda_forro')
        # varanda coberta do terreo no lado +y (sem unidade): parede com a caixa de correio e banco
        ge.caixa(VAR_FUNDO, VAR_FUNDO + 0.02, Y_VAR0 + 0.5, Y_VAR0 + 3.5, 0.12, 2.75, 'ripado_claro')
        ge.caixa(VAR_FUNDO + 0.02, VAR_FUNDO + 0.42, Y_VAR0 + 0.9, Y_VAR0 + 3.1, 0.52, 0.56, 'madeira')
    ob = b.to_object((cx, cy, 0))
    me = bpy.data.meshes.new('_tmpgc'); gl.bm.to_mesh(me); gl.bm.free()
    me.transform(__import__('mathutils').Matrix.Translation((cx, cy, 0)))
    g.bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    return ge.objeto()

# ------------------------------------------------------------------ malha "unidades" (contrato com a pagina)
FINAIS = {   # face, faixa horizontal (y local) da varanda principal de cada final
    '06': ('-x', -Y_VAR1, -Y_DIV), '05': ('-x', -Y_DIV, -Y_VAR0),
    '04': ('-x', Y_VAR0, Y_DIV),   '03': ('-x', Y_DIV, Y_VAR1),
    '07': ('+x', -Y_VAR1, -Y_DIV), '08': ('+x', -Y_DIV, -Y_VAR0),
    '01': ('+x', Y_VAR0, Y_DIV),   '02': ('+x', Y_DIV, Y_VAR1),
}
UN_OFF = 0.05          # quad 5 cm a frente da parede do fundo da varanda
SEM_UNIDADE_TERREO = ('01', '08')  # planilha: terreo so tem finais 2 a 7; ali ficam hall e lazer

def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for t, (nome, (cx, cy)) in enumerate(TORRES.items(), start=1):
        for fin, (face, ya, yb) in FINAIS.items():
            sgn = 1 if face == '+x' else -1
            x = cx + sgn * (VAR_FUNDO + UN_OFF)
            y0, y1 = cy + min(ya, yb) + 0.10, cy + max(ya, yb) - 0.10
            for andar in range(NPAV):
                if andar == 0 and fin in SEM_UNIDADE_TERREO:
                    continue
                z0 = andar * PD + 0.35
                z1 = (andar + 1) * PD - 0.15
                cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)] if sgn > 0 else [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
                k = len(verts)
                verts += cs
                faces.append((k, k + 1, k + 2, k + 3))
                larg = abs(yb - ya) - 0.20
                uvs += [((abs(abs(p[1] - cy) - Y_DIV) - 0.10) / larg, 0 if p[2] == z0 else 1) for p in cs]
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
        'schema': 'gaia-unidades-layout/3',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': NPAV,
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]',
        'z_rel': [0.35, -0.15],
        'plano': 'fundo da varanda: x_plano = centro + normal*(4,9 + 0,05)',
        'sem_unidade_no_terreo': list(SEM_UNIDADE_TERREO),
        'torres': {},
    }
    for nome, (cx, cy) in TORRES.items():
        t = {'centro': [round(cx, 3), round(cy, 3), 0.0], 'rotacao_z_graus': 0.0, 'finais': {}}
        for fin, (face, ya, yb) in FINAIS.items():
            sgn = 1 if face == '+x' else -1
            t['finais'][fin] = {
                'elemento': 'varanda (fundo)', 'face': face, 'normal': [sgn, 0, 0],
                'x_plano': round(cx + sgn * (VAR_FUNDO + UN_OFF), 3),
                'y_faixa': [round(cy + min(ya, yb) + 0.1, 3), round(cy + max(ya, yb) - 0.1, 3)],
            }
        out['torres'][nome] = t
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ modulos (mesmo namespace)
def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())

_carrega('gaia_geo.py')
_pl = {}
exec(compile(open(SCR + '/gaia_planta.py').read(), SCR + '/gaia_planta.py', 'exec'), _pl)
class _Plano: pass
PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper():
        setattr(PL, _k, _v)
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
ATL = json.load(open(TEXDIR + '/atlas_lazer.json'))
TORRES = {
    'torre-1': (X(PL.TORRES_PX[1]), Y(PL.TORRE_Y)),
    'torre-2': (X(PL.TORRES_PX[1]) - (44.16 + 2 * (BUMP - 0.05)), Y(PL.TORRE_Y)),
    'torre-3': (X(PL.TORRES_PX[1]) - (44.16 + 44.46 + 4 * (BUMP - 0.05)), Y(PL.TORRE_Y)),
}
_carrega('gaia_patio.py')
_carrega('gaia_paisagem.py')
_carrega('gaia_lazer.py')
_carrega('gaia_moveis.py')

# ------------------------------------------------------------------ main
OBJETOS_EXPORTADOS = []

def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer(); materiais_moveis()
    g = Builder('guarda-corpo')
    nomes = ['unidades', 'guarda-corpo', 'entorno', 'entorno-rua', 'terreno', 'lazer', 'moveis', 'vegetacao', 'carros']
    for nome, (cx, cy) in TORRES.items():
        det = torre(nome, cx, cy, g)
        nomes += [nome, det.name]
    g.mats = [MATS['guarda_corpo']]
    g.to_object()
    _, nun = unidades()
    # chao e muros
    t = Geo('terreno', ao=False)
    chao(t)
    for c in PL.TORRES_PX.values():
        jardim_torre(t, c)
    muros_perimetro(t)
    cisternas_e_bombas(t)
    t.objeto()
    e = Geo('entorno', ao=False)
    dx0, dx1, dy0, dy1 = RM(PL.DECK)     # sem chao sob a piscina
    for a_, b_, c_, d_ in ((-4000, dx0, -4000, 4000), (dx1, 4000, -4000, 4000), (dx0, dx1, -4000, dy0), (dx0, dx1, dy1, 4000)):
        e.piso(a_, b_, c_, d_, -0.04, 'entorno')
    e.objeto()
    r = Geo('entorno-rua', ao=False)     # separado: nao entra no enquadramento da sombra
    rua_lateral(r)
    r.objeto()
    # lazer
    lz = Geo('lazer')
    lazer(lz)
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
    OBJETOS_EXPORTADOS[:] = nomes
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun, 'materiais': len(bpy.data.materials)}

result['build'] = build()
