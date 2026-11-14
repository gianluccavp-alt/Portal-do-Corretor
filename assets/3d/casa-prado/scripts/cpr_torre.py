# cpr_torre.py -- forma da torre do Casa Prado em metros, lida nas plantas de contrato do Drive
# (PLANTAS / Tipo, Garden e Coberturas: "06. Anexo VI - Planta - TORRE 1 - ...png", 2339 x 1654 px).
# So dados e funcoes puras (sem bpy): usado por cpr_modelo.py (Blender) e cpr_ver.py (conferencia na implantacao).
#
# Escala das plantas: escala grafica 100..400 cm = 140..376 px -> 78,67 px/m; confere com as cotas (quarto 1 470,
# sala 744, varanda 480 x 323). Paredes de concreto de 12 cm. Medidas por perfil de cor das paredes (cinza 88..90).
#
# Referencial local da torre: x ao longo do eixo maior (+x = testa leste, finais 02 e 03), v para a FRENTE (+v = sul,
# finais 06 01 02, "acesso no terreo" no mapa chave). No Blender: (x, y) = (cx + x, cy - v).
# Mapa chave do pavimento:   05 04 03   (fundos, norte)
#                            06 01 02   (frente, sul)
# Os pontas sao simetricos: 06 = 02 espelhado em x, 03 = 02 espelhado em v, 05 = 02 girado 180 graus. O meio 04 e o
# 01 girado 180 graus (a planta do 04 confere). Pavimentos: terreo (gardens 02 e 06; o resto e hall e lazer),
# 1o ao 16o tipo (6 por andar), 17o cobertura (so os pontas 02, 03, 05, 06; no lugar do 01 e do 04 ficam os
# terracos descobertos das coberturas). FAQ: pe-direito 2,50 m, laje 12 cm -> 2,62 m piso a piso.

PD = 2.62
LAJE = 0.12
NPAV = 18                 # terreo + 17
ANDAR_COB = 17

# ------------------------------------------------------------------ contorno do pavimento tipo (x, v), anti-horario
# no Blender (frente da esquerda para a direita, fundos da direita para a esquerda).
# Ponta 02 (F2): parede do 01 em x = 6,03; frente 7,605; corpo ate 17,72; saliencia do quarto 1 ate a testa 19,745
# entre v = 1,45 e 5,14; area tecnica (brise) em x = 18,16 entre o eixo e v = 1,45 (recorte aberto na testa).
# Meio 01 (F1): 12,30 m centrado (x -6,17..6,17), frente 8,113 (0,51 m a frente dos pontas) ate x = 3,55; dali ate 6,03
# a area tecnica do 01 com brise no plano dos pontas (v = 7,605).
XT, XB, XC = 19.745, 17.72, 18.16       # testa, corpo do ponta, brise da testa
VB0, VB1 = 1.45, 5.14                   # saliencia do quarto 1 do ponta
VF, VM = 7.605, 8.113                   # frente dos pontas e do meio
XM0, XM1 = -6.17, 3.55                  # frente saliente do meio 01
XD = 6.03                               # divisa meio | ponta

_FRENTE = [(-XC, 0.0), (-XC, VB0), (-XT, VB0), (-XT, VB1), (-XB, VB1), (-XB, VF), (XM0, VF), (XM0, VM), (XM1, VM),
           (XM1, VF), (XB, VF), (XB, VB1), (XT, VB1), (XT, VB0), (XC, VB0), (XC, 0.0)]


def _rot(p):
    return (-p[0], -p[1])


def _ev(p):
    return (p[0], -p[1])


def contorno_tipo():
    """Contorno fechado (lista de (x, v)), sem repetir o primeiro ponto."""
    fr = _FRENTE[:-1]
    fundo = [_rot(p) for p in _FRENTE[:-1]]       # fundos = frente girada 180 (04 = 01 girado; pontas simetricos)
    return fr + fundo


# 17o pavimento: sem o 01 e o 04 (terracos descobertos das coberturas 172/176 e 173/175). Fica o nucleo e o hall.
# Limites do 01 (F1): bloco esquerdo x -6,17..-1,75 desde v = 1,364; recorte do hall x -1,75..3,43 desde v = 3,258;
# bloco direito x 3,43..6,17 desde v = 1,669.
V01_E, V01_N, V01_D = 1.364, 3.258, 1.669
X01_N0, X01_N1 = -1.75, 3.43
_FRENTE17 = [(-XC, 0.0), (-XC, VB0), (-XT, VB0), (-XT, VB1), (-XB, VB1), (-XB, VF), (-XD, VF), (-XD, V01_E),
             (X01_N0, V01_E), (X01_N0, V01_N), (X01_N1, V01_N), (X01_N1, V01_D), (XD, V01_D), (XD, VF), (XB, VF),
             (XB, VB1), (XT, VB1), (XT, VB0), (XC, VB0), (XC, 0.0)]


def contorno_cobertura():
    fr = _FRENTE17[:-1]
    return fr + [_rot(p) for p in _FRENTE17[:-1]]


def terraco_01():
    """Planta do 01 (frente) = terraco descoberto no 17o; o do 04 e este girado 180 graus."""
    return [(XM0, V01_E), (X01_N0, V01_E), (X01_N0, V01_N), (X01_N1, V01_N), (X01_N1, V01_D), (6.17, V01_D),
            (6.17, VF), (XM1, VF), (XM1, VM), (XM0, VM)]


# ------------------------------------------------------------------ aberturas por unidade (referencial do 02 e do 01)
# Varanda (loggia): abertura no plano da fachada (a0, a1 em x), fundo com a porta de correr da sala (onde vai a
# malha "unidades") e, no ponta, a porta da area de servico mais a frente. Guarda-corpo: parede de concreto 0,78 m +
# vidro 0,32 m (planta). Janelas: (plano, coordenada, a0, a1, tipo). 'dorm' = persiana embutida, 'banho' = basculante.
VARANDA_02 = dict(face=('v', VF), a=(6.72, 10.97),
                  fundos=[('v', 5.69, 6.72, 8.23, 'servico'), ('x', 8.23, 4.19, 5.69, None), ('v', 4.19, 8.23, 10.97, 'sala')],
                  lados=[('x', 6.72, 5.69, VF), ('x', 10.97, 4.19, VF)])
JANELAS_02 = [('v', VF, 11.81, 13.00, 'dorm'), ('v', VF, 13.82, 14.39, 'banho'), ('v', VF, 15.86, 17.05, 'dorm'),
              ('v', VB1, 17.88, 19.48, 'dorm')]
# brise: (plano, coordenada da face, a0, a1, profundidade do recesso para dentro)
BRISES_02 = [('x', XC, 0.0, VB0, 1.22)]

VARANDA_01 = dict(face=('v', VM), a=(-5.52, -1.86),
                  fundos=[('v', 6.575, -5.52, -1.86, 'sala')],
                  lados=[('x', -5.52, 6.575, VM), ('x', -1.86, 6.575, VM)])
JANELAS_01 = [('v', VM, -0.98, 0.22, 'dorm'), ('v', VM, 1.02, 1.59, 'banho'), ('v', VM, 2.50, 3.12, 'banho')]
BRISES_01 = [('v', VF, XM1, XD, 0.83)]

# transformacao de cada final a partir da base (02 ou 01): (base, sx, sv)
FINAIS = {2: ('02', 1, 1), 6: ('02', -1, 1), 3: ('02', 1, -1), 5: ('02', -1, -1), 1: ('01', 1, 1), 4: ('01', -1, -1)}
FRENTE_FINAIS = (6, 1, 2)
EXISTE = {0: (2, 6), ANDAR_COB: (2, 3, 5, 6)}          # demais andares: todos os 6


def existe(andar, final):
    return final in EXISTE.get(andar, (1, 2, 3, 4, 5, 6))


def _tp(p, sx, sv):
    return (p[0] * sx, p[1] * sv)


def _tseg(s, sx, sv):
    """Transforma uma abertura (plano, c, a0, a1, ...) pelo espelhamento (sx, sv)."""
    pl, c = s[0], s[1]
    if pl == 'v':
        a0, a1 = sorted((s[2] * sx, s[3] * sx))
        return ('v', c * sv, a0, a1) + tuple(s[4:])
    a0, a1 = sorted((s[2] * sv, s[3] * sv))
    return ('x', c * sx, a0, a1) + tuple(s[4:])


def aberturas(final):
    """Varanda, janelas e brises do final, ja no referencial da torre."""
    base, sx, sv = FINAIS[final]
    V, J, B = (VARANDA_02, JANELAS_02, BRISES_02) if base == '02' else (VARANDA_01, JANELAS_01, BRISES_01)
    pl, c = V['face']
    a0, a1 = sorted((V['a'][0] * sx, V['a'][1] * sx))
    var = dict(face=(pl, c * sv), a=(a0, a1), sinal=sv,
               fundos=[_tseg(f, sx, sv) for f in V['fundos']],
               lados=[_tseg(l, sx, sv) for l in V['lados']])
    return var, [_tseg(j, sx, sv) for j in J], [(_tseg(b, sx, sv), b[4]) for b in B]


# fachada de cada unidade em planta (para o contorno da selecionada), no referencial da base
FACHADA_02 = [(XD, VF), (XB, VF), (XB, VB1), (XT, VB1), (XT, VB0), (XC, VB0), (XC, 0.0)]
FACHADA_01 = [(XM0, VF), (XM0, VM), (XM1, VM), (XM1, VF), (XD, VF)]


def fachada(final):
    base, sx, sv = FINAIS[final]
    pts = [_tp(p, sx, sv) for p in (FACHADA_02 if base == '02' else FACHADA_01)]
    return pts


# ------------------------------------------------------------------ terreo
# Gardens 02 e 06 (planta Garden): terraco descoberto + jardim ate o fechamento de 1,80 m, 1,47 m a frente da
# fachada (v = 9,07) e contornando a saliencia ate x = 19,59.
GARDEN_V = 9.07
GARDEN_X = 19.59
# hall (19) e mini market (20) na frente do meio; lazer (12 a 18) nos fundos, no lugar do 03, 04 e 05
