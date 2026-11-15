# jbo_modelo.py -- reconstroi do zero a cena do Reserva Direcional Jardim Botanico (maquete externa, etapa 1: tres
# torres, implantacao, edificio-garagem e lazer em volumes). Roda DENTRO do Blender (run_all.py ou
# Blender -b --factory-startup -P run_all.py). Metros, Z para cima, origem perto do centro do lote (jbo_planta.ORIGEM_PX).
# Modulos executados no mesmo namespace:
#   jbo_geo.py (geometria)  jbo_torre.py (forma da torre)  jbo_patio.py (chao, vagas, garagem, muros)
#   jbo_lazer.py (lazer e apoio em volumes)  jbo_paisagem.py (arvores, palmeiras, carros)
# Medidas: jbo_planta.py (px da implantacao), jbo_torre.py (m) e a ficha tecnica; chao: tex/chao.json (jbo_chao.py).
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/jardim-botanico/scripts
TEXDIR = SCR + '/tex'


def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())


_carrega('jbo_torre.py')          # PD, LAJE, NPAV, contorno, aberturas, existe()...
PARAPEITO = 1.20                  # platibanda da cobertura
TILE = PD                         # reboco: 1 repeticao por pavimento (junta na laje)

GRADE_TORRES = [1, 2, 3]
GRADE_ANDARES, GRADE_FINAIS = max(NPAV.values()), FINAIS


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
    # cores da perspectiva GUI_01_Fachada: blocos em cinza claro com a base em cinza medio, recuo da suite do meio em
    # cinza medio, recuos da cozinha e o entorno das varandas em azul-grafite, venezianas e caixilhos brancos,
    # guarda-corpo de barras brancas
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.6, img_mean=0.88, uv=TILE)
    mat('fachada_clara', '#dcdcd9', 0.93, **kw)
    mat('fachada_media', '#a3a4a6', 0.93, **kw)
    mat('fachada_escura', '#3e434d', 0.9, **kw)
    mat('laje_borda', '#d6d6d3', 0.92, **kw)
    mat('cobertura', '#8c8b88', 0.95, **kw)
    mat('varanda_parede', '#d4d1cb', 0.9, **kw)
    mat('varanda_forro', '#ecebe6', 0.9)
    mat('varanda_piso', '#b8ab9a', 0.8, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('gradil_varanda', '#f1f1ef', 0.45, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(0.6, 0.6))
    mat('pingadeira', '#dedcd6', 0.9)
    mat('janela_veneziana', '#e9e9e6', 0.4, img='veneziana2.png', tint=True, img_mean=0.8, emit_img='veneziana2_luz.jpg')
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')
    mat('unidade', '#2b3440', 0.2, img='porta_unidade2.png', tint=True, img_mean=0.7)
    mat('caixilho', '#ecebe8', 0.45)
    mat('vidro_porta', '#34444f', 0.08, metal=0.2)
    mat('vidro_lazer', '#4a5d68', 0.06, metal=0.15)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)
    mat('forro', '#ece7dd', 0.9)
    mat('luz_forro', '#fff4dc', 0.5)


# ------------------------------------------------------------------ geometria da torre (referencial local x, y)
TX = TY = 0.0                     # centro da torre em construcao (definido em torre())


def B(p, z=0.0):
    return (TX + p[0], TY + p[1], z)


def quad_n(g, a, b, z0, z1, m, n, uvs=None, cor=None):
    """Quad vertical entre os pontos de planta a, b com a normal virada para n (direcao em planta)."""
    cs = [B(a, z0), B(b, z0), B(b, z1), B(a, z1)]
    nn = _normal(cs)
    if nn[0] * n[0] + nn[1] * n[1] < 0:
        cs = [cs[1], cs[0], cs[3], cs[2]]
        if uvs is not None:
            uvs = [uvs[1], uvs[0], uvs[3], uvs[2]]
    g.face(cs, m, uvs=uvs, cor=cor)


def piso_n(g, x0, x1, y0, y1, z, m, cima=True):
    cs = [B((x0, y0), z), B((x1, y0), z), B((x1, y1), z), B((x0, y1), z)]
    if (_normal(cs)[2] > 0) != cima:
        cs = cs[::-1]
    g.face(cs, m)


def caixa_l(g, x0, x1, y0, y1, z0, z1, m, topo=None):
    g.caixa(TX + min(x0, x1), TX + max(x0, x1), TY + min(y0, y1), TY + max(y0, y1), z0, z1, m, topo=topo)


class Seg:
    """Trecho reto do contorno (anti-horario), com a normal para fora."""

    def __init__(self, a, b):
        self.a, self.b = a, b
        dx, dy = b[0] - a[0], b[1] - a[1]
        self.L = math.hypot(dx, dy)
        self.d = (dx / self.L, dy / self.L)
        self.n = (self.d[1], -self.d[0])
        self.pl = 'y' if abs(dy) < 1e-6 else 'x'
        self.c = a[1] if self.pl == 'y' else a[0]

    def P(self, t, off=0.0):
        return (self.a[0] + self.d[0] * t + self.n[0] * off, self.a[1] + self.d[1] * t + self.n[1] * off)

    def t_de(self, s):
        k = 0 if self.pl == 'y' else 1
        return (s - self.a[k]) / self.d[k]

    def quad(self, g, t0, t1, z0, z1, m, off=0.0, uvs=None, cor=None):
        if t1 - t0 < 1e-4 or z1 - z0 < 1e-4:
            return
        quad_n(g, self.P(t0, off), self.P(t1, off), z0, z1, m, self.n, uvs=uvs, cor=cor)

    def caixa(self, g, t0, t1, o0, o1, z0, z1, m, topo=None):
        p = [self.P(t0, o0), self.P(t1, o0), self.P(t1, o1), self.P(t0, o1)]
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        caixa_l(g, min(xs), max(xs), min(ys), max(ys), z0, z1, m, topo=topo)


def _segmentos(cont):
    out = []
    for i in range(len(cont)):
        a, b = cont[i], cont[(i + 1) % len(cont)]
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6:
            out.append(Seg(a, b))
    return out


def _dentro(p, cont):
    x, y = p
    c = False
    n = len(cont)
    for i in range(n):
        (x0, y0), (x1, y1) = cont[i], cont[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


ABERT = {f: aberturas(f) for f in range(1, FINAIS + 1)}
JAN_Z = {'dorm': (1.00, 2.20), 'banho': (1.60, 2.15), 'servico': (1.10, 2.20)}


def _feicoes(seg):
    """Janelas e varandas que caem neste trecho: lista (t0, t1, tipo, final, dados)."""
    out = []
    for f in range(1, FINAIS + 1):
        var, jans = ABERT[f]
        pl, c, a0, a1 = var['face']
        if pl == seg.pl and abs(c - seg.c) < 1e-6:
            t0, t1 = sorted((seg.t_de(a0), seg.t_de(a1)))
            if t0 >= -1e-6 and t1 <= seg.L + 1e-6:
                out.append((t0, t1, 'varanda', f, var))
        for j in jans:
            if j[0] == seg.pl and abs(j[1] - seg.c) < 1e-6:
                t0, t1 = sorted((seg.t_de(j[2]), seg.t_de(j[3])))
                if t0 >= -1e-6 and t1 <= seg.L + 1e-6:
                    out.append((t0, t1, 'janela', f, j))
    out.sort()
    return out


def _mat_parede(seg, andar):
    cls = classe_face(seg.a, seg.b)
    if cls in ('ponta', 'bloco'):
        lado = 1 if (seg.a[0] + seg.b[0]) > 0 else -1
        return 'fachada_clara' if andar >= CLARO_DESDE[(cls, lado)] else 'fachada_media'
    return 'fachada_media' if cls == 'suite' else 'fachada_escura'


def _janela(g, seg, t0, t1, z0, z1, m, mp):
    """Janela recuada 6 cm (quad com a textura inteira), requadro, caixilho branco e peitoril."""
    e = 0.05
    seg.quad(g, t0, t1, z0, z1, m, off=-0.06, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], cor=1.0)
    quad_n(g, seg.P(t0, -0.06), seg.P(t0, 0.0), z0, z1, mp, seg.d)
    quad_n(g, seg.P(t1, 0.0), seg.P(t1, -0.06), z0, z1, mp, (-seg.d[0], -seg.d[1]))
    for zz, cima in ((z0, True), (z1, False)):
        cs = [B(seg.P(t0, -0.06), zz), B(seg.P(t1, -0.06), zz), B(seg.P(t1, 0.0), zz), B(seg.P(t0, 0.0), zz)]
        if (_normal(cs)[2] > 0) != cima:
            cs = cs[::-1]
        g.face(cs, mp)
    seg.caixa(g, t0 - e, t1 + e, -0.06, 0.03, z1, z1 + e, 'caixilho')
    seg.caixa(g, t0 - e, t0, -0.06, 0.03, z0, z1, 'caixilho')
    seg.caixa(g, t1, t1 + e, -0.06, 0.03, z0, z1, 'caixilho')
    seg.caixa(g, t0 - 0.04, t1 + 0.04, -0.06, 0.05, z0 - 0.03, z0, 'pingadeira')


def _parede_com_furos(g, seg, t0, t1, z0, z1, m, furos):
    furos = sorted(f for f in furos if f[1] > t0 and f[0] < t1)
    t = t0
    for ta, tb, za, zb in furos:
        seg.quad(g, t, ta, z0, z1, m)
        seg.quad(g, ta, tb, z0, za, m)
        seg.quad(g, ta, tb, zb, z1, m)
        t = tb
    seg.quad(g, t, t1, z0, z1, m)


def _varanda(g, seg, t0, t1, torre, final, var, andar):
    """Loggia de um pavimento: borda da laje, guarda-corpo de barras brancas (1,10 m) no plano da fachada, paredes do
    fundo (porta de correr da sala, onde fica a malha "unidades") e laterais em azul-grafite, piso e forro. No terreo
    as unidades garden abrem para o jardim (sem guarda-corpo); no hall (01 do terreo) o fundo e de vidro."""
    z0 = andar * PD
    zt = z0 + PD - LAJE
    tem = existe(torre, andar, final)
    if andar > 0:
        seg.quad(g, t0, t1, z0 - LAJE, z0, 'fachada_escura')
        seg.caixa(g, t0, t1, -0.05, 0.0, z0 - LAJE, z0 + 0.001, 'fachada_escura')
    if tem and andar > 0:
        L = t1 - t0
        uv = [(0, 0), (L / 0.6, 0), (L / 0.6, 1.1 / 0.6), (0, 1.1 / 0.6)]
        seg.quad(g, t0, t1, z0, z0 + 1.10, 'gradil_varanda', off=-0.06, uvs=uv)
        quad_n(g, seg.P(t1, -0.06), seg.P(t0, -0.06), z0, z0 + 1.10, 'gradil_varanda', (-seg.n[0], -seg.n[1]), uvs=uv)
        seg.caixa(g, t0, t1, -0.09, -0.03, z0 + 1.08, z0 + 1.12, 'caixilho')
    pl, c, a0, a1 = var['face']
    s = var['sinal']
    fz = var['fundo']
    nf = (float(s), 0.0) if pl == 'x' else (0.0, float(s))
    if pl == 'x':
        pa, pb = (fz, a0), (fz, a1)
        lados = [((fz, a0), (c, a0), (0.0, 1.0)), ((fz, a1), (c, a1), (0.0, -1.0))]
        pisos = (min(fz, c), max(fz, c), a0, a1)
    else:
        pa, pb = (a0, fz), (a1, fz)
        lados = [((a0, fz), (a0, c), (1.0, 0.0)), ((a1, fz), (a1, c), (-1.0, 0.0))]
        pisos = (a0, a1, min(fz, c), max(fz, c))
    hall = (andar == 0 and final == 1)
    quad_n(g, pa, pb, z0, zt, 'vidro_lazer' if hall else 'varanda_parede', nf)
    for p0, p1, nl in lados:
        quad_n(g, p0, p1, z0, zt, 'fachada_escura', nl)
    piso_n(g, *pisos, z0 + 0.002, 'varanda_piso', cima=True)
    piso_n(g, *pisos, zt, 'varanda_forro', cima=False)
    if andar > 0 and tem:
        xm, ym = (pisos[0] + pisos[1]) / 2, (pisos[2] + pisos[3]) / 2
        g.cil(B((xm, ym))[0], B((xm, ym))[1], 0.08, zt - 0.012, zt, 'luz_forro', seg=8, tampa=False, base=True)


def _paredes(g, segs, torre):
    npav = NPAV[torre]
    for seg in segs:
        feic = _feicoes(seg)
        for andar in range(npav):
            z0, z1 = andar * PD, (andar + 1) * PD
            m = _mat_parede(seg, andar)
            furos = []
            for t0, t1, tipo, f, dados in feic:
                if tipo == 'varanda':
                    furos.append((t0, t1, z0, z1))
                    _varanda(g, seg, t0, t1, torre, f, dados, andar)
                    continue
                kind = dados[4]
                if existe(torre, andar, f):
                    za, zb = JAN_Z[kind]
                    mj = 'janela_veneziana' if kind == 'dorm' else 'janela_banheiro'
                    ta, tb = t0, t1
                else:      # hall no terreo: vidro do piso ate 2,4 m no lugar da janela
                    za, zb = 0.12, 2.40
                    mj = 'vidro_lazer'
                    ta, tb = max(0.05, t0 - 0.3), min(seg.L - 0.05, t1 + 0.3)
                furos.append((ta, tb, z0 + za, z0 + zb))
                _janela(g, seg, ta, tb, z0 + za, z0 + zb, mj, m)
            _parede_com_furos(g, seg, 0.0, seg.L, z0, z1, m, furos)
            for t0, t1, tipo, f, dados in feic:      # laje sobre a varanda do ultimo pavimento
                if tipo == 'varanda' and andar == npav - 1:
                    seg.quad(g, t0, t1, z1 - LAJE, z1, 'fachada_escura')


def _cobertura(g, torre, cont, segs):
    """Platibanda, laje de cobertura, nucleo (escada, elevadores, casa de maquinas) e caixa d'agua."""
    H = NPAV[torre] * PD
    Hp = H + PARAPEITO
    g.poligono([B(p)[:2] for p in cont], Hp, 'cobertura')
    for seg in segs:
        m = _mat_parede(seg, NPAV[torre])
        seg.quad(g, 0.0, seg.L, H, Hp, m)
        seg.caixa(g, 0.0, seg.L, -0.02, 0.06, Hp - 0.06, Hp, 'pingadeira')
    # nucleo: elevadores do lado de cima (T3 tem 3) e a escada no eixo, como na implantacao
    caixa_l(g, -3.4, 3.4, -1.9, 3.0, Hp - 0.6, Hp + 3.0, 'fachada_media', topo='cobertura')
    caixa_l(g, -3.5, 3.5, -2.0, 3.1, Hp + 3.0, Hp + 3.15, 'laje_borda', topo='cobertura')
    caixa_l(g, -2.4, 2.4, -1.4, 2.4, Hp + 3.15, Hp + 5.0, 'fachada_clara', topo='cobertura')
    for xx, yy in ((9.0, 3.0), (-9.0, -3.0), (14.5, -3.6), (-14.5, 3.6), (14.5, 3.6), (-14.5, -3.6)):
        caixa_l(g, xx - 0.5, xx + 0.5, yy - 0.35, yy + 0.35, Hp - 0.6, Hp - 0.02, 'fachada_media', topo='ferragem')


def _jardins(g):
    """Gradil baixo dos jardins das unidades garden do terreo (implantacao: linhas claras finas)."""
    def gradil(a, b, h=1.2):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        A, Bp = B(a), B(b)
        g.painel(A[0], A[1], Bp[0], Bp[1], 0.0, h, 'gradil_varanda', (0, 0, L / 0.6, h / 0.6))
        g.painel(Bp[0], Bp[1], A[0], A[1], 0.0, h, 'gradil_varanda', (0, 0, L / 0.6, h / 0.6))
        g.caixa(min(A[0], Bp[0]) - 0.02, max(A[0], Bp[0]) + 0.02, min(A[1], Bp[1]) - 0.02, max(A[1], Bp[1]) + 0.02,
                h - 0.04, h, 'caixilho')
    xt = JARDIM_TESTA_X
    for sx in (1, -1):
        gradil((sx * xt, -YQ), (sx * xt, YQ))
        gradil((sx * XT, YQ), (sx * xt, YQ))
        gradil((sx * XT, -YQ), (sx * xt, -YQ))
        gradil((sx * XV, 0.0), (sx * xt, 0.0))
    xa, xb, yb = JARDIM_BAIXO
    gradil((xa, yb), (xb, yb))
    gradil((xa, yb), (xa, -YB))
    gradil((xb, yb), (xb, -YB))
    gradil((0.0, -YB), (0.0, yb))
    xa, xb, yt = JARDIM_08
    gradil((xa, yt), (xb, yt))
    gradil((xa, YB), (xa, yt))
    gradil((xb, YV), (xb, yt))


def torre(t):
    global TX, TY
    TX, TY = X(PL.TORRES[t][0]), Y(PL.TORRES[t][1])
    g = Geo('torre-%d' % t, ao=False)
    cont = contorno()
    segs = _segmentos(cont)
    _paredes(g, segs, t)
    _cobertura(g, t, cont, segs)
    _jardins(g)
    return g.objeto()


# ------------------------------------------------------------------ malha "unidades" (contrato com a pagina)
UN_OFF = 0.04          # 4 cm a frente da parede do fundo da varanda (porta de correr da sala)
Z_UN = (0.06, -LAJE - 0.10)


def _quad_unidade(final):
    """(plano, coordenada, a0, a1, sinal) da porta da sala no fundo da varanda."""
    var = ABERT[final][0]
    pl, c, a0, a1 = var['face']
    s = var['sinal']
    return pl, var['fundo'] + s * UN_OFF, a0 + 0.08, a1 - 0.08, s


def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for t in GRADE_TORRES:
        tx_, ty_ = X(PL.TORRES[t][0]), Y(PL.TORRES[t][1])
        for f in range(1, FINAIS + 1):
            pl, c, a0, a1, s = _quad_unidade(f)
            for andar in range(NPAV[t]):
                if not existe(t, andar, f):
                    continue
                z0 = andar * PD + Z_UN[0]
                z1 = (andar + 1) * PD + Z_UN[1]
                if pl == 'x':
                    p0, p1, nrm = (tx_ + c, ty_ + a0), (tx_ + c, ty_ + a1), (s, 0)
                else:
                    p0, p1, nrm = (tx_ + a0, ty_ + c), (tx_ + a1, ty_ + c), (0, s)
                loc = [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)]
                uv4 = [(0, 0), (1, 0), (1, 1), (0, 1)]
                nn = _normal(loc)
                if nn[0] * nrm[0] + nn[1] * nrm[1] < 0:
                    loc = [loc[1], loc[0], loc[3], loc[2]]
                    uv4 = [(1, 0), (0, 0), (0, 1), (1, 1)]
                k = len(verts)
                verts += loc
                faces.append((k, k + 1, k + 2, k + 3))
                uvs += uv4
                unit += [float(indice(t, andar, f))] * 4
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


# ------------------------------------------------------------------ contorno da unidade selecionada
def _afasta(pts, d, cont):
    """Polilinha deslocada d m para fora do contorno da torre, juntas em esquadria."""
    nrm = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
        m = ((a[0] + b[0]) / 2 + n[0] * 0.3, (a[1] + b[1]) / 2 + n[1] * 0.3)
        if _dentro(m, cont):
            n = (-n[0], -n[1])
        nrm.append(n)
    out = []
    for i, p in enumerate(pts):
        ns = [nrm[j] for j in (i - 1, i) if 0 <= j < len(nrm)]
        mx, my = sum(v[0] for v in ns), sum(v[1] for v in ns)
        Lm = math.hypot(mx, my) or 1
        mx, my = mx / Lm, my / Lm
        kk = d / max(0.5, mx * ns[0][0] + my * ns[0][1])
        out.append((p[0] + mx * kk, p[1] + my * kk))
    return out


def exportar_contornos():
    """jardim-botanico-contornos.json: por torre e final, a fachada da unidade em planta (x, z do Three, 6 cm para
    fora), para o contorno da selecionada seguir a parede (padrao do Ipiranga e do Casa Prado)."""
    ct = contorno()
    out = {'schema': 'contornos-unidade/1', 'pe_direito': PD, 'torres': {}}
    for t in GRADE_TORRES:
        tx_, ty_ = X(PL.TORRES[t][0]), Y(PL.TORRES[t][1])
        out['torres'][str(t)] = {}
        for f in range(1, FINAIS + 1):
            pts = _afasta(fachada(f), 0.06, ct)
            out['torres'][str(t)][str(f)] = [[round(tx_ + x, 3), round(-(ty_ + y), 3)] for x, y in pts]
    with open(os.path.join(SCR, '..', 'jardim-botanico-contornos.json'), 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))


def layout_unidades():
    out = {
        'schema': 'jbo-unidades-layout/1',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': NPAV, 'finais': FINAIS, 'grade_andares': GRADE_ANDARES,
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]', 'z_rel': list(Z_UN),
        'existe': 'todos os finais em todos os pavimentos da torre, menos o 01 do terreo (hall)',
        'torres': {str(t): [round(X(PL.TORRES[t][0]), 3), round(Y(PL.TORRES[t][1]), 3), 0.0] for t in GRADE_TORRES},
        'porta_sala': {str(f): dict(zip(('plano', 'c', 'a0', 'a1', 'face'), _quad_unidade(f))) for f in range(1, FINAIS + 1)},
    }
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ modulos (mesmo namespace)
_carrega('jbo_geo.py')
_pl = {}
exec(compile(open(SCR + '/jbo_planta.py').read(), SCR + '/jbo_planta.py', 'exec'), _pl)


class _Plano:
    pass


PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper() or _k == 'topo':
        setattr(PL, _k, _v)
assert abs(PL.S_PX - S_PX) < 1e-12 and PL.ORIGEM_PX == ORIGEM_PX, 'jbo_geo.X/Y fora de sincronia com jbo_planta'
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
CHAO = json.load(open(TEXDIR + '/chao.json'))
_carrega('jbo_patio.py')
_carrega('jbo_paisagem.py')
_carrega('jbo_lazer.py')

# ------------------------------------------------------------------ main
NOMES = ['torre-1', 'torre-2', 'torre-3', 'unidades', 'terreno', 'garagem', 'entorno', 'lazer', 'vegetacao', 'carros']


def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer()
    for t in GRADE_TORRES:
        torre(t)
    _, nun = unidades()
    tg = Geo('terreno', ao=False)
    chao(tg)
    vagas(tg)
    muros_perimetro(tg)
    tg.objeto()
    gg = Geo('garagem', ao=False)
    garagem(gg)
    gg.objeto()
    e = Geo('entorno', ao=False)
    e.piso(-4000, 4000, -4000, 4000, -0.04, 'entorno')
    e.objeto()
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
    exportar_contornos()
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun, 'materiais': len(bpy.data.materials)}


result['build'] = build()
