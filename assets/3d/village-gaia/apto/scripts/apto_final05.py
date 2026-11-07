# apto_final05.py -- apartamento decorado do final 05 do Village Gaia (planta tipo meio, espelhada em relacao ao 04).
#   Blender -b --factory-startup -P apto_final05.py -- [RES_ARQ RES_MOV AMOSTRAS]
# Medidas: planta-tipo-meio.jpg, 129 px/m. Conversao para o quadro do apartamento (o 05 e o 04 espelhado):
#   x = (py - 38) / 129   do ressalto do dormitorio (x = 0) para o corredor (x = 6,17)
#   y = (1842 - px) / 129 da divisa com o final 06 (y = 0) para a divisa com o final 04 (y = 9,81)
# Mundo (Blender): X = centro_torre.x - 7 + x; Y = centro_torre.y - 9,806 + y; Z = andar * 2,9 + z.
# Estilo e mobiliario: fotos do decorado real (planta ponta), adaptados a esta planta.
import bpy, json, math, os, sys, time
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(AQUI, 'apto_lib.py')).read(), 'apto_lib.py', 'exec'))
TEX_APTO = os.path.join(AQUI, '..', 'tex')
TEX_GAIA = os.path.join(AQUI, '..', '..', 'scripts', 'tex')
SAIDA = os.path.join(AQUI, '..')
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
RES_ARQ = int(ARGS[0]) if len(ARGS) > 0 else 1024
RES_MOV = int(ARGS[1]) if len(ARGS) > 1 else 1024
AMOSTRAS = int(ARGS[2]) if len(ARGS) > 2 else 32

H = 2.55            # forro
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ------------------------------------------------------------------ materiais (cores tiradas das fotos)
mat('piso_social', '#ded8cb', 0.28, img='porcelanato.jpg', tint=True, uv=3.6, spec=0.5)
mat('piso_banho', '#cfcabd', 0.34, img='porcelanato.jpg', tint=True, uv=2.4)
mat('piso_madeira', '#ffffff', 0.42, img='piso_laminado.jpg', uv=1.2, troca=True)
mat('parede', '#efece6', 0.9, img='parede.jpg', tint=True, uv=1.0)
mat('parede_cinza', '#a9aeac', 0.9, img='parede.jpg', tint=True, uv=1.0)
mat('parede_tv', '#f2f0ea', 0.88, img='linho.jpg', tint=True, uv=0.35)
mat('teto', '#f4f2ee', 0.95, img='teto.jpg', tint=True, uv=1.0)
mat('fachada', '#94918f', 0.93)
mat('laje', '#aaa6a2', 0.92)
mat('terracota', '#b98a5f', 0.88, img='parede.jpg', tint=True, uv=1.0)
mat('vinho', '#96392c', 0.75)
mat('vinho_tampo', '#7f2f25', 0.55)
mat('ocre', '#c4982f', 0.88, img='parede.jpg', tint=True, uv=1.0)
mat('verde_mata', '#86a262', 0.88, img='parede.jpg', tint=True, uv=1.0)
mat('listrado', '#ffffff', 0.9, img='listrado.jpg', uv=1.2)
mat('branco', '#f1eee8', 0.45)
mat('branco_fosco', '#ece9e2', 0.7)
mat('rodape', '#f4f2ed', 0.5)
mat('alum_branco', '#f3f2ee', 0.4)
mat('azulejo_branco', '#ffffff', 0.32, img='azulejo_branco.jpg', uv=0.6)
mat('azulejo_salvia', '#ffffff', 0.25, img='azulejo_salvia.jpg', uv=0.6)
mat('granilite', '#ffffff', 0.55, img='granilite_bege.jpg', uv=1.2)
mat('granito', '#ffffff', 0.25, img='granito_cinza.jpg', uv=0.8)
mat('marmore', '#ffffff', 0.22, img='marmore.jpg', uv=0.9)
mat('nogueira', '#ffffff', 0.42, img='mad_nogueira.jpg', uv=1.0, troca=True)
mat('carvalho', '#ffffff', 0.5, img='mad_carvalho.jpg', uv=1.0, troca=True)
mat('carvalho_h', '#ffffff', 0.5, img='mad_carvalho.jpg', uv=1.0)
mat('azul', '#2f55b4', 0.4, metal=0.3)
mat('azul_escuro', '#1f3f7f', 0.4)
mat('preto', '#1b1b1d', 0.4, metal=0.2)
mat('preto_fosco', '#232325', 0.65)
mat('inox', '#bfc2c4', 0.28, metal=1.0)
mat('inox_escuro', '#5c5f63', 0.3, metal=0.9)
mat('latao', '#c99a45', 0.28, metal=1.0)
mat('cromo', '#d8dade', 0.1, metal=1.0)
mat('boucle', '#ece7db', 0.97, img='boucle.jpg', tint=True, uv=0.16)
mat('linho_cinza', '#a6a8a4', 0.95, img='linho.jpg', tint=True, uv=0.25)
mat('linho_claro', '#d9d4c7', 0.95, img='linho.jpg', tint=True, uv=0.25)
mat('linho_areia', '#c9c3b1', 0.95, img='linho.jpg', tint=True, uv=0.25)
mat('azul_manta', '#454c68', 0.95, img='linho.jpg', tint=True, uv=0.18)
mat('couro_terracota', '#c0754d', 0.62, img='linho.jpg', tint=True, uv=0.6)
mat('juta', '#ffffff', 0.97, img='juta.jpg')
mat('palhinha', '#ffffff', 0.7, img='palhinha.jpg', uv=0.25)
mat('sage_coluna', '#cfd3bd', 0.5)
mat('sousplat', '#5f8a86', 0.8)
mat('verde_tapete', '#8b9a78', 0.95, img='linho.jpg', tint=True, uv=0.3)
mat('cortina', '#f1eadb', 0.95, img='cortina.jpg', tint=True, duplo=True)
mat('ceramica', '#f1ece3', 0.35)
mat('ceramica_terra', '#b0663f', 0.5)
mat('tela', '#0b0c0e', 0.08)
mat('toalha', '#f2efe7', 0.98, img='boucle.jpg', tint=True, uv=0.2)
mat('vaso_preto', '#303032', 0.5)
mat('livro_v', '#b5342c', 0.6)
mat('livro_a', '#e0a93b', 0.6)
mat('livro_b', '#2f5f7f', 0.6)
mat('roupa', '#f5f3ee', 0.95)
mat('roupa_az', '#7f97ad', 0.95)
mat('couro', '#9a6a3f', 0.55)
mat('arte_1', '#ffffff', 0.7, img='arte_1.jpg')
mat('arte_2', '#ffffff', 0.7, img='arte_2.jpg')
mat('arte_3', '#ffffff', 0.7, img='arte_3.jpg')
mat('arte_4', '#ffffff', 0.7, img='arte_4.jpg')
mat('arte_5', '#ffffff', 0.7, img='arte_5.jpg')
mat('arte_6', '#ffffff', 0.7, img='arte_6.jpg')
mat('mural', '#ffffff', 0.9, img='mural.jpg')
mat('vidro', '#dfe9ec', 0.04, alfa=0.10, duplo=True)
mat('vidro_canelado', '#fff3df', 0.25, img='canelado.png', alfa=0.55, duplo=True)
mat('luz_led', '#ffe7c4', 0.5, emite=7.0)
mat('luz_spot', '#fff0da', 0.5, emite=11.0)
mat('folha_a', '#5f8f47', 0.6, img='folhas2.png', tint=True, recorte=True, duplo=True)
mat('folha_b', '#4b8141', 0.6, img='fronde.png', tint=True, recorte=True, duplo=True)
mat('ratan', '#ffffff', 0.7, img='ratan.png', recorte=True, duplo=True, uv=0.22)

LUZES = []
def spot(x, y, z=H - 0.012, w=10.0, cor=(1.0, 0.86, 0.70), cone=75, disco_luz=True):
    LUZES.append(('SPOT', (x, y, z), w, cor, cone))
    if disco_luz:
        cil(x, y, 0.045, z - 0.004, H, 'alum_branco', 'arq', seg=20, base=False)
        disco(x, y, z - 0.005, 0.034, 'luz_spot', 'luz', seg=16)
def ponto(x, y, z, w=10.0, cor=(1.0, 0.82, 0.62)):
    LUZES.append(('POINT', (x, y, z), w, cor, 0))
def area(x, y, z, sx, sy, w, cor=(1.0, 0.86, 0.70), dir_=(0, 0, -1)):
    LUZES.append(('AREA', (x, y, z), w, cor, (sx, sy, dir_)))


def parede(x0, x1, y0, y1, z0=0.0, z1=H, m='parede', colide=True, fora=''):
    """fora: faces voltadas para fora do apartamento, que nunca aparecem e nao gastam lightmap."""
    caixa(x0, x1, y0, y1, z0, z1, m, 'arq', sem=fora + ('t' if z1 >= H else '') + ('b' if z0 <= 0 else ''))
    if colide and z0 < 1.7 and z1 > 0.3:
        BLOCOS.append([round(min(x0, x1), 3), round(min(y0, y1), 3), round(max(x0, x1), 3), round(max(y0, y1), 3)])


def rev_x(x, lado, y0, y1, z0, z1, m, e=0.006, L='arq'):
    """Revestimento na face de uma parede perpendicular a x; lado = sentido que aponta para o ambiente."""
    caixa(x, x + lado * e, y0, y1, z0, z1, m, L, sem='btfk' + ('l' if lado > 0 else 'r'))


def rev_y(y, lado, x0, x1, z0, z1, m, e=0.006, L='arq'):
    caixa(x0, x1, y, y + lado * e, z0, z1, m, L, sem='btlr' + ('f' if lado > 0 else 'k'))


def rod_x(x, lado, y0, y1, h=0.07, m='rodape'):
    caixa(x, x + lado * 0.014, y0, y1, 0, h, m, 'ext')


def rod_y(y, lado, x0, x1, h=0.07, m='rodape'):
    caixa(x0, x1, y, y + lado * 0.014, 0, h, m, 'ext')


# ================================================================== ARQUITETURA
PORTA_H = 2.1
# pisos
caixa(2.2, 6.08, 0.1, 4.8, -0.02, 0, 'piso_social', 'arq', sem='bfklr')
caixa(3.3, 4.3, 4.8, 6.72, -0.02, 0, 'piso_social', 'arq', sem='bfklr')
caixa(1.016, 2.2, 0.1, 4.06, -0.02, 0, 'piso_social', 'arq', sem='bfklr')
caixa(4.3, 5.56, 4.8, 9.74, -0.02, 0, 'piso_banho', 'arq', sem='bfklr')
caixa(1.56, 4.3, 6.72, 9.74, -0.02, 0, 'piso_madeira', 'arq', sem='bfklr')
caixa(0.1, 3.3, 4.15, 6.72, -0.02, 0, 'piso_madeira', 'arq', sem='bfklr')
# forros e lajes (mesma planta); o ressalto do dormitorio e a laje tecnica nao tem forro na parte aberta
for x0, x1, y0, y1 in ((1.016, 6.171, 0.016, 4.845), (1.016, 5.659, 4.845, 6.78), (0.0, 1.016, 4.047, 6.78), (1.473, 5.659, 6.78, 9.806)):
    caixa(x0, x1, y0, y1, H, H + 0.01, 'teto', 'arq', sem='tfklr')
    caixa(x0, x1, y0, y1, H + 0.01, 2.9, 'laje', 'ext', sem='b')
    caixa(x0, x1, y0, y1, -0.15, -0.02, 'laje', 'ext', sem='t')
# laje tecnica vista pela janela da suite
caixa(0.868, 1.473, 6.78, 9.806, -0.15, 0.02, 'laje', 'ext')
caixa(0.868, 0.92, 6.78, 9.806, 0.02, 0.18, 'laje', 'ext')

# ---- perimetro
parede(1.016, 6.171, 0.016, 0.116, fora='f')                                     # divisa com o final 06
parede(6.062, 6.171, 0.116, 0.93, fora='r')                                       # corredor: lado da geladeira
parede(6.062, 6.171, 0.93, 1.80, z0=PORTA_H, colide=False, fora='r')              # verga da porta de entrada
parede(6.062, 6.171, 1.80, 4.845, fora='r')                                       # corredor: parede terracota
parede(4.279, 6.171, 4.76, 4.845, fora='k')                                       # fundo do jantar
parede(5.55, 5.659, 4.845, 9.806, fora='r')                                       # fundo dos banheiros
parede(1.473, 5.659, 9.729, 9.806, fora='k')                                      # divisa com o final 04
parede(0.0, 0.11, 4.047, 4.86, fora='l')                                          # fachada do ressalto
parede(0.0, 0.11, 6.05, 6.78, fora='l')
parede(0.0, 0.11, 4.86, 6.05, z1=0.85, fora='l')
parede(0.0, 0.11, 4.86, 6.05, z0=2.2, colide=False, fora='l')
caixa(0.0, 1.132, 4.047, 4.163, 0, H, 'fachada', 'ext')
BLOCOS.append([0.0, 4.047, 1.132, 4.163])                           # lateral do ressalto, vista da sacada
parede(1.132, 2.116, 4.047, 4.163)                                      # fundo da sacada
parede(0.0, 1.581, 6.651, 6.78, fora='k')                                         # lateral do ressalto, lado da laje tecnica
parede(1.473, 1.581, 6.78, 7.45, fora='l')                                        # fachada da suite
parede(1.473, 1.581, 8.63, 9.729, fora='l')
parede(1.473, 1.581, 7.45, 8.63, z1=0.9, fora='l')
parede(1.473, 1.581, 7.45, 8.63, z0=2.2, colide=False, fora='l')
# ---- divisorias
parede(2.116, 3.364, 4.047, 4.163)                                      # parede da TV
parede(3.271, 3.364, 4.163, 5.775)                                      # dorm 2 x circulacao (parede dos quadros)
parede(3.271, 3.364, 5.775, 6.651, z0=PORTA_H, colide=False)            # verga da porta do dorm 2
parede(1.581, 3.35, 6.651, 6.729)                                       # dorm 2 x suite
parede(3.271, 3.35, 6.651, 6.729)
parede(3.35, 4.279, 6.651, 6.729, z0=PORTA_H, colide=False)             # verga da porta da suite
parede(4.20, 4.279, 6.651, 6.729)
parede(4.279, 4.349, 8.29, 9.729)                                       # suite x banho 1
parede(4.279, 4.349, 7.46, 8.29, z0=PORTA_H, colide=False)              # verga banho 1
parede(4.279, 4.349, 5.81, 7.46)
parede(4.279, 4.349, 4.98, 5.81, z0=PORTA_H, colide=False)              # verga banho 2
parede(4.279, 4.349, 4.76, 4.98)
parede(4.349, 5.55, 7.256, 7.333)                                       # banho 1 x banho 2
# ---- fundo da sacada (vaos da porta de vidro e da porta da cozinha)
parede(2.116, 2.24, 0.116, 0.829)
parede(2.116, 2.24, 0.829, 1.55, z0=PORTA_H, colide=False)
parede(2.116, 2.24, 1.55, 1.992)
parede(2.116, 2.24, 1.992, 3.76, z0=2.2, colide=False)
parede(2.116, 2.24, 3.76, 4.047)
# ---- meia parede sala x cozinha (no decorado real ela tem 1,10 m e leva a estante azul)
parede(2.24, 3.54, 1.605, 1.705, z1=1.10)


def batente_x(x0, x1, y0, y1, h=PORTA_H, m='branco'):
    """Guarnicao de vao em parede perpendicular a x."""
    caixa(x0 - 0.012, x1 + 0.012, y0, y0 + 0.03, 0, h, m, 'ext')
    caixa(x0 - 0.012, x1 + 0.012, y1 - 0.03, y1, 0, h, m, 'ext')
    caixa(x0 - 0.012, x1 + 0.012, y0, y1, h - 0.03, h, m, 'ext')


def batente_y(y0, y1, x0, x1, h=PORTA_H, m='branco'):
    caixa(x0, x0 + 0.03, y0 - 0.012, y1 + 0.012, 0, h, m, 'ext')
    caixa(x1 - 0.03, x1, y0 - 0.012, y1 + 0.012, 0, h, m, 'ext')
    caixa(x0, x1, y0 - 0.012, y1 + 0.012, h - 0.03, h, m, 'ext')


def folha_porta(x, y, ang, w=0.8, m='branco', puxador='cromo', e=0.035):
    """Folha aberta, dobradica em (x, y); ang em graus (0 = +x)."""
    with em(x, y, 0, ang):
        caixa(0.01, w, -e / 2, e / 2, 0.005, PORTA_H - 0.04, m, 'mov', bev=0.002)
        cil(w - 0.07, e / 2 + 0.03, 0.025, 1.0, 1.0 + 0.008, puxador, seg=12)
        for s in (1, -1):
            tubo([(w - 0.07, s * (e / 2), 1.02), (w - 0.07, s * (e / 2 + 0.04), 1.02), (w - 0.19, s * (e / 2 + 0.04), 1.02)], 0.009, puxador, seg=8)
        bloco(0, w, -e / 2 - 0.01, e / 2 + 0.01)


# portas abertas: entrada, dorm 2, suite, banhos
batente_x(6.062, 6.171, 0.93, 1.80)
caixa(6.169, 6.18, 0.93, 1.80, 0, PORTA_H, 'branco', 'arq')                        # folha de entrada fechada, por fora
BLOCOS.append([6.06, 0.93, 6.2, 1.80])
with em(6.06, 0.965, 0, 0):                                                         # folha de entrada fechada, vista de dentro
    caixa(-0.02, 0.0, 0.0, 0.80, 0.005, PORTA_H - 0.035, 'branco', 'mov', bev=0.002)
    tubo([(-0.02, 0.72, 1.03), (-0.06, 0.72, 1.03), (-0.06, 0.58, 1.03)], 0.009, 'cromo', seg=8)
    caixa(-0.024, -0.02, 0.66, 0.75, 0.98, 1.16, 'preto', 'mov')
batente_x(3.271, 3.364, 5.775, 6.651)
folha_porta(3.27, 6.60, 180, w=0.8)
batente_y(6.651, 6.729, 3.35, 4.20)
folha_porta(4.17, 6.74, 90, w=0.78)
batente_x(4.279, 4.349, 7.46, 8.29)
folha_porta(4.36, 7.41, 0, w=0.76)
batente_x(4.279, 4.349, 4.98, 5.81)
folha_porta(4.36, 4.93, 0, w=0.76)


def janela_x(x0, x1, y0, y1, z0, z1):
    """Janela de correr em parede perpendicular a x, meia folha aberta."""
    xm = (x0 + x1) / 2
    m = 'alum_branco'
    caixa(x0, x1, y0, y0 + 0.04, z0, z1, m, 'ext')
    caixa(x0, x1, y1 - 0.04, y1, z0, z1, m, 'ext')
    caixa(x0, x1, y0, y1, z0, z0 + 0.04, m, 'ext')
    caixa(x0, x1, y0, y1, z1 - 0.04, z1, m, 'ext')
    ym = (y0 + y1) / 2
    caixa(xm - 0.02, xm, ym - 0.02, ym + 0.02, z0, z1, m, 'ext')
    malha([(xm, y0 + 0.04, z0 + 0.04), (xm, ym, z0 + 0.04), (xm, ym, z1 - 0.04), (xm, y0 + 0.04, z1 - 0.04)], [(0, 1, 2, 3)], 'vidro', 'vidro')
    caixa(x0 + 0.002, x1 + 0.016, y0 - 0.03, y1 + 0.03, z0 - 0.03, z0, 'branco', 'ext')


janela_x(0.0, 0.11, 4.86, 6.05, 0.85, 2.2)         # dormitorio 2
janela_x(1.473, 1.581, 7.45, 8.63, 0.9, 2.2)       # suite

# porta de correr da sala para a sacada: folha fixa + folha correndo sobre ela (vao livre de 0,88 m)
XP = 2.18
for y0, y1 in ((1.992, 2.03), (2.86, 2.90), (3.72, 3.76)):
    caixa(XP - 0.03, XP + 0.03, y0, y1, 0, 2.2, 'alum_branco', 'ext')
caixa(XP - 0.03, XP + 0.03, 1.992, 3.76, 2.16, 2.2, 'alum_branco', 'ext')
caixa(XP - 0.03, XP + 0.03, 1.992, 2.90, 0, 0.04, 'alum_branco', 'ext')
caixa(XP - 0.03, XP + 0.03, 2.90, 3.76, 0, 0.012, 'alum_branco', 'ext')
malha([(XP, 2.03, 0.04), (XP, 2.86, 0.04), (XP, 2.86, 2.16), (XP, 2.03, 2.16)], [(0, 1, 2, 3)], 'vidro', 'vidro')
malha([(XP + 0.02, 2.03, 0.04), (XP + 0.02, 2.86, 0.04), (XP + 0.02, 2.86, 2.16), (XP + 0.02, 2.03, 2.16)], [(0, 1, 2, 3)], 'vidro', 'vidro')
BLOCOS.append([2.12, 1.992, 2.24, 2.90])

# porta da cozinha para a sacada: folha de vidro aberta sobre a sacada, como na planta
batente_x(2.116, 2.24, 0.829, 1.55)
with em(2.09, 1.55, 0, 90):
    caixa(0.0, 0.72, -0.02, 0.02, 0, 0.05, 'alum_branco', 'ext')
    caixa(0.0, 0.72, -0.02, 0.02, 2.05, 2.10, 'alum_branco', 'ext')
    caixa(0.0, 0.04, -0.02, 0.02, 0, 2.1, 'alum_branco', 'ext')
    caixa(0.68, 0.72, -0.02, 0.02, 0, 2.1, 'alum_branco', 'ext')
    malha([(0.04, 0, 0.05), (0.68, 0, 0.05), (0.68, 0, 2.05), (0.04, 0, 2.05)], [(0, 1, 2, 3)], 'vidro', 'vidro')
    bloco(0, 0.72, -0.03, 0.03)

# ---- guarda-corpo e pano de vidro da sacada
caixa(1.016, 1.132, 0.116, 4.047, 0, 0.62, 'branco_fosco', 'arq')
BLOCOS.append([1.0, 0.116, 1.132, 4.047])
caixa(1.0, 1.15, 0.116, 4.047, 0.62, 0.65, 'branco', 'arq')
BLOCOS.append([0.0, 0.0, 1.016, 4.05])
for y in np.linspace(0.2, 3.97, 6):
    cil(1.075, float(y), 0.022, 0.65, 1.12, 'alum_branco', 'ext', seg=12)
    cil(1.075, float(y), 0.04, 0.65, 0.665, 'alum_branco', 'ext', seg=16)
tubo([(1.075, 0.116, 1.13), (1.075, 4.047, 1.13)], 0.03, 'alum_branco', 'ext', seg=12, ry=0.022)
tubo([(1.075, 0.116, 0.86), (1.075, 4.047, 0.86)], 0.016, 'alum_branco', 'ext', seg=10)
malha([(1.045, 0.116, 0.65), (1.045, 4.047, 0.65), (1.045, 4.047, H), (1.045, 0.116, H)], [(0, 1, 2, 3)], 'vidro', 'vidro')
for y in (1.1, 2.1, 3.1):
    malha([(1.044, y - 0.003, 0.65), (1.044, y + 0.003, 0.65), (1.044, y + 0.003, H), (1.044, y - 0.003, H)], [(0, 1, 2, 3)], 'alum_branco', 'ext')
caixa(1.016, 1.09, 0.116, 4.047, H - 0.05, H, 'alum_branco', 'ext')

# ---- acabamentos de parede por ambiente
# sala e jantar
rev_y(4.047, -1, 2.24, 3.271, 0.0, H, 'parede_tv')
rod_y(4.041, -1, 2.24, 3.27)
rev_x(3.364, 1, 4.163, 5.775, 0, H, 'parede')
rod_x(3.364, 1, 4.163, 5.775)
rev_x(6.062, -1, 1.80, 4.76, 0, H, 'terracota')
rod_x(6.056, -1, 1.80, 4.76)
rev_y(4.76, -1, 4.279, 6.056, 0, H, 'parede_tv')
rod_y(4.754, -1, 4.28, 6.056)
rev_x(2.24, 1, 3.76, 4.047, 0, H, 'parede')
rev_x(4.279, -1, 4.76, 4.98, 0, H, 'parede')
rod_x(4.279, -1, 5.81, 6.651)
rod_y(6.651, -1, 3.364, 3.35)
# cozinha
rev_y(0.116, 1, 2.24, 5.36, 0.92, H, 'azulejo_branco')
rev_y(0.116, 1, 5.36, 6.062, 0, H, 'vinho')
rev_x(6.062, -1, 0.116, 0.93, 0, H, 'vinho')
rev_y(1.605, -1, 2.24, 3.54, 0, 1.10, 'parede')
rev_x(2.24, 1, 0.116, 0.829, 0, H, 'azulejo_branco')
rod_x(2.24, 1, 1.55, 1.992)
# suite
rev_y(9.729, -1, 1.581, 4.279, 0, 1.28, 'listrado')
rev_y(9.729, -1, 1.581, 4.279, 1.28, H, 'ocre')
rev_x(4.279, -1, 8.29, 9.729, 0, H, 'parede_cinza')
rod_y(9.72, -1, 1.581, 4.279)
rod_x(4.27, -1, 8.29, 9.72)
rod_y(6.729, 1, 3.32, 3.35)
# dormitorio 2: faixa verde em cima, mural embaixo e moldura branca
for args in ((6.651, -1, 0.11, 3.271), (4.163, 1, 0.11, 3.271)):
    rev_y(args[0], args[1], args[2], args[3], 1.36, H, 'verde_mata')
    caixa(args[2], args[3], args[0], args[0] + args[1] * 0.018, 1.33, 1.36, 'rodape', 'ext')
    rod_y(args[0], args[1], args[2], args[3])
rev_x(0.11, 1, 4.163, 6.651, 1.36, H, 'verde_mata')
caixa(0.11, 0.128, 4.163, 4.86, 1.33, 1.36, 'rodape', 'ext')
caixa(0.11, 0.128, 6.05, 6.651, 1.33, 1.36, 'rodape', 'ext')
rev_x(3.271, -1, 5.775, 6.651, 1.36, H, 'verde_mata')
# mural (recorte da foto do decorado): parede do berco e parede da comoda
Z0M, Z1M = 0.07, 1.33
imagem((0.11, 6.644, Z0M), (3.271, 6.644, Z0M), (3.271, 6.644, Z1M), (0.11, 6.644, Z1M), 'mural', 'arq')
imagem((3.271, 4.170, Z0M), (0.11, 4.170, Z0M), (0.11, 4.170, Z1M), (3.271, 4.170, Z1M), 'mural', 'arq', uv=((1, 0), (0, 0), (0, 1), (1, 1)))
imagem((0.117, 6.05, Z0M), (0.117, 6.644, Z0M), (0.117, 6.644, Z1M), (0.117, 6.05, Z1M), 'mural', 'arq', uv=((0, 0), (0.22, 0), (0.22, 1), (0, 1)))
imagem((0.117, 4.163, Z0M), (0.117, 4.86, Z0M), (0.117, 4.86, Z1M), (0.117, 4.163, Z1M), 'mural', 'arq', uv=((0.7, 0), (0.95, 0), (0.95, 1), (0.7, 1)))
rev_x(0.11, 1, 4.86, 6.05, 0.0, 0.85, 'branco_fosco')
caixa(0.11, 0.128, 4.163, 6.651, 0, 0.07, 'rodape', 'ext')

# ================================================================== SALA
def sofa_curvo():
    """Sofa boucle de 2 lugares, encosto envolvendo os bracos (referencia: DSC_0652). Origem no centro; frente = +y."""
    macio(0, 0.02, 0.17, 0.78, 0.43, 0.17, 'boucle', e1=0.5, e2=0.42, seg=44, aneis=14)
    macio(0, 0.05, 0.42, 0.64, 0.34, 0.11, 'boucle', e1=0.55, e2=0.45, seg=36, aneis=12, ruido=0.03, seed=3)
    arco = []
    for i in range(23):
        t = i / 22
        a = math.radians(205 + 130 * t)
        arco.append((0.68 * math.cos(a), -0.02 + 0.38 * math.sin(a), 0.54))
    tubo(arco, 0.14, 'boucle', seg=16, ry=0.27, tampa=False)
    # pontas arredondadas dos bracos
    for s, p in ((-1, arco[0]), (1, arco[-1])):
        macio(p[0], p[1], 0.54, 0.14, 0.15, 0.27, 'boucle', e1=0.8, e2=0.8, seg=16, aneis=10)


with em(3.06, 2.26, 0, 0):
    sofa_curvo()
    macio(-0.42, -0.17, 0.68, 0.24, 0.07, 0.2, 'linho_claro', e1=0.45, e2=0.45, ruido=0.04, seed=4, inc=-16)
    macio(0.10, -0.15, 0.65, 0.22, 0.07, 0.18, 'linho_cinza', e1=0.45, e2=0.45, ruido=0.05, seed=5, inc=-18)
    bloco(-0.78, 0.78, -0.41, 0.42)
# tapete de juta redondo
disco(3.20, 3.02, 0.008, 1.02, 'juta', 'mov', seg=72, uv_disco=True)
# mesa lateral com tampo organico e haste fina
with em(4.02, 2.06, 0, 0):
    disco(0, 0, 0.012, 0.18, 'azul_escuro', seg=28)
    cil(0, 0, 0.012, 0.012, 0.58, 'azul_escuro', seg=10)
    extruda([(0.23 * math.cos(a) * (1 + 0.14 * math.cos(2 * a)), 0.19 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)], 0.58, 0.60, 'carvalho_h', sem_base=False)
    bloco(-0.1, 0.1, -0.1, 0.1)
# rack branco flutuante com ponta redonda
with em(0, 0, 0, 0):
    poli = [(2.30, 3.70), (3.14, 3.70)] + [(3.14 + 0.17 * math.sin(a), 3.87 - 0.17 * math.cos(a)) for a in np.linspace(0.2, math.pi - 0.2, 12)] + [(3.14, 4.04), (2.30, 4.04)]
    extruda(poli, 0.14, 0.60, 'branco', lados_suaves=True, sem_base=False)
    for x in (2.56, 2.82, 3.08):
        caixa(x, x + 0.004, 3.697, 3.701, 0.15, 0.59, 'preto_fosco')
    BLOCOS.append([2.3, 3.68, 3.31, 4.05])
    caixa(2.32, 2.62, 3.79, 3.99, 0.60, 0.635, 'couro')        # bandeja de couro
    cil(2.76, 3.86, 0.07, 0.60, 0.65, 'ceramica', seg=20)
    # porta-retrato
    imagem((2.95, 3.88, 0.61), (3.15, 3.82, 0.61), (3.15, 3.84, 0.86), (2.95, 3.90, 0.86), 'arte_3')
    # TV e prateleira com plantas
    caixa(2.29, 3.23, 4.015, 4.038, 1.0, 1.56, 'preto')
    imagem((2.305, 4.0145, 1.015), (3.215, 4.0145, 1.015), (3.215, 4.0145, 1.545), (2.305, 4.0145, 1.545), 'tela')
    caixa(2.30, 3.25, 3.84, 4.04, 1.86, 1.895, 'branco', bev=0.003)
    # ar-condicionado split
    macio(2.82, 3.92, 2.31, 0.42, 0.11, 0.135, 'branco', e1=0.28, e2=0.2, seg=20, aneis=8)
    caixa(2.42, 3.22, 3.81, 3.812, 2.215, 2.235, 'preto_fosco')
# trilho de spots da sala
caixa(2.65, 3.65, 3.02, 3.05, H - 0.03, H, 'preto', 'mov')
for x in (2.82, 3.15, 3.48):
    tubo([(x, 3.035, H - 0.03), (x, 3.035, H - 0.06)], 0.012, 'preto')
    cil(x, 3.035, 0.035, H - 0.17, H - 0.06, 'preto', seg=14, base=False)
    disco(x, 3.035, H - 0.172, 0.028, 'luz_spot', 'luz', seg=14)
    LUZES.append(('SPOT', (x, 3.035, H - 0.17), 7.0, (1.0, 0.86, 0.70), 60))


# quadros na parede em frente ao jantar (fotos reais do decorado)
def quadro_x(x, lado, yc, zc, w, h, arte):
    """Quadro em parede perpendicular a x, olhando para +x (lado=1) ou -x (lado=-1)."""
    y0, y1, z0, z1 = yc - w / 2, yc + w / 2, zc - h / 2, zc + h / 2
    caixa(x, x + lado * 0.022, y0, y1, z0, z1, 'carvalho')
    xx = x + lado * 0.0225
    if lado > 0:
        imagem((xx, y0 + 0.012, z0 + 0.012), (xx, y1 - 0.012, z0 + 0.012), (xx, y1 - 0.012, z1 - 0.012), (xx, y0 + 0.012, z1 - 0.012), arte)
    else:
        imagem((xx, y1 - 0.012, z0 + 0.012), (xx, y0 + 0.012, z0 + 0.012), (xx, y0 + 0.012, z1 - 0.012), (xx, y1 - 0.012, z1 - 0.012), arte)


def quadro_y(y, lado, xc, zc, w, h, arte):
    x0, x1, z0, z1 = xc - w / 2, xc + w / 2, zc - h / 2, zc + h / 2
    caixa(x0, x1, y, y + lado * 0.022, z0, z1, 'carvalho')
    yy = y + lado * 0.0225
    if lado < 0:
        imagem((x0 + 0.012, yy, z0 + 0.012), (x1 - 0.012, yy, z0 + 0.012), (x1 - 0.012, yy, z1 - 0.012), (x0 + 0.012, yy, z1 - 0.012), arte)
    else:
        imagem((x1 - 0.012, yy, z0 + 0.012), (x0 + 0.012, yy, z0 + 0.012), (x0 + 0.012, yy, z1 - 0.012), (x1 - 0.012, yy, z1 - 0.012), arte)


XA = 3.37
quadro_x(XA, 1, 4.52, 1.78, 0.46, 0.38, 'arte_1')
quadro_x(XA, 1, 5.02, 1.92, 0.40, 0.42, 'arte_4')
quadro_x(XA, 1, 5.02, 1.42, 0.40, 0.40, 'arte_6')
quadro_x(XA, 1, 4.52, 1.34, 0.40, 0.36, 'arte_5')
quadro_x(XA, 1, 5.48, 1.60, 0.34, 0.38, 'arte_2')

# ================================================================== JANTAR
TX, TY = 5.28, 3.72
with em(TX, TY, 0, 0):
    for a in (90, 210, 330):
        cil(0.11 * math.cos(math.radians(a)), 0.11 * math.sin(math.radians(a)), 0.085, 0, 0.72, 'sage_coluna', seg=28)
    extruda([(0.58 * math.cos(a), 0.52 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 56, endpoint=False)], 0.72, 0.752, 'carvalho_h', sem_base=False)
    bloco(-0.22, 0.22, -0.22, 0.22)
    for a in (35, 150, 265):
        px, py = 0.34 * math.cos(math.radians(a)), 0.30 * math.sin(math.radians(a))
        disco(px, py, 0.7535, 0.17, 'sousplat', seg=28)
        cil(px, py, 0.13, 0.755, 0.77, 'ceramica', seg=28, r2=0.15)
        cil(px, py, 0.07, 0.77, 0.80, 'ceramica_terra', seg=20, r2=0.09)
    cil(-0.04, 0.02, 0.055, 0.752, 0.94, 'sage_coluna', seg=16, r2=0.05)


def cadeira_redonda(h_assento=0.46, perna='sage_coluna', alto=False):
    """Cadeira de encosto redondo (referencia DSC_0656/0663). Frente = +y."""
    z = h_assento
    macio(0, 0.02, z + 0.03, 0.225, 0.215, 0.06, 'boucle', e1=0.45, e2=1.0, seg=32, aneis=10)
    macio(0, -0.215, z + 0.42, 0.205, 0.035, 0.225, 'boucle', e1=1.0, e2=0.55, seg=32, aneis=18)
    # K metalico no encosto
    for a, b in (((-0.07, -0.26, z + 0.20), (-0.07, -0.26, z + 0.56)),
                 ((-0.07, -0.26, z + 0.40), (0.10, -0.26, z + 0.58)),
                 ((-0.07, -0.26, z + 0.34), (0.11, -0.26, z + 0.20))):
        tubo([a, b], 0.006, perna, seg=6)
    for sx in (-1, 1):
        tubo([(sx * 0.17, 0.16, 0), (sx * 0.17, 0.16, z - 0.02)], 0.010, perna, seg=8)
        tubo([(sx * 0.17, -0.20, 0), (sx * 0.17, -0.22, z + 0.22)], 0.010, perna, seg=8)
    tubo([(-0.17, 0.16, z - 0.02), (0.17, 0.16, z - 0.02)], 0.008, perna, seg=6)
    tubo([(-0.17, -0.20, z - 0.02), (0.17, -0.20, z - 0.02)], 0.008, perna, seg=6)
    if alto:
        tubo([(-0.17, 0.16, 0.30), (0.17, 0.16, 0.30)], 0.008, perna, seg=6)
    bloco(-0.2, 0.2, -0.24, 0.2)


with em(4.54, 3.50, 0, -70):
    cadeira_redonda()
with em(5.26, 2.86, 0, -8):
    cadeira_redonda()
# banco de canto em couro terracota
with em(0, 0, 0, 0):
    caixa(4.42, 6.03, 4.24, 4.75, 0.0, 0.10, 'carvalho')
    for x in np.arange(4.44, 6.0, 0.048):
        caixa(float(x), float(x) + 0.03, 4.25, 4.27, 0.10, 0.42, 'carvalho')
    caixa(4.42, 6.03, 4.27, 4.75, 0.10, 0.42, 'carvalho_h', sem='t')
    caixa(4.42, 6.03, 4.24, 4.75, 0.42, 0.45, 'carvalho')
    macio(5.225, 4.495, 0.50, 0.80, 0.255, 0.055, 'couro_terracota', e1=0.4, e2=0.2, seg=36, aneis=10)
    macio(5.225, 4.70, 0.74, 0.80, 0.05, 0.22, 'couro_terracota', e1=0.4, e2=0.2, seg=36, aneis=10)
    BLOCOS.append([4.42, 4.24, 6.06, 4.76])
# dois espelhos organicos na parede terracota (a superficie espelhada entra pela pagina)
ESPELHOS = []
def espelho_x(yc, zc, ry, rz, deform, x=6.052):
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        k = 1 + deform * math.cos(a - 1.2) + 0.09 * math.sin(2 * a + 1)
        pts.append((x, yc + ry * k * math.cos(a), zc + rz * k * math.sin(a)))
    tubo(pts, 0.008, 'preto', seg=6, fechado=True)
    ESPELHOS.append({'pts': [[round(p[0], 3), round(p[1], 3), round(p[2], 3)] for p in pts], 'n': [-1, 0, 0]})
espelho_x(3.22, 1.42, 0.25, 0.38, 0.20)
espelho_x(3.98, 1.50, 0.29, 0.42, 0.16)
# pendente de disco caramelo
tubo([(TX, TY, H), (TX, TY, 1.88)], 0.003, 'preto', seg=6)
cil(TX, TY, 0.34, 1.76, 1.82, 'couro', seg=48, r2=0.05, base=True)
disco(TX, TY, 1.755, 0.08, 'luz_spot', 'luz', seg=20)
ponto(TX, TY, 1.70, 10.0)

# ================================================================== COZINHA
def frente_shaker(x0, x1, y, z0, z1, m='nogueira', puxador=True):
    """Porta de almofada; frente em y (voltada para +y)."""
    caixa(x0 + 0.002, x1 - 0.002, y - 0.012, y, z0 + 0.002, z1 - 0.002, m, bev=0.002)
    e = 0.055
    caixa(x0 + 0.002, x1 - 0.002, y, y + 0.006, z1 - e, z1 - 0.002, m)
    caixa(x0 + 0.002, x1 - 0.002, y, y + 0.006, z0 + 0.002, z0 + e, m)
    caixa(x0 + 0.002, x0 + e, y, y + 0.006, z0 + e, z1 - e, m)
    caixa(x1 - e, x1 - 0.002, y, y + 0.006, z0 + e, z1 - e, m)
    if puxador:
        xc = (x0 + x1) / 2
        caixa(xc - 0.05, xc + 0.05, y + 0.006, y + 0.018, z1 - 0.02, z1 - 0.008, 'preto')


YF = 0.775
caixa(3.50, 5.36, 0.116, YF - 0.012, 0.10, 0.88, 'nogueira', sem='t')
caixa(3.50, 5.36, 0.116, YF - 0.05, 0.0, 0.10, 'preto_fosco')
frente_shaker(4.16, 4.76, YF, 0.10, 0.50, puxador=True)
frente_shaker(4.16, 4.76, YF, 0.50, 0.88)
frente_shaker(4.76, 5.36, YF, 0.10, 0.88)
frente_shaker(3.50, 3.545, YF, 0.10, 0.88, puxador=False)
BLOCOS.append([2.24, 0.116, 5.38, 0.82])
# bancada de granito com vao da cuba
BZ = (0.88, 0.92)
for x0, x1, y0, y1 in ((2.85, 4.56, 0.116, 0.81), (5.06, 5.36, 0.116, 0.81), (4.56, 5.06, 0.116, 0.26), (4.56, 5.06, 0.66, 0.81)):
    caixa(x0, x1, y0, y1, BZ[0], BZ[1], 'granito', bev=0.003)
# cuba de inox embutida
caixa(4.56, 5.06, 0.26, 0.66, 0.73, 0.735, 'inox')
malha([(4.56, 0.26, 0.92), (5.06, 0.26, 0.92), (5.06, 0.26, 0.735), (4.56, 0.26, 0.735)], [(3, 2, 1, 0)], 'inox')
malha([(4.56, 0.66, 0.92), (5.06, 0.66, 0.92), (5.06, 0.66, 0.735), (4.56, 0.66, 0.735)], [(0, 1, 2, 3)], 'inox')
malha([(4.56, 0.26, 0.92), (4.56, 0.66, 0.92), (4.56, 0.66, 0.735), (4.56, 0.26, 0.735)], [(0, 1, 2, 3)], 'inox')
malha([(5.06, 0.26, 0.92), (5.06, 0.66, 0.92), (5.06, 0.66, 0.735), (5.06, 0.26, 0.735)], [(3, 2, 1, 0)], 'inox')
# torneira gourmet de latao
arco = [(4.81 + 0.0, 0.20, 0.92), (4.81, 0.20, 1.18)]
for i in range(1, 13):
    a = math.pi * i / 12
    arco.append((4.81, 0.20 + 0.09 - 0.09 * math.cos(a), 1.18 + 0.09 * math.sin(a)))
arco.append((4.81, 0.38, 1.12))
tubo(arco, 0.011, 'latao', seg=10)
cil(4.81, 0.20, 0.022, 0.92, 0.98, 'latao', seg=14)
tubo([(4.81, 0.20, 0.98), (4.87, 0.20, 1.01)], 0.006, 'latao', seg=8)
# cooktop preto de 4 bocas com grelhas
caixa(3.56, 4.14, 0.18, 0.75, 0.92, 0.928, 'preto')
for px_ in (3.71, 3.99):
    for py_ in (0.32, 0.61):
        cil(px_, py_, 0.042, 0.928, 0.945, 'preto_fosco', seg=16)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            tubo([(px_ + 0.03 * math.cos(a), py_ + 0.03 * math.sin(a), 0.955), (px_ + 0.115 * math.cos(a), py_ + 0.115 * math.sin(a), 0.955)], 0.005, 'preto_fosco', seg=5)
# forno de embutir
caixa(3.545, 4.16, YF - 0.01, YF, 0.12, 0.86, 'inox_escuro')
caixa(3.59, 4.11, YF, YF + 0.004, 0.17, 0.66, 'tela')
caixa(3.56, 4.145, YF, YF + 0.004, 0.72, 0.84, 'preto')
tubo([(3.60, YF + 0.04, 0.70), (4.10, YF + 0.04, 0.70)], 0.009, 'inox', seg=8)
for k in (3.60, 4.10):
    tubo([(k, YF, 0.70), (k, YF + 0.04, 0.70)], 0.006, 'inox', seg=6)
macio(3.84, YF + 0.05, 0.54, 0.09, 0.012, 0.16, 'toalha', e1=0.5, e2=0.5, seg=12, aneis=8)
# lava e seca sob a bancada
caixa(2.85, 3.47, 0.15, YF - 0.02, 0.0, 0.86, 'inox_escuro', bev=0.006)
pts = [(3.16 + 0.22 * math.cos(a), YF - 0.018, 0.42 + 0.22 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
tubo(pts, 0.02, 'preto', seg=8, fechado=True)
imagem((3.36, YF - 0.016, 0.22), (2.96, YF - 0.016, 0.22), (2.96, YF - 0.016, 0.62), (3.36, YF - 0.016, 0.62), 'tela')
caixa(2.9, 3.42, YF - 0.02, YF - 0.016, 0.72, 0.84, 'preto')
# tanque e prumada
caixa(2.24, 2.82, 0.116, 0.40, 0, H, 'branco_fosco', 'arq')
caixa(2.28, 2.80, 0.40, 0.81, 0.0, 0.62, 'branco_fosco', bev=0.003)
macio(2.54, 0.60, 0.74, 0.26, 0.20, 0.13, 'ceramica', e1=0.4, e2=0.3, seg=24, aneis=10)
cil(2.54, 0.60, 0.17, 0.872, 0.876, 'inox_escuro', seg=24)
tubo([(2.54, 0.42, 1.02), (2.54, 0.50, 1.02), (2.54, 0.50, 0.96)], 0.01, 'cromo', seg=8)
# armarios altos vinho, frentes de vidro canelado e LED
AZ0, AZ1 = 1.62, 2.34
caixa(4.14, 5.36, 0.122, 0.44, AZ0, AZ1, 'vinho', sem='fk')
caixa(4.15, 5.35, 0.124, 0.13, AZ0 + 0.02, AZ1 - 0.02, 'carvalho_h')
for x0, x1 in ((4.14, 4.54), (4.54, 4.95), (4.95, 5.36)):
    caixa(x0, x0 + 0.02, 0.44, 0.45, AZ0, AZ1, 'vinho')
    caixa(x1 - 0.02, x1, 0.44, 0.45, AZ0, AZ1, 'vinho')
    caixa(x0, x1, 0.44, 0.45, AZ0, AZ0 + 0.02, 'vinho')
    caixa(x0, x1, 0.44, 0.45, AZ1 - 0.02, AZ1, 'vinho')
    imagem((x0 + 0.02, 0.445, AZ0 + 0.02), (x1 - 0.02, 0.445, AZ0 + 0.02), (x1 - 0.02, 0.445, AZ1 - 0.02), (x0 + 0.02, 0.445, AZ1 - 0.02), 'vidro_canelado', 'vidro', uv=((0, 0), (2, 0), (2, 1), (0, 1)))
    for zz, zl in ((1.86, 'c'), (2.10, 'c')):
        caixa(x0 + 0.02, x1 - 0.02, 0.13, 0.42, zz, zz + 0.012, 'vinho_tampo')
        caixa(x0 + 0.03, x1 - 0.03, 0.40, 0.41, zz - 0.006, zz, 'luz_led', 'luz')
    for k, (dx, cm) in enumerate(((0.1, 'ceramica'), (0.26, 'ceramica_terra'))):
        cil(x0 + dx, 0.26, 0.045, 1.872, 1.97, cm, seg=14)
    cil((x0 + x1) / 2, 0.26, 0.09, 1.64, 1.70, 'ceramica', seg=22, r2=0.10)
area(4.75, 0.36, 2.09, 1.1, 0.1, 9.0)
area(4.75, 0.36, 1.85, 1.1, 0.1, 9.0)
# coifa preta em cunha sobre o cooktop, armario pequeno em cima
caixa(3.52, 4.14, 0.122, 0.40, 1.92, AZ1, 'vinho', sem='f')
caixa(3.52, 4.14, 0.40, 0.41, 1.92, AZ1, 'vinho')
malha([(3.54, 0.12, 1.72), (4.12, 0.12, 1.72), (4.12, 0.62, 1.60), (3.54, 0.62, 1.60)], [(0, 1, 2, 3)], 'preto')
caixa(3.54, 4.12, 0.12, 0.62, 1.58, 1.60, 'inox_escuro')
caixa(3.54, 4.12, 0.12, 0.34, 1.60, 1.92, 'preto')
malha([(3.54, 0.34, 1.60), (4.12, 0.34, 1.60), (4.12, 0.34, 1.92), (3.54, 0.34, 1.92)], [(0, 1, 2, 3)], 'preto')
malha([(3.54, 0.34, 1.92), (4.12, 0.34, 1.92), (4.12, 0.62, 1.60), (3.54, 0.62, 1.60)], [(3, 2, 1, 0)], 'preto')
# prateleira de madeira com potes e varao azul com ganchos
caixa(4.14, 5.36, 0.122, 0.34, 1.40, 1.43, 'carvalho_h', bev=0.002)
for i, x in enumerate((4.3, 4.55, 4.8, 5.05)):
    cil(x, 0.23, 0.05, 1.43, 1.56, 'ceramica', seg=16)
    cil(x, 0.23, 0.052, 1.56, 1.585, 'carvalho_h', seg=16)
tubo([(4.25, 0.14, 1.30), (5.25, 0.14, 1.30)], 0.006, 'azul', seg=6)
for x in (4.25, 5.25):
    tubo([(x, 0.122, 1.30), (x, 0.14, 1.30), (x, 0.14, 1.40)], 0.006, 'azul', seg=6)
macio(5.0, 0.15, 1.10, 0.09, 0.012, 0.19, 'linho_cinza', e1=0.5, e2=0.5, seg=12, aneis=8)
extruda([(4.72 + 0.035 * math.cos(a), 0.15 + 0.012 * math.sin(a)) for a in np.linspace(0, 6.28, 12, endpoint=False)], 1.0, 1.28, 'carvalho')
macio(4.72, 0.15, 1.0, 0.05, 0.016, 0.075, 'carvalho', e1=0.8, e2=0.8, seg=12, aneis=8)
# geladeira inox
caixa(5.40, 6.05, 0.13, 0.775, 0.04, 0.64, 'inox', bev=0.006)
caixa(5.40, 6.05, 0.13, 0.775, 0.65, 1.86, 'inox', bev=0.006)
caixa(5.42, 6.03, 0.775, 0.777, 0.60, 0.69, 'preto_fosco')
caixa(5.40, 6.05, 0.13, 0.7, 0.0, 0.04, 'preto_fosco')
BLOCOS.append([5.38, 0.116, 6.06, 0.79])
caixa(5.36, 6.056, 0.122, 0.68, 2.02, H, 'vinho', bev=0.002)
caixa(5.70, 5.704, 0.68, 0.682, 2.02, H, 'vinho_tampo')
# itens da bancada
cil(3.20, 0.32, 0.09, 0.92, 0.98, 'carvalho_h', seg=20, r2=0.11)
cil(3.20, 0.32, 0.018, 0.96, 1.12, 'carvalho', seg=8)
cil(2.98, 0.26, 0.032, 0.92, 1.12, 'ceramica_terra', seg=12, r2=0.015)
caixa(4.30, 4.50, 0.45, 0.62, 0.92, 0.94, 'ceramica')
# meia parede: revestimento de madeira, tampo e peninsula
rev_y(1.705, 1, 2.24, 3.54, 0, 1.10, 'carvalho', e=0.014, L='mov')
caixa(3.54, 4.09, 1.55, 1.719, 0, 1.10, 'carvalho')
caixa(2.24, 4.12, 1.54, 1.735, 1.10, 1.135, 'carvalho_h', bev=0.003)
BLOCOS.append([3.54, 1.55, 4.09, 1.72])
# prateleiras da ponta da peninsula, do lado da cozinha
for z in (0.25, 0.55, 0.85):
    caixa(3.58, 4.05, 1.38, 1.55, z, z + 0.025, 'carvalho_h')
    tubo([(3.58, 1.38, z + 0.10), (4.05, 1.38, z + 0.10)], 0.005, 'azul', seg=6)
    tubo([(3.58, 1.38, z + 0.025), (3.58, 1.38, z + 0.10)], 0.005, 'azul', seg=6)
    tubo([(4.05, 1.38, z + 0.025), (4.05, 1.38, z + 0.10)], 0.005, 'azul', seg=6)
    cil(3.72, 1.46, 0.045, z + 0.025, z + 0.13, 'ceramica', seg=14)
    cil(3.90, 1.46, 0.05, z + 0.025, z + 0.12, 'carvalho_h', seg=14)
BLOCOS.append([3.56, 1.38, 4.07, 1.55])

# estante azul suspensa sobre a meia parede, do teto ate o tampo (referencia DSC_0656)
E_X0, E_X1, E_Y0, E_Y1 = 2.70, 3.50, 1.52, 1.78
for x in (E_X0, E_X1):
    for y in (E_Y0, E_Y1):
        caixa(x - 0.012, x + 0.012, y - 0.012, y + 0.012, 1.135, H, 'azul', 'ext')
for z in (1.42, 1.78):
    caixa(E_X0, E_X1, E_Y0, E_Y1, z, z + 0.028, 'carvalho_h', bev=0.002)
    caixa(E_X0, E_X1, E_Y0 - 0.012, E_Y0 + 0.012, z + 0.028, z + 0.048, 'azul', 'ext')
    caixa(E_X0, E_X1, E_Y1 - 0.012, E_Y1 + 0.012, z + 0.028, z + 0.048, 'azul', 'ext')
caixa(E_X0 - 0.01, E_X1 + 0.01, E_Y0 - 0.01, E_Y1 + 0.01, 2.12, 2.145, 'azul', 'ext')
caixa(E_X0, E_X1, E_Y0, E_Y1, 2.145, 2.15, 'preto_fosco')
for k, x in enumerate((2.85, 3.05, 3.25, 3.4)):
    cil(x, 1.65, 0.038, 1.448, 1.56, 'ceramica' if k % 2 else 'latao', seg=14, r2=0.03)
    cil(x + 0.02, 1.65, 0.04, 1.808, 1.90, 'ceramica_terra' if k % 2 else 'ceramica', seg=14, r2=0.05)
area(3.1, 1.65, 2.11, 0.75, 0.2, 5.0)
caixa(2.74, 3.46, 1.545, 1.553, 2.11, 2.12, 'luz_led', 'luz')
caixa(2.74, 3.46, 1.747, 1.755, 2.11, 2.12, 'luz_led', 'luz')


def planta(x, y, z, h=0.55, vaso='ceramica', r=0.11, m='folha_a', n=3):
    if vaso:
        cil(x, y, r * 0.85, z, z + r * 1.5, vaso, seg=18, r2=r)
    w = h * 0.62
    zb = z + r * 1.25
    for i in range(n):
        a = math.radians(i * 180 / n + 17)
        dx, dy = w * math.cos(a), w * math.sin(a)
        imagem((x - dx, y - dy, zb), (x + dx, y + dy, zb), (x + dx, y + dy, zb + h), (x - dx, y - dy, zb + h), m, 'folha')


planta(2.47, 3.92, 1.895, h=0.26, r=0.06, n=2)
planta(3.12, 3.94, 1.895, h=0.24, r=0.055, vaso='ceramica_terra', n=2)
# plantas pendentes sobre a estante azul
planta(3.05, 1.65, 2.15, h=0.44, r=0.09, m='folha_b', n=3)
planta(3.38, 1.66, 2.15, h=0.34, r=0.07, m='folha_a', n=3, vaso='ceramica_terra')
for x, y in ((2.88, 1.60), (3.30, 1.74)):
    imagem((x - 0.16, y, 1.62), (x + 0.16, y, 1.62), (x + 0.16, y, 2.16), (x - 0.16, y, 2.16), 'folha_b', 'folha')

# ================================================================== SACADA
# banco branco capitonado com casinha de pet (referencia DSC_0645)
caixa(1.22, 2.10, 3.52, 4.04, 0.0, 0.40, 'branco', bev=0.004)
BLOCOS.append([1.2, 3.5, 2.12, 4.05])
poli = [(1.42 + 0.20 * math.cos(a), 0.0 + 0.04 + 0.20 * (1 + math.sin(a))) for a in np.linspace(0, math.pi, 16)]
malha([(p[0], 3.518, p[1]) for p in poli], [tuple(range(len(poli)))], 'azul_escuro')
for i in range(3):
    cx = 1.37 + i * 0.29
    macio(cx, 3.78, 0.46, 0.145, 0.25, 0.065, 'boucle', e1=0.35, e2=0.2, seg=22, aneis=8, ruido=0.05, seed=i + 10)
    macio(cx, 4.00, 0.68, 0.145, 0.05, 0.16, 'boucle', e1=0.45, e2=0.25, seg=22, aneis=8, ruido=0.04, seed=i + 20)
quadro_y(4.047, -1, 1.40, 1.70, 0.30, 0.28, 'arte_3')
quadro_y(4.047, -1, 1.82, 1.60, 0.28, 0.26, 'arte_5')
quadro_y(4.047, -1, 1.40, 1.32, 0.30, 0.28, 'arte_6')
# mesa alta junto ao guarda-corpo, coluna azul, balde de inox e banquetas
extruda(arredondado(1.14, 1.46, 2.32, 3.02, 0.04), 1.04, 1.08, 'branco', sem_base=False)
caixa(1.17, 1.40, 2.36, 2.44, 0, 1.04, 'branco')
cil(1.29, 2.90, 0.04, 0, 1.04, 'azul', seg=18)
BLOCOS.append([1.14, 2.32, 1.46, 3.02])
cil(1.31, 2.66, 0.09, 0.84, 1.08, 'inox', seg=24, r2=0.11, tampa=False)
for dx, dy in ((-0.03, 0.03), (0.04, -0.03)):
    cil(1.31 + dx, 2.66 + dy, 0.032, 1.0, 1.26, 'sage_coluna', seg=12, r2=0.012)
with em(1.34, 2.10, 0, 0):
    cadeira_redonda(h_assento=0.72, alto=True)
with em(1.34, 3.24, 0, 180):
    cadeira_redonda(h_assento=0.72, alto=True)
# bancada da churrasqueira no canto da sacada, com armario de madeira e prateleira
caixa(1.16, 2.116, 0.116, 0.70, 0.42, 0.85, 'carvalho_h', bev=0.003)
caixa(1.14, 2.116, 0.116, 0.72, 0.85, 0.89, 'granito', bev=0.003)
caixa(1.40, 1.90, 0.20, 0.60, 0.89, 0.905, 'preto')
for k in range(9):
    tubo([(1.43, 0.22 + k * 0.045, 0.91), (1.87, 0.22 + k * 0.045, 0.91)], 0.003, 'inox', seg=5)
BLOCOS.append([1.14, 0.116, 2.116, 0.72])
caixa(1.2, 2.08, 0.116, 0.30, 1.55, 1.585, 'carvalho_h', bev=0.002)
caixa(1.55, 1.75, 0.13, 0.15, 1.585, 1.86, 'carvalho')
cil(1.9, 0.22, 0.055, 1.585, 1.68, 'ceramica', seg=16)
planta(1.35, 0.22, 1.585, h=0.24, r=0.06, vaso='vaso_preto', n=2)
tubo([(1.25, 0.14, 1.38), (2.03, 0.14, 1.38)], 0.006, 'azul', seg=6)
caixa(1.25, 2.03, 0.122, 0.15, 1.42, 1.43, 'azul')
for x in (1.5, 1.68, 1.86):
    tubo([(x, 0.14, 1.38), (x, 0.14, 1.20)], 0.004, 'cromo', seg=6)
    macio(x, 0.14, 1.17, 0.022, 0.006, 0.04, 'cromo', e1=0.8, e2=0.8, seg=10, aneis=6)
# luminaria de sobrepor no forro da sacada
disco(1.6, 2.0, H - 0.004, 0.05, 'luz_spot', 'luz', seg=18)
LUZES.append(('POINT', (1.6, 2.0, H - 0.1), 2.0, (1.0, 0.88, 0.74), 0))

# ================================================================== SUITE
HX0, HX1 = 2.12, 3.72       # largura da cama
BY0, BY1 = 7.68, 9.68
caixa(HX0 + 0.02, HX1 - 0.02, BY0 + 0.02, BY1 - 0.02, 0.0, 0.28, 'linho_claro', bev=0.02)
macio((HX0 + HX1) / 2, (BY0 + BY1) / 2, 0.42, (HX1 - HX0) / 2, (BY1 - BY0) / 2, 0.15, 'linho_claro', e1=0.22, e2=0.12, seg=44, aneis=12)
macio((HX0 + HX1) / 2, BY0 + 0.72, 0.555, (HX1 - HX0) / 2 + 0.03, 0.75, 0.05, 'linho_claro', e1=0.28, e2=0.15, seg=40, aneis=12, ruido=0.25, seed=31)
macio((HX0 + HX1) / 2, BY0 + 0.42, 0.615, (HX1 - HX0) / 2 + 0.07, 0.25, 0.022, 'azul_manta', e1=0.3, e2=0.1, seg=36, aneis=8, ruido=0.2, seed=32)
BLOCOS.append([HX0, BY0, HX1, 9.73])
# cabeceira de duas placas de linho
macio((HX0 + 2.92) / 2 - 0.01, 9.655, 0.86, (2.92 - HX0) / 2, 0.055, 0.40, 'linho_cinza', e1=0.2, e2=0.15, seg=28, aneis=10)
macio((HX1 + 2.92) / 2 + 0.01, 9.655, 0.86, (HX1 - 2.92) / 2, 0.055, 0.40, 'linho_cinza', e1=0.2, e2=0.15, seg=28, aneis=10)
for s, x in ((31, 2.52), (32, 3.32)):
    macio(x, 9.50, 0.77, 0.33, 0.07, 0.23, 'linho_areia', e1=0.42, e2=0.42, ruido=0.05, seed=s, inc=-12)
    macio(x, 9.36, 0.74, 0.29, 0.07, 0.19, 'linho_cinza', e1=0.42, e2=0.42, ruido=0.05, seed=s + 2, inc=-14)
    macio(x, 9.20, 0.70, 0.20, 0.06, 0.12, 'linho_claro', e1=0.42, e2=0.42, ruido=0.06, seed=s + 3, inc=-18)
# criado-mudo com frente de palhinha e mesa redonda de haste
caixa(3.77, 4.22, 9.28, 9.72, 0.14, 0.62, 'carvalho_h', bev=0.004)
caixa(3.80, 4.19, 9.276, 9.28, 0.40, 0.60, 'palhinha')
caixa(3.80, 4.19, 9.276, 9.28, 0.17, 0.38, 'palhinha')
for x, y in ((3.79, 9.30), (4.20, 9.30), (3.79, 9.70), (4.20, 9.70)):
    cil(x, y, 0.012, 0, 0.14, 'carvalho', seg=8)
BLOCOS.append([3.77, 9.28, 4.22, 9.73])
cil(3.88, 9.50, 0.04, 0.62, 0.70, 'ceramica', seg=16, r2=0.045)
caixa(3.98, 4.18, 9.40, 9.56, 0.62, 0.65, 'livro_a')
with em(1.93, 9.48, 0, 0):
    disco(0, 0, 0.012, 0.13, 'sage_coluna', seg=24)
    cil(0, 0, 0.01, 0.012, 0.56, 'sage_coluna', seg=10)
    extruda([(0.15 * math.cos(a), 0.15 * math.sin(a)) for a in np.linspace(0, 6.28, 24, endpoint=False)], 0.56, 0.58, 'carvalho_h', sem_base=False)
    bloco(-0.09, 0.09, -0.09, 0.09)
# pendente de ratan
tubo([(4.0, 9.42, H), (4.0, 9.42, 1.92)], 0.003, 'preto', seg=6)
cil(4.0, 9.42, 0.19, 1.60, 1.92, 'ratan', 'folha', seg=24, r2=0.09, tampa=False)
disco(4.0, 9.42, 1.72, 0.05, 'luz_spot', 'luz', seg=14)
ponto(4.0, 9.42, 1.70, 6.0)
# painel ocre: fita de LED sob a pintura, quadros de juta
caixa(1.581, 4.279, 9.70, 9.722, 1.265, 1.285, 'ocre')
caixa(1.70, 4.15, 9.695, 9.70, 1.268, 1.276, 'luz_led', 'luz')
area(2.9, 9.66, 1.26, 2.4, 0.04, 8.0, (1.0, 0.96, 0.72))
for i, x in enumerate((2.30, 2.71, 3.12, 3.53)):
    for j, z in enumerate((1.56, 1.98)):
        caixa(x - 0.17, x + 0.17, 9.722, 9.704, z - 0.17, z + 0.17, 'carvalho')
        caixa(x - 0.15, x + 0.15, 9.704, 9.702, z - 0.15, z + 0.15, 'rodape')
        caixa(x - 0.09, x + 0.09, 9.702, 9.700, z - 0.09, z + 0.09, 'linho_areia')
# cortinas de linho do piso ao forro, com sanca de LED (abertas no vao da janela)
def cortina_x(x, y0, y1, ondas, amp=0.035, z0=0.02, z1=H - 0.04):
    n = int(ondas * 10)
    vs, fs, uvs = [], [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        dx = amp * math.sin(t * ondas * 2 * math.pi)
        vs.append((x + dx, y, z0))
        vs.append((x + dx * 0.8, y, z1))
        uvs.extend([(t * ondas, 0.0), (t * ondas, 1.0)])
    for i in range(n):
        fs.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    malha(vs, fs, 'cortina', 'ext', suave=True, uvs=uvs)


def cortina_y(y, x0, x1, ondas, amp=0.035, z0=0.02, z1=H - 0.04):
    n = int(ondas * 10)
    vs, fs, uvs = [], [], []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        dy = amp * math.sin(t * ondas * 2 * math.pi)
        vs.append((x, y + dy, z0))
        vs.append((x, y + dy * 0.8, z1))
        uvs.extend([(t * ondas, 0.0), (t * ondas, 1.0)])
    for i in range(n):
        fs.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    malha(vs, fs, 'cortina', 'ext', suave=True, uvs=uvs)


cortina_x(1.68, 6.76, 7.50, 6)
cortina_x(1.68, 8.60, 9.70, 9)
BLOCOS.append([1.58, 6.73, 1.74, 7.5])
BLOCOS.append([1.58, 8.6, 1.74, 9.73])
caixa(1.60, 1.80, 6.73, 9.729, H - 0.05, H - 0.038, 'teto', 'arq')
caixa(1.79, 1.80, 6.8, 9.68, H - 0.042, H - 0.038, 'luz_led', 'luz')
area(1.76, 8.2, H - 0.06, 0.05, 2.7, 7.0)
# painel de madeira com TV na parede oposta a janela
caixa(4.25, 4.273, 8.34, 9.70, 1.22, 2.02, 'carvalho')
caixa(4.232, 4.25, 8.52, 9.62, 1.33, 1.97, 'preto')
imagem((4.2315, 9.60, 1.35), (4.2315, 8.54, 1.35), (4.2315, 8.54, 1.95), (4.2315, 9.60, 1.95), 'tela')
macio(4.16, 9.0, 2.33, 0.11, 0.42, 0.13, 'branco', e1=0.28, e2=0.2, seg=20, aneis=8)
# armario de vidro com cabideiro iluminado (referencia DSC_0684)
YC0, YC1 = 6.729, 7.18
caixa(1.74, 3.33, YC0, YC0 + 0.012, 0, H, 'carvalho_h', sem='')
caixa(1.74, 3.33, YC0, YC1, 0, 0.08, 'carvalho')
caixa(1.74, 3.33, YC0, YC1, 2.46, H, 'branco_fosco')
caixa(1.74, 3.33, YC0, YC1 - 0.03, 0.72, 0.75, 'carvalho')
caixa(1.74, 3.33, YC0, YC1 - 0.03, 1.98, 2.0, 'carvalho')
for x in np.linspace(1.74, 3.33, 5):
    x = float(x)
    caixa(x - 0.022, x + 0.022, YC0, YC1, 0, 2.46, 'linho_areia')
for i in range(4):
    x0_ = 1.76 + i * 0.3975
    x1_ = x0_ + 0.3575
    caixa(x0_, x1_, YC1 - 0.05, YC1 - 0.03, 0.08, 0.40, 'carvalho')
    caixa(x0_, x1_, YC1 - 0.05, YC1 - 0.03, 0.40, 0.72, 'carvalho')
    imagem((x0_ + 0.01, YC1 - 0.005, 0.76), (x1_ - 0.01, YC1 - 0.005, 0.76), (x1_ - 0.01, YC1 - 0.005, 2.44), (x0_ + 0.01, YC1 - 0.005, 2.44), 'vidro', 'vidro')
tubo([(1.76, 6.95, 1.92), (3.31, 6.95, 1.92)], 0.008, 'cromo', seg=8)
rng_ = np.random.default_rng(9)
for i, x in enumerate(np.arange(1.84, 3.30, 0.115)):
    m_ = 'roupa_az' if i % 5 == 3 else 'roupa'
    h_ = float(rng_.uniform(0.75, 0.98))
    macio(float(x), 6.95, 1.90 - h_ / 2, 0.024, 0.18, h_ / 2, m_, e1=0.3, e2=0.3, seg=12, aneis=6, ruido=0.03, seed=i)
for x in (2.1, 2.9):
    caixa(x - 0.2, x + 0.2, 6.78, 7.10, 2.0, 2.22, 'ceramica')
caixa(1.76, 3.31, 7.12, 7.13, 2.44, 2.452, 'luz_led', 'luz')
area(2.52, 7.05, 2.42, 1.4, 0.06, 7.0)
BLOCOS.append([1.74, 6.729, 3.33, 7.18])
# tapete claro
spot(3.2, 7.6, w=6.0)
# (o banheiro da suite vem depois, em banho())

# ================================================================== DORMITORIO 2 (decorado real: quarto de bebe)
# cortina
cortina_x(0.20, 4.20, 4.92, 6)
cortina_x(0.20, 5.98, 6.62, 5)
BLOCOS.append([0.11, 4.163, 0.26, 4.92])
BLOCOS.append([0.11, 5.98, 0.26, 6.65])
caixa(0.13, 0.30, 4.163, 6.651, H - 0.05, H - 0.038, 'teto', 'arq')
caixa(0.29, 0.30, 4.25, 6.55, H - 0.042, H - 0.038, 'luz_led', 'luz')
area(0.27, 5.4, H - 0.06, 0.05, 2.2, 9.0)
# berco branco de grade
CX0, CX1, CY0, CY1 = 0.75, 2.05, 5.96, 6.62
caixa(CX0, CX1, CY0, CY1, 0.30, 0.42, 'branco')
macio((CX0 + CX1) / 2, (CY0 + CY1) / 2, 0.47, (CX1 - CX0) / 2 - 0.03, (CY1 - CY0) / 2 - 0.03, 0.06, 'linho_claro', e1=0.2, e2=0.15, seg=28, aneis=8)
for x, y in ((CX0, CY0), (CX1, CY0), (CX0, CY1), (CX1, CY1)):
    caixa(x - 0.022, x + 0.022, y - 0.022, y + 0.022, 0, 0.92, 'branco', bev=0.003)
for y in (CY0, CY1):
    caixa(CX0, CX1, y - 0.015, y + 0.015, 0.86, 0.90, 'branco')
    caixa(CX0, CX1, y - 0.015, y + 0.015, 0.34, 0.38, 'branco')
    for x in np.arange(CX0 + 0.05, CX1, 0.07):
        cil(float(x), y, 0.009, 0.38, 0.86, 'branco', seg=8)
for x in (CX0, CX1):
    caixa(x - 0.015, x + 0.015, CY0, CY1, 0.86, 0.90, 'branco')
    caixa(x - 0.015, x + 0.015, CY0, CY1, 0.34, 0.38, 'branco')
    for y in np.arange(CY0 + 0.05, CY1, 0.07):
        cil(x, float(y), 0.009, 0.38, 0.86, 'branco', seg=8)
BLOCOS.append([CX0 - 0.03, CY0 - 0.03, CX1 + 0.03, 6.65])
macio(1.05, 6.28, 0.57, 0.11, 0.09, 0.08, 'toalha', e1=0.7, e2=0.7, seed=3)
macio(1.05, 6.30, 0.70, 0.07, 0.07, 0.07, 'toalha', e1=0.9, e2=0.9, seed=4)
# comoda branca com trocador e pes de carvalho (referencia DSC_0675)
with em(1.30, 4.173, 0, 0):
    W, P = 1.05, 0.52
    for x in (0.0, W - 0.04):
        caixa(x, x + 0.04, 0, P, 0, 1.0, 'carvalho')
    caixa(0.04, W - 0.04, 0.0, P, 0.14, 0.90, 'branco')
    for i, (z0_, z1_) in enumerate(((0.15, 0.39), (0.40, 0.64), (0.65, 0.89))):
        caixa(0.05, W - 0.05, P, P + 0.015, z0_, z1_, 'branco', bev=0.003)
        for x in (0.25, W - 0.25):
            caixa(x - 0.012, x + 0.012, P + 0.015, P + 0.03, (z0_ + z1_) / 2 - 0.04, (z0_ + z1_) / 2 + 0.03, 'couro')
    caixa(-0.02, W + 0.02, -0.0, P + 0.04, 0.90, 0.93, 'branco')
    macio(W / 2, P * 0.55, 0.98, 0.44, 0.22, 0.05, 'linho_areia', e1=0.3, e2=0.2, seg=24, aneis=8)
    caixa(0.02, W - 0.02, P * 0.02, P * 0.14, 0.93, 1.02, 'branco')
    cil(0.14, 0.08, 0.05, 1.02, 1.09, 'ceramica', seg=16)
    cil(0.32, 0.08, 0.05, 1.02, 1.08, 'ceramica_terra', seg=16)
    bloco(-0.02, W + 0.02, -0.01, P + 0.04)
# prateleiras presas por alcas de couro, com livros
for xc, z, livros in ((1.55, 1.55, ('livro_v', 'livro_a', 'livro_b')), (2.40, 1.72, ('livro_a', 'livro_v')), (0.70, 1.85, ('livro_b', 'livro_a'))):
    caixa(xc - 0.28, xc + 0.28, 4.176, 4.34, z, z + 0.022, 'carvalho_h', bev=0.002)
    for s in (-1, 1):
        tubo([(xc + s * 0.24, 4.34, z + 0.01), (xc + s * 0.24, 4.178, z + 0.42)], 0.012, 'couro', seg=6, ry=0.003)
    for k, m_ in enumerate(livros):
        caixa(xc - 0.20 + k * 0.05, xc - 0.16 + k * 0.05, 4.19, 4.31, z + 0.022, z + 0.022 + 0.21, m_)
# poltrona boucle giratoria e cesto
with em(0.62, 4.60, 0, 40):
    cil(0, 0, 0.26, 0, 0.03, 'sage_coluna', seg=28)
    macio(0, 0, 0.26, 0.36, 0.36, 0.20, 'boucle', e1=0.5, e2=0.8, seg=32, aneis=12)
    arco = [(0.34 * math.cos(math.radians(a)), 0.34 * math.sin(math.radians(a)), 0.55) for a in np.linspace(150, 390, 24)]
    tubo(arco, 0.09, 'boucle', seg=12, ry=0.20, tampa=True)
    bloco(-0.36, 0.36, -0.36, 0.36)
cil(1.08, 4.35, 0.14, 0, 0.3, 'palhinha', seg=24, r2=0.16, tampa=False)
# tapete em forma de folha
def folha_tapete(cx, cy, comp, larg, ang):
    a = math.radians(ang)
    ca_, sa_ = math.cos(a), math.sin(a)
    pts = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        rx = comp * math.cos(t)
        lobos = 1 + 0.12 * math.cos(6 * t) * (abs(math.sin(t)) ** 0.5)
        ry = larg * math.sin(t) * lobos * (1 - 0.25 * math.cos(t))
        pts.append((cx + ca_ * rx - sa_ * ry, cy + sa_ * rx + ca_ * ry))
    extruda(pts, 0.0, 0.01, 'verde_tapete', lados_suaves=True)
    for s in np.linspace(-0.8, 0.8, 9):
        p0 = (cx + ca_ * comp * s, cy + sa_ * comp * s)
        tubo([(p0[0], p0[1], 0.0115), (cx + ca_ * comp * (s + 0.05) - sa_ * larg * 0.72, cy + sa_ * comp * (s + 0.05) + ca_ * larg * 0.72, 0.0115)], 0.005, 'sage_coluna', seg=4, ry=0.001, tampa=False)
        tubo([(p0[0], p0[1], 0.0115), (cx + ca_ * comp * (s + 0.05) + sa_ * larg * 0.72, cy + sa_ * comp * (s + 0.05) - ca_ * larg * 0.72, 0.0115)], 0.005, 'sage_coluna', seg=4, ry=0.001, tampa=False)
    tubo([(cx - ca_ * comp * 0.95, cy - sa_ * comp * 0.95, 0.0115), (cx + ca_ * comp * 0.95, cy + sa_ * comp * 0.95, 0.0115)], 0.008, 'sage_coluna', seg=4, ry=0.001, tampa=False)
folha_tapete(1.68, 5.28, 0.95, 0.58, 12)
# armario branco com vidro no lugar do armario da planta
caixa(2.72, 3.271, 4.163, 5.775, 0, H, 'branco_fosco')
BLOCOS.append([2.70, 4.163, 3.28, 5.775])
for y in np.linspace(4.17, 5.775, 4):
    caixa(2.712, 2.722, float(y) - 0.012, float(y) + 0.012, 0, H, 'carvalho_h')
for y0, y1 in ((4.18, 4.70), (4.71, 5.23), (5.24, 5.76)):
    caixa(2.71, 2.72, y0, y1, 0.08, 0.72, 'carvalho')
    for yy in np.arange(y0 + 0.06, y1 - 0.02, 0.07):
        macio(2.705, float(yy), 1.46, 0.006, 0.026, 0.42, 'roupa' if int(yy * 100) % 3 else 'roupa_az', e1=0.3, e2=0.3, seg=8, aneis=4)
    imagem((2.698, y1 - 0.01, 0.74), (2.698, y0 + 0.01, 0.74), (2.698, y0 + 0.01, 2.44), (2.698, y1 - 0.01, 2.44), 'vidro', 'vidro')
# ar-condicionado e spot central
macio(1.65, 6.54, 2.33, 0.42, 0.10, 0.13, 'branco', e1=0.28, e2=0.2, seg=20, aneis=8)
spot(1.65, 5.3, w=16.0)
spot(0.85, 5.0, w=10.0)
spot(3.0, 6.2, w=6.0)


# ================================================================== BANHEIROS (ventilados por shaft, sem janela: toda a luz e artificial)
def banho(y0, est):
    """y0 = parede de menor y; bancada na ponta de menor y, chuveiro na de maior y. X vai de 4,349 a 5,55."""
    y1 = y0 + 2.40
    tile = 'azulejo_salvia' if est == 1 else 'granilite'
    x0, x1 = 4.349, 5.55
    alt_faixa = 1.18
    # paredes: banda de revestimento, revestimento inteiro no boxe, pintura em cima
    rev_x(x1, -1, y0, y0 + 1.60, 0, alt_faixa, tile)
    rev_x(x1, -1, y0, y0 + 1.60, alt_faixa, H, 'parede' if est == 1 else 'granilite')
    rev_x(x1, -1, y0 + 1.60, y1, 0, H, tile)
    rev_y(y1, -1, x0, x1, 0, H, tile)
    rev_y(y0, 1, x0, x1, 0, alt_faixa, tile)
    rev_y(y0, 1, x0, x1, alt_faixa, H, 'parede' if est == 1 else 'granilite')
    rev_x(x0, 1, y0 + 1.60, y1, 0, H, tile)
    rev_x(x0, 1, y0, y0 + 0.135 if est == 2 else y0 + 0.12, 0, H, 'parede' if est == 1 else 'granilite')
    # bancada com cuba de marmore; est 1: madeira e latao; est 2: branco e preto
    corpo = 'carvalho_h' if est == 1 else 'branco_fosco'
    metal = 'latao' if est == 1 else 'preto'
    caixa(5.11, x1 - 0.006, y0 + 0.006, y0 + 0.76, 0.32, 0.80, corpo, bev=0.003)
    if est == 2:
        caixa(5.105, 5.11, y0 + 0.02, y0 + 0.375, 0.34, 0.78, 'rodape')
        caixa(5.105, 5.11, y0 + 0.385, y0 + 0.74, 0.34, 0.78, 'rodape')
        for yy in (y0 + 0.33, y0 + 0.43):
            caixa(5.095, 5.105, yy - 0.03, yy + 0.03, 0.70, 0.73, 'preto')
    caixa(5.09, x1 - 0.006, y0 + 0.006, y0 + 0.78, 0.80, 0.97, 'marmore', bev=0.006)
    disco(5.30, y0 + 0.39, 0.9715, 0.13, 'inox_escuro', seg=24)
    tubo([(5.48, y0 + 0.39, 0.97), (5.48, y0 + 0.39, 1.14), (5.32, y0 + 0.39, 1.14), (5.32, y0 + 0.39, 1.10)], 0.012, metal, seg=10)
    BLOCOS.append([5.08, y0, x1, y0 + 0.79])
    # prateleira e nicho
    caixa(5.36, x1 - 0.006, y0 + 0.02, y0 + 1.58, alt_faixa, alt_faixa + 0.025, 'carvalho_h' if est == 1 else 'rodape', bev=0.002)
    for k, yy in enumerate((0.92, 1.02, 1.12, 1.26)):
        cil(5.45, y0 + yy, 0.028, alt_faixa + 0.025, alt_faixa + 0.11, 'ceramica' if k % 2 else ('ceramica_terra' if est == 2 else 'ceramica'), seg=14, r2=0.024)
    planta(5.45, y0 + 1.42, alt_faixa + 0.025, h=0.16, r=0.04, n=2)
    # espelho: est 1 redondo com moldura de madeira, est 2 armario retangular
    zc = 1.72
    if est == 1:
        pts = [(5.54, y0 + 0.52 + 0.46 * math.cos(a), zc + 0.46 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 56, endpoint=False)]
        tubo(pts, 0.018, 'carvalho_h', seg=8, fechado=True)
        ESPELHOS.append({'pts': [[5.536, round(p[1], 3), round(p[2], 3)] for p in pts], 'n': [-1, 0, 0]})
    else:
        caixa(5.47, 5.542, y0 + 0.08, y0 + 1.02, 1.32, 2.14, 'rodape')
        pts = [(5.466, y0 + 0.10, 1.34), (5.466, y0 + 1.00, 1.34), (5.466, y0 + 1.00, 2.12), (5.466, y0 + 0.10, 2.12)]
        ESPELHOS.append({'pts': [[p[0], round(p[1], 3), round(p[2], 3)] for p in pts], 'n': [-1, 0, 0]})
    # toalheiro e toalha
    tubo([(5.07, y0 + 0.10, 0.74), (5.07, y0 + 0.70, 0.74)], 0.008, metal, seg=8)
    macio(5.065, y0 + 0.36, 0.56, 0.016, 0.18, 0.20, 'toalha', e1=0.4, e2=0.4, seg=14, aneis=8)
    # vaso sanitario com caixa acoplada
    yv = y0 + 1.15
    caixa(5.36, 5.54, yv - 0.20, yv + 0.20, 0.40, 0.78, 'ceramica', bev=0.02)
    macio(5.14, yv, 0.20, 0.26, 0.19, 0.20, 'ceramica', e1=0.5, e2=0.8, seg=28, aneis=12)
    macio(5.12, yv, 0.41, 0.28, 0.20, 0.03, 'ceramica', e1=0.4, e2=0.8, seg=28, aneis=8)
    BLOCOS.append([4.94, yv - 0.2, 5.55, yv + 0.2])
    # shaft (no chuveiro, contra o fundo)
    caixa(5.33, 5.544, y1 - 0.77, y1 - 0.006, 0, H, tile)
    BLOCOS.append([5.33, y1 - 0.77, 5.55, y1])
    # painel de vidro canelado com perfil metalico
    yb = y0 + 1.63
    xv0, xv1 = 4.96, 5.544
    perfil = 'latao' if est == 1 else 'preto'
    for a, b, c_, d in ((xv0, xv0 + 0.03, 0, 2.2), (xv1 - 0.03, xv1, 0, 2.2), (xv0, xv1, 0, 0.03), (xv0, xv1, 2.17, 2.2), (xv0, xv1, 1.08, 1.11)):
        caixa(a, b, yb - 0.015, yb + 0.015, c_, d, perfil)
    imagem((xv0 + 0.03, yb, 0.03), (xv1 - 0.03, yb, 0.03), (xv1 - 0.03, yb, 2.17), (xv0 + 0.03, yb, 2.17), 'vidro_canelado', 'vidro', uv=((0, 0), (10, 0), (10, 1), (0, 1)))
    BLOCOS.append([xv0, yb - 0.02, xv1, yb + 0.02])
    # chuveiro de teto e prateleira do boxe
    cil(4.90, y1 - 0.38, 0.10, H - 0.22, H - 0.20, metal, seg=20, base=True)
    tubo([(4.90, y1 - 0.38, H), (4.90, y1 - 0.38, H - 0.2)], 0.01, metal, seg=8)
    caixa(4.40, 5.33, y1 - 0.14, y1 - 0.005, 1.20, 1.225, 'marmore')
    for k, m_ in enumerate(('vaso_preto', 'couro', 'vaso_preto')):
        cil(4.70 + k * 0.1, y1 - 0.07, 0.03, 1.225, 1.40, m_, seg=12)
    # luz: faixa de LED no forro e luz geral
    caixa(4.55, 5.2, y0 + 0.70, y0 + 0.72, H - 0.004, H, 'luz_led', 'luz')
    area(4.9, y0 + 0.71, H - 0.02, 0.8, 0.14, 26.0, (1.0, 0.90, 0.76))
    area(4.9, y1 - 0.38, H - 0.02, 0.5, 0.1, 10.0, (1.0, 0.90, 0.76))


banho(4.845, 2)
banho(7.333, 1)

# ================================================================== CIRCULACAO E ENTRADA
spot(3.8, 5.3, w=7.0)
spot(5.6, 1.35, w=7.0)
spot(4.65, 1.2, w=7.0)
spot(3.0, 1.2, w=6.0)
area(4.5, 0.5, 1.60, 1.2, 0.12, 4.0, dir_=(0, 0, -1))
# interruptor preto da entrada (detalhe das fotos)
caixa(6.053, 6.056, 2.05, 2.13, 1.10, 1.22, 'preto')

# ================================================================== OBJETOS, LUZES, MUNDO
ROOMS = [
    {'id': 'entrada', 'nome': 'Entrada', 'caixa': [5.15, 0.8, 6.06, 1.8], 'pos': [5.72, 1.36], 'olha': [-1.0, 0.55]},
    {'id': 'cozinha', 'nome': 'Cozinha', 'caixa': [2.24, 0.116, 5.15, 1.7], 'pos': [4.95, 1.30], 'olha': [-1.0, -0.42]},
    {'id': 'sala', 'nome': 'Sala', 'caixa': [2.24, 1.7, 4.1, 4.05], 'pos': [3.72, 3.30], 'olha': [-1.0, -0.20]},
    {'id': 'jantar', 'nome': 'Jantar', 'caixa': [3.36, 1.7, 6.06, 4.76], 'pos': [3.75, 2.95], 'olha': [1.0, 0.45]},
    {'id': 'sacada', 'nome': 'Sacada', 'caixa': [1.0, 0.116, 2.24, 4.05], 'pos': [1.80, 1.45], 'olha': [-1.0, 0.45]},
    {'id': 'circulacao', 'nome': 'Circulação', 'caixa': [3.36, 4.76, 4.28, 6.7], 'pos': [3.82, 4.5], 'olha': [0.0, 1.0]},
    {'id': 'suite', 'nome': 'Suíte', 'caixa': [1.58, 6.73, 4.28, 9.73], 'pos': [3.82, 7.30], 'olha': [-0.75, 1.0]},
    {'id': 'banho-suite', 'nome': 'Banho da suíte', 'caixa': [4.35, 7.33, 5.55, 9.73], 'pos': [4.68, 7.85], 'olha': [0.75, 0.05]},
    {'id': 'dorm2', 'nome': 'Quarto', 'caixa': [0.11, 4.16, 3.27, 6.65], 'pos': [2.62, 6.15], 'olha': [-1.0, -0.42]},
    {'id': 'banho', 'nome': 'Banho social', 'caixa': [4.35, 4.84, 5.55, 7.26], 'pos': [4.68, 5.40], 'olha': [0.75, 0.05]},
]
objs = {n: objeto(n) for n in CAMADAS}
print('faces', {n: len(C[n].f) for n in CAMADAS}, flush=True)

cena = bpy.context.scene
for tipo, p, w, cor, extra in LUZES:
    d = bpy.data.lights.new('l', tipo)
    d.energy = w
    d.color = cor
    if tipo == 'SPOT':
        d.spot_size = math.radians(extra)
        d.spot_blend = 0.6
        d.shadow_soft_size = 0.03
    elif tipo == 'POINT':
        d.shadow_soft_size = 0.05
    elif tipo == 'AREA':
        d.shape = 'RECTANGLE'
        d.size, d.size_y = extra[0], extra[1]
    o = bpy.data.objects.new('l', d)
    o.location = p
    cena.collection.objects.link(o)
# sol da tarde: o final 05 fica na face poente da torre (-x)
SOL = (-0.72, -0.34, 0.60)
sd = bpy.data.lights.new('sol', 'SUN')
sd.energy = 6.0
sd.color = (1.0, 0.91, 0.78)
sd.angle = math.radians(2.0)
so = bpy.data.objects.new('sol', sd)
from mathutils import Vector
so.rotation_mode = 'QUATERNION'
so.rotation_quaternion = Vector(SOL).normalized().to_track_quat('Z', 'Y')
cena.collection.objects.link(so)
# ceu com gradiente (fica por tras do vidro; chao claro devolve luz pelas janelas)
w = bpy.data.worlds.new('ceu')
cena.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
rmp = nt.nodes.new('ShaderNodeValToRGB')
map_ = nt.nodes.new('ShaderNodeMapRange')
map_.inputs['From Min'].default_value = -1
map_.inputs['From Max'].default_value = 1
bg = nt.nodes.new('ShaderNodeBackground')
sai = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(tc.outputs['Generated'], sep.inputs[0])
nt.links.new(sep.outputs['Z'], map_.inputs['Value'])
nt.links.new(map_.outputs['Result'], rmp.inputs['Fac'])
nt.links.new(rmp.outputs['Color'], bg.inputs['Color'])
nt.links.new(bg.outputs[0], sai.inputs[0])
rmp.color_ramp.elements[0].position = 0.46
rmp.color_ramp.elements[0].color = (0.30, 0.30, 0.26, 1)
rmp.color_ramp.elements[1].position = 0.52
rmp.color_ramp.elements[1].color = (0.92, 0.95, 1.0, 1)
el = rmp.color_ramp.elements.new(0.85)
el.color = (0.42, 0.62, 0.95, 1)
bg.inputs['Strength'].default_value = 3.4

# ================================================================== LIGHTMAPS
def uv_lightmap(ob, margem):
    me = ob.data
    for o in bpy.data.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    lm = me.uv_layers.new(name='lightmap')
    me.uv_layers.active = lm
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margem, area_weight=0.0, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margem, shape_method='CONCAVE')
    bpy.ops.object.mode_set(mode='OBJECT')


def bake(ob, res, nome):
    t0 = time.time()
    img = bpy.data.images.new(nome, res, res, alpha=False, float_buffer=True)
    me = ob.data
    me.uv_layers.active = me.uv_layers['lightmap']
    me.uv_layers['UVMap'].active_render = True
    for o in bpy.data.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    for m in me.materials:
        nt_ = m.node_tree
        n = nt_.nodes.get('__bake') or nt_.nodes.new('ShaderNodeTexImage')
        n.name = '__bake'
        n.image = img
        nt_.nodes.active = n
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=6, margin_type='EXTEND', use_clear=True)
    print('bake', nome, res, 'ok em %.0f s' % (time.time() - t0), flush=True)
    return img


def suaviza_ilhas(a, cob, passos):
    """Reduz o ruido sem vazar entre as ilhas: media 3x3 ponderada pela cobertura do mapa."""
    for _ in range(passos):
        s = np.zeros_like(a)
        n = np.zeros(a.shape[:2], np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                k = 4.0 if dx == 0 and dy == 0 else (2.0 if dx == 0 or dy == 0 else 1.0)
                s += np.roll(np.roll(a * cob[..., None], dy, 0), dx, 1) * k
                n += np.roll(np.roll(cob, dy, 0), dx, 1) * k
        r = s / np.maximum(n, 1e-6)[..., None]
        a = np.where(cob[..., None] > 0, r, a)
    return a


def denoise(img):
    """OIDN (no denoise do compositor) sobre o mapa cru, em uma cena vazia. Devolve o nome do EXR limpo."""
    t0 = time.time()
    w, h = img.size
    sc = bpy.data.scenes.new('dn')
    ng = bpy.data.node_groups.new('dn', 'CompositorNodeTree')
    sc.compositing_node_group = ng
    n_ = ng.nodes.new('CompositorNodeImage')
    n_.image = img
    d_ = ng.nodes.new('CompositorNodeDenoise')
    d_.inputs['HDR'].default_value = True
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    g_ = ng.nodes.new('NodeGroupOutput')
    ng.links.new(n_.outputs[0], d_.inputs[0])
    ng.links.new(d_.outputs[0], g_.inputs[0])
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.use_compositing = True
    sc.render.use_sequencer = False
    sc.render.image_settings.file_format = 'OPEN_EXR'
    sc.render.image_settings.color_depth = '32'
    caminho = os.path.join(bpy.app.tempdir, img.name + '_dn.exr')
    sc.render.filepath = caminho
    bpy.ops.render.render(scene=sc.name, write_still=True)
    r = bpy.data.images.load(caminho)
    b = np.zeros(w * h * 4, np.float32)
    r.pixels.foreach_get(b)
    bpy.data.images.remove(r)
    bpy.data.scenes.remove(sc)
    print('denoise', img.name, 'ok em %.0f s' % (time.time() - t0), flush=True)
    return b.reshape(h, w, 4)[..., :3]


def grava_lm(img, nome, escala, passos):
    w, h = img.size
    a = np.zeros(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[..., :3]
    cob = (a.sum(2) > 0).astype(np.float32)
    try:
        a = denoise(img)
    except Exception as e:
        print('denoise falhou:', e, flush=True)
    # o denoise preserva ruido em faixas estreitas (vergas, pontas de parede): media local dentro da ilha
    a = suaviza_ilhas(a, cob, passos)
    # linear -> sRGB, com escala (a pagina multiplica de volta por lightMapIntensity)
    v = np.clip(a / escala, 0, 1)
    v = np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1 / 2.4) - 0.055)
    out = bpy.data.images.new(nome, w, h, alpha=True)
    out.colorspace_settings.name = 'Non-Color'
    rgba = np.dstack([v, np.ones((h, w), np.float32)])
    out.pixels.foreach_set(rgba.astype(np.float32).ravel())
    caminho = os.path.join(SAIDA, nome)
    out.filepath_raw = caminho
    out.file_format = 'WEBP'
    cena.render.image_settings.quality = 90
    out.save(quality=90)
    print('lightmap', caminho, os.path.getsize(caminho), 'max %.2f medio %.2f' % (a.max(), a[cob > 0].mean()), flush=True)


cena.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'METAL'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    cena.cycles.device = 'GPU'
    print('cycles: metal', [d.name for d in pr.devices if d.use], flush=True)
except Exception as e:
    print('cycles: cpu', e, flush=True)
cena.cycles.samples = AMOSTRAS
cena.cycles.use_denoising = False
cena.cycles.max_bounces = 6
cena.cycles.diffuse_bounces = 5
cena.cycles.glossy_bounces = 2
cena.cycles.transmission_bounces = 4
cena.cycles.transparent_max_bounces = 8
cena.cycles.caustics_reflective = False
cena.cycles.caustics_refractive = False
cena.cycles.sample_clamp_indirect = 6.0
cena.render.bake.use_selected_to_active = False

objs['folha'].hide_render = True
objs['vidro'].hide_render = False
# vidro nao segura luz nem sombra: transparente puro para o Cycles
for nome in ('vidro', 'vidro_canelado'):
    m = MATS[nome]
    nt_ = m.node_tree
    p_ = next(n for n in nt_.nodes if n.type == 'BSDF_PRINCIPLED')
    p_.inputs['Alpha'].default_value = 0.02 if nome == 'vidro' else 0.45
    p_.inputs['Roughness'].default_value = 0.05
    for lk in list(p_.inputs['Alpha'].links):
        nt_.links.remove(lk)

METAIS = {}
for nome_m, m_ in MATS.items():
    p_ = next(n for n in m_.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if p_.inputs['Metallic'].default_value > 0:
        METAIS[nome_m] = p_.inputs['Metallic'].default_value
        p_.inputs['Metallic'].default_value = 0.0

uv_lightmap(objs['arq'], 0.003)
uv_lightmap(objs['mov'], 0.002)
print('uv ok', flush=True)
PASSOS = 2
img_a = bake(objs['arq'], RES_ARQ, 'lm_arq')
grava_lm(img_a, 'lm-arq.webp', 3.2, 4)
img_m = bake(objs['mov'], RES_MOV, 'lm_mov')
grava_lm(img_m, 'lm-mov.webp', 3.2, PASSOS)

# ================================================================== EXPORT
for nome_m, v_ in METAIS.items():
    p_ = next(n for n in MATS[nome_m].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p_.inputs['Metallic'].default_value = v_
for ob_nome in ('arq', 'mov'):
    ob = objs[ob_nome]
    me = ob.data
    # o exportador grava cada mapa UV na ordem: UVMap = TEXCOORD_0, lightmap = TEXCOORD_1 (uv1 na pagina)
    me.uv_layers.active = me.uv_layers['UVMap']
    for m in me.materials:
        nd = m.node_tree.nodes.get('__bake')
        if nd:
            m.node_tree.nodes.remove(nd)
for nome in ('vidro', 'vidro_canelado'):
    m = MATS[nome]
    p_ = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p_.inputs['Alpha'].default_value = 0.10 if nome == 'vidro' else 0.55
for o in bpy.data.objects:
    o.select_set(o.name.startswith('apto_'))
bpy.context.view_layer.objects.active = objs['arq']
OUT = os.path.join(SAIDA, 'apto-final05.glb')
bpy.ops.export_scene.gltf(
    filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_apply=False,
    export_attributes=True, export_cameras=False, export_lights=False, export_extras=False,
    export_image_format='WEBP', export_image_quality=82,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=16, export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=14, export_draco_generic_quantization=16)
print('glb', os.path.getsize(OUT), flush=True)
json.dump({
    'schema': 'gaia-apto/1',
    'nome': 'Final 05',
    'pe_direito': H,
    'olho': 1.60,
    'raio': 0.18,
    'torre_x_para_apto': -7.0,
    'torre_y_para_apto': -9.806,
    'sol': list(SOL),
    'blocos': BLOCOS,
    'ambientes': ROOMS,
    'espelhos': ESPELHOS,
    'lm_arq': 'lm-arq.webp',
    'lm_mov': 'lm-mov.webp',
    'lm_escala': 3.2,
}, open(os.path.join(SAIDA, 'apto-final05.json'), 'w'), ensure_ascii=False)
print('fim', flush=True)
