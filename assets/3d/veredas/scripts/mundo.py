# mundo.py -- monta o bairro (colecao "mundo") ao redor do Gaia. Rodar no Blender aberto com veredas.blend.
# Dados: OpenStreetMap (c) colaboradores do OSM, ODbL. Planta: TIF FyrStudio.
import bpy, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
def _rodar(n):
    exec(compile(open(os.path.join(AQUI, n)).read(), n, 'exec'), globals())
_rodar('comum.py'); _rodar('mundo_ruas.py'); _rodar('mundo_cidade.py')
limpar()
T = os.path.join(AQUI, 'tex')
mats = {
  'asfalto': bpy.data.materials['asfalto'],
  'guia': material('mundo_guia', (0.62, 0.61, 0.58), 0.9),
  'passeio': bpy.data.materials['passeio'],
  'faixa_branca': material('mundo_faixa_branca', (0.85, 0.85, 0.82), 0.8),
  'faixa_amarela': material('mundo_faixa_amarela', (0.85, 0.62, 0.08), 0.8),
}
M = {k: Malha('mundo-' + k, v) for k, v in mats.items()}
montar_solo_planta(material('mundo_planta', img=os.path.join(T, 'planta.jpg')))
eixos = montar_ruas(M)
est = montar_cidade(M, eixos)
for m in M.values():
    m.objeto()
bpy.ops.wm.save_mainfile()
result = est
