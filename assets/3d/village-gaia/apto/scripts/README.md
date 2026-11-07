# Apartamento decorado do Village Gaia

Passeio em primeira pessoa dentro da maquete. Cada planta tem um gerador; `apto_lib.py` é comum.

    Blender -b --factory-startup -P apto_tex.py -- <pasta das fotos do decorado>
    Blender -b --factory-startup -P apto_final05.py -- 2048 2560 128   # lightmap da arquitetura, dos móveis, amostras

Saída em `..`: `apto-final05.glb`, `apto-final05.json` (colisão, ambientes, espelhos) e os lightmaps `lm-*.webp`.
Depois de gerar, suba `versao` em `maquete.apto` (assets/config.js) para o navegador não usar o cache.
Teste direto: `maquete.html?e=village-gaia&apto=2-12-5` (torre-andar-final).
