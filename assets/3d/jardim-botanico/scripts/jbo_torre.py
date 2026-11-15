# jbo_torre.py -- forma da torre do Reserva Direcional Jardim Botanico em metros. So dados e funcoes puras (sem bpy):
# usado por jbo_modelo.py (Blender) e jbo_ver.py (conferencia sobre a implantacao).
#
# Fontes (Drive do produto, pasta PLANTAS E IMPLANTACAO):
#   GUI_M01_Implantacao_REV_05_00a.jpg (14003 x 1991 px): paredes pretas lidas por perfil de cor; as 3 torres tem a
#     mesma forma, sem giro, simetrica nos dois eixos. Escala 36,5 px/m.
#   GUI_P01_Apartamento Ponta (246 px/m: dormitorio 2,50 = 615 px) e GUI_P07_Tipo Meio (220 px/m: dormitorio 2,95 =
#     648 px). Conferencia planta x implantacao: bloco dos quartos do ponta 7,95 m (1955 px / 290 px), fundo do bloco
#     3,42 m (841 / 125 px), cozinha 1,58 m (389 / 57 px), varanda do meio 4,12 m (906 / 150 px), bloco do quarto do
#     meio 3,17 x 1,36 m (697 x 300 / 116 x 50 px). Diferencas abaixo de 5 cm.
#
# Referencial local da torre (metros): origem no centro, x ao longo do eixo maior (+x = lado direito da implantacao,
# finais 06 e 07), y para CIMA da implantacao (lado da entrada do hall, finais 01, 02, 07 e 08). No Blender o eixo y
# da implantacao ja e o +Y da cena, entao (X, Y) = (TX + x, TY + y).
#
# Mapa do pavimento como aparece na implantacao (o mapa chave das plantas esta girado 180 graus):
#     02   01 | 08   07          (cima: acesso do hall no terreo, no lugar do 01)
#     03   04 | 05   06
# Ponta base = 07 (x > 0, y > 0): 02 = 07 espelhado em x, 06 = espelhado em y, 03 = girado 180.
# Meio base  = 08 (x > 0, y > 0): 01 = 08 espelhado em x, 05 = espelhado em y, 04 = girado 180.
# Ficha tecnica: torres 1 e 2 terreo + 15, torre 3 terreo + 16; terreo com 7 unidades (sem o 01, que e o hall),
# demais pavimentos com 8. Total 389. Parede de concreto: pe-direito 2,50 + laje 0,10.

PD = 2.60
LAJE = 0.10
NPAV = {1: 16, 2: 16, 3: 17}          # pavimentos por torre, contando o terreo
FINAIS = 8

# ------------------------------------------------------------------ contorno do pavimento tipo
# Quadrante de cima a direita (finais 08 e 07), do eixo x = 0 ate o eixo y = 0, em sentido horario:
YS = 5.370           # fachada da suite do 08 (recuada)
XB0, XB1 = 3.329, 6.507   # bloco saliente do quarto 2 do 08
YB = 6.740           # frente do bloco
YV = 6.110           # face da varanda do 08 (laje)
XK = 10.616          # divisa 08 | 07 (lateral da varanda do 08 e parede da cozinha do 07)
YK = 5.205           # janela da area de servico do 07 (recuada)
XQ = 12.123          # inicio do bloco dos quartos do 07
YQ = 5.945           # frente do bloco dos quartos do ponta
XT = 20.068          # testa da torre
YL = 2.521           # fundo do bloco dos quartos = lateral do recuo da varanda do ponta
XV = 17.553          # face da varanda do ponta (testa recuada)

QUAD = [(0.0, YS), (XB0, YS), (XB0, YB), (XB1, YB), (XB1, YV), (XK, YV), (XK, YK), (XQ, YK), (XQ, YQ), (XT, YQ),
        (XT, YL), (XV, YL), (XV, 0.0)]


def contorno():
    """Contorno fechado anti-horario (visto de cima), sem repetir o primeiro ponto."""
    tr = QUAD                                                   # cima-direita, horario
    br = [(x, -y) for x, y in reversed(QUAD)][1:]               # baixo-direita
    bl = [(-x, -y) for x, y in QUAD][1:]                        # baixo-esquerda
    tl = [(-x, y) for x, y in reversed(QUAD)][1:-1]             # cima-esquerda (sem repetir o inicio)
    pts = tr + br + bl + tl
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-9 or abs(out[-1][1] - p[1]) > 1e-9:
            out.append(p)
    return out[::-1]


# ------------------------------------------------------------------ aberturas (referencial do 07 e do 08)
# Janelas: (plano, coordenada do plano, a0, a1, tipo). 'dorm' = veneziana 1,22 m; 'banho' = basculante 0,62 m;
# 'servico' = janela da area de servico (1,50 de cota interna, vao 1,02 m).
JANELAS_07 = [('y', YQ, 12.877, 14.093, 'dorm'), ('y', YQ, 15.076, 15.698, 'banho'),
              ('y', YQ, 16.511, 17.133, 'banho'), ('y', YQ, 18.145, 19.361, 'dorm'),
              ('y', YK, 10.926, 11.942, 'servico')]
JANELAS_08 = [('y', YB, 4.275, 5.489, 'dorm'), ('y', YS, 0.861, 2.075, 'dorm')]

# Varandas (loggias): face no plano da fachada (plano, coordenada, a0, a1), fundo com a porta de correr da sala
# (onde fica a malha "unidades") e a profundidade. Ponta: varanda na testa recuada, voltada para fora da torre,
# 1,04 m de fundo e 2,48 m de largura (divisoria de 9 cm no eixo com o vizinho). Meio: 4,11 x 1,03 m, voltada para a
# frente, com a churrasqueira na ponta junto a cozinha.
VARANDA_07 = dict(face=('x', XV, 0.045, YL), fundo=XV - 1.04)
VARANDA_08 = dict(face=('y', YV, XB1, XK), fundo=YV - 1.025)

# finais: (base, sx, sy)
TRANSF = {7: ('07', 1, 1), 2: ('07', -1, 1), 6: ('07', 1, -1), 3: ('07', -1, -1),
          8: ('08', 1, 1), 1: ('08', -1, 1), 5: ('08', 1, -1), 4: ('08', -1, -1)}
PONTAS = (2, 3, 6, 7)


def existe(torre, andar, final):
    if andar >= NPAV[torre]:
        return False
    return not (andar == 0 and final == 1)        # terreo: hall no lugar do 01


def _tseg(s, sx, sy):
    pl, c = s[0], s[1]
    if pl == 'y':
        a0, a1 = sorted((s[2] * sx, s[3] * sx))
        return ('y', c * sy, a0, a1) + tuple(s[4:])
    a0, a1 = sorted((s[2] * sy, s[3] * sy))
    return ('x', c * sx, a0, a1) + tuple(s[4:])


def aberturas(final):
    """(varanda, janelas) do final no referencial da torre. varanda: face (plano, c, a0, a1), fundo (coordenada do
    plano da porta), sinal (para fora = +1/-1 no eixo do plano)."""
    base, sx, sy = TRANSF[final]
    V, J = (VARANDA_07, JANELAS_07) if base == '07' else (VARANDA_08, JANELAS_08)
    pl, c, a0, a1 = V['face']
    face = _tseg((pl, c, a0, a1), sx, sy)
    s = sx if pl == 'x' else sy
    var = dict(face=face, fundo=V['fundo'] * s, sinal=s)
    return var, [_tseg(j, sx, sy) for j in J]


# fachada de cada unidade em planta (contorno da selecionada), no referencial da base
FACHADA_07 = [(XK, YK), (XQ, YK), (XQ, YQ), (XT, YQ), (XT, YL), (XV, YL), (XV, 0.0)]
FACHADA_08 = [(0.0, YS), (XB0, YS), (XB0, YB), (XB1, YB), (XB1, YV), (XK, YV), (XK, YK)]


def fachada(final):
    base, sx, sy = TRANSF[final]
    return [(p[0] * sx, p[1] * sy) for p in (FACHADA_07 if base == '07' else FACHADA_08)]


# ------------------------------------------------------------------ cores da fachada (perspectiva GUI_01_Fachada)
# Blocos salientes em cinza claro com a parte de baixo em cinza medio (a altura da troca varia de bloco para bloco
# na perspectiva), recuo da suite do meio em cinza medio, recuo da cozinha do ponta e o entorno das varandas em
# azul-grafite. Andar a partir do qual o bloco fica claro, por (bloco, lado x):
CLARO_DESDE = {('ponta', -1): 6, ('bloco', -1): 9, ('bloco', 1): 6, ('ponta', 1): 0}


def classe_face(a, b):
    """Classe do trecho de fachada entre a e b (pontos do contorno): 'ponta', 'bloco', 'suite', 'escuro'."""
    xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax, ay = abs(xm), abs(ym)
    horiz = abs(a[1] - b[1]) < 1e-6
    if horiz:
        if abs(ay - YQ) < 1e-6 or (abs(ay - YL) < 1e-6 and ax > XV):
            return 'ponta'
        if abs(ay - YB) < 1e-6:
            return 'bloco'
        if abs(ay - YS) < 1e-6:
            return 'suite'
        return 'escuro'                     # cozinha recuada (YK) e face da varanda (YV)
    if abs(ax - XT) < 1e-6:
        return 'ponta'
    if abs(ax - XB0) < 1e-6 or (abs(ax - XB1) < 1e-6 and ay > YV):
        return 'bloco'
    return 'escuro'                         # laterais do recuo da cozinha, da varanda e da testa recuada


# ------------------------------------------------------------------ terreo: jardins das unidades garden
# Gradil baixo (implantacao): na testa, 0,5 m a frente (x = 20,57) entre as frentes dos blocos dos quartos, com
# divisoria no eixo; embaixo, 1,46 m a frente das varandas do 04 e do 05 (y = -7,62) entre x = -9,09 e 8,71; em cima,
# o jardim do 08 ate y = 7,85 entre x = 3,33 e 8,98.
JARDIM_TESTA_X = 20.57
JARDIM_BAIXO = (-9.09, 8.71, -7.62)
JARDIM_08 = (XB0, 8.98, 7.85)
