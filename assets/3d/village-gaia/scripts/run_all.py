# run_all.py -- pipeline completo: reconstroi a cena (gaia_modelo.py), exporta gaia.glb e salva
# gaia.blend (exportar.py). Uso: python3 -I bl.py run_all.py
# Texturas: rode gaia_tex.py e ver_planta.py fora do Blender antes, quando mudarem.
import os
_DIR = os.path.dirname(os.path.abspath(__file__))
for _nome in ('gaia_modelo.py', 'exportar.py'):
    _p = os.path.join(_DIR, _nome)
    _g = {'__file__': _p, 'result': result, '__name__': '__main__'}
    exec(compile(open(_p).read(), _p, 'exec'), _g)
