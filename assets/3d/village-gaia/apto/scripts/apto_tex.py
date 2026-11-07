# apto_tex.py -- texturas do apartamento decorado (numpy + bpy, roda no Blender sem interface):
#   Blender -b --factory-startup -P apto_tex.py -- [pasta com as fotos do decorado, para os quadros e o mural]
# Procedurais: pisos, azulejos, madeiras, pedras, tecidos. Quadros e mural: recortes retificados das fotos reais.
import bpy, math, os, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(AQUI, '..', 'tex')
os.makedirs(TEX, exist_ok=True)
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
FOTOS = ARGS[0] if ARGS else None


def salva(a, nome, q=88):
    """a: h x w x 3|4, 0..1, linha 0 = topo da imagem."""
    a = np.clip(np.asarray(a, np.float32), 0, 1)
    h, w = a.shape[:2]
    if a.shape[2] == 3:
        a = np.dstack([a, np.ones((h, w), np.float32)])
    im = bpy.data.images.new(nome, w, h, alpha=True)
    im.pixels.foreach_set(a[::-1].ravel())
    im.filepath_raw = os.path.join(TEX, nome)
    im.file_format = 'PNG' if nome.endswith('.png') else 'JPEG'
    bpy.context.scene.render.image_settings.quality = q
    im.save(quality=q) if nome.endswith('.jpg') else im.save()
    bpy.data.images.remove(im)
    print('  ', nome, w, h)


def ruido(n, sig, seed, m=None):
    m = m or n
    r = np.random.default_rng(seed).normal(0, 1, (n, m))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.rfftfreq(m)[None, :]
    k = np.exp(-2 * (math.pi ** 2) * (sig ** 2) * (fx ** 2 + fy ** 2))
    a = np.fft.irfft2(np.fft.rfft2(r) * k, s=(n, m))
    return (a - a.mean()) / (a.std() + 1e-9)


def ruido_aniso(n, sx, sy, seed):
    r = np.random.default_rng(seed).normal(0, 1, (n, n))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.rfftfreq(n)[None, :]
    k = np.exp(-2 * (math.pi ** 2) * ((sx * fx) ** 2 + (sy * fy) ** 2))
    a = np.fft.irfft2(np.fft.rfft2(r) * k, s=(n, n))
    return (a - a.mean()) / (a.std() + 1e-9)


def madeira(nome, cor, reguas=0, seed=1, contraste=1.0, n=1024):
    """Veio na horizontal (u). reguas>0: piso em reguas; 0: painel continuo de marcenaria."""
    c = np.array(cor, np.float32)
    veio = ruido_aniso(n, 90, 1.6, seed)
    largo = ruido_aniso(n, 160, 14, seed + 1)
    fino = ruido_aniso(n, 26, 0.7, seed + 2)
    v = 1 + contraste * (0.040 * veio + 0.055 * largo + 0.020 * fino)
    if reguas:
        rng = np.random.default_rng(seed + 3)
        h = n // reguas
        for j in range(reguas):
            a, b = j * h, (j + 1) * h if j < reguas - 1 else n
            v[a:b] += rng.normal(0, 0.035)
            v[a:b] = np.roll(v[a:b], int(rng.integers(0, n)), 1)
            v[a:a + 2] *= 0.72
            for x in (int(rng.integers(0, n)), int(rng.integers(0, n))):
                v[a:b, x:x + 2] *= 0.72
    salva(v[..., None] * c, nome)


def azulejo(nome, cor, nx, ny, junta, seed, var=0.03, junta_cor=0.8, zellige=0.0, n=1024):
    """Grade nx x ny de pecas; junta em px. zellige>0: tom e relevo irregulares por peca."""
    rng = np.random.default_rng(seed)
    a = np.zeros((n, n), np.float32) + 1
    a += 0.008 * ruido(n, 2, seed + 1) + zellige * 0.25 * ruido(n, 18, seed + 2)
    px, py = n / nx, n / ny
    m = np.ones((n, n), np.float32)
    for j in range(ny):
        for i in range(nx):
            x0, x1, y0, y1 = int(i * px), int((i + 1) * px), int(j * py), int((j + 1) * py)
            a[y0:y1, x0:x1] += rng.normal(0, var + zellige)
            m[y0:y0 + junta, x0:x1] = 0
            m[y0:y1, x0:x0 + junta] = 0
    c = np.array(cor, np.float32)
    im = a[..., None] * c
    im = im * m[..., None] + (1 - m[..., None]) * c * junta_cor
    salva(im, nome)


def pedra(nome, cor, seed, grao=0.05, pintas=0.10, n=1024):
    c = np.array(cor, np.float32)
    rng = np.random.default_rng(seed)
    v = 1 + 0.02 * ruido(n, 40, seed) + grao * ruido(n, 1.2, seed + 1)
    esc = (ruido(n, 1.8, seed + 2) > 1.25) * -pintas * 2
    cla = (ruido(n, 1.6, seed + 3) > 1.45) * pintas * 1.5
    salva((v + esc + cla)[..., None] * c, nome, 86)


def marmore(nome, seed, n=1024):
    base = 0.82 + 0.03 * ruido(n, 60, seed)
    veio = np.abs(ruido(n, 50, seed + 1) + 0.5 * ruido(n, 18, seed + 2))
    v = np.exp(-(veio / 0.09) ** 2)
    a = base - 0.22 * v + 0.012 * ruido(n, 1.5, seed + 3)
    salva(np.dstack([a, a, a * 1.005]), nome, 86)


def tecido(nome, seed, boucle=False, n=512):
    if boucle:
        v = 0.95 + 0.028 * ruido(n, 2.6, seed) + 0.016 * ruido(n, 1.0, seed + 1)
    else:
        y, x = np.mgrid[0:n, 0:n]
        t = np.sin(x * math.pi / 2) * 0.02 + np.sin(y * math.pi / 2) * 0.02
        v = 0.90 + t + 0.022 * ruido_aniso(n, 14, 0.6, seed) + 0.022 * ruido_aniso(n, 0.6, 14, seed + 1)
    salva(np.dstack([v, v, v]), nome, 84)


def juta(n=1024):
    y, x = np.mgrid[0:n, 0:n] - n / 2 + 0.5
    r = np.hypot(x, y) / (n / 2)
    th = np.arctan2(y, x)
    espiral = np.sin(r * 2 * math.pi * 34 + th) * 0.5 + 0.5
    trama = np.sin(th * 260 + r * 90) * 0.5 + 0.5
    v = 0.62 + 0.26 * espiral + 0.10 * trama * espiral + 0.05 * ruido(n, 1.2, 77)
    c = np.array([0.80, 0.66, 0.45], np.float32)
    salva(v[..., None] * c, 'juta.jpg', 86)


def listrado(n=1024):
    x = np.arange(n)
    v = np.ones(n, np.float32) * 0.93
    rng = np.random.default_rng(5)
    p = 0
    while p < n:
        w = int(rng.integers(10, 44))
        v[p:p + w] = rng.choice([0.93, 0.90, 0.86, 0.95])
        v[p:p + 2] -= 0.05
        p += w
    a = np.tile(v[None, :], (n, 1)) + 0.006 * ruido(n, 2, 8)
    salva(np.dstack([a, a * 0.985, a * 0.955]), 'listrado.jpg', 86)


def teto(n=1024):
    v = 0.965 + 0.012 * ruido(n, 1.0, 21) + 0.006 * ruido(n, 6, 22)
    salva(np.dstack([v, v, v]), 'teto.jpg', 80)


def reboco_claro(n=1024):
    v = 0.965 + 0.010 * ruido(n, 1.2, 31) + 0.006 * ruido(n, 40, 32)
    salva(np.dstack([v, v, v]), 'parede.jpg', 80)


def canelado(n=256):
    x = np.arange(n)
    onda = 0.5 + 0.5 * np.cos(x * 2 * math.pi / (n / 8))
    a = np.ones((16, n, 4), np.float32)
    a[..., :3] = np.array([0.94, 0.96, 0.95])
    a[..., 3] = 0.42 + 0.34 * onda
    salva(a, 'canelado.png')


def cortina(n=512):
    """Uma dobra por repeticao em u: claro na crista, sombra no vale, com trama fina de linho."""
    x = np.arange(n) / n
    dobra = 0.74 + 0.26 * (0.5 + 0.5 * np.cos(2 * math.pi * x)) ** 0.8
    v = np.tile(dobra[None, :], (n, 1)) * (0.97 + 0.016 * ruido_aniso(n, 0.6, 14, 91) + 0.016 * ruido_aniso(n, 14, 0.6, 92))
    salva(np.dstack([v, v, v * 0.985]), 'cortina.jpg', 86)


def ratan(n=512):
    y, x = np.mgrid[0:n, 0:n]
    a = np.zeros((n, n, 4), np.float32)
    d1 = np.sin((x + y) * 2 * math.pi / 40)
    d2 = np.sin((x - y) * 2 * math.pi / 40)
    m = ((d1 > 0.55) | (d2 > 0.55)) | (y % 128 < 8)
    a[..., :3] = np.array([0.62, 0.46, 0.28])
    a[..., 3] = m.astype(np.float32)
    salva(a, 'ratan.png')


def palhinha(n=256):
    y, x = np.mgrid[0:n, 0:n]
    v = 0.78 + 0.09 * np.sin(x * 2 * math.pi / 16) * np.sign(np.sin(y * 2 * math.pi / 32)) + 0.05 * ruido(n, 1.5, 44)
    salva(v[..., None] * np.array([0.92, 0.80, 0.58], np.float32), 'palhinha.jpg', 84)


# ---------------------------------------------------------- recortes das fotos (homografia inversa)
def homografia(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.array(A, float))
    return vt[-1].reshape(3, 3)


def carrega(nome):
    im = bpy.data.images.load(os.path.join(FOTOS, nome))
    w, h = im.size
    a = np.zeros(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1, :, :3]   # linha 0 = topo; valores como estao no arquivo


def retifica(foto, cantos, w, h, nome, escala=3000 / 760, brilho=1.0):
    """cantos: tl, tr, br, bl em px da miniatura de 760 de largura."""
    a = carrega(foto)
    p = [(c[0] * escala, c[1] * escala) for c in cantos]
    H = homografia([(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)], p)
    yy, xx = np.mgrid[0:h, 0:w]
    q = H @ np.stack([xx.ravel(), yy.ravel(), np.ones(w * h)])
    u, v = q[0] / q[2], q[1] / q[2]
    u0 = np.clip(np.floor(u).astype(int), 0, a.shape[1] - 2)
    v0 = np.clip(np.floor(v).astype(int), 0, a.shape[0] - 2)
    fu, fv = (u - u0)[:, None], (v - v0)[:, None]
    c = (a[v0, u0] * (1 - fu) * (1 - fv) + a[v0, u0 + 1] * fu * (1 - fv) +
         a[v0 + 1, u0] * (1 - fu) * fv + a[v0 + 1, u0 + 1] * fu * fv)
    salva(c.reshape(h, w, 3) * brilho, nome, 88)


# ---------------------------------------------------------- saida
print('texturas do apartamento')
madeira('piso_laminado.jpg', (0.84, 0.70, 0.53), reguas=6, seed=11, contraste=0.9)       # 1024 px = 1,2 m (reguas de 20 cm)
madeira('mad_nogueira.jpg', (0.62, 0.43, 0.29), seed=21, contraste=1.5)                   # armarios da cozinha
madeira('mad_carvalho.jpg', (0.80, 0.63, 0.45), seed=31, contraste=1.1)                   # meia parede, prateleiras, paineis
azulejo('azulejo_branco.jpg', (0.90, 0.89, 0.86), 8, 2, 3, 41, var=0.015, junta_cor=0.86)  # 7,5 x 30 cm (uv 0,6 m)
azulejo('azulejo_salvia.jpg', (0.66, 0.74, 0.67), 4, 4, 3, 51, var=0.02, zellige=0.025, junta_cor=0.92)  # 15 x 15 cm (uv 0,6 m)
pedra('granito_cinza.jpg', (0.50, 0.50, 0.49), 61, grao=0.07, pintas=0.14)
pedra('granilite_bege.jpg', (0.82, 0.77, 0.67), 62, grao=0.03, pintas=0.05)
marmore('marmore.jpg', 71)
tecido('boucle.jpg', 81, boucle=True)
tecido('linho.jpg', 82)
juta()
listrado()
teto()
reboco_claro()
canelado()
cortina()
ratan()
palhinha()
if FOTOS:
    retifica('DSC_0691.jpg', [(8, 2), (124, 21), (122, 110), (6, 96)], 620, 500, 'arte_1.jpg', brilho=1.3)
    retifica('DSC_0691.jpg', [(5, 110), (122, 122), (120, 207), (4, 198)], 620, 480, 'arte_2.jpg', brilho=1.3)
    retifica('DSC_0691.jpg', [(130, 209), (222, 211), (221, 291), (129, 291)], 620, 540, 'arte_3.jpg', brilho=1.3)
    retifica('DSC_0652.jpg', [(464, 70), (516, 65), (516, 118), (464, 124)], 520, 520, 'arte_4.jpg', brilho=1.3)
    retifica('DSC_0652.jpg', [(372, 138), (412, 132), (412, 178), (372, 180)], 420, 480, 'arte_5.jpg', brilho=1.3)
    retifica('DSC_0652.jpg', [(415, 133), (460, 126), (460, 172), (415, 176)], 460, 480, 'arte_6.jpg', brilho=1.3)
    retifica('DSC_0677.jpg', [(410, 172), (645, 146), (643, 412), (410, 365)], 1000, 900, 'mural.jpg', brilho=1.08)
print('ok')
