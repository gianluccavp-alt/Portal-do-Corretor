#!/usr/bin/env python3
"""ipi_tex.py -- texturas proprias do Conquista Clube Ipiranga (as demais vem do gerador do Gaia, em tex/).
Fora do Blender, num venv com numpy e pillow:  python ipi_tex.py
  tex/vaga_drenante.jpg  uma vaga de piso drenante (faixas de concreto e grama), u = largura da vaga, v = fundo
  tex/janela_unidade.png janela de dormitorio em cinza claro (1 folha de vidro + 2 de veneziana, FAQ); e o mapa de
                         detalhe da malha "unidades": a cena multiplica pela cor do status (verde, vermelho, cinza)
  tex/placa_conquista.jpg placa da guarita (perspectiva do acesso): fundo branco, moldura azul e o logo oficial do
                         pack do Drive (tex/logo_conquista.png, "541.8_PACK LOGO ... V1F.png"), com DIRECIONAL e
                         CLUBE IPIRANGA em azul-marinho para aparecerem no fundo branco
  tex/vidro_guarita.jpg  vidro da guarita de dia (reflexo azulado) e tex/vidro_guarita_luz.jpg o mesmo vidro com a
                         sala acesa (mapa de emissao: a cena acende a noite, como as janelas das torres)
"""
import os
import numpy as np
from PIL import Image

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')


def _ladrilho(nome, w, h):
    im = Image.open(os.path.join(TEX, nome)).convert('RGB')
    reps = (int(np.ceil(w / im.size[0])) + 1, int(np.ceil(h / im.size[1])) + 1)
    big = Image.new('RGB', (im.size[0] * reps[0], im.size[1] * reps[1]))
    for i in range(reps[0]):
        for j in range(reps[1]):
            big.paste(im, (i * im.size[0], j * im.size[1]))
    return np.asarray(big.crop((0, 0, w, h)), np.float32) / 255.0


def vaga():
    """256 px = 2,30 m de largura, 512 px = fundo da vaga. Como na implantacao: duas faixas de concreto
    (trilhos das rodas) com grama entre elas e nas bordas, e uma testeira de concreto na frente e no fundo."""
    W, H = 256, 512
    grama = _ladrilho('grama2.jpg', W * 2, H * 2)[::2, ::2]
    conc = _ladrilho('concreto.jpg', W, H)
    conc = 0.78 + 0.22 * (conc - conc.mean())             # concreto claro, pouca variacao
    conc = np.clip(conc * np.array([0.93, 0.92, 0.9]), 0, 1)
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    faixa = ((u > 0.05) & (u < 0.25)) | ((u > 0.62) & (u < 0.80)) | (u > 0.965) | (u < 0.012)
    testeira = (v < 0.045) | (v > 0.955)
    m = faixa[None, :] | testeira[:, None]
    out = np.where(m[..., None], conc, grama * 0.92)
    # junta escura entre a grama e o concreto (le como meio-fio do bloco)
    borda = np.zeros((H, W), bool)
    borda[:, 1:] |= m[:, 1:] != m[:, :-1]
    borda[1:, :] |= m[1:, :] != m[:-1, :]
    out[borda] *= 0.72
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(os.path.join(TEX, 'vaga_drenante.jpg'), quality=88)


def janela_unidade():
    """512 x 512: caixilho claro, folha de vidro a esquerda e duas folhas de veneziana a direita. Tons entre 0,6 e
    0,95 para a cor do status continuar viva depois da multiplicacao."""
    S = 512
    a = np.full((S, S), 0.93, np.float32)
    e = 18                                     # caixilho
    x = np.arange(S)[None, :].repeat(S, 0)
    y = np.arange(S)[:, None].repeat(S, 1)
    dentro = (x > e) & (x < S - e) & (y > e) & (y < S - e)
    xv = int(S * 0.36)
    vidro = dentro & (x < xv - 5)
    t = (y / S)
    a[vidro] = (0.62 + 0.16 * t + 0.08 * np.clip(1 - np.abs((x + y * 0.55) / S - 0.62) * 9, 0, 1))[vidro]
    ven = dentro & (x > xv + 5)
    passo = 22
    lam = ((y - e) % passo).astype(np.float32) / passo
    a[ven] = (0.90 - 0.22 * (lam > 0.78) - 0.08 * lam)[ven]
    a[(np.abs(x - xv) <= 5) & dentro] = 0.95                      # montante entre vidro e veneziana
    a[(np.abs(x - (xv + (S - e - xv) // 2)) <= 3) & ven] = 0.80   # encontro das duas folhas de veneziana
    rgb = np.stack([a, a, a * 1.0], -1)
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(os.path.join(TEX, 'janela_unidade.png'))




def placa():
    W, H = 1024, 448
    im = Image.new('RGB', (W, H), (247, 247, 244))
    px = np.asarray(im, np.float32)
    b = 14
    azul = np.array([86, 170, 226], np.float32)
    px[:b, :] = azul; px[-b:, :] = azul; px[:, :b] = azul; px[:, -b:] = azul
    logo = Image.open(os.path.join(TEX, 'logo_conquista.png')).convert('RGBA')
    lw = int(W * 0.78)
    logo = logo.resize((lw, int(logo.size[1] * lw / logo.size[0])), Image.LANCZOS)
    L = np.asarray(logo, np.float32)
    rgb, a = L[..., :3], L[..., 3:] / 255.0
    branco = (rgb.min(axis=2) > 200)[..., None]
    rgb = np.where(branco, np.array([28, 47, 92], np.float32), rgb)      # branco do logo -> azul-marinho
    x0, y0 = (W - lw) // 2, (H - logo.size[1]) // 2
    reg = px[y0:y0 + logo.size[1], x0:x0 + lw]
    px[y0:y0 + logo.size[1], x0:x0 + lw] = reg * (1 - a) + rgb * a
    Image.fromarray(px.clip(0, 255).astype(np.uint8)).save(os.path.join(TEX, 'placa_conquista.jpg'), quality=92)



def vidro_guarita():
    W, H = 128, 128
    yy = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    dia = np.stack([0.20 + 0.16 * yy, 0.26 + 0.17 * yy, 0.31 + 0.18 * yy], -1)
    Image.fromarray((dia.clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(TEX, 'vidro_guarita.jpg'), quality=90)
    xx = np.linspace(-1, 1, W)[None, :] * np.ones((H, 1))
    k = np.clip(1.0 - 0.35 * xx ** 2 - 0.5 * (1 - yy) ** 2, 0, 1)        # forro aceso, mais claro no alto
    luz = np.stack([1.0 * k, 0.83 * k, 0.6 * k], -1) * 0.85
    luz[int(H * 0.72):, :] *= 0.45                                          # bancada escura embaixo
    Image.fromarray((luz.clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(TEX, 'vidro_guarita_luz.jpg'), quality=90)


if __name__ == '__main__':
    vaga()
    janela_unidade()
    placa()
    vidro_guarita()
    print('ok', os.listdir(TEX))
