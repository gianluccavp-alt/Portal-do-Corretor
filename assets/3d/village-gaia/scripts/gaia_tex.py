#!/usr/bin/env python3
"""Texturas de alta definicao do Village Gaia, 100% procedurais (numpy + pillow, fora do Blender).
Saida em tex/. As tileaveis usam ruido periodico (FFT). Rode antes do gerador quando mudar algo aqui:
  python gaia_tex.py"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(AQUI, 'tex')
os.makedirs(TEX, exist_ok=True)
FONTE = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONTE_B = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def fonte(t, b=False):
    return ImageFont.truetype(FONTE_B if b else FONTE, t)


def ruido(n, sig, seed, m=None):
    """ruido gaussiano periodico normalizado (media 0, desvio 1)."""
    m = m or n
    r = np.random.default_rng(seed).normal(0, 1, (n, m))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.rfftfreq(m)[None, :]
    k = np.exp(-2 * (math.pi ** 2) * (sig ** 2) * (fx ** 2 + fy ** 2))
    a = np.fft.irfft2(np.fft.rfft2(r) * k, s=(n, m))
    return (a - a.mean()) / (a.std() + 1e-9)


def salva(a, nome, q=88):
    a = np.clip(a, 0, 1)
    im = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    p = os.path.join(TEX, nome)
    if nome.endswith('.jpg'):
        im.convert('RGB').save(p, quality=q, subsampling=0)
    else:
        im.save(p, optimize=True)
    return p


def cinza(a):
    return np.stack([a] * 3, 2)


def normal_de(h, k):
    du = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    dv = np.roll(h, 1, 0) - np.roll(h, -1, 0)
    n = np.stack([-k * du, -k * dv, np.ones_like(h)], 2)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


# ------------------------------------------------------------------ pisos e paredes
def asfalto():
    n = 1024
    rng = np.random.default_rng(1)
    g = ruido(n, 0.7, 2)
    m = ruido(n, 40, 3)
    m2 = ruido(n, 6, 4)
    sal = (rng.random((n, n)) > 0.975) * 0.10 - (rng.random((n, n)) > 0.97) * 0.06
    v = 0.335 + 0.022 * g + 0.018 * m + 0.012 * m2 + sal
    salva(np.stack([v, v, v * 1.02], 2), 'asfalto2.jpg', 80)


def concreto():
    n = 1024  # 4 m: placas de 2 m com junta
    g = ruido(n, 0.8, 5)
    m = ruido(n, 30, 6)
    v = 0.86 + 0.018 * g + 0.022 * m
    j = np.zeros((n, n))
    for p in (0, n // 2):
        j[max(0, p - 1):p + 2, :] = 1
        j[:, max(0, p - 1):p + 2] = 1
    v = v - 0.28 * j
    salva(cinza(v), 'concreto.jpg', 80)


def paver():
    """Paver retangular 10x20 em espinha de peixe: 1024 px = 2,4 m (24 modulos). Cinza neutro, tingido."""
    n, mods = 1024, 24
    c = n / mods
    rng = np.random.default_rng(7)
    ids = np.zeros((mods, mods), int)
    tom = {}
    k = 1
    for j0 in range(0, mods, 4):
        for i0 in range(0, mods, 4):
            for j in range(4):
                for cel in (((i0 + j) % mods, (j0 + j) % mods), ((i0 + j + 1) % mods, (j0 + j) % mods)):
                    ids[cel[1], cel[0]] = k
                k += 1
                for cel in (((i0 + j + 2) % mods, (j0 + j) % mods), ((i0 + j + 2) % mods, (j0 + j - 1) % mods)):
                    ids[cel[1], cel[0]] = k
                k += 1
    for u in np.unique(ids):
        tom[u] = rng.normal(0, 0.05)
    yy, xx = np.mgrid[0:n, 0:n]
    cx, cy = (xx / c).astype(int), (yy / c).astype(int)
    idp = ids[cy % mods, cx % mods]
    v = np.vectorize(tom.get)(idp).astype(np.float32) + 0.80
    # junta onde o id muda
    junta = (idp != np.roll(idp, 2, 0)) | (idp != np.roll(idp, 2, 1)) | (idp != np.roll(idp, -2, 0)) | (idp != np.roll(idp, -2, 1))
    v -= 0.42 * junta
    v += 0.018 * ruido(n, 0.8, 8) + 0.02 * ruido(n, 25, 9)
    salva(cinza(v), 'paver.jpg', 82)


def porcelanato():
    """Porcelanato 90x90 (4 x 4 pecas em 3,6 m), veio de pedra suave. Cinza neutro, tingido."""
    n = 1024
    p = n // 4
    v = 0.88 + 0.012 * ruido(n, 45, 10) + 0.006 * ruido(n, 6, 11) + 0.004 * ruido(n, 1, 12)
    rng = np.random.default_rng(13)
    for j in range(4):
        for i in range(4):
            v[j * p:(j + 1) * p, i * p:(i + 1) * p] += rng.normal(0, 0.012)
    for k in range(0, n, p):
        v[max(0, k - 1):k + 1, :] -= 0.34
        v[:, max(0, k - 1):k + 1] -= 0.34
    salva(cinza(v), 'porcelanato.jpg', 82)


def madeira_piso():
    """Piso vinilico amadeirado: reguas de 19 cm, 1024 px = 3 m."""
    n = 1024
    rng = np.random.default_rng(14)
    h = 65
    fibra = ruido(n, 1.2, 15)
    fibra = np.apply_along_axis(lambda c: c, 0, fibra)
    a = np.zeros((n, n, 3), np.float32)
    grao = ruido(n, 0.6, 16)
    for lin in range(0, n, h):
        d = rng.integers(0, n)
        tom = rng.normal(0, 0.05)
        fim = min(n, lin + h)
        y = np.arange(lin, fim)
        ond = ruido(n, 18, int(rng.integers(1000, 9000)))[y][:, :]
        tracos = np.sin((y[:, None] / 2.3 + 6 * ond)) * 0.5
        v = 1 + tom + 0.05 * tracos + 0.025 * np.roll(grao[y], d, 1)
        cor = np.array([0.72, 0.55, 0.37], np.float32)
        a[lin:fim] = v[..., None] * cor
        a[lin:min(n, lin + 2)] *= 0.62
        for x in (d, (d + n // 2) % n):
            a[lin:fim, x:x + 2] *= 0.62
    salva(a, 'madeira_piso.jpg', 84)


def madeira_fina():
    n = 512
    # veio alongado no sentido u: mistura ruido bem esticado em x (repete a linha filtrada em y)
    base = ruido(n, 3, 17, n)
    r = np.zeros((n, n))
    for k in range(-40, 41, 8):
        r += np.roll(base, k * 3, 1)
    r = (r - r.mean()) / r.std()
    y = np.arange(n)[:, None]
    tr = 0.5 + 0.5 * np.sin(y / 3.1 + 3.2 * r)
    v = 0.76 + 0.09 * tr + 0.018 * ruido(n, 0.7, 18)
    salva(cinza(v), 'madeira_fina.jpg', 82)


def ripado():
    """Painel ripado (ripas verticais de 3 cm com sombra entre elas), 512 px = 1 m. Cinza, tingido."""
    n = 512
    x = np.arange(n)
    p = n // 20
    per = (x % p) / p
    perfil = 0.92 - 0.55 * (per > 0.78) + 0.05 * np.sin(per * math.pi)
    v = perfil[None, :] * np.ones((n, 1)) + 0.012 * ruido(n, 6, 19)
    salva(cinza(v), 'ripado.jpg', 80)


def pastilha():
    """Pastilha de vidro da piscina: 5 x 5 cm, verde-agua com variacao. 1024 px = 1,6 m."""
    n, q = 1024, 32
    rng = np.random.default_rng(20)
    a = np.zeros((n, n, 3), np.float32)
    base = np.array([0.20, 0.56, 0.54], np.float32)
    for j in range(n // q):
        for i in range(n // q):
            t = rng.normal(0, 0.11)
            cor = base * (1 + t) + np.array([0.0, rng.normal(0, 0.03), rng.normal(0, 0.03)])
            a[j * q:(j + 1) * q, i * q:(i + 1) * q] = cor
    for k in range(0, n, q):
        a[k:k + 2, :] = (0.62, 0.70, 0.70)
        a[:, k:k + 2] = (0.62, 0.70, 0.70)
    salva(a, 'pastilha.jpg', 84)


def agua_normal():
    n = 512
    h = 0.55 * ruido(n, 9, 21) + 0.3 * ruido(n, 4, 22) + 0.15 * ruido(n, 1.8, 23)
    salva(normal_de(h, 1.3), 'agua_normal.jpg', 85)


def reboco_fino():
    """Textura grafiato fino (grao da fachada): cor neutra + normal. 1024 px = 2,9 m (1 pavimento:
    junta horizontal exatamente na laje). v = 0 na laje."""
    n = 1024
    g = ruido(n, 0.9, 24)
    g2 = ruido(n, 2.2, 25)
    m = ruido(n, 60, 26)
    y = np.arange(n)[:, None]
    dist = np.minimum(y, n - 1 - y) * np.ones((1, n))
    junta = np.clip(2.6 - dist, 0, 1)
    sombra = np.exp(-np.maximum(0, y - 2) / 22.0) * np.ones((1, n))  # linha logo abaixo da junta
    v = 0.90 + 0.026 * g + 0.02 * g2 + 0.012 * m - 0.42 * junta - 0.03 * sombra
    salva(cinza(v), 'reboco_fino.jpg', 80)
    salva(normal_de(0.6 * g + 0.4 * g2 - 3.5 * junta, 0.11)[::1, ::1], 'reboco_fino_n.jpg', 82)


def bloco():
    """Bloco de concreto aparente 39 x 19 cm: 1024 px = 3,2 m."""
    n, w, h = 1024, 128, 64
    rng = np.random.default_rng(27)
    v = np.zeros((n, n), np.float32)
    for j in range(n // h):
        ofs = (j % 2) * w // 2
        for i in range(-1, n // w + 1):
            x0 = (i * w + ofs)
            t = 0.60 + rng.normal(0, 0.035)
            xs = np.arange(x0, x0 + w) % n
            v[j * h:(j + 1) * h, xs] = t
    v += 0.022 * ruido(n, 1.0, 28) + 0.02 * ruido(n, 7, 29)
    for j in range(n // h):
        v[j * h:j * h + 3, :] -= 0.22
        ofs = (j % 2) * w // 2
        for i in range(0, n // w + 1):
            xs = np.arange(i * w + ofs, i * w + ofs + 3) % n
            v[j * h:(j + 1) * h, xs] -= 0.22
    salva(cinza(v), 'bloco.jpg', 80)


def emborrachado():
    n = 512
    rng = np.random.default_rng(30)
    v = 0.86 + 0.05 * ruido(n, 0.8, 31) + 0.015 * ruido(n, 20, 32)
    v += (rng.random((n, n)) > 0.93) * 0.09 - (rng.random((n, n)) > 0.93) * 0.11
    salva(cinza(v), 'emborrachado.jpg', 80)


def tecido():
    n = 256
    x = np.arange(n)
    t = (np.sin(x * math.pi / 2)[None, :] * 0.5 + np.sin(x * math.pi / 2)[:, None] * 0.5)
    v = 0.84 + 0.05 * t + 0.03 * ruido(n, 0.7, 33)
    salva(cinza(v), 'tecido.jpg', 80)


def grama():
    """Grama de jardim, verde profundo, sem o aspecto de ruido liso. 1024 px = 6 m."""
    n = 1024
    rng = np.random.default_rng(34)
    im = Image.new('RGB', (n, n), (58, 86, 34))
    d = ImageDraw.Draw(im)
    for _ in range(60000):
        x, y = rng.integers(0, n, 2)
        L = rng.integers(5, 13)
        a = rng.uniform(-0.6, 0.6)
        t = rng.random()
        c = (int(46 + 44 * t), int(78 + 58 * t), int(24 + 24 * t))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                if 0 <= x + ox < n + 14 and 0 <= y + oy < n + 14:
                    d.line((x + ox, y + oy, x + ox + L * math.sin(a), y + oy - L * math.cos(a)), fill=c, width=1)
    a = np.asarray(im).astype(np.float32) / 255
    m = ruido(n, 55, 35)[..., None]
    m2 = ruido(n, 14, 36)[..., None]
    a *= 1 + 0.045 * m + 0.05 * m2
    a += (m * 0.006) * np.array([1.0, 0.6, 0.0], np.float32)
    salva(a, 'grama2.jpg', 80)


def tronco_palmeira():
    h, w = 512, 128
    a = np.ones((h, w, 3), np.float32) * np.array([0.42, 0.36, 0.28], np.float32)
    rng = np.random.default_rng(37)
    for y in range(0, h, 16):
        d = rng.integers(0, 6)
        a[y + d:y + d + 3] *= 0.8
        a[y + d + 3:y + d + 5] *= 1.08
    a *= (1 + 0.14 * ruido(h, 3, 38, w))[..., None]
    salva(a, 'tronco_palmeira.jpg', 78)


# ------------------------------------------------------------------ vegetacao (alfa)
def _alfa_salva(im, nome):
    """Preenche o RGB transparente com a cor media (evita halo escuro nos mipmaps)."""
    a = np.asarray(im).astype(np.float32) / 255
    al = a[..., 3:] > 0.02
    med = a[..., :3][al[..., 0]].mean(0)
    a[..., :3] = np.where(al, a[..., :3], med)
    salva(a, nome)


def fronde():
    """Fronde de palmeira: u ao longo da raque, v atravessa. Folhetos finos caindo para as bordas."""
    w, h = 1024, 256
    k = 2
    im = Image.new('RGBA', (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(40)
    cy = h * k / 2
    for i in range(170):
        t = i / 170
        x = (0.04 + t * 0.95) * w * k
        L = (h * k * 0.49) * math.sin(math.pi * min(1, (t * 0.92 + 0.08))) ** 0.55 * (1 - 0.15 * t)
        for lado in (-1, 1):
            ang = (0.82 - 0.35 * t) + rng.uniform(-0.07, 0.07)
            comp = L * rng.uniform(0.86, 1.0)
            x1 = x + comp * math.cos(ang) * 1.05
            y1 = cy + lado * comp * math.sin(ang) / max(0.5, math.sin(ang))
            esp = 4 * k * (1.1 - 0.5 * t)
            tom = rng.uniform(0.70, 1.0)
            cor = (int(255 * tom), int(255 * tom), int(255 * tom), 255)
            base = [(x - esp, cy), (x + esp, cy), (x1, y1)]
            d.polygon(base, fill=cor)
    d.line((0, cy, w * k, cy), fill=(236, 226, 170, 255), width=3 * k)
    salva_im = im.resize((w, h), Image.LANCZOS)
    _alfa_salva(salva_im, 'fronde.png')


def cacho(nome, seed, n_folhas, L0, L1, W0, W1, n=512, redondo=False):
    """Cacho de folhas/flores (cinza, tingido pela especie) para os cartoes das copas."""
    k = 2
    N = n * k
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    for _ in range(n_folhas):
        r = N * 0.47 * math.sqrt(rng.random())
        th = rng.random() * 6.283
        px, py = N / 2 + r * math.cos(th), N / 2 + r * math.sin(th)
        L = rng.uniform(L0, L1) * k
        W = rng.uniform(W0, W1) * k
        ang = rng.random() * 6.283
        tom = rng.uniform(0.55, 1.0) * (0.86 + 0.14 * (1 - r / (N * 0.47)))
        if redondo:
            tom = rng.uniform(0.74, 1.0)
        c = int(255 * tom)
        if redondo:
            d.ellipse((px - W, py - W, px + W, py + W), fill=(c, c, c, 255))
        else:
            ca, sa = math.cos(ang), math.sin(ang)
            pts = []
            for s in np.linspace(0, 1, 7):
                pts.append((px + (s * L) * ca - (W * math.sin(s * math.pi)) * sa, py + (s * L) * sa + (W * math.sin(s * math.pi)) * ca))
            for s in np.linspace(1, 0, 7):
                pts.append((px + (s * L) * ca + (W * math.sin(s * math.pi)) * sa, py + (s * L) * sa - (W * math.sin(s * math.pi)) * ca))
            d.polygon(pts, fill=(c, c, c, 255))
            c2 = int(c * 0.78)
            d.line((px, py, px + L * ca, py + L * sa), fill=(c2, c2, c2, 255), width=k)
    _alfa_salva(im.resize((n, n), Image.LANCZOS), nome)


def touceira():
    """Touceira vista de lado (forracao, bromelia, moreia): laminas saindo da base. Cinza, tingido."""
    w, h = 512, 256
    k = 2
    im = Image.new('RGBA', (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(44)
    for _ in range(520):
        x0 = rng.uniform(0.04, 0.96) * w * k
        H = rng.uniform(0.45, 0.98) * h * k
        inc = rng.uniform(-0.45, 0.45)
        pts_e, pts_d = [], []
        larg = rng.uniform(5, 13) * k
        for s in np.linspace(0, 1, 7):
            x = x0 + inc * H * s * s
            y = h * k - H * s
            e = larg * (1 - s) ** 0.7
            pts_e.append((x - e, y)); pts_d.append((x + e, y))
        tom = rng.uniform(0.5, 1.0)
        c = int(255 * tom)
        d.polygon(pts_e + pts_d[::-1], fill=(c, c, c, 255))
    _alfa_salva(im.resize((w, h), Image.LANCZOS), 'touceira.png')


def alambrado():
    """Tela de alambrado em losango: 512 px = 0,5 m... usada a 1 m por tile. Alfa."""
    n = 256
    k = 3
    im = Image.new('RGBA', (n * k, n * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = n * k // 4
    for i in range(-4, 9):
        d.line((i * p, 0, i * p + n * k, n * k), fill=(255, 255, 255, 255), width=2 * k)
        d.line((i * p + n * k, 0, i * p, n * k), fill=(255, 255, 255, 255), width=2 * k)
    _alfa_salva(im.resize((n, n), Image.LANCZOS), 'alambrado.png')


def gradil():
    """Gradil de barras verticais (1 tile = 1 m x 1 m altura relativa). Alfa."""
    w, h = 256, 64
    a = np.zeros((h, w, 4), np.float32)
    a[..., :3] = 1
    for x in range(0, w, 26):
        a[:, x:x + 7, 3] = 1
    salva(a, 'gradil.png')


def guarda_corpo():
    """Guarda-corpo branco das varandas (quase 4 m por 0,75 m): montantes finos a cada 10 cm."""
    w, h = 1024, 200
    a = np.zeros((h, w, 4), np.float32)
    a[..., :3] = 0.97
    a[0:13, :, 3] = 1
    a[-8:, :, 3] = 1
    a[13:17, :, :3] = 0.74
    a[13:17, :, 3] = 1
    for x in range(0, w, 25):
        a[:, x:x + 5, 3] = 1
        a[:, x + 4:x + 5, :3] = 0.78
    a[:, :9, 3] = 1
    a[:, -9:, 3] = 1
    salva(a, 'guarda_corpo2.png')


# ------------------------------------------------------------------ esquadrias das torres
def janela_veneziana():
    """Janela de dormitorio: folha de veneziana + folha de vidro com reflexo (cor e luz)."""
    n, f, c = 512, 20, 256
    a = np.ones((n, n, 3), np.float32) * 0.94
    for yy in range(f + 6, n - f - 4, 18):
        a[yy:yy + 4, f:c] = 0.56
        a[yy + 4:yy + 7, f:c] = 0.76
        a[yy + 7:yy + 18, f:c] = np.linspace(0.90, 0.97, 11)[:, None, None]
    y = (np.arange(n - 2 * f)[:, None] / (n - 2 * f)).astype(np.float32)
    x = (np.arange(n - f - c)[None, :] / (n - f - c)).astype(np.float32)
    t = 1 - y
    base = np.stack([0.11 + 0.26 * t, 0.15 + 0.32 * t, 0.20 + 0.38 * t], 2) * np.ones((n - 2 * f, n - f - c, 1))
    base += np.exp(-((x * 0.9 + y * 0.6 - 0.55) / 0.08) ** 2)[..., None] * 0.12
    a[f:n - f, c:n - f] = base
    a[:, c - 7:c + 7] = 0.97
    a[:, c + 7:c + 10] = 0.5
    a[:f], a[-f:], a[:, :f], a[:, -f:] = 0.98, 0.98, 0.98, 0.98
    a[:5], a[-5:], a[:, :5], a[:, -5:] = 0.42, 0.42, 0.42, 0.42
    salva(a, 'veneziana2.png')
    luz = np.zeros((n, n, 3), np.float32)
    q = np.array([1.0, 0.80, 0.52], np.float32)
    luz[f:n - f, c + 10:n - f] = q * (0.72 + 0.28 * y[..., None])
    salva(luz, 'veneziana2_luz.jpg', 80)


def basculante():
    """Janela de banheiro: caixilho branco e 2 basculantes de vidro mini-boreal (cor e luz)."""
    n = 256
    y = (np.arange(n)[:, None] / (n - 1)).astype(np.float32)
    t = 0.035 * ruido(n, 1.2, 47)
    a = np.stack([0.30 + 0.10 * (1 - y) + t, 0.34 + 0.10 * (1 - y) + t, 0.39 + 0.10 * (1 - y) + t], 2)
    v = np.zeros((n, n), bool); v[14:-14, 14:-14] = True
    a[:14], a[-14:], a[:, :14], a[:, -14:] = 0.97, 0.97, 0.97, 0.97
    a[n // 2 - 5:n // 2 + 5] = 0.93
    v[n // 2 - 5:n // 2 + 10] = False
    a[n // 2 + 5:n // 2 + 10, 14:-14] = 0.22
    a[:4], a[-4:], a[:, :4], a[:, -4:] = 0.42, 0.42, 0.42, 0.42
    salva(a, 'basculante2.png')
    l = np.zeros((n, n, 3), np.float32)
    l[v] = (0.96, 0.93, 0.84)
    salva(l, 'basculante2_luz.jpg', 78)


def porta_unidade():
    """Fundo da varanda (malha 'unidades'): cinza que multiplica a cor do estado. Parede, duas portas
    de correr de 2 folhas e cortina clara por tras do vidro."""
    w, h = 1024, 512
    PORTAS = ((0.12, 0.37), (0.48, 0.92))
    a = np.full((h, w), 0.60, np.float32)
    alt = 2.9 - 0.15 - 0.35
    ytop = int(round((1 - (2.10 - 0.35) / alt) * h))
    rng = np.random.default_rng(45)
    fr = 9
    a += 0.012 * ruido(h, 1, 46, w)
    yy = np.arange(h)[:, None] / h
    for u0, u1 in PORTAS:
        x0, x1 = int(u0 * w), int(u1 * w)
        a[ytop - 7:ytop, x0 - 7:x1 + 7] = 0.40
        a[ytop:, x0 - 7:x0] = 0.40
        a[ytop:, x1:x1 + 7] = 0.40
        vid = 0.92 + 0.08 * (1 - yy[ytop:])
        a[ytop:, x0:x1] = vid
        # cortina: pregas verticais suaves ocupando uma das folhas
        c = (x0 + x1) // 2
        xs = np.arange(x0, c)
        preg = 0.82 + 0.18 * np.sin(xs / 7.0 + np.sin(xs / 23.0) * 2)
        a[ytop + fr:h - fr, x0:c] = 1.0 * preg[None, :] * 1.08
        a[ytop:ytop + fr, x0:x1] = 0.32
        a[ytop:, x0:x0 + fr] = 0.32
        a[ytop:, x1 - fr:x1] = 0.32
        a[-fr:, x0:x1] = 0.32
        a[ytop:, c - 6:c + 6] = 0.32
        a[ytop:, c + 6:c + 9] = 0.46
        pm = ytop + int(0.45 * (h - ytop))
        a[pm - 18:pm + 18, c - 15:c - 10] = 0.2
        a[pm - 18:pm + 18, c + 11:c + 16] = 0.2
    salva(cinza(a), 'porta_unidade2.png')


# ------------------------------------------------------------------ atlas de quadros e paineis
ATLAS = {}


def atlas():
    W = 2048
    tela = Image.new('RGB', (W, W), (120, 120, 120))
    x, y, lin = 0, 0, 0

    def poe(nome, im):
        nonlocal x, y, lin
        if x + im.width > W:
            x, y, lin = 0, y + lin, 0
        tela.paste(im, (x, y))
        ATLAS[nome] = [x / W, 1 - (y + im.height) / W, (x + im.width) / W, 1 - y / W]
        x += im.width
        lin = max(lin, im.height)

    def novo(w, h, c):
        i = Image.new('RGB', (w, h), c)
        return i, ImageDraw.Draw(i)

    # TV show (salao/gourmet): palco, luzes
    i, d = novo(256, 144, (15, 24, 58))
    for k in range(9):
        d.polygon([(128 + (k - 4) * 8, 0), (128 + (k - 4) * 34 - 26, 110), (128 + (k - 4) * 34 + 26, 110)], fill=(70 + k * 12, 60, 150 - k * 6))
    d.rectangle((40, 92, 216, 110), fill=(230, 200, 150))
    for k in range(260):
        px, py = random.randint(0, 255), random.randint(108, 143)
        d.point((px, py), fill=(20, 18, 28))
    poe('tv_show', i)
    # TV esporte (academia): verde/amarelo com grafico
    i, d = novo(256, 144, (18, 20, 28))
    d.rectangle((0, 0, 256, 34), fill=(220, 180, 40))
    d.text((12, 8), 'TREINO DO DIA', font=fonte(18, True), fill=(20, 20, 20))
    for k, h in enumerate((40, 62, 52, 80, 70, 92)):
        d.rectangle((26 + k * 34, 136 - h, 50 + k * 34, 136), fill=(60, 190, 120))
    poe('tv_treino', i)
    # podcast (coworking)
    i, d = novo(256, 144, (18, 18, 20))
    d.ellipse((98, 40, 158, 100), outline=(235, 235, 235), width=3)
    d.rounded_rectangle((120, 50, 136, 80), 8, fill=(235, 235, 235))
    d.rectangle((96, 114, 160, 128), fill=(226, 60, 110))
    d.text((106, 114), 'ON AIR', font=fonte(13, True), fill=(255, 255, 255))
    poe('tv_podcast', i)
    # desenho infantil (brinquedoteca)
    i, d = novo(256, 144, (90, 170, 220))
    d.rectangle((0, 100, 256, 144), fill=(90, 170, 80))
    d.ellipse((30, 50, 110, 120), fill=(240, 150, 60))
    d.ellipse((150, 60, 210, 120), fill=(240, 90, 110))
    d.ellipse((200, 12, 240, 52), fill=(250, 220, 90))
    poe('tv_kids', i)
    # cinema: entardecer na savana, sem personagem
    i = Image.new('RGB', (512, 216))
    d = ImageDraw.Draw(i)
    for yy in range(216):
        t = yy / 216
        d.line((0, yy, 512, yy), fill=(int(70 + 180 * t), int(90 + 90 * t), int(150 - 70 * t)))
    d.ellipse((330, 70, 410, 150), fill=(255, 226, 150))
    d.polygon([(0, 216), (0, 170), (120, 150), (260, 174), (380, 150), (512, 176), (512, 216)], fill=(120, 72, 40))
    d.polygon([(60, 216), (150, 130), (250, 120), (330, 216)], fill=(88, 52, 34))
    i = i.filter(ImageFilter.GaussianBlur(0.8))
    poe('cinema', i)
    # quadro floral (spa/beauty)
    i, d = novo(180, 220, (235, 224, 205))
    d.rectangle((14, 14, 166, 206), fill=(226, 205, 178))
    for k in range(7):
        a = k * 0.9
        d.ellipse((90 + 36 * math.cos(a) - 28, 110 + 36 * math.sin(a) - 22, 90 + 36 * math.cos(a) + 28, 110 + 36 * math.sin(a) + 22), fill=(244, 232, 214))
    d.ellipse((76, 96, 104, 124), fill=(214, 164, 92))
    poe('quadro', i)
    # mural academia: diagonal laranja/grafite + "be powerful"
    i, d = novo(512, 200, (46, 58, 66))
    d.polygon([(360, 0), (512, 0), (512, 200), (440, 200)], fill=(205, 92, 42))
    d.text((230, 18), 'be', font=fonte(26), fill=(150, 160, 165))
    d.text((268, 18), 'powerful', font=fonte(26, True), fill=(150, 160, 165))
    poe('mural_gym', i)
    # espelho da academia: reflexo suave do salao, com a parede laranja e os aparelhos ao fundo
    i = Image.new('RGB', (512, 256))
    d = ImageDraw.Draw(i)
    for yy in range(256):
        t = yy / 255
        d.line((0, yy, 512, yy), fill=(int(198 - 40 * t), int(204 - 44 * t), int(208 - 52 * t)))
    d.polygon([(330, 0), (512, 0), (512, 190), (400, 190)], fill=(190, 112, 72))
    d.rectangle((0, 190, 512, 256), fill=(176, 146, 112))
    for x_ in (70, 150):
        d.line((x_, 40, x_, 196), fill=(40, 42, 46), width=6)
        d.line((x_ + 50, 40, x_ + 50, 196), fill=(40, 42, 46), width=6)
        d.line((x_, 44, x_ + 50, 44), fill=(40, 42, 46), width=6)
    i = i.filter(ImageFilter.GaussianBlur(1.2))
    poe('espelho_gym', i)
    i, d = novo(512, 96, (88, 92, 96))
    d.text((60, 20), 'Mini Market', font=fonte(46), fill=(232, 232, 232))
    poe('placa_mercado', i)
    i, d = novo(512, 96, (66, 80, 88))
    d.text((70, 18), 'clean ', font=fonte(50), fill=(232, 222, 202))
    d.text((208, 18), 'ON', font=fonte(50, True), fill=(240, 232, 214))
    poe('placa_lavanderia', i)
    i, d = novo(512, 96, (52, 76, 92))
    d.text((60, 26), 'SPORT IS ART', font=fonte(38), fill=(160, 180, 192))
    poe('placa_pub', i)
    # geladeira: garrafas em prateleiras
    rng = random.Random(50)
    i, d = novo(128, 256, (24, 26, 30))
    d.rectangle((6, 28, 122, 226), fill=(180, 190, 200))
    d.text((10, 8), 'BEBIDAS', font=fonte(16, True), fill=(235, 235, 235))
    cores = [(236, 150, 40), (240, 200, 60), (70, 150, 70), (200, 40, 40), (40, 60, 150), (120, 40, 90), (120, 190, 230)]
    for s in range(5):
        ys = 34 + s * 39
        c = cores[s % len(cores)]
        for k in range(6):
            xs = 10 + k * 19
            cc = tuple(min(255, int(v * rng.uniform(0.85, 1.1))) for v in c)
            d.rounded_rectangle((xs, ys + 6, xs + 15, ys + 33), 3, fill=cc)
            d.rectangle((xs + 5, ys, xs + 10, ys + 8), fill=cc)
        d.rectangle((6, ys + 34, 122, ys + 37), fill=(80, 86, 92))
    poe('geladeira', i)
    # prateleira de produtos (fileira de caixas)
    i, d = novo(256, 64, (72, 74, 78))
    xs = 4
    while xs < 250:
        w_ = rng.randint(14, 30)
        h_ = rng.randint(30, 58)
        c = rng.choice([(190, 60, 50), (60, 110, 170), (225, 195, 90), (70, 130, 90), (230, 225, 215), (40, 40, 44), (190, 110, 50)])
        d.rectangle((xs, 64 - h_, xs + w_, 64), fill=c)
        d.rectangle((xs + 2, 64 - h_ + 8, xs + w_ - 2, 64 - h_ + 16), fill=(245, 240, 230))
        xs += w_ + 2
    poe('produtos', i)
    # caixas de encomenda (delivery)
    i, d = novo(256, 64, (70, 66, 62))
    xs = 4
    while xs < 250:
        w_ = rng.randint(28, 52)
        h_ = rng.randint(26, 58)
        c = rng.choice([(184, 140, 96), (200, 156, 110), (168, 124, 84), (232, 226, 210)])
        d.rectangle((xs, 64 - h_, xs + w_, 64), fill=c)
        d.rectangle((xs + w_ // 2 - 2, 64 - h_, xs + w_ // 2 + 2, 64), fill=(150, 112, 76))
        xs += w_ + 3
    poe('caixas', i)
    # maquina de lavar (frente)
    i, d = novo(128, 128, (225, 222, 216))
    d.ellipse((24, 34, 104, 114), fill=(150, 152, 156))
    d.ellipse((32, 42, 96, 106), fill=(52, 58, 66))
    d.arc((38, 48, 90, 100), 200, 300, fill=(160, 170, 180), width=3)
    d.rectangle((10, 8, 70, 22), fill=(180, 182, 186))
    d.ellipse((96, 8, 112, 24), fill=(120, 124, 128))
    poe('lavadora', i)
    # porta de geladeira/inox
    i, d = novo(64, 128, (205, 208, 212))
    d.rectangle((0, 42, 64, 44), fill=(120, 122, 126))
    d.rectangle((6, 20, 10, 38), fill=(110, 112, 116))
    d.rectangle((6, 48, 10, 80), fill=(110, 112, 116))
    poe('geladeira_inox', i)
    # mural brinquedoteca: copas verdes no alto, parede creme
    i, d = novo(512, 128, (240, 232, 214))
    for k in range(13):
        cx = k * 44
        d.ellipse((cx - 44, -46, cx + 44, 34 + (k % 3) * 12), fill=(112, 158, 68))
    for k in range(12):
        cx, cy = rng.randint(0, 512), rng.randint(60, 120)
        d.ellipse((cx - 6, cy - 3, cx + 6, cy + 3), fill=rng.choice([(112, 158, 68), (205, 90, 60), (230, 180, 70)]))
    poe('mural_brinq', i)
    # menu do food truck / lousa
    i, d = novo(128, 192, (32, 34, 34))
    d.rectangle((3, 3, 124, 188), outline=(150, 110, 70), width=4)
    d.text((22, 12), 'MENU', font=fonte(24, True), fill=(235, 235, 225))
    for k in range(9):
        d.line((16, 50 + k * 15, 16 + rng.randint(50, 95), 50 + k * 15), fill=(205, 205, 195), width=2)
    poe('menu', i)
    # lateral do food truck: janela de atendimento
    i, d = novo(256, 96, (32, 28, 26))
    d.rectangle((6, 8, 96, 80), fill=(52, 50, 48))
    for k in range(6):
        d.line((12, 16 + k * 10, 80, 16 + k * 10), fill=(214, 206, 180), width=2)
    d.rectangle((110, 16, 250, 84), fill=(150, 112, 70))
    d.rectangle((112, 60, 248, 84), fill=(190, 180, 170))
    poe('truck_janela', i)
    # quadro negro (brinquedoteca)
    i, d = novo(128, 128, (38, 44, 42))
    for k in range(6):
        d.arc((rng.randint(4, 70), rng.randint(4, 70), rng.randint(72, 124), rng.randint(72, 124)), 0, 300, fill=(222, 222, 212), width=2)
    poe('lousa', i)
    # carro: vidro e grade
    i, d = novo(128, 64, (24, 28, 34))
    d.polygon([(0, 64), (0, 20), (128, 8), (128, 64)], fill=(58, 72, 88))
    poe('vidro_carro', i)
    tela.save(os.path.join(TEX, 'atlas_lazer.jpg'), quality=86, subsampling=0)
    json.dump(ATLAS, open(os.path.join(TEX, 'atlas_lazer.json'), 'w'), indent=0)


def placa_gaia():
    """Placa da portaria com a logo real (fonte/logo_gaia_branco.png, texto branco) e a marca Direcional,
    sobre pedra taupe, como em 01-fachada.jpg. Proporcao da placa: 1,1 x 1,8 m."""
    W, H = 660, 1080
    v = 0.5 + 0.02 * ruido(H, 2, 60, W) + 0.018 * ruido(H, 30, 61, W)
    fundo = np.stack([v * 1.03, v * 0.98, v * 0.90], 2)
    im = Image.fromarray((np.clip(fundo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, W - 15, H - 15), outline=(150, 142, 128, 255), width=3)
    logo = Image.open(os.path.join(AQUI, 'fonte', 'logo_gaia_branco.png')).convert('RGBA')
    lw = 470
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    im.alpha_composite(logo, ((W - lw) // 2, 95))
    # marca Direcional (so a palavra, sem "GRUPO"): cinza do arquivo vira branco, a seta vermelha fica
    dr = Image.open(os.path.join(AQUI, '..', '..', '..', 'img', 'logo-direcional-header.png')).convert('RGBA')
    dr = dr.crop((0, 30, dr.width, dr.height))
    a = np.asarray(dr).astype(np.float32)
    cinza = (a[..., :3].max(2) - a[..., :3].min(2)) < 45
    a[..., :3][cinza] = 245
    dr = Image.fromarray(a.astype(np.uint8))
    dw = 330
    dr = dr.resize((dw, int(dr.height * dw / dr.width)), Image.LANCZOS)
    im.alpha_composite(dr, ((W - dw) // 2, H - 150))
    im.convert('RGB').save(os.path.join(TEX, 'placa_gaia.jpg'), quality=90, subsampling=0)


def piso_marcas():
    """Marcas de piso sobre fundo transparente: PCD, moto, carga e descarga, carro eletrico."""
    W = 1024
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    marcas = {}

    def reg(nome, x0, y0, x1, y1):
        marcas[nome] = [x0 / W, 1 - y1 / W, x1 / W, 1 - y0 / W]
    # PCD: quadrado azul com pictograma (0..256)
    d.rectangle((0, 0, 255, 255), fill=(44, 104, 196, 255))
    b = (255, 255, 255, 255)
    d.ellipse((104, 30, 140, 66), fill=b)
    d.line((122, 70, 122, 140), fill=b, width=20)
    d.line((122, 94, 176, 94), fill=b, width=16)
    d.line((122, 140, 172, 140), fill=b, width=20)
    d.line((172, 140, 196, 196), fill=b, width=20)
    d.arc((62, 102, 172, 212), 40, 250, fill=b, width=16)
    reg('pcd', 0, 0, 256, 256)
    # moto (256..384)
    d.rectangle((256, 0, 383, 255), outline=(255, 255, 255, 255), width=6)
    d.ellipse((296, 28, 344, 76), outline=(255, 255, 255, 255), width=8)
    d.ellipse((296, 180, 344, 228), outline=(255, 255, 255, 255), width=8)
    d.line((320, 76, 320, 180), fill=(255, 255, 255, 255), width=10)
    reg('moto', 256, 0, 384, 256)
    # carga e descarga (texto na vertical) (384..640)
    t = Image.new('RGBA', (512, 128), (0, 0, 0, 0))
    dt = ImageDraw.Draw(t)
    dt.text((20, 4), 'CARGA E', font=fonte(54, True), fill=(255, 255, 255, 255))
    dt.text((20, 62), 'DESCARGA', font=fonte(54, True), fill=(255, 255, 255, 255))
    t = t.rotate(90, expand=True)
    im.paste(t, (384, 0), t)
    reg('carga', 384, 0, 512, 512)
    # carro eletrico: raio + tomada (512..1024 x 0..512)
    d.rectangle((512, 0, 1023, 511), fill=(44, 72, 150, 255))
    d.polygon([(760, 60), (690, 240), (760, 240), (720, 400), (850, 190), (780, 190), (830, 60)], fill=(255, 255, 255, 255))
    reg('charge', 512, 0, 1024, 512)
    # seta de entrada (0..256 x 256..512)
    d.polygon([(128, 270), (220, 380), (160, 380), (160, 500), (96, 500), (96, 380), (36, 380)], fill=(255, 255, 255, 255))
    reg('seta', 0, 256, 256, 512)
    # luz no chao (brilho radial preto no fundo: somado na cena)
    q = np.zeros((256, 256, 3), np.float32)
    yy2, xx2 = np.mgrid[0:256, 0:256]
    r2 = np.sqrt((xx2 - 127.5) ** 2 + (yy2 - 127.5) ** 2) / 127.5
    q[...] = (np.clip(1 - r2, 0, 1) ** 2)[..., None] * np.array([1.0, 0.82, 0.55], np.float32)
    salva(q, 'luz_radial.jpg', 80)
    # manchas de sombra de contato: disco e faixa com alfa (512..768 x 512..768; 768..1024)
    g = np.zeros((256, 256, 4), np.float32)
    yy, xx = np.mgrid[0:256, 0:256]
    r = np.sqrt((xx - 127.5) ** 2 + (yy - 127.5) ** 2) / 127.5
    g[..., 3] = 0.62 * np.clip(1 - r, 0, 1) ** 1.2
    im.paste(Image.fromarray((g * 255).astype(np.uint8)), (512, 512))
    reg('sombra_disco', 512, 512, 768, 768)
    s = np.zeros((256, 256, 4), np.float32)
    ex = np.minimum(np.minimum(xx, 255 - xx), np.minimum(yy, 255 - yy)) / 60.0
    s[..., 3] = 0.62 * np.clip(ex, 0, 1) ** 1.1
    im.paste(Image.fromarray((s * 255).astype(np.uint8)), (768, 512))
    reg('sombra_ret', 768, 512, 1024, 768)
    im.save(os.path.join(TEX, 'piso_marcas.png'), optimize=True)
    json.dump(marcas, open(os.path.join(TEX, 'piso_marcas.json'), 'w'), indent=0)


if __name__ == '__main__':
    random.seed(99)
    for f in (asfalto, concreto, paver, porcelanato, madeira_piso, madeira_fina, ripado, pastilha, agua_normal, reboco_fino,
              bloco, emborrachado, tecido, grama, tronco_palmeira, fronde, touceira, alambrado, gradil, guarda_corpo,
              janela_veneziana, basculante, porta_unidade, atlas, piso_marcas, placa_gaia):
        f()
    cacho('folhas2.png', 41, 900, 18, 34, 6, 11)
    cacho('flores.png', 42, 1500, 0, 0, 5, 10, redondo=True)
    cacho('folhinhas.png', 43, 2000, 9, 15, 2.5, 4.5)
    tam = sorted(((os.path.getsize(os.path.join(TEX, a)), a) for a in os.listdir(TEX)), reverse=True)
    print(sum(t for t, _ in tam) // 1024, 'KB')
    for t, a in tam[:14]:
        print(t // 1024, a)
