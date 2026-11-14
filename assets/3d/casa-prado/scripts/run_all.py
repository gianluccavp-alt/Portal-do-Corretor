# run_all.py -- pipeline completo: reconstroi a cena (cpr_modelo.py), exporta casa-prado.glb e salva casa-prado.blend
# (exportar.py). Dois jeitos de rodar (o Blender aberto do usuario nunca e tocado no primeiro):
#   Blender -b --factory-startup -P run_all.py        (sem interface, recomendado)
#   python3 -I bl.py run_all.py                       (add-on MCP; limpa a cena do Blender aberto)
# Para conferir as medidas: python cpr_ver.py <implantacao.png> saida.jpg (venv com pillow).
import os
try:
    result
except NameError:
    result = {}
_DIR = os.path.dirname(os.path.abspath(__file__))
for _nome in ('cpr_modelo.py', 'exportar.py'):
    _p = os.path.join(_DIR, _nome)
    _g = {'__file__': _p, 'result': result, '__name__': '__main__'}
    exec(compile(open(_p).read(), _p, 'exec'), _g)
print('RESULTADO', result)
