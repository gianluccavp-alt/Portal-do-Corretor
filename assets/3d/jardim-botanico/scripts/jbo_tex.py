#!/usr/bin/env python3
"""jbo_tex.py -- texturas proprias do Jardim Botanico (as demais vem do gerador do Casa Prado, em tex/). Fora do
Blender, num venv com numpy e pillow:  python -I jbo_tex.py
  drenante.jpg: uma vaga de piso drenante (2,40 x 5,0 m; u ao longo da fileira, v da frente para o fundo), como na
  implantacao: faixa branca de divisa nas bordas, dois trilhos de concreto (8-30% e 70-92% da largura) e grama."""
import os
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(AQUI, 'tex')
W, H = 256, 512


def ladrilho(nome, w, h):
    """Textura ladrilhavel redimensionada para o quadro inteiro (sem emenda no meio)."""
    im = Image.open(os.path.join(TEX, nome)).convert('RGB').resize((w, h), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


grama = ladrilho('grama2.jpg', W, H)
conc = ladrilho('concreto.jpg', W, H)
conc = conc / conc.mean() * np.array([178, 176, 172], np.float32)
u = (np.arange(W) + 0.5) / W
m = ((u > 0.08) & (u < 0.30)) | ((u > 0.70) & (u < 0.92))
out = np.where(m[None, :, None], conc, grama * 0.92)
borda = (u < 0.012) | (u > 0.988)
out[:, borda] = 225
v = (np.arange(H) + 0.5) / H
out[(v < 0.010) | (v > 0.990), :] = 225
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(os.path.join(TEX, 'drenante.jpg'), quality=88)
print('ok drenante.jpg')
