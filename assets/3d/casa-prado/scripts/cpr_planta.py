# cpr_planta.py -- medidas do Casa Prado Residence Riva lidas no Drive do produto. So dados.
#
# IMPLANTACAO: imagem embutida na pagina 8 do book de mesa (497.43_BOOK DE MESA_30X30_V12F.pdf, 2671 x 1083 px),
# em pixels dessa imagem (x para a direita, y para baixo). Avenida Maria Emilia a oeste (esquerda), edificio-garagem
# a leste. Escala 0,0558 m/px, conferida contra a ficha tecnica e as plantas:
#   torre de ponta a ponta 39,49 m (plantas) = 745..1453 px (0,0558); fundo da torre ate a frente dos pontas 15,38 m =
#   347..622 px (0,0559); meio (finais 01/04) 12,30 m = 990..1208 px (0,0563) e a frente do 01 a 8,11 m do eixo = 630 px;
#   piscina adulto 18,78 m = 341 px; infantil 4,28 x 2,28 m = 78 x 41 px; recuos do FAQ: lateral esquerdo 15,27 m
#   (fundo da torre ate o muro norte, 275 px), lateral direito 22,68 m (frente ate o muro sul, ~410 px), frontal 12,05 m
#   (testa oeste ate a divisa, 216 px -> divisa em x = 529); vaga 2,50 m = 45 px.
# Usado pelo gerador (cpr_modelo.py e modulos) e por cpr_ver.py (sobreposicao na imagem, fora do Blender).

S_PX = 0.0558
ORIGEM_PX = (1099.0, 484.5)       # centro da torre (vira a origem da cena)

# Norte da rosa dos ventos do book: ~9 graus a leste do "para cima" da implantacao.
NORTE_GRAUS = 9.0

# Divisa do lote (muro). Frente na avenida (x = 529, gradil), muro norte levemente inclinado, a cunha a leste
# paralela a diagonal do edificio-garagem e o muro sul reto.
TERRENO = [(529, 76), (2520, 35), (2623, 104), (2073, 1035), (529, 1035)]
# grama do lote em dois poligonos (corte em x = 2050) para abrir o buraco da rampa do subsolo
GRAMA_LOTE = [[(529, 76), (2050, 44.7), (2050, 1035), (529, 1035)],
              [(2050, 44.7), (2520, 35), (2623, 104), (2073, 1035), (2050, 1035), (2050, 750), (2131, 800),
               (2250, 604), (2154, 554), (2050, 554)]]
FRENTE_X = 529
ENTRADA_Y = (800, 900)            # acesso de veiculos (portoes na linha da guarita)
PORTAO_X = 560

# ------------------------------------------------------------------ avenida (publica, fora do lote)
# Bordos inclinados: x(y) = x0 - INCL * y. Pista leste (lado do lote), canteiro central, pista oeste e a calcada.
AV_INCL = 0.134
AV_PISTA_L = (223, 350)           # x em y = 0 (bordo oeste e leste da pista do lado do lote)
AV_CANTEIRO = (100, 223)
AV_PISTA_O = (23, 100)
AV_GRAMA = (350, 395)             # faixa de grama entre o meio-fio e a calcada
AV_CALCADA = (395, 440)
# alca de embarque (baia em "D" na frente do lote, contornando uma ilha com palmeiras)
ALCA = [(272, 545), (300, 592), (340, 630), (375, 672), (398, 720), (410, 770), (430, 798), (529, 800), (529, 900),
        (430, 902), (395, 915), (355, 935), (318, 965), (290, 1000), (262, 1045), (205, 1045), (205, 545)]
ILHA = [(276, 640), (305, 660), (333, 700), (348, 760), (352, 820), (343, 875), (322, 912), (290, 935), (262, 930),
        (262, 640)]

# ------------------------------------------------------------------ torre (so posicao; a forma vem das plantas,
# em metros, em cpr_modelo.py). Eixo maior em x, frente (finais 06 01 02) para o sul (-y no Blender).
TORRE = (1099.0, 484.5)

# ------------------------------------------------------------------ chao (poligonos px, sem sobreposicao)
ASFALTO = [
    # rua interna: do portao ate o edificio-garagem
    [(529, 800), (1500, 800), (1500, 900), (529, 900)],
]
# piso do edificio-garagem (terreo; o subsolo fica embaixo, acessado pela rampa). A rampa e um recorte na borda
# diagonal: o lado leste dela fica sobre a diagonal (2453,283)-(2011,1000).
DECK = [(1566, 104), (2453, 104), (2453, 283), (2250, 604), (2154, 554), (2050, 750), (2131, 800), (2011, 1000),
        (1500, 1000), (1500, 725), (1566, 725)]
# bordas do piso da garagem com mureta (as que dao para a grama)
DECK_MURETA = [((1566, 104), (2453, 104)), ((2453, 104), (2453, 283)), ((2453, 283), (2250, 604)),
               ((2131, 800), (2011, 1000)), ((2011, 1000), (1500, 1000)), ((1566, 556), (1566, 104))]

# Fileiras de vagas: 4 cantos (a, b = frente no corredor; c, d = fundo), numero de vagas e tipo.
# FAQ: vaga M 2,50 x 4,50; PcD e carro eletrico 2,50 x 5,00 com faixa zebrada de 1,20 m.
VAGAS = [
    # descobertas, lado norte da rua (R10 a R07 PcD com as zebras, 147 a 137)
    ([(757, 800), (871, 800), (871, 712), (757, 712)], 2, 'pcd'),
    ([(871, 800), (982, 800), (982, 712), (871, 712)], 2, 'pcd'),
    ([(982, 800), (1475, 800), (1475, 712), (982, 712)], 11, 'asf'),
    # descobertas, lado sul (01 e 02 carro eletrico, R1 a R6 rotativas, 03 a 11)
    ([(727, 900), (825, 900), (825, 995), (727, 995)], 2, 'eletrica'),
    ([(825, 900), (1500, 900), (1500, 978), (825, 978)], 15, 'asf'),
    # edificio-garagem (terreo): fileira dupla 106 a 123 (A na frente, B atras) com os depositos no fundo
    ([(1572, 284), (2396, 284), (2396, 200), (1572, 200)], 18, 'deck'),
    ([(1572, 200), (2396, 200), (2396, 120), (1572, 120)], 18, 'deck'),
    # bloco 124 a 129
    ([(1572, 382), (1712, 382), (1712, 463), (1572, 463)], 3, 'deck'),
    ([(1572, 544), (1712, 544), (1712, 463), (1572, 463)], 3, 'deck'),
    # bloco 97 a 105 e 92 a 104B (a direita do nucleo de escada)
    ([(1902, 382), (2311, 382), (2311, 463), (1902, 463)], 9, 'deck'),
    ([(1902, 544), (2269, 544), (2269, 463), (1902, 463)], 8, 'deck'),
    # bloco 130 a 136
    ([(1572, 644), (1712, 644), (1712, 723), (1572, 723)], 3, 'deck'),
    ([(1528, 802), (1712, 802), (1712, 723), (1528, 723)], 4, 'deck'),
    # bloco 83 a 91
    ([(1812, 644), (2032, 644), (2032, 723), (1812, 723)], 5, 'deck'),
    ([(1812, 802), (1992, 802), (1992, 723), (1812, 723)], 4, 'deck'),
    # fileira 12 a 22 (fundo com os depositos)
    ([(1503, 902), (2008, 902), (2008, 975), (1503, 975)], 11, 'deck'),
    # motos (1,00 x 2,00 m)
    ([(2316, 382), (2355, 382), (2355, 418), (2316, 418)], 2, 'moto'),
    ([(2008, 902), (2045, 902), (2045, 938), (2008, 938)], 2, 'moto'),
    ([(2032, 644), (2068, 644), (2068, 666), (2032, 666)], 2, 'moto'),
]
# espaco para deposito (2,50 x 0,80 m) no fundo das vagas: so a faixa pintada (a obra fica por conta do morador)
DEPOSITOS = [(1572, 104, 2396, 120), (1503, 975, 2008, 998)]
BIKE = (2396, 104, 2453, 284)          # bike sharing (22) com as setas amarelas
# coberturas metalicas das vagas do terreo da garagem (perspectiva da implantacao 058)
COBERTURAS = [(1566, 104, 2453, 286), (1566, 378, 1716, 548), (1898, 378, 2315, 548), (1524, 640, 1716, 806),
              (1808, 640, 2036, 806), (1500, 898, 2049, 1000)]
NUCLEO_GARAGEM = (1812, 380, 1902, 474)   # escada e elevador para o subsolo
# rampa que desce para o subsolo: borda de cima (no deck) e borda de baixo
RAMPA = [(2050, 750), (2131, 800), (2250, 604), (2154, 554)]

# faixas de pedestre: (x0, y0, x1, y1, 'h' = listras ao longo de x empilhadas em y, 'v' = ao longo de y)
ZEBRAS = [(682, 804, 706, 896, 'h'), (382, 756, 432, 784, 'v')]

# ------------------------------------------------------------------ passeios (paver) e pracas (concreto)
PASSEIOS = [
    [(590, 262), (1500, 262), (1500, 292), (590, 292)],            # passeio norte (entre a torre e a piscina)
    [(662, 292), (692, 292), (692, 684), (662, 684)],              # passeio oeste (ao lado da quadra de areia)
    [(700, 317), (1468, 317), (1468, 347), (700, 347)],            # volta da torre: fundos
    [(700, 347), (744, 347), (744, 645), (700, 645)],              # volta da torre: testa oeste
    [(1453, 347), (1468, 347), (1468, 645), (1453, 645)],          # volta da torre: testa leste
    [(692, 645), (990, 645), (990, 684), (692, 684)],              # ligacao da praca ao hall
    [(735, 684), (1572, 684), (1572, 712), (735, 712)],            # passarela coberta ao longo das vagas
    [(990, 630), (1208, 630), (1208, 660), (990, 660)],            # varanda coberta do hall
    [(990, 660), (1020, 660), (1020, 684), (990, 684)],
    [(1545, 556), (1572, 556), (1572, 684), (1545, 684)],          # passarela que sobe para a garagem
    [(540, 640), (735, 640), (735, 800), (540, 800)],              # praca da guarita e do delivery
]
PRACAS = [
    [(529, 900), (720, 900), (720, 1010), (529, 1010)],            # abrigo de lixo e pet place
    [(1495, 96), (1566, 96), (1566, 150), (1495, 150)],            # casa de maquinas da piscina
]

# ------------------------------------------------------------------ lazer e apoio (retangulos px x0, y0, x1, y1)
PLAYGROUND = (600, 106, 741, 240)
GOURMET = (833, 110, 1033, 262)
GOURMET_DECK = (765, 106, 833, 260)       # varanda com pergolado e mesas
DECK_PISCINA = (1103, 106, 1491, 288)
PISCINA = (1150, 106, 1491, 175)
PISCINA_INFANTIL = (1126, 234, 1204, 275)
DECK_MOLHADO = (1312, 176, 1368, 222)
OFURO = (1369, 176, 1417, 222)
CASA_MAQ = (1497, 98, 1545, 146)
QUADRA = (559, 312, 662, 504)
PRACA_CHEGADA = (550, 567, 637, 625)
GUARITA = (575, 690, 645, 760)
DELIVERY = (650, 688, 735, 775)
LIXO = (540, 935, 615, 1000)
PET = (620, 925, 690, 978)
PERGOLA_PORTARIA = (556, 672, 744, 1004)  # grande pergolado metalico sobre o acesso (perspectiva da guarita)
# passarelas cobertas (estrutura escura e cobertura de vidro): retangulos px
PASSARELAS = [(735, 684, 1572, 712), (990, 630, 1208, 660), (990, 660, 1020, 684), (1545, 556, 1572, 684)]
SEBES = [
    (700, 298, 807, 317), (833, 298, 1468, 317),                  # entre o passeio norte e a volta da torre
    (1468, 298, 1495, 690),                                         # leste da torre
    (1020, 660, 1208, 684),                                         # frente do hall
    (549, 80, 567, 560),                                            # frente na avenida
    (741, 106, 765, 250), (590, 245, 760, 262),                     # playground
    (1495, 160, 1560, 300),                                         # leste da piscina
    (712, 900, 727, 1000),                                          # ao lado da vaga 01
]
ESCADA = (807, 292, 833, 322)            # escada do passeio norte para a volta da torre (degraus no desenho)

# ------------------------------------------------------------------ paisagismo (px)
IPES = [(625, 117), (599, 225), (1627, 73), (1355, 1017), (1470, 1017), (360, 215), (340, 400)]
FLORIDAS = [(1207, 655), (1300, 660), (1390, 660), (708, 717)]       # copas vermelhas na frente do 02 e no delivery
ARVORES = [
    (770, 1015, 'verde'), (1000, 1010, 'verde_clara'), (1175, 1015, 'verde'), (1385, 60, 'verde_clara'),
    (1710, 62, 'verde'), (1900, 58, 'verde_clara'), (2100, 55, 'verde'), (1600, 1020, 'verde_clara'),
    (1800, 1020, 'verde'), (2480, 300, 'verde_clara'), (2300, 650, 'verde'),
]
PALMEIRAS = [
    (1075, 170), (1092, 250), (1062, 120), (1478, 205), (1500, 262), (1281, 267), (1376, 272),
    (545, 120), (552, 330), (560, 520), (548, 600), (1468, 120),
    (320, 690), (310, 770), (305, 850), (292, 915), (402, 925), (432, 960), (360, 1000),
]
# carros parados como na implantacao (px, giro em graus no Blender: 0 = eixo ao longo de x, 90 = ao longo de y)
CARROS = [
    (1050, 758, 90), (1222, 758, 90), (1312, 758, 90), (752, 945, 90), (895, 940, 90), (985, 940, 90),
    (1300, 940, 90), (2312, 165, 90), (1640, 245, 90), (1950, 500, 90), (1690, 760, 90), (1855, 945, 90),
]
