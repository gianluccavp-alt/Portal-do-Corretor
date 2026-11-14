# cpr_modelo.py -- reconstroi do zero a cena do Casa Prado Residence Riva (maquete externa, etapa 1: torre,
# implantacao, edificio-garagem e lazer em volumes simples). Roda DENTRO do Blender (run_all.py ou
# Blender -b --factory-startup -P run_all.py). Metros, Z para cima, origem no centro da torre (cpr_planta.ORIGEM_PX).
# Modulos executados no mesmo namespace:
#   cpr_geo.py (geometria)  cpr_torre.py (forma da torre, das plantas)  cpr_patio.py (chao, vagas, garagem, muros,
#   avenida)  cpr_lazer.py (lazer e apoio em volumes)  cpr_paisagem.py (arvores, palmeiras, carros)
# Medidas: cpr_planta.py (px da implantacao), cpr_torre.py (m, plantas de contrato) e o FAQ da ficha tecnica.
import bpy, bmesh, math, json, os, random
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/casa-prado/scripts
TEXDIR = SCR + '/tex'


def _carrega(nome):
    p = SCR + '/' + nome
    exec(compile(open(p).read(), p, 'exec'), globals())


_carrega('cpr_torre.py')          # PD, LAJE, NPAV, contornos, aberturas, existe()...
PARAPEITO = 1.10                  # platibanda da cobertura
TILE = PD                         # reboco: 1 repeticao por pavimento (junta na laje)
H17 = ANDAR_COB * PD              # piso do 17o (topo do corpo do 01 e do 04: terracos)
HTOPO = NPAV * PD                 # laje de cobertura
ANDARES_BASE = 4                  # testas em cinza ate o 4o pavimento (perspectiva aerea 059)

GRADE_TORRES = [1]
GRADE_ANDARES, GRADE_FINAIS = NPAV, 6


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
    # cores da perspectiva aerea (762-...-F059-FOT) e da fachada noturna (F051-PDO): moldura e fachadas em branco
    # gelo, campos cinza em volta das janelas, testas (pilares dos quartos 1) em creme com paineis mais escuros e base
    # cinza, guarda-corpos de concreto cinza com vidro, brises das areas tecnicas em grafite, caixilhos pretos (FAQ)
    R, Rn = 'reboco_fino.jpg', 'reboco_fino_n.jpg'
    kw = dict(img=R, tint=True, nrm=Rn, nrm_str=0.6, img_mean=0.88, uv=TILE)
    mat('fachada_cinza', '#a3a5a6', 0.93, **kw)       # fundo das fachadas longas
    mat('fachada_clara', '#dadbd9', 0.93, **kw)       # pilaretes, molduras das varandas e paineis sob as janelas
    mat('fachada_branca', '#e9e8e4', 0.93, **kw)
    mat('fachada_creme', '#e3dccf', 0.93, **kw)       # testas (pilares dos quartos 1)
    mat('fachada_creme2', '#cdc2b1', 0.93, **kw)      # paineis taupe das testas e coroamento
    mat('fachada_base', '#aaaaa7', 0.93, **kw)        # base cinza das testas
    mat('laje_borda', '#dcddda', 0.92, **kw)
    mat('cobertura', '#8c8b88', 0.95, **kw)
    mat('varanda_parede', '#c9c8c3', 0.9, **kw)
    mat('varanda_forro', '#ecebe6', 0.9)
    mat('varanda_piso', '#b8ab9a', 0.8, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('parapeito', '#cfd0cd', 0.9, **kw)
    mat('gradil_escuro', '#232427', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(0.6, 0.6))
    mat('pingadeira', '#d5d3cd', 0.9)
    mat('vidro_guarda', '#7d97a3', 0.05, blend=0.35, double=True)
    mat('janela_veneziana', '#6f747b', 0.4, img='veneziana2.png', tint=True, img_mean=0.8, emit_img='veneziana2_luz.jpg')   # persiana e caixilho pretos (FAQ)
    mat('janela_banheiro', '#ffffff', 0.3, img='basculante2.png', emit_img='basculante2_luz.jpg')
    mat('unidade', '#2b3440', 0.2, img='porta_unidade2.png', tint=True, img_mean=0.7)
    mat('caixilho', '#26272a', 0.45)                  # esquadrias pretas (FAQ)
    mat('vidro_porta', '#34444f', 0.08, metal=0.2)
    mat('vidro_lazer', '#4a5d68', 0.06, metal=0.15)
    mat('brise', '#45484c', 0.55, metal=0.25)
    mat('brise_fundo', '#8e9195', 0.9, **kw)
    mat('ferragem', '#2a2b2e', 0.5, metal=0.4)
    mat('forro', '#ece7dd', 0.9)
    mat('piso_terraco', '#bcb3a6', 0.8, img='porcelanato.jpg', tint=True, img_mean=0.8, uv=1.2)
    mat('luz_forro', '#fff4dc', 0.5)


# ------------------------------------------------------------------ geometria da torre
def B(p, z=0.0):
    """(x, v) da torre -> ponto do Blender (y = -v)."""
    return (TX + p[0], TY - p[1], z)


def quad_n(g, a, b, z0, z1, m, n, uvs=None, cor=None):
    """Quad vertical entre os pontos de planta a, b (x, v) com a normal virada para n (direcao em x, v)."""
    cs = [B(a, z0), B(b, z0), B(b, z1), B(a, z1)]
    nn = _normal(cs)
    if nn[0] * n[0] - nn[1] * n[1] < 0:            # n em (x, v): y do Blender = -v
        cs = [cs[1], cs[0], cs[3], cs[2]]
        if uvs is not None:
            uvs = [uvs[1], uvs[0], uvs[3], uvs[2]]
    g.face(cs, m, uvs=uvs, cor=cor)


def piso_n(g, x0, x1, v0, v1, z, m, cima=True):
    cs = [B((x0, v0), z), B((x1, v0), z), B((x1, v1), z), B((x0, v1), z)]
    if (_normal(cs)[2] > 0) != cima:
        cs = cs[::-1]
    g.face(cs, m)


def caixa_tv(g, x0, x1, v0, v1, z0, z1, m, topo=None):
    """Caixa alinhada aos eixos, em coordenadas (x, v) da torre."""
    g.caixa(TX + min(x0, x1), TX + max(x0, x1), TY - max(v0, v1), TY - min(v0, v1), z0, z1, m, topo=topo)


def poly_tv(g, pts, z, m):
    g.poligono([B(p)[:2] for p in pts], z, m)


class Seg:
    """Trecho reto do contorno (x, v), com a normal para fora."""

    def __init__(self, a, b, n):
        self.a, self.b, self.n = a, b, n
        self.L = math.hypot(b[0] - a[0], b[1] - a[1])
        self.d = ((b[0] - a[0]) / self.L, (b[1] - a[1]) / self.L)
        self.pl = 'v' if abs(a[1] - b[1]) < 1e-6 else 'x'
        self.c = a[1] if self.pl == 'v' else a[0]

    def P(self, t, off=0.0):
        return (self.a[0] + self.d[0] * t + self.n[0] * off, self.a[1] + self.d[1] * t + self.n[1] * off)

    def t_de(self, s):
        """Parametro ao longo do trecho para a coordenada s (x se o trecho e em v constante, v se em x)."""
        k = 0 if self.pl == 'v' else 1
        return (s - self.a[k]) / self.d[k]

    def quad(self, g, t0, t1, z0, z1, m, off=0.0, uvs=None, cor=None):
        if t1 - t0 < 1e-4 or z1 - z0 < 1e-4:
            return
        quad_n(g, self.P(t0, off), self.P(t1, off), z0, z1, m, self.n, uvs=uvs, cor=cor)

    def caixa(self, g, t0, t1, o0, o1, z0, z1, m, topo=None):
        """Caixa no referencial do trecho: t ao longo, o para fora (o0 < o1)."""
        p = [self.P(t0, o0), self.P(t1, o0), self.P(t1, o1), self.P(t0, o1)]
        xs, vs = [q[0] for q in p], [q[1] for q in p]
        caixa_tv(g, min(xs), max(xs), min(vs), max(vs), z0, z1, m, topo=topo)


def _segmentos(cont):
    """Trechos do contorno (anti-horario no Blender) com a normal para fora."""
    out = []
    n = len(cont)
    for i in range(n):
        a, b = cont[i], cont[(i + 1) % n]
        dx, dv = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dv)
        if L < 1e-6:
            continue
        # anti-horario no Blender (x, y=-v): normal para fora = direita do percurso em (x, y) -> (dy, -dx) =
        # (-dv, -dx); em (x, v) (v = -y): (-dv, dx)/L
        out.append(Seg(a, b, (-dv / L, dx / L)))
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


# aberturas de todas as unidades, ja no referencial da torre
ABERT = {f: aberturas(f) for f in range(1, 7)}


def _andares_corpo(final):
    """Pavimentos em que o volume do final existe (o 01 e o 04 terminam no 16o; no 17o viram terraco)."""
    return range(0, ANDAR_COB) if final in (1, 4) else range(0, NPAV)


def _feicoes(seg):
    """Janelas, varandas e brises que caem neste trecho: lista (t0, t1, tipo, final, dados)."""
    out = []
    for f in range(1, 7):
        var, jans, bris = ABERT[f]
        pl, c = var['face']
        if pl == seg.pl and abs(c - seg.c) < 1e-6:
            t0, t1 = sorted((seg.t_de(var['a'][0]), seg.t_de(var['a'][1])))
            if t0 >= -1e-6 and t1 <= seg.L + 1e-6:
                out.append((t0, t1, 'varanda', f, var))
        for j in jans:
            if j[0] == seg.pl and abs(j[1] - seg.c) < 1e-6:
                t0, t1 = sorted((seg.t_de(j[2]), seg.t_de(j[3])))
                if t0 >= -1e-6 and t1 <= seg.L + 1e-6:
                    out.append((t0, t1, 'janela', f, j))
        for b, prof in bris:
            if b[0] == seg.pl and abs(b[1] - seg.c) < 1e-6:
                t0, t1 = sorted((seg.t_de(b[2]), seg.t_de(b[3])))
                if t0 >= -1e-6 and t1 <= seg.L + 1e-6:
                    out.append((max(0.0, t0), min(seg.L, t1), 'brise', f, prof))
    out.sort()
    return out


def _testa(seg):
    return abs(seg.a[0]) >= XB - 1e-6 and abs(seg.b[0]) >= XB - 1e-6


def _mat_parede(seg, andar):
    if _testa(seg):
        if andar >= NPAV:
            return 'fachada_creme2'                    # coroamento das testas (platibanda taupe)
        return 'fachada_base' if andar < ANDARES_BASE else 'fachada_creme'
    return 'fachada_cinza'


JAN_DORM = (1.05, 2.25)        # peitoril e verga (persiana embutida)
JAN_BANHO = (1.60, 2.15)


def _janela(g, seg, t0, t1, z0, z1, m, mp='fachada_cinza'):
    """Janela recuada 6 cm (quad com a textura inteira), caixilho preto e peitoril; campo cinza em volta."""
    e = 0.05
    seg.quad(g, t0, t1, z0, z1, m, off=-0.06, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], cor=1.0)
    # requadro (espessura da parede) e caixilho
    quad_n(g, seg.P(t0, -0.06), seg.P(t0, 0.0), z0, z1, mp, seg.d)
    quad_n(g, seg.P(t1, 0.0), seg.P(t1, -0.06), z0, z1, mp, (-seg.d[0], -seg.d[1]))
    for zz, cima in ((z0, True), (z1, False)):        # requadro de cima e de baixo
        cs = [B(seg.P(t0, -0.06), zz), B(seg.P(t1, -0.06), zz), B(seg.P(t1, 0.0), zz), B(seg.P(t0, 0.0), zz)]
        if (_normal(cs)[2] > 0) != cima:
            cs = cs[::-1]
        g.face(cs, mp)
    seg.caixa(g, t0 - e, t1 + e, -0.06, 0.03, z1, z1 + e, 'caixilho')
    seg.caixa(g, t0 - e, t0, -0.06, 0.03, z0, z1, 'caixilho')
    seg.caixa(g, t1, t1 + e, -0.06, 0.03, z0, z1, 'caixilho')
    seg.caixa(g, t0 - 0.04, t1 + 0.04, -0.06, 0.04, z0 - 0.03, z0, 'caixilho')


def _parede_com_furos(g, seg, t0, t1, z0, z1, m, furos):
    """Parede de t0 a t1 (z0..z1) com furos retangulares (ta, tb, za, zb) que nao se sobrepoem."""
    furos = sorted(f for f in furos if f[1] > t0 and f[0] < t1)
    t = t0
    for ta, tb, za, zb in furos:
        seg.quad(g, t, ta, z0, z1, m)
        seg.quad(g, ta, tb, z0, za, m)
        seg.quad(g, ta, tb, zb, z1, m)
        t = tb
    seg.quad(g, t, t1, z0, z1, m)


def _varanda(g, seg, t0, t1, final, var, andar):
    """Loggia de um pavimento: laje e guarda-corpo (concreto 0,78 + vidro 0,32) no plano da fachada, paredes do
    fundo e laterais, piso e forro. No terreo, onde nao ha unidade (hall e lazer), sem guarda-corpo e com vidro."""
    z0 = andar * PD
    zt = z0 + PD - LAJE
    tem = existe(andar, final)
    sv = var['sinal']
    if andar > 0:
        seg.quad(g, t0, t1, z0 - LAJE, z0, 'laje_borda')
        seg.caixa(g, t0, t1, -0.10, 0.0, z0 - LAJE, z0 + 0.001, 'laje_borda')
    if tem:
        seg.caixa(g, t0, t1, -0.15, 0.0, z0, z0 + 0.78, 'parapeito', topo='pingadeira')
        L = t1 - t0
        seg.quad(g, t0, t1, z0 + 0.78, z0 + 1.10, 'gradil_escuro', off=-0.08, uvs=[(0, 0), (L / 0.6, 0), (L / 0.6, 0.53), (0, 0.53)])
        quad_n(g, seg.P(t1, -0.08), seg.P(t0, -0.08), z0 + 0.78, z0 + 1.10, 'gradil_escuro', (-seg.n[0], -seg.n[1]),
               uvs=[(0, 0), (L / 0.6, 0), (L / 0.6, 0.53), (0, 0.53)])
        seg.caixa(g, t0, t1, -0.11, -0.05, z0 + 1.08, z0 + 1.12, 'caixilho')
    # fundo e laterais
    nface = (0.0, float(sv))
    for fu in var['fundos']:
        pl, c, a0, a1, tipo = fu
        if pl == 'v':
            pa, pb = (a0, c), (a1, c)
            n = nface
        else:
            pa, pb = (c, a0), (c, a1)
            xm = (var['a'][0] + var['a'][1]) / 2
            n = (1.0 if xm > c else -1.0, 0.0)
        if tipo is None:
            quad_n(g, pa, pb, z0, zt, 'varanda_parede', n)
            continue
        if not tem:
            quad_n(g, pa, pb, z0, zt, 'vidro_lazer' if andar == 0 else 'varanda_parede', n)
            continue
        if tipo == 'servico':
            quad_n(g, pa, pb, z0, z0 + 2.2, 'vidro_porta', n)
            quad_n(g, pa, pb, z0 + 2.2, zt, 'varanda_parede', n)
        else:     # sala: a malha "unidades" fica 4 cm a frente (em unidades()); atras dela a parede
            quad_n(g, pa, pb, z0, zt, 'varanda_parede', n)
    for pl, c, a0, a1 in var['lados']:
        xm = (var['a'][0] + var['a'][1]) / 2
        quad_n(g, (c, a0), (c, a1), z0, zt, 'varanda_parede', (1.0 if xm > c else -1.0, 0.0))
    for pl, c, a0, a1, tipo in var['fundos']:
        if pl != 'v':
            continue
        vface = var['face'][1]
        piso_n(g, a0, a1, c, vface, z0 + 0.002, 'varanda_piso', cima=True)
        piso_n(g, a0, a1, c, vface, zt, 'varanda_forro', cima=False)
        if andar > 0 and tem:
            xm, vm = (a0 + a1) / 2, (c + vface) / 2
            g.cil(B((xm, vm))[0], B((xm, vm))[1], 0.08, zt - 0.012, zt, 'luz_forro', seg=8, tampa=False, base=True)


def _brise(g, seg, t0, t1, prof, andar):
    """Area tecnica das condensadoras (planta: "fechamento em brise"; perspectiva 059: em cada pavimento uma laje
    fina com gradil escuro de ~1,1 m na face, e no fundo cinza a janelinha do banho)."""
    z0, z1 = andar * PD, (andar + 1) * PD
    seg.quad(g, t0, t1, z0, z1, 'brise_fundo', off=-prof)
    quad_n(g, seg.P(t0, -prof), seg.P(t0, 0.0), z0, z1, 'brise_fundo', seg.d)
    quad_n(g, seg.P(t1, 0.0), seg.P(t1, -prof), z0, z1, 'brise_fundo', (-seg.d[0], -seg.d[1]))
    seg.caixa(g, t0, t1, -prof, 0.06, z0 - 0.001 if andar else 0.0, z0 + 0.10, 'laje_borda')
    L = t1 - t0
    uv = [(0, 0), (L / 0.6, 0), (L / 0.6, 1.1 / 0.6), (0, 1.1 / 0.6)]
    seg.quad(g, t0, t1, z0 + 0.10, z0 + 1.20, 'gradil_escuro', off=0.02, uvs=uv)
    quad_n(g, seg.P(t1, 0.02), seg.P(t0, 0.02), z0 + 0.10, z0 + 1.20, 'gradil_escuro', (-seg.n[0], -seg.n[1]), uvs=uv)
    seg.caixa(g, t0, t1, -0.02, 0.05, z0 + 1.17, z0 + 1.22, 'ferragem')
    if L > 1.0 and andar > 0:      # janelinha do banho no fundo
        tm = (t0 + t1) / 2
        seg.quad(g, tm - 0.3, tm + 0.3, z0 + 1.55, z0 + 2.1, 'janela_banheiro', off=-prof + 0.01,
                 uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], cor=1.0)


def _paredes(g, segs, andares):
    """Fachadas do contorno nos pavimentos dados: paredes, janelas, varandas e brises."""
    for seg in segs:
        feic = _feicoes(seg)
        testa = _testa(seg)
        for andar in andares:
            z0, z1 = andar * PD, (andar + 1) * PD
            m = _mat_parede(seg, andar)
            furos = []
            for t0, t1, tipo, f, dados in feic:
                if andar not in _andares_corpo(f):
                    continue
                if tipo == 'varanda':
                    furos.append((t0, t1, z0, z1))
                    _varanda(g, seg, t0, t1, f, dados, andar)
                elif tipo == 'brise':
                    furos.append((t0, t1, z0, z1))
                    _brise(g, seg, t0, t1, dados, andar)
                else:
                    banho = dados[4] == 'banho'
                    if existe(andar, f):
                        za, zb = JAN_BANHO if banho else JAN_DORM
                        mj = 'janela_banheiro' if banho else 'janela_veneziana'
                        ta, tb = t0, t1
                    else:      # terreo do hall e do lazer: vidro do piso ate 2,4 m no lugar da janela
                        za, zb = 0.12, 2.40
                        mj = 'vidro_lazer'
                        ta, tb = max(0.05, t0 - 0.35), min(seg.L - 0.05, t1 + 0.35)
                    furos.append((ta, tb, z0 + za, z0 + zb))
                    _janela(g, seg, ta, tb, z0 + za, z0 + zb, mj, m)
                    if not testa and existe(andar, f) and not banho and andar > 0:
                        # painel cinza claro sob a janela (perspectiva 059), 1,5 cm a frente da parede
                        seg.quad(g, ta, tb, z0 + 0.12, z0 + za - 0.08, 'fachada_clara', off=0.015)
            _parede_com_furos(g, seg, 0.0, seg.L, z0, z1, m, furos)
            # laje sobre a varanda do ultimo pavimento do volume (fecha a faixa entre o forro e a cobertura)
            for t0, t1, tipo, f, dados in feic:
                if tipo == 'varanda' and andar == _andares_corpo(f).stop - 1:
                    seg.quad(g, t0, t1, z1 - LAJE, z1, 'laje_borda')


def _molduras(g, segs, andar0, andar1):
    """Pilaretes brancos dos dois lados de cada varanda, de alto a baixo (moldura da perspectiva)."""
    for seg in segs:
        if _testa(seg):
            continue
        for t0, t1, tipo, f, dados in _feicoes(seg):
            if tipo != 'varanda':
                continue
            a = max(andar0, _andares_corpo(f).start)
            b = min(andar1, _andares_corpo(f).stop)
            if b <= a:
                continue
            for tt in (t0, t1):
                seg.caixa(g, tt - 0.16, tt + 0.16, 0.0, 0.10, a * PD, b * PD, 'fachada_clara', topo='pingadeira')


def _paineis_testa(g, segs):
    """Paineis taupe nas testas (perspectiva 059): um por pavimento acima da base, no terco externo da face (longe
    do recorte da area tecnica), separados por faixas creme na altura das lajes."""
    for seg in segs:
        if not (seg.pl == 'x' and abs(abs(seg.c) - XT) < 1e-6):
            continue
        # t cresce de um extremo ao outro; o lado externo e o de |v| maior
        va, vb = seg.a[1], seg.b[1]
        if abs(vb) > abs(va):
            ta, tb = seg.L * 0.42, seg.L * 0.86
        else:
            ta, tb = seg.L * 0.14, seg.L * 0.58
        for andar in range(ANDARES_BASE, NPAV):
            seg.quad(g, ta, tb, andar * PD + 0.22, (andar + 1) * PD - 0.12, 'fachada_creme2', off=0.012)


def _cobertura(g):
    """Laje do 17o (terracos no lugar do 01 e do 04), cobertura com platibanda, nucleo e caixa d'agua."""
    c17 = contorno_cobertura()
    Hp = HTOPO + PARAPEITO
    # terracos descobertos das coberturas sobre o 01 e o 04: piso, guarda-corpo de 1,30 m e divisoria no eixo
    for sgn in (1, -1):
        pts = terraco_01() if sgn > 0 else [(-p[0], -p[1]) for p in terraco_01()]
        poly_tv(g, pts, H17, 'piso_terraco')
        for seg in _segmentos(pts if _area(pts) < 0 else pts[::-1]):   # area < 0 em (x, v) = anti-horario no Blender
            fora = (seg.P(seg.L / 2, 0.3))
            if _dentro(fora, contorno_cobertura()):
                continue
            seg.caixa(g, 0.0, seg.L, -0.15, 0.0, H17, H17 + 1.30, 'fachada_branca', topo='pingadeira')
        # divisoria entre os terracos das duas coberturas (x ~ 0, planta 172)
        v0, v1 = (V01_N, VM) if sgn > 0 else (-VM, -V01_N)
        caixa_tv(g, -0.06, 0.06, v0, v1, H17, H17 + 1.8, 'fachada_branca', topo='pingadeira')
        # beiral da cobertura sobre parte do terraco (projecao na planta 172), dos dois lados
        for sx in (1, -1):
            xa, xb = sorted((sx * XD, sx * 4.73))
            va, vb = (V01_E if sx < 0 else V01_D, VM) if sgn > 0 else (-VM, -(V01_D if sx < 0 else V01_E))
            caixa_tv(g, xa, xb, va, vb, HTOPO - 0.05, HTOPO + 0.15, 'laje_borda', topo='cobertura')
    # laje e platibanda da cobertura: a parede do 17o sobe ate Hp; tampa em Hp
    poly_tv(g, c17, Hp, 'cobertura')
    for seg in _segmentos(c17):
        seg.quad(g, 0.0, seg.L, HTOPO, Hp, _mat_parede(seg, NPAV))
        seg.caixa(g, 0.0, seg.L, -0.02, 0.06, Hp - 0.06, Hp, 'pingadeira')
    # nucleo (escada, elevadores, casa de maquinas e caixa d'agua), como na perspectiva aerea
    caixa_tv(g, -3.2, 3.2, -3.0, 3.0, Hp - 0.5, Hp + 3.4, 'fachada_branca', topo='cobertura')
    caixa_tv(g, -3.3, 3.3, -3.1, 3.1, Hp + 3.4, Hp + 3.55, 'laje_borda', topo='cobertura')
    caixa_tv(g, -1.2, 1.6, -3.0, 0.4, Hp + 3.55, Hp + 5.0, 'fachada_branca', topo='cobertura')
    for vv in (-2.4, -1.0):     # escada marinheiro para o topo da caixa
        caixa_tv(g, 3.2, 3.26, vv - 0.02, vv + 0.02, Hp + 2.0, Hp + 4.4, 'ferragem')
    for k in range(9):
        caixa_tv(g, 3.2, 3.26, -2.42, -0.98, Hp + 2.1 + k * 0.3, Hp + 2.13 + k * 0.3, 'ferragem')
    # condensadoras e exaustores soltos na laje
    for xx, vv in ((10.0, 3.0), (-10.0, -3.0), (13.5, -3.5), (-13.5, 3.5)):
        caixa_tv(g, xx - 0.5, xx + 0.5, vv - 0.35, vv + 0.35, Hp - 0.6, Hp - 0.02, 'fachada_cinza', topo='brise')


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2


def _terreo(g):
    """Gardens dos finais 02 e 06 (terraco descoberto e jardim com fechamento de 1,80 m, planta Garden) e
    o piso em volta da torre no terreo."""
    for sx in (1, -1):
        def X_(v):
            return v * sx
        xa, xb = sorted((X_(XD), X_(GARDEN_X)))
        # piso do terraco descoberto (porcelanato) na faixa de 1,50 m e jardim no resto
        piso_n(g, min(X_(XD), X_(XB)), max(X_(XD), X_(XB)), VF, VF + 1.0, 0.07, 'varanda_piso')
        piso_n(g, xa, xb, VF + 1.0, GARDEN_V, 0.05, 'grama_garden')
        piso_n(g, min(X_(XB), X_(GARDEN_X)), max(X_(XB), X_(GARDEN_X)), VB1, VF + 1.0, 0.05, 'grama_garden')
        # fechamento (muro 1,80 m)
        e = 0.12
        caixa_tv(g, xa, xb, GARDEN_V, GARDEN_V + e, 0.0, 1.8, 'fachada_branca', topo='pingadeira')
        caixa_tv(g, X_(GARDEN_X), X_(GARDEN_X) + sx * e, VB1, GARDEN_V + e, 0.0, 1.8, 'fachada_branca', topo='pingadeira')
        caixa_tv(g, X_(XD - 0.06), X_(XD + 0.06), VM, GARDEN_V, 0.0, 1.8, 'fachada_branca', topo='pingadeira')
    # hall: porta de vidro de duas folhas no fundo da varanda do 01 (entrada no terreo) e marquise
    caixa_tv(g, -5.4, -2.0, VM - 0.02, VM + 0.02, 2.55, 2.62, 'laje_borda')


def torre():
    g = Geo('torre-1', ao=False)
    ct, c17 = contorno_tipo(), contorno_cobertura()
    st, s17 = _segmentos(ct), _segmentos(c17)
    _paredes(g, st, range(0, ANDAR_COB))
    _paredes(g, s17, [ANDAR_COB])
    _molduras(g, st, 0, ANDAR_COB)
    _molduras(g, s17, ANDAR_COB, NPAV)
    _paineis_testa(g, s17)
    _cobertura(g)
    _terreo(g)
    return g.objeto()


# ------------------------------------------------------------------ malha "unidades" (contrato com a pagina)
UN_OFF = 0.04          # 4 cm a frente da parede do fundo da varanda (porta de correr da sala)
Z_UN = (0.06, -LAJE - 0.10)


def _quad_unidade(final):
    var = ABERT[final][0]
    for pl, c, a0, a1, tipo in var['fundos']:
        if tipo == 'sala':
            return c + var['sinal'] * UN_OFF, a0 + 0.06, a1 - 0.06, var['sinal']
    raise ValueError(final)


def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for f in range(1, 7):
        v, x0, x1, sv = _quad_unidade(f)
        for andar in range(NPAV):
            if not existe(andar, f):
                continue
            z0 = andar * PD + Z_UN[0]
            z1 = (andar + 1) * PD + Z_UN[1]
            loc = [B((x0, v), z0), B((x1, v), z0), B((x1, v), z1), B((x0, v), z1)]
            uv4 = [(0, 0), (1, 0), (1, 1), (0, 1)]
            if (_normal(loc)[1] < 0) != (sv > 0):        # face para fora (frente: -y; fundos: +y)
                loc = [loc[1], loc[0], loc[3], loc[2]]
                uv4 = [(1, 0), (0, 0), (0, 1), (1, 1)]
            k = len(verts)
            verts += loc
            faces.append((k, k + 1, k + 2, k + 3))
            uvs += uv4
            unit += [float(indice(1, andar, f))] * 4
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
    """casa-prado-contornos.json: por final, a fachada da unidade em planta (x, z do Three, 6 cm para fora)."""
    ct = contorno_tipo()
    out = {'schema': 'contornos-unidade/1', 'pe_direito': PD, 'torres': {'1': {}}}
    for f in range(1, 7):
        pts = _afasta(fachada(f), 0.06, ct)
        out['torres']['1'][str(f)] = [[round(TX + x, 3), round(-(TY - v), 3)] for x, v in pts]
    with open(os.path.join(SCR, '..', 'casa-prado-contornos.json'), 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))


def layout_unidades():
    out = {
        'schema': 'cpr-unidades-layout/1',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': NPAV, 'finais': 6,
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]', 'z_rel': list(Z_UN),
        'existe': {'terreo': list(EXISTE[0]), '17': list(EXISTE[ANDAR_COB]), 'demais': [1, 2, 3, 4, 5, 6]},
        'torre-1': {'centro': [round(TX, 3), round(TY, 3), 0.0],
                    'quad_porta_sala': {str(f): dict(zip(('v', 'x0', 'x1', 'face'), _quad_unidade(f))) for f in range(1, 7)}},
    }
    with open(SCR + '/unidades_layout.json', 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ modulos (mesmo namespace)
_carrega('cpr_geo.py')
_pl = {}
exec(compile(open(SCR + '/cpr_planta.py').read(), SCR + '/cpr_planta.py', 'exec'), _pl)


class _Plano:
    pass


PL = _Plano()
for _k, _v in _pl.items():
    if _k.isupper():
        setattr(PL, _k, _v)
assert abs(PL.S_PX - S_PX) < 1e-9 and PL.ORIGEM_PX == ORIGEM_PX, 'cpr_geo.X/Y fora de sincronia com cpr_planta'
TX, TY = X(PL.TORRE[0]), Y(PL.TORRE[1])
MARCAS = json.load(open(TEXDIR + '/piso_marcas.json'))
_carrega('cpr_patio.py')
_carrega('cpr_paisagem.py')
_carrega('cpr_lazer.py')

# ------------------------------------------------------------------ main
OBJETOS_EXPORTADOS = []


def build():
    limpar()
    MATS.clear(); IMAGENS.clear(); UVESC.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    materiais_torre(); materiais_patio(); materiais_paisagem(); materiais_lazer()
    nomes = ['torre-1', 'unidades', 'terreno', 'garagem', 'entorno', 'entorno-rua', 'lazer', 'vegetacao', 'carros']
    torre()
    _, nun = unidades()
    t = Geo('terreno', ao=False)
    chao(t)
    vagas(t)
    muros_perimetro(t)
    t.objeto()
    gg = Geo('garagem', ao=False)
    garagem(gg)
    gg.objeto()
    e = Geo('entorno', ao=False)
    # plano do entorno com um furo sob a rampa do subsolo (senao ele tamparia a rampa)
    hx0, hx1, hy0, hy1 = X(2045), X(2255), Y(805), Y(550)
    for x0, x1, y0, y1 in ((-4000, hx0, -4000, 4000), (hx1, 4000, -4000, 4000), (hx0, hx1, -4000, hy0), (hx0, hx1, hy1, 4000)):
        e.piso(x0, x1, y0, y1, -0.04, 'entorno')
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
    exportar_contornos()
    OBJETOS_EXPORTADOS[:] = nomes
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun, 'materiais': len(bpy.data.materials)}


result['build'] = build()
