# gaia_modelo.py -- reconstroi do zero a cena do Village Gaia (Task 7, rodada 2).
# Roda DENTRO do Blender (via bl.py). Unidades em metros, Z para cima, origem no centro do terreno.
# Fontes das medidas: ver task-7a-report.md. Mudancas da rodada 2: ver task-7b-report.md
#  - cores do book (grafite / cinza medio / prumada escura / guarda-corpo branco)
#  - textura de reboco tileavel (cor + normal) com juntas por pavimento; vidro com reflexo
#  - malha "unidades" (fundo das varandas, 1 quad por unidade, atributo _unit)
#  - chao vetorial (poligonos por classe + faixas de estacionamento) e arvores organicas
import bpy, bmesh, math, json, os, random
import numpy as np

# caminhos relativos ao repo: bl.py injeta __file__ (= caminho deste script) antes de executar
SCR = os.path.dirname(os.path.abspath(__file__))                      # assets/3d/village-gaia/scripts
REPO = os.path.abspath(os.path.join(SCR, '..', '..', '..', '..'))
IMPL = REPO + '/assets/img/village-gaia/plantas/implantacao.jpg'
TEXDIR = SCR + '/tex'
os.makedirs(TEXDIR, exist_ok=True)

# ------------------------------------------------------------------ parametros
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
TILE = 5.8          # textura de reboco: 2 pavimentos x 5,8 m

S = 0.0998          # m por pixel do implantacao.jpg (39 m = 391 px)
OX, OY = 1184.0, 879.5
def px2m(px, py):
    return ((px - OX) * S, (OY - py) * S)

T1X, TY = px2m(1503.5, 682.5)
TORRES = {
    'torre-1': (T1X, TY),
    'torre-2': (T1X - (44.16 + 2 * (BUMP - 0.05)), TY),
    'torre-3': (T1X - (44.16 + 44.46 + 4 * (BUMP - 0.05)), TY),
}
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

# ------------------------------------------------------------------ utilidades de imagem
def img_from_array(name, arr, fmt='PNG', alpha=False, quality=88, noncolor=False):
    """arr: float32 (h,w,3|4) de cima para baixo, valores 0..1."""
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1), np.float32)], 2)
    im = bpy.data.images.new(name, w, h, alpha=alpha)
    if noncolor:
        im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).ravel().astype(np.float32))
    ext = '.png' if fmt == 'PNG' else '.jpg'
    im.filepath_raw = TEXDIR + '/' + name + ext
    im.file_format = fmt
    bpy.context.scene.render.image_settings.quality = quality
    im.save()
    im.pack()
    return im

def blur_wrap(a, ry, rx=None):
    """media movel separavel periodica (para texturas tileaveis)."""
    rx = ry if rx is None else rx
    out = a
    if ry > 0:
        k = 2 * ry + 1
        p = np.pad(out, ((ry, ry), (0, 0)), mode='wrap')
        c = np.cumsum(p, 0); c = np.concatenate([np.zeros((1, c.shape[1])), c], 0)
        out = (c[k:] - c[:-k]) / k
    if rx > 0:
        k = 2 * rx + 1
        p = np.pad(out, ((0, 0), (rx, rx)), mode='wrap')
        c = np.cumsum(p, 1); c = np.concatenate([np.zeros((c.shape[0], 1)), c], 1)
        out = (c[:, k:] - c[:, :-k]) / k
    return out

def norm01(a):
    a = a - a.mean()
    return a / (a.std() + 1e-9)

def boxblur(a, r):
    k = 2 * r + 1
    p = np.pad(a, ((r, r), (r, r)), mode='edge')
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)

def normal_de_altura(h, k):
    du = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    dv = np.roll(h, 1, 0) - np.roll(h, -1, 0)      # linha de cima = v maior
    n = np.stack([-k * du, -k * dv, np.ones_like(h)], 2)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return (n * 0.5 + 0.5).astype(np.float32)

# ------------------------------------------------------------------ texturas
def tex_reboco():
    """Reboco/pintura texturizada: 1024 px = 5,8 m (2 pavimentos). Cinza neutro (~0.9),
    tingido pelo fator de cor de cada material. Juntas horizontais em cada laje."""
    n = 1024
    rng = np.random.default_rng(3)
    grain = norm01(blur_wrap(rng.normal(0, 1, (n, n)), 1))
    grao2 = norm01(blur_wrap(rng.normal(0, 1, (n, n)), 3))
    mancha = norm01(blur_wrap(blur_wrap(rng.normal(0, 1, (n, n)), 30), 30))
    escorr = norm01(blur_wrap(rng.normal(0, 1, (n, n)), 70, 2))   # escorrido vertical leve
    r = np.arange(n)[:, None].astype(np.float32)
    groove = np.zeros((n, n), np.float32)
    streak = np.zeros((n, n), np.float32)
    for j in (0, n // 2):                 # juntas em z = 0 e z = 2,9 (v = 0 e 0,5)
        d = (r - (n - 1 - j)) % n          # distancia para baixo (linhas maiores = mais baixo)
        du = ((n - 1 - j) - r) % n         # distancia para cima
        dd = np.minimum(d, du)
        groove = np.maximum(groove, np.clip(1.6 - dd, 0, 1) * np.ones((1, n)))
        streak += (np.exp(-d / 14.0) * (d > 1)) * np.ones((1, n))
    alb = 0.90 + 0.012 * mancha + 0.014 * grain + 0.010 * grao2 + 0.007 * escorr \
        - 0.28 * groove - 0.035 * streak
    alb = np.clip(alb, 0, 1).astype(np.float32)
    rgb = np.stack([alb, alb, alb], 2)
    img = img_from_array('reboco', rgb, 'JPEG', quality=86)
    hgt = 0.55 * grain + 0.35 * grao2 - 4.0 * groove
    nrm = img_from_array('reboco_normal', normal_de_altura(blur_wrap(hgt, 0), 0.05)[::2, ::2], 'JPEG',
                         quality=90, noncolor=True)
    return img, nrm

def tex_chao():
    """Detalhe neutro do chao (asfalto/grama/passeio), 512 px = 8 m."""
    n = 512
    rng = np.random.default_rng(5)
    g = norm01(blur_wrap(rng.normal(0, 1, (n, n)), 1))
    m = norm01(blur_wrap(blur_wrap(rng.normal(0, 1, (n, n)), 20), 20))
    m2 = norm01(blur_wrap(rng.normal(0, 1, (n, n)), 5))
    alb = np.clip(0.90 + 0.035 * g + 0.04 * m + 0.02 * m2, 0, 1).astype(np.float32)
    return img_from_array('detalhe_chao', np.stack([alb] * 3, 2), 'JPEG', quality=82)

def tex_vidro():
    """Janela: caixilho claro + vidro escuro com reflexo do ceu (degrade + faixa diagonal)."""
    w, h = 128, 256
    y = (np.arange(h)[:, None] / (h - 1)).astype(np.float32)     # 0 topo
    x = (np.arange(w)[None, :] / (w - 1)).astype(np.float32)
    t = 1 - y
    base = np.stack([0.10 + 0.20 * t, 0.12 + 0.25 * t, 0.15 + 0.30 * t], 2) * np.ones((h, w, 1))
    faixa = np.exp(-((x * 0.9 + y * 0.6 - 0.55) / 0.10) ** 2)[..., None] * 0.10
    a = (base + faixa).astype(np.float32)
    f = 6
    a[:f], a[-f:], a[:, :f], a[:, -f:] = 0.86, 0.86, 0.86, 0.86
    a[:, w // 2 - 2:w // 2 + 2] = 0.80
    return img_from_array('vidro', np.clip(a, 0, 1), 'PNG')

def tex_veneziana():
    """Janela de dormitorio (1,20 x 1,20 m): caixilho branco, 2 folhas de veneziana de correr
    (laminas horizontais) e contramarco escuro em volta (sombra do vao)."""
    w, h = 128, 128
    a = np.ones((h, w, 3), np.float32) * 0.94
    for yy in range(10, h - 8, 5):          # laminas: sombra embaixo de cada uma
        a[yy:yy + 1, 7:-7] = 0.62
        a[yy + 1:yy + 2, 7:-7] = 0.78
    a[:, 62:66] = 0.84                       # encontro das folhas
    a[:, 60:62] = 0.70
    a[:7], a[-7:], a[:, :7], a[:, -7:] = 0.99, 0.99, 0.99, 0.99    # caixilho
    a[:2], a[-2:], a[:, :2], a[:, -2:] = 0.35, 0.35, 0.35, 0.35    # contramarco/sombra do vao
    return img_from_array('veneziana', a, 'PNG')

def tex_basculante():
    """Janela de banheiro (0,60 x 0,60 m, alta): caixilho branco e 2 basculantes de vidro
    mini-boreal (translucido, cinza-azulado), sem veneziana."""
    w, h = 64, 64
    y = (np.arange(h)[:, None] / (h - 1)).astype(np.float32)
    rng = np.random.default_rng(9)
    tx = blur_wrap(rng.normal(0, 1, (h, w)), 1) * 0.03                 # textura do vidro
    v = np.stack([0.30 + 0.10 * (1 - y) + tx, 0.34 + 0.10 * (1 - y) + tx, 0.39 + 0.10 * (1 - y) + tx], 2)
    a = (v * np.ones((h, w, 1))).astype(np.float32)
    a[:4], a[-4:], a[:, :4], a[:, -4:] = 0.97, 0.97, 0.97, 0.97      # caixilho
    a[h // 2 - 1:h // 2 + 1] = 0.92                                   # travessa entre basculantes
    a[h // 2 + 1:h // 2 + 3, 4:-4] = 0.22                             # sombra da folha basculada
    a[4:6, 4:-4] = 0.24
    a[:2], a[-2:], a[:, :2], a[:, -2:] = 0.35, 0.35, 0.35, 0.35
    return img_from_array('basculante', np.clip(a, 0, 1), 'PNG')

def tex_guarda_corpo():
    w, h = 256, 64
    a = np.zeros((h, w, 4), np.float32)
    a[..., :3] = 0.96
    a[0:5, :, 3] = 1          # corrimao
    a[-4:, :, 3] = 1          # rodape
    for x in range(0, w, 6):  # montantes
        a[:, x:x + 2, 3] = 1
    a[:, :3, 3] = 1; a[:, -3:, 3] = 1
    return img_from_array('guarda_corpo', a, 'PNG', alpha=True)

def tex_porta_unidade():
    """Fundo da varanda (malha 'unidades'): parede (0.55), porta de correr de vidro (1.0),
    caixilhos (0.30). Cinza: a pagina multiplica pela cor do estado da unidade."""
    w, h = 256, 160
    a = np.full((h, w), 0.55, np.float32)
    x0, x1 = int(0.17 * w), int(0.83 * w)
    ytop = int(0.10 * h)
    a[ytop:, x0:x1] = 1.0
    fr = 3
    a[ytop:ytop + fr, x0:x1] = 0.30
    a[ytop:, x0:x0 + fr] = 0.30; a[ytop:, x1 - fr:x1] = 0.30
    for u in (0.335, 0.5, 0.665):
        c = int(u * w); a[ytop:, c - 2:c + 2] = 0.30
    a[-3:, x0:x1] = 0.30
    yy = (np.arange(h)[:, None] / h)
    a[ytop:, x0:x1] *= (0.92 + 0.08 * (1 - yy[ytop:]))     # leve degrade no vidro
    return img_from_array('porta_unidade', np.stack([a] * 3, 2), 'PNG')

# ------------------------------------------------------------------ materiais
MATS = {}

def srgb(hx):
    hx = hx.lstrip('#')
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def lin(v):
    return ((v + 0.055) / 1.055) ** 2.4

def mat(name, rgb, rough=0.85, img=None, tint=False, nrm=None, nrm_str=1.0, emit=None, emit_str=0.0,
        alpha_img=False, metal=0.0, double=False, img_mean=0.9):
    """rgb linear. tint=True: imagem cinza multiplicada pela cor (baseColorFactor no glTF);
    a cor e compensada pela media da imagem para o resultado medio dar ~rgb."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if img is not None:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; t.location = (-700, 250)
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
        if alpha_img:
            # alfa recortado (MASK no glTF): Round(alpha)
            rd = nt.nodes.new('ShaderNodeMath'); rd.operation = 'ROUND'; rd.location = (-300, -50)
            nt.links.new(t.outputs['Alpha'], rd.inputs[0])
            nt.links.new(rd.outputs[0], p.inputs['Alpha'])
            m.surface_render_method = 'DITHERED'
            double = True
    else:
        p.inputs['Base Color'].default_value = (*rgb, 1)
    if nrm is not None:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = nrm; tn.location = (-700, -300)
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (-300, -300)
        nm.inputs['Strength'].default_value = nrm_str
        nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    if emit is not None:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = emit_str
    m.use_backface_culling = not double
    MATS[name] = m
    return m

def criar_materiais():
    reb, reb_n = tex_reboco()
    ch = tex_chao()
    # cores medidas em 02-torre.jpg (rodada 1 do usuario: "tudo claro demais")
    mat('fachada_clara', srgb('#8b8790'), 0.92, img=reb, tint=True, nrm=reb_n)      # cinza medio
    mat('fachada_grafite', srgb('#5a565e'), 0.92, img=reb, tint=True, nrm=reb_n)    # grafite
    mat('prumada_escura', srgb('#3e3b41'), 0.92, img=reb, tint=True, nrm=reb_n)     # prumada central
    mat('laje_borda', srgb('#9d99a0'), 0.9, img=reb, tint=True, nrm=reb_n)          # faixas das varandas
    mat('varanda_forro', srgb('#d3c9ba'), 0.9)
    mat('varanda_parede', srgb('#b9b1a9'), 0.9)
    mat('vidro', (1, 1, 1), 0.15, img=tex_vidro())
    mat('janela_veneziana', (1, 1, 1), 0.7, img=tex_veneziana())          # dormitorios
    mat('janela_banheiro', (1, 1, 1), 0.3, img=tex_basculante())          # banheiros (basculante)
    mat('guarda_corpo', (1, 1, 1), 0.45, img=tex_guarda_corpo(), alpha_img=True)
    mat('cobertura', srgb('#77757a'), 0.95, img=reb, tint=True)
    mat('muro', srgb('#6a6870'), 0.95, img=reb, tint=True)
    mat('unidade', srgb('#2b3440'), 0.2, img=tex_porta_unidade(), tint=True, img_mean=0.8,
        emit=srgb('#ffc77a'), emit_str=0.0)
    # chao
    mat('grama', srgb('#5f8a3c'), 0.95, img=ch, tint=True)
    mat('asfalto', srgb('#5c5e63'), 0.9, img=ch, tint=True)
    mat('passeio', srgb('#bdb8ae'), 0.9, img=ch, tint=True)
    mat('faixa', srgb('#ececea'), 0.8)
    mat('agua', srgb('#4fb0c6'), 0.1)
    mat('quadra', srgb('#3e5a8c'), 0.8)
    mat('entorno', srgb('#7d9257'), 0.95, img=ch, tint=True)
    # arvores
    mat('tronco', srgb('#5b4a3a'), 0.95)
    mat('copa_verde', srgb('#4d7a35'), 0.9)
    mat('copa_verde_clara', srgb('#6f9440'), 0.9)
    mat('copa_verde_escura', srgb('#355a2a'), 0.9)
    mat('ipe_rosa', srgb('#b65f97'), 0.9)
    mat('ipe_amarelo', srgb('#d9b53a'), 0.9)
    mat('palmeira', srgb('#5d8236'), 0.9, double=True)

# ------------------------------------------------------------------ geometria
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
        y0, y1 = min(y0, y1), max(y0, y1)   # a normal depende so de `outward` (espelho em y nao vira a face)
        if outward > 0:
            cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
        else:
            cs = [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
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
        if outward > 0:
            cs = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)]
        else:
            cs = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        f.material_index = self.mi(m)
        f.normal_update()
        if uvfit:
            for l, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                l[self.uv].uv = uv
        else:
            self._uv(f, (TILE, TILE))
        return f

    def to_object(self, loc=(0, 0, 0), smooth=False):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.name, me)
        ob.location = loc
        bpy.context.scene.collection.objects.link(ob)
        return ob


# ------------------------------------------------------------------ aberturas por planta (Task 8)
# Coordenadas locais do quadrante +x/+y (o resto e espelhado): x = distancia ao eixo longo,
# y = distancia ao eixo transversal. Escala das plantas: 3,00 m = 388 px (129,3 px/m).
# Fontes: planta-tipo-ponta.jpg (finais 2,3,6,7), planta-tipo-meio.jpg (1,4,5 e 8 do 6o andar
# para cima), planta-office-tipo-meio.jpg (8, andares 1-5) e planta-garden-*.jpg (andar 0):
# as aberturas externas sao as mesmas em todos os tipos (garden so troca o piso da varanda).
# Banheiros dos aptos de meio ventilam por shaft (sem janela na fachada).
JANELA_DORM = (0.85, 2.20)    # peitoril e verga (z relativo ao piso do andar), dormitorios
JANELA_BANHO = (1.55, 2.15)   # basculante alto dos banheiros
JANELAS = [
    # (tipo, plano, coordenada do plano, faixa no plano, material, unidade/ambiente)
    ('face', 'x', HW, (17.50, 18.69), 'janela_veneziana', 'ponta: dormitorio 1 (casal)'),
    ('face', 'x', HW, (15.87, 16.48), 'janela_banheiro', 'ponta: banheiro 1'),
    ('face', 'x', HW, (14.47, 15.09), 'janela_banheiro', 'ponta: banheiro 2'),
    ('recorte', 'y', L / 2 - NOTCH_D, (0.82, 1.98), 'janela_veneziana', 'ponta: dormitorio 2 (no recorte, sobre a laje tecnica)'),
    ('saliencia', 'x', BUMP, (3.92, 5.12), 'janela_veneziana', 'meio: dormitorio 2 (saliencia)'),
    ('laje_tec', 'x', LAJE_TEC, (1.29, 2.45), 'janela_veneziana', 'meio: dormitorio 1 (sobre a laje tecnica)'),
]

def quadrante(b, g, sx, sy):
    """1/4 da torre (x*sx>=0, y*sy>=0). b = corpo, g = guarda-corpos (objeto separado)."""
    M = MATS
    X = lambda v: v * sx
    Y = lambda v: v * sy
    Hp = H + PARAPEITO
    b.box(0, X(LAJE_TEC), 0, Y(Y_BUMP0), 0, H + 0.6, M['prumada_escura'], mtop=M['cobertura'])
    b.box(X(LAJE_TEC), X(BUMP), Y(Y_BUMP0), Y(Y_BUMP0 + 0.45), 0, Hp + 0.8, M['fachada_grafite'], mtop=M['cobertura'])
    b.box(X(LAJE_TEC), X(BUMP), Y(Y_BUMP0 + 0.45), Y(Y_BUMP1), 0, Hp + 0.8, M['fachada_clara'], mtop=M['cobertura'])
    b.box(0, X(VAR_FUNDO), Y(Y_BUMP0), Y(Y_VAR1), 0, H, M['varanda_parede'], mtop=M['cobertura'])
    b.box(0, X(LAJE_TEC), Y(Y_BUMP1), Y(Y_VAR0), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(X(LAJE_TEC - 0.01), X(HW), Y(Y_BUMP1), Y(Y_VAR0), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(X(VAR_FUNDO), X(HW), Y(Y_VAR0), Y(Y_VAR1), H, Hp, M['laje_borda'], mtop=M['cobertura'])
    b.box(0, X(VAR_FUNDO), Y(Y_VAR0), Y(Y_VAR1), H, Hp - 0.4, M['cobertura'])
    b.box(0, X(HW), Y(Y_VAR1), Y(Y_GRAF1), 0, Hp, M['fachada_grafite'], mtop=M['cobertura'])
    b.box(X(NOTCH_X), X(HW), Y(Y_GRAF1), Y(L / 2), 0, Hp, M['fachada_clara'], mtop=M['cobertura'])
    b.box(0, X(NOTCH_X), Y(Y_GRAF1), Y(L / 2 - NOTCH_D), 0, Hp, M['fachada_grafite'], mtop=M['cobertura'])

    for i in range(NPAV):
        z = i * PD
        for (ya, yb) in ((Y_VAR0, Y_DIV), (Y_DIV, Y_VAR1)):
            # laje da varanda: faixa cinza na frente, forro claro embaixo; peitoril macico de 0,35 m
            if i > 0:
                b.box(X(VAR_FUNDO), X(HW + 0.03), Y(ya), Y(yb), z - 0.15, z + 0.35,
                      M['laje_borda'], mbot=M['varanda_forro'])
            else:
                b.box(X(VAR_FUNDO), X(HW + 0.03), Y(ya), Y(yb), z, z + 0.35, M['laje_borda'])
            g.quad_x(X(HW), Y(ya + 0.05), Y(yb - 0.05), z + 0.35, z + 1.10,
                     M['guarda_corpo'], outward=sx, uvfit=True)
        b.box(X(VAR_FUNDO), X(HW), Y(Y_DIV - 0.08), Y(Y_DIV + 0.08), z, z + PD, M['laje_borda'])
        b.box(X(LAJE_TEC), X(HW), 0, Y(Y_BUMP0), z + PD - 0.18, z + PD, M['prumada_escura'])
        for _t, plano, c, (a0, a1), mn, _d in JANELAS:
            zz = JANELA_BANHO if mn == 'janela_banheiro' else JANELA_DORM
            if plano == 'x':
                b.quad_x(X(c + 0.01), Y(a0), Y(a1), z + zz[0], z + zz[1], M[mn], outward=sx, uvfit=True)
            else:
                b.quad_y(Y(c + 0.01), X(a0), X(a1), z + zz[0], z + zz[1], M[mn], outward=sy, uvfit=True)
        b.box(0, X(NOTCH_X), Y(L / 2 - NOTCH_D), Y(L / 2 - 1.4), z + PD - 0.15, z + PD, M['prumada_escura'])
    if sy > 0:
        b.box(X(LAJE_TEC), X(HW - 0.05), -0.08, 0.08, 0, H, M['prumada_escura'])
    if sx > 0 and sy > 0:
        b.box(-3.2, 3.2, -4.0, 4.0, Hp - 0.4, Hp + 3.6, M['fachada_clara'], mtop=M['cobertura'])
        b.box(-1.6, 1.6, 4.0, 6.6, Hp - 0.4, Hp + 2.2, M['fachada_grafite'], mtop=M['cobertura'])


def torre(nome, cx, cy, g):
    b = Builder(nome)
    gl = Builder('_tmp')
    for sx in (1, -1):
        for sy in (1, -1):
            quadrante(b, gl, sx, sy)
    ob = b.to_object((cx, cy, 0))
    # guarda-corpos desta torre vao para o objeto unico 'guarda-corpo' (em coordenadas de mundo)
    me = bpy.data.meshes.new('_tmpgc'); gl.bm.to_mesh(me); gl.bm.free()
    me.transform(__import__('mathutils').Matrix.Translation((cx, cy, 0)))
    g.bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    return ob

# ------------------------------------------------------------------ malha "unidades"
FINAIS = {   # face, faixa horizontal (y local) da varanda principal de cada final (ver 7a)
    '06': ('-x', -Y_VAR1, -Y_DIV), '05': ('-x', -Y_DIV, -Y_VAR0),
    '04': ('-x', Y_VAR0, Y_DIV),   '03': ('-x', Y_DIV, Y_VAR1),
    '07': ('+x', -Y_VAR1, -Y_DIV), '08': ('+x', -Y_DIV, -Y_VAR0),
    '01': ('+x', Y_VAR0, Y_DIV),   '02': ('+x', Y_DIV, Y_VAR1),
}
UN_OFF = 0.05          # quad 5 cm a frente da parede do fundo da varanda

def unidades():
    verts, faces, uvs, unit = [], [], [], []
    for t, (nome, (cx, cy)) in enumerate(TORRES.items(), start=1):
        for fin, (face, ya, yb) in FINAIS.items():
            sgn = 1 if face == '+x' else -1
            x = cx + sgn * (VAR_FUNDO + UN_OFF)
            y0, y1 = cy + min(ya, yb) + 0.10, cy + max(ya, yb) - 0.10
            for andar in range(NPAV):
                z0 = andar * PD + 0.35
                z1 = (andar + 1) * PD - 0.15
                if sgn > 0:
                    cs = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
                else:
                    cs = [(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)]
                k = len(verts)
                verts += cs
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

# ------------------------------------------------------------------ analise da implantacao
CROP = (43, 400, 2460, 1400)

def analisar_implantacao():
    src = bpy.data.images.load(IMPL)
    w, h = src.size
    arr = np.empty(w * h * 4, np.float32)
    src.pixels.foreach_get(arr)
    arr = arr.reshape(h, w, 4)[::-1]
    bpy.data.images.remove(src)
    x0, y0, x1, y1 = CROP
    a = arr[y0:y1, x0:x1, :3] * 255.0
    r, g, bb = a[..., 0], a[..., 1], a[..., 2]
    lum = (r + g + bb) / 3
    sat = a.max(2) - a.min(2)
    H_, W_ = lum.shape
    white = ((r > 240) & (g > 240) & (bb > 240)).astype(np.float32)
    out = boxblur(white, 6) > 0.97
    yy, xx = np.mgrid[0:H_, 0:W_]
    gx_, gy_ = xx + x0, yy + y0
    out |= (gx_ > 1870) & (gy_ < 640) & (gx_ < 2300)
    out = boxblur(out.astype(np.float32), 2) > 0.5
    cls = np.full((H_, W_), -1, np.int8)
    lum_s = boxblur(lum, 4)
    neutral = sat < 20
    linha = neutral & (lum > 205)                         # faixas brancas (vetorizadas a parte)
    cls[neutral & (lum <= 205) & (lum > 95) & (lum_s < 182)] = 2   # asfalto
    cls[neutral & (lum <= 205) & (lum > 95) & (lum_s >= 182)] = 3  # passeio
    grass = (g > r + 6) & (g > bb + 8) & (lum > 62) & (lum < 150)
    cls[grass] = 1
    water = (bb > r + 25) & (g > r + 15) & (lum > 120)
    cls[water] = 5
    court = (bb > r + 30) & (g < bb - 15) & (lum < 120)
    cls[court] = 6
    lazer = (gx_ > 1830) & (gx_ < 2330) & (gy_ > 640) & (gy_ < 1250)
    quadra = (gx_ > 2150) & (gx_ < 2265) & (gy_ > 690) & (gy_ < 825)
    cls[(cls == 5) & ~lazer] = -1
    cls[(cls == 6) & ~quadra] = -1
    db = ((bb > r + 35) & (lum < 150)).astype(np.float32)
    marc = (boxblur(db, 9) > 0.03) & ~quadra & ~((cls == 5) & lazer)
    cls[marc] = -1
    cls[out] = 0
    # preenche o que estava sob arvores/carros: primeiro so na vertical (os canteiros e as
    # fileiras de vagas correm na vertical da imagem -> divisas retas), depois nas 4 direcoes
    for it in range(120):
        unk = cls < 0
        if not unk.any():
            break
        dirs = ((1, 0), (-1, 0)) if it < 60 else ((1, 0), (-1, 0), (0, 1), (0, -1))
        for dy, dx in dirs:
            sh = np.roll(np.roll(cls, dy, 0), dx, 1)
            m = (cls < 0) & (sh >= 0)
            cls[m] = sh[m]
    cls[cls < 0] = 1
    # filtro de maioria (tira ruido da segmentacao)
    ks = [0, 1, 2, 3, 5, 6]
    acc = np.stack([boxblur((cls == k).astype(np.float32), 3) for k in ks], 0)
    cls = np.array(ks, np.int8)[acc.argmax(0)]
    linha &= ~out & ~lazer & ~marc
    # arvores (manchas rosa/amarelas/verde-escuras), como na rodada 1
    pink = (r > 165) & (bb > 125) & (g < r - 40)
    yel = (r > 190) & (g > 155) & (bb < 110) & (r - bb > 100)
    dkg = (g >= r) & (g > bb) & (lum < 62) & ~out
    arvores, cand, cell = [], [], 12
    for kind, m in (('rosa', pink), ('amarela', yel), ('verde', dkg)):
        hh, ww = H_ // cell, W_ // cell
        frac = m[:hh * cell, :ww * cell].reshape(hh, cell, ww, cell).mean((1, 3))
        for (cy_, cx_) in zip(*np.nonzero(frac > 0.35)):
            cand.append((frac[cy_, cx_], kind, (cx_ + 0.5) * cell + x0, (cy_ + 0.5) * cell + y0))
    cand.sort(key=lambda t: -t[0])
    torres_px = [(1503.5, 682.5), (919, 682.5), (330.5, 682.5)]
    for sc, kind, px, py in cand:
        if any(abs(px - tx) < 95 and abs(py - ty) < 215 for tx, ty in torres_px):
            continue
        if any((px - q[2]) ** 2 + (py - q[3]) ** 2 < 42 ** 2 for q in arvores):
            continue
        arvores.append((sc, kind, px, py))
        if len(arvores) >= 240:
            break
    return cls, linha, arvores

# ------------------------------------------------------------------ vetorizacao (marching squares)
def contornos(F, iso=0.5):
    """Contornos fechados de F (ja com borda zero). Retorna lista de arrays (n,2) em (x, y) de pixel."""
    Hh, Ww = F.shape
    B = F >= iso
    tl, tr, br, bl = B[:-1, :-1], B[:-1, 1:], B[1:, 1:], B[1:, :-1]
    case = tl * 8 + tr * 4 + br * 2 + bl * 1
    NHE = Hh * Ww
    def eid(kind, i, j):
        return (i * Ww + j) if kind == 'h' else (NHE + i * Ww + j)
    tab = {1: [('L', 'B')], 2: [('B', 'R')], 3: [('L', 'R')], 4: [('T', 'R')],
           5: [('T', 'R'), ('L', 'B')], 6: [('T', 'B')], 7: [('T', 'L')], 8: [('T', 'L')],
           9: [('T', 'B')], 10: [('T', 'L'), ('B', 'R')], 11: [('T', 'R')], 12: [('L', 'R')],
           13: [('B', 'R')], 14: [('L', 'B')]}
    segA, segB = [], []
    for cv, pairs in tab.items():
        ii, jj = np.nonzero(case == cv)
        if not len(ii):
            continue
        ed = {'T': eid('h', ii, jj), 'B': eid('h', ii + 1, jj), 'L': eid('v', ii, jj), 'R': eid('v', ii, jj + 1)}
        for a_, b_ in pairs:
            segA.append(ed[a_]); segB.append(ed[b_])
    if not segA:
        return []
    A = np.concatenate(segA); Bv = np.concatenate(segB)
    ids = np.unique(np.concatenate([A, Bv]))
    # posicao de cada ponto de aresta (interpolada)
    hmask = ids < NHE
    pos = {}
    hi = ids[hmask]; i_, j_ = hi // Ww, hi % Ww
    f0, f1 = F[i_, j_], F[i_, j_ + 1]
    t = np.clip((iso - f0) / np.where(np.abs(f1 - f0) < 1e-9, 1e-9, f1 - f0), 0, 1)
    px_h = np.stack([j_ + t, i_.astype(float)], 1)
    vi = ids[~hmask] - NHE; i2, j2 = vi // Ww, vi % Ww
    f0, f1 = F[i2, j2], F[i2 + 1, j2]
    t = np.clip((iso - f0) / np.where(np.abs(f1 - f0) < 1e-9, 1e-9, f1 - f0), 0, 1)
    px_v = np.stack([j2.astype(float), i2 + t], 1)
    P = np.zeros((len(ids), 2)); P[hmask] = px_h; P[~hmask] = px_v
    idx_of = {int(e): k for k, e in enumerate(ids)}
    nb = [[] for _ in range(len(ids))]
    for a_, b_ in zip(A.tolist(), Bv.tolist()):
        ka, kb = idx_of[a_], idx_of[b_]
        nb[ka].append(kb); nb[kb].append(ka)
    seen = np.zeros(len(ids), bool)
    out = []
    for s in range(len(ids)):
        if seen[s] or not nb[s]:
            continue
        chain = [s]; seen[s] = True
        prev, cur = -1, s
        while True:
            nx = [q for q in nb[cur] if q != prev and not seen[q]]
            if not nx:
                break
            prev, cur = cur, nx[0]
            seen[cur] = True
            chain.append(cur)
        if len(chain) >= 4:
            out.append(P[chain])
    return out

def dp(pts, tol):
    """Douglas-Peucker iterativo para polilinha fechada."""
    n = len(pts)
    if n < 5:
        return pts
    # divide no ponto mais distante do primeiro
    far = int(np.argmax(((pts - pts[0]) ** 2).sum(1)))
    keep = np.zeros(n, bool); keep[0] = keep[far] = True
    stack = [(0, far), (far, n - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        seg = pts[b] - pts[a]
        L2 = (seg ** 2).sum()
        q = pts[a + 1:b] - pts[a]
        if L2 < 1e-12:
            d = np.sqrt((q ** 2).sum(1))
        else:
            d = np.abs(q[:, 0] * seg[1] - q[:, 1] * seg[0]) / math.sqrt(L2)
        k = int(np.argmax(d))
        if d[k] > tol:
            m = a + 1 + k
            keep[m] = True
            stack += [(a, m), (m, b)]
    keep[n - 1] = True
    return pts[keep]

def area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

def poligonos_classe(cls, k, up=2, tol_m=0.14, min_area=1.5):
    m = (cls == k).astype(np.float32)
    m = np.repeat(np.repeat(m, up, 0), up, 1)
    F = boxblur(m, up + 1)
    F = np.pad(F, 1)
    polys = []
    s = S / up
    x0, y0 = CROP[0], CROP[1]
    for c in contornos(F):
        c = c - 1.0                                   # tira o pad
        c = dp(np.vstack([c, c[:1]]), tol_m / s)[:-1]
        if len(c) < 3:
            continue
        w = np.empty_like(c)
        w[:, 0] = (x0 + (c[:, 0] + 0.5) / up - OX) * S
        w[:, 1] = (OY - (y0 + (c[:, 1] + 0.5) / up)) * S
        if area(w) < min_area:
            continue
        polys.append(w)
    return polys

def faixas(linha):
    """Faixas brancas como retangulos alinhados (vagas, eixos, faixas de pedestre)."""
    rects = []
    H_, W_ = linha.shape
    x0, y0 = CROP[0], CROP[1]
    def runs(mask):  # comprimento da sequencia horizontal que contem cada pixel
        m = mask.astype(np.int32)
        L_ = np.zeros_like(m); R_ = np.zeros_like(m)
        for j in range(m.shape[1]):
            L_[:, j] = (L_[:, j - 1] + 1) * m[:, j] if j else m[:, j]
        for j in range(m.shape[1] - 1, -1, -1):
            R_[:, j] = (R_[:, j + 1] + 1) * m[:, j] if j < m.shape[1] - 1 else m[:, j]
        return L_ + R_ - 1
    def rotular(mask):
        lab = np.where(mask, np.arange(mask.size).reshape(mask.shape), mask.size).astype(np.int64)
        for _ in range(400):
            n = lab.copy()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sh = np.roll(np.roll(lab, dy, 0), dx, 1)
                n = np.where(mask, np.minimum(n, np.where(np.roll(np.roll(mask, dy, 0), dx, 1), sh, mask.size)), n)
            if (n == lab).all():
                break
            lab = n
        return lab
    for orient in ('h', 'v'):
        msk = linha if orient == 'h' else linha.T
        rl = runs(msk)
        sel = msk & (rl >= 7)
        lab = rotular(sel)
        ids = lab[sel]
        ys, xs = np.nonzero(sel)
        order = np.argsort(ids, kind='stable')
        ids, ys, xs = ids[order], ys[order], xs[order]
        cuts = np.nonzero(np.diff(ids))[0] + 1
        for gy, gx in zip(np.split(ys, cuts), np.split(xs, cuts)):
            if len(gy) < 6:
                continue
            ya, yb, xa, xb = gy.min(), gy.max() + 1, gx.min(), gx.max() + 1
            th, ln = yb - ya, xb - xa          # espessura (perpendicular) e comprimento
            if th > 7 or ln < 7 or ln < 3 * th:
                continue
            if orient == 'v':
                ya, yb, xa, xb = xa, xb, ya, yb
            # pixels -> metros; espessura minima de 0,12 m
            X0 = (x0 + xa - OX) * S; X1 = (x0 + xb - OX) * S
            Y1 = (OY - (y0 + ya)) * S; Y0 = (OY - (y0 + yb)) * S
            if orient == 'h':
                c = (Y0 + Y1) / 2; t = max(0.12, (Y1 - Y0) * 0.75)
                Y0, Y1 = c - t / 2, c + t / 2
            else:
                c = (X0 + X1) / 2; t = max(0.12, (X1 - X0) * 0.75)
                X0, X1 = c - t / 2, c + t / 2
            rects.append((X0, X1, Y0, Y1))
    return rects

def malha_de_poligonos(polys, nome):
    """Preenche poligonos (com furos por par/impar) via curva 2D e devolve uma malha."""
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.resolution_u = 1
    for p in polys:
        sp = cu.splines.new('POLY')
        sp.points.add(len(p) - 1)
        co = np.zeros((len(p), 4)); co[:, :2] = p; co[:, 3] = 1
        sp.points.foreach_set('co', co.ravel())
        sp.use_cyclic_u = True
    ob = bpy.data.objects.new(nome, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    return me

# ------------------------------------------------------------------ terreno vetorial
def terreno(cls, linha):
    b = Builder('terreno')
    bm = b.bm
    x0, y0, x1, y1 = CROP
    X0, Y0 = px2m(x0, y1); X1, Y1 = px2m(x1, y0)
    def plano(cs, m, scale=8.0):
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        f.material_index = b.mi(m); f.normal_update(); b._uv(f, (scale, scale))
    plano([(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], MATS['grama'])
    # entorno (moldura de 4 km) em objeto separado: a quantizacao Draco e por primitiva,
    # e a moldura gigante estragaria a precisao do chao do condominio
    be = Builder('entorno')
    E = 4000.0
    ring = [(-E, -E), (E, -E), (E, E), (-E, E)]
    inner = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    for k in range(4):
        a1, a2 = ring[k], ring[(k + 1) % 4]
        b1, b2 = inner[k], inner[(k + 1) % 4]
        f = be.bm.faces.new([be.bm.verts.new(c) for c in ((*a1, -0.02), (*a2, -0.02), (*b2, -0.02), (*b1, -0.02))])
        f.material_index = be.mi(MATS['entorno']); f.normal_update(); be._uv(f, (30.0, 30.0))
    be.to_object()
    stats = {}
    camadas = [(0, 'entorno', 0.004), (2, 'asfalto', 0.010), (3, 'passeio', 0.025),
               (5, 'agua', 0.03), (6, 'quadra', 0.03)]
    for k, mname, z in camadas:
        polys = poligonos_classe(cls, k)
        stats[mname] = [len(polys), int(sum(len(p) for p in polys))]
        if not polys:
            continue
        me = malha_de_poligonos(polys, 'tmp_' + mname)
        mi = b.mi(MATS[mname])
        for p in me.polygons:
            p.material_index = mi
        uvl = me.uv_layers.new(name='UVMap')
        for li, loop in enumerate(me.loops):
            co = me.vertices[loop.vertex_index].co
            uvl.data[li].uv = (co.x / 8.0, co.y / 8.0)
        for v in me.vertices:
            v.co.z = z
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    # faixas brancas
    rects = faixas(linha)
    for (a, c, d, e) in rects:
        plano([(a, d, 0.035), (c, d, 0.035), (c, e, 0.035), (a, e, 0.035)], MATS['faixa'])
    stats['faixas'] = len(rects)
    # muro do garden em volta de cada torre (17,1 x 41,7 m pela implantacao), aberto na entrada (+x)
    for nome, (cx, cy) in TORRES.items():
        gx, gy, t, hm = 8.55, 20.85, 0.2, 1.8
        b.box(cx - gx, cx - gx + t, cy - gy, cy + gy, 0, hm, MATS['muro'])
        b.box(cx - gx, cx + gx, cy - gy, cy - gy + t, 0, hm, MATS['muro'])
        b.box(cx - gx, cx + gx, cy + gy - t, cy + gy, 0, hm, MATS['muro'])
        b.box(cx + gx - t, cx + gx, cy - gy, cy - 4.0, 0, hm, MATS['muro'])
        b.box(cx + gx - t, cx + gx, cy + 4.0, cy + gy, 0, hm, MATS['muro'])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    ob = b.to_object()
    return ob, stats

# ------------------------------------------------------------------ arvores organicas
def _ruido(rnd):
    ds = []
    for _ in range(4):
        v = np.array([rnd.gauss(0, 1) for _ in range(3)]); v /= np.linalg.norm(v)
        ds.append((v, rnd.uniform(1.6, 3.2), rnd.uniform(0, 6.28)))
    return lambda p: sum(math.sin(w * float(np.dot(p, d)) + ph) for d, w, ph in ds) / 4.0

def copa(bm, b, rnd, c, rad, esc_z, mname, sub=2, amp=0.16):
    ret = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    f = _ruido(rnd)
    for v in ret['verts']:
        p = np.array(v.co[:])
        k = 1 + amp * f(p * 1.0)
        v.co.x = c[0] + p[0] * rad * k
        v.co.y = c[1] + p[1] * rad * k
        v.co.z = c[2] + p[2] * rad * k * esc_z
        if v.co.z < c[2] - rad * esc_z * 0.55:          # base mais achatada
            v.co.z = c[2] - rad * esc_z * 0.55 + (v.co.z - (c[2] - rad * esc_z * 0.55)) * 0.35
    for ff in {f_ for v in ret['verts'] for f_ in v.link_faces}:
        ff.material_index = b.mi(MATS[mname]); ff.smooth = True
        b._uv(ff, (5, 5))

def tronco(bm, b, x, y, h, r0, r1, inc=(0, 0)):
    ret = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=r0, radius2=r1, depth=h)
    for v in ret['verts']:
        t = (v.co.z + h / 2) / h
        v.co.x += x + inc[0] * t * h; v.co.y += y + inc[1] * t * h; v.co.z += h / 2
    for ff in {f for v in ret['verts'] for f in v.link_faces}:
        ff.material_index = b.mi(MATS['tronco']); ff.smooth = True
        b._uv(ff, (2, 2))

def palmeira(bm, b, rnd, x, y):
    h = rnd.uniform(8.0, 11.5)
    inc = (rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04))
    tronco(bm, b, x, y, h, 0.22, 0.16, inc)
    top = np.array([x + inc[0] * h, y + inc[1] * h, h])
    n = 9
    a0 = rnd.uniform(0, 6.28)
    mi = b.mi(MATS['palmeira'])
    for k in range(n):
        a = a0 + k * 2 * math.pi / n + rnd.uniform(-0.15, 0.15)
        Lf = rnd.uniform(3.0, 4.0)
        up = rnd.uniform(0.6, 1.2)
        d = np.array([math.cos(a), math.sin(a), 0.0]); s = np.array([-d[1], d[0], 0.0])
        segs = 5
        row = []
        for i in range(segs + 1):
            t = i / segs
            c = top + d * Lf * t + np.array([0, 0, up * t - (up + 1.6) * t * t])
            w = 0.55 * math.sin(math.pi * min(1, t * 1.1)) + 0.04
            row.append((c - s * w + np.array([0, 0, -0.12 * w]), c, c + s * w + np.array([0, 0, -0.12 * w])))
        for i in range(segs):
            for (pa, pb) in ((0, 1), (1, 2)):
                vs = [bm.verts.new(row[i][pa]), bm.verts.new(row[i][pb]),
                      bm.verts.new(row[i + 1][pb]), bm.verts.new(row[i + 1][pa])]
                f = bm.faces.new(vs); f.material_index = mi; f.smooth = True
                b._uv(f, (3, 3))

def arvores_obj(arvores):
    b = Builder('arvores')
    bm = b.bm
    rnd = random.Random(11)
    cont = {}
    for sc, kind, px, py in arvores:
        x, y = px2m(px, py)
        lazer = px > 1830
        if kind == 'verde' and lazer and rnd.random() < 0.7:
            esp = 'palmeira'
        elif kind == 'rosa':
            esp = 'ipe_rosa'
        elif kind == 'amarela':
            esp = 'ipe_amarelo'
        else:
            esp = rnd.choice(['copa_verde', 'copa_verde', 'copa_verde_clara', 'copa_verde_escura'])
        cont[esp] = cont.get(esp, 0) + 1
        if esp == 'palmeira':
            palmeira(bm, b, rnd, x, y)
            continue
        # fuste curto (2-3 m ate a base da copa) e copa larga, como nos renders do book
        if esp.startswith('ipe'):
            fuste = rnd.uniform(2.4, 3.2); rad = rnd.uniform(2.7, 3.4); ez = 0.62
        else:
            fuste = rnd.uniform(1.8, 2.8); rad = rnd.uniform(2.5, 3.4); ez = 0.82
        cz = fuste + rad * ez * 0.55
        tronco(bm, b, x, y, cz + rad * ez * 0.2, 0.22, 0.12)
        copa(bm, b, rnd, (x, y, cz), rad, ez, esp, sub=3)
        for _ in range(3):                    # lobulos laterais (silhueta irregular)
            a = rnd.uniform(0, 6.28); dd = rad * rnd.uniform(0.40, 0.62)
            copa(bm, b, rnd, (x + dd * math.cos(a), y + dd * math.sin(a), cz + rad * ez * rnd.uniform(-0.3, 0.25)),
                 rad * rnd.uniform(0.48, 0.62), ez, esp, sub=2, amp=0.12)
    return b.to_object(), cont

# ------------------------------------------------------------------ layout das unidades (referencia)
def layout_unidades():
    out = {
        'schema': 'gaia-unidades-layout/2',
        'unidades_medida': 'metros; Z para cima (Blender). No glTF Y-up: (x, y, z)_blender -> (x, z, -y)_gltf',
        'pe_direito': PD, 'pavimentos': NPAV,
        'andar_z': 'z0 = andar*pe_direito + z_rel[0], z1 = (andar+1)*pe_direito + z_rel[1]',
        'z_rel': [0.35, -0.15],
        'plano': 'fundo da varanda: x_plano = centro + normal*(4,9 + 0,05)',
        'janelas_quadrante_local': [dict(zip(('tipo', 'plano', 'coord', 'faixa', 'material', 'ambiente'),
                                             (j[0], j[1], round(j[2], 3), list(j[3]), j[4], j[5]))) for j in JANELAS],
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

# ------------------------------------------------------------------ main
def build():
    limpar()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    criar_materiais()
    cls, linha, arv = analisar_implantacao()
    g = Builder('guarda-corpo')
    for nome, (cx, cy) in TORRES.items():
        torre(nome, cx, cy, g)
    g.mats = [MATS['guarda_corpo']]
    g.to_object()
    _, nun = unidades()
    _, st = terreno(cls, linha)
    _, cont = arvores_obj(arv)
    layout_unidades()
    tris = {}
    for o in sc.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            tris[o.name] = len(o.data.loop_triangles)
    return {'tris': tris, 'total': sum(tris.values()), 'unidades_unicas': nun,
            'arvores': cont, 'chao': st}

result['build'] = build()
