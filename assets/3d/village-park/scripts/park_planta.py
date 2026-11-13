# park_planta.py -- medidas do Village Park lidas da implantacao (assets/img/village-park/plantas/implantacao.jpg,
# 2600 x 2870 px). So dados, em pixels da imagem (x para a direita, y para baixo).
# Escala 0,0790 m/px, conferida contra o FAQ da ficha tecnica:
#   torre de ponta a ponta 42,02 m = 532 px; T1-T2 70,95 m = 896 px (70,8 m); piscina adulto 20 m = 260 px;
#   piscina infantil 3,5 m = 44 px; piscina do Village Club 8,7 x 4,7 m = 100 x 60 px.
# Usado por park_mapa.py (segmentacao do chao, fora do Blender) e pelo gerador (park_modelo.py e modulos).

S_PX = 0.0790
ORIGEM_PX = (1296.0, 1486.0)      # centro do terreno (vira a origem da cena)

# Terreno (muro de divisa) e a avenida em frente
TERRENO = [(190, 396), (2402, 396), (2402, 2578), (190, 2420)]
AVENIDA = (30, 176, 2570, 396)

# Torres: centro (px) e giro (graus, anti-horario visto de cima) da planta local.
# Planta local: eixo maior em y, finais 3 a 6 na face +x, 7, 8, 1 e 2 na face -x (como a torre 2 na implantacao).
TORRES = {
    1: ((1833.0, 1147.5), 180.0),
    2: ((759.0, 1147.5), 0.0),
    3: ((1303.0, 1636.0), -90.0),
}
# gardens do terreo (linhas finas em volta das torres na implantacao): meia largura e meio comprimento do muro
# externo, em metros na planta local da torre. As divisorias seguem a torre (park_patio.jardins_torres).
GARDEN_MEIA = (9.75, 23.4)
# andares por torre (FAQ: T1 e T2 terreo ao 19, T3 terreo ao 18)
PAVIMENTOS = {1: 20, 2: 20, 3: 19}

# ------------------------------------------------------------------ lazer (retangulos x0, y0, x1, y1 em px)
DECK_PISCINA = (1121, 850, 1467, 1066)                            # porcelanato dentro da cerca viva
SEBE_PISCINA = (1111, 840, 1477, 1078)                            # cerca viva em volta do deck (aberta a leste e oeste)
ENTRADAS_PISCINA = [(1098, 963, 1131, 986), (1462, 963, 1487, 987)]
FLOREIRA_TOPO_PISCINA = (1130, 850, 1463, 862)                    # canteiro florido entre a cerca e a piscina
# piscina adulto 20 x 7,5 m = 257 x 101 px: retangulo com floreira no meio da borda sul e prainha a leste
PISCINA = [(1164, 861, 1421, 932), (1164, 932, 1231, 962), (1352, 932, 1421, 962)]
FLOREIRA_PISCINA = (1231, 932, 1352, 962)
PISCINA_INFANTIL = (1268, 969, 1317, 1018)                       # 3,5 x 3,5 m
VESTIARIOS = (1139, 1026, 1225, 1062)
QUADRA_LAJE = (1120, 1084, 1340, 1213)
QUADRA = (1127, 1099, 1330, 1200)                                 # 16 x 9 m (o desenho tem 16 x 8)
BEACH = (1387, 1118, 1623, 1253)                                   # areia; quadra 18,6 x 10,6 m
PLAYGROUND = (960, 930, 1095, 1220)
BIKESHARE = (1045, 830, 1080, 910)
BLOCO_LAZER = (1038, 1288, 1470, 1393)                             # 34,1 x 8,3 m
# salas do bloco (x0, x1 em px; o bloco inteiro de 1288 a 1393 em y, salvo as quatro salas do fim)
SALAO_X, BRINQ_X, ACADEMIA_X = (1038, 1200), (1200, 1255), (1255, 1362)
SALAO_WC = (1038, 1328, 1092, 1393)
FIM_X, FIM_XM, FIM_YM = (1362, 1470), 1416, 1340                   # pub | cowork em cima, beauty | market embaixo
CHURRASQUEIRA_T1 = (1550, 932, 1614, 1024)                         # 2 salas (norte e sul) + WC a oeste
DECK_CHURRASQUEIRA_T1 = (1505, 908, 1635, 1077)                    # laje de concreto em volta
DECKS_T1 = [(1520, 912, 1566, 968), (1550, 1030, 1615, 1075)]      # decks de madeira com mesas
CHURRASQUEIRA_T2 = (830, 1507, 895, 1602)
DECK_CHURRASQUEIRA_T2 = (790, 1480, 950, 1630)
DECKS_T2 = [(795, 1487, 845, 1537), (900, 1562, 943, 1625)]
PET = (600, 1480, 740, 1630)
CLUB_DECK = (1680, 1545, 1885, 1705)
CLUB_PISCINA = (1815, 1570, 1875, 1670)
CLUB_SALAO = (1671, 1615, 1782, 1680)
CLUB_PERGOLA = (1680, 1597, 1780, 1615)
CROSSFIT = (1495, 1265, 1622, 1377)
DECKS_SUL = [(1063, 1230, 1192, 1265), (1320, 1230, 1343, 1265)]   # decks de madeira entre a quadra e o bloco
DECK_PIQUENIQUE = (1470, 1060, 1520, 1078)                        # deck com a arvore branca, junto da areia
# caminhos do lazer (passeio levantado), desenhados a mao: o resto da zona e grama
CAMINHOS_LAZER = [
    (1098, 822, 1111, 1265),       # oeste do bloco da piscina e da quadra
    (1487, 822, 1505, 1078),       # leste da piscina, ate a churrasqueira
    (1340, 1078, 1505, 1098),      # entre a piscina e a areia
    (1343, 1098, 1370, 1265),      # entre a quadra e a areia
    (1013, 1265, 1530, 1288),      # frente do bloco de salas
    (1013, 1288, 1038, 1405),      # lateral oeste do bloco
    (1473, 1288, 1495, 1405),      # lateral leste do bloco, ate o crossfit
    (1038, 1393, 1473, 1405),      # fundo do bloco
]
# cercas vivas e canteiros (sebe baixa) e palmeiras do lazer, lidos da implantacao
SEBES = [
    (1111, 840, 1477, 850), (1111, 1066, 1477, 1078), (1111, 850, 1121, 963), (1111, 986, 1121, 1066),
    (1467, 850, 1477, 963), (1467, 987, 1477, 1066),
    (1508, 927, 1517, 975), (1508, 1018, 1517, 1060),
]
PALMEIRAS = [
    (1162, 833), (1260, 833), (1343, 833), (1435, 833), (1105, 907), (1105, 950), (1104, 1012), (1482, 907),
    (1482, 953), (1482, 1010), (1250, 945), (1290, 945), (1330, 945), (1172, 993), (1223, 993), (1363, 992),
    (1417, 992), (1260, 1063), (1313, 1060), (1393, 1060),
    (1105, 1090), (1105, 1145), (1105, 1195), (1352, 1110), (1352, 1160), (1352, 1210),
    (1380, 1110), (1380, 1175), (1380, 1240), (1630, 1125), (1630, 1180), (1630, 1235),
    (1415, 1257), (1460, 1257), (1510, 1257), (1555, 1257), (1600, 1257), (1410, 1100), (1460, 1100), (1545, 1100), (1597, 1100),
    (1545, 1385), (1590, 1385),
]

# ------------------------------------------------------------------ entrada e apoio
LIXO = (875, 392, 1040, 478)
GUARITA = (1200, 475, 1250, 530)
PORTICO = (1185, 460, 1275, 560)
PORTOES = [(1060, 478, 1185, 492), (1275, 478, 1420, 492)]
APOIO = (1545, 435, 1640, 480)
RESERVATORIOS = [(1717, 460, 25), (268, 2325, 28)]                 # (cx, cy, raio) px

# zonas onde a segmentacao nao entra (modelado a mao) e onde nao se procuram copas automaticamente
ZONAS_A_MAO = [(1098, 822, 1645, 1265), (1005, 1265, 1645, 1405)]   # lazer: chao a mao (park_lazer.chao_lazer)
SEM_ARVORE_AUTO = [
    (1100, 830, 1460, 1075), BLOCO_LAZER, (1500, 900, 1650, 1075), (780, 1475, 960, 1640), (1655, 1540, 1890, 1710),
    (660, 870, 860, 1425), (1735, 870, 1935, 1425), (1030, 1540, 1580, 1735), LIXO, PORTICO, APOIO, (1665, 430, 1770, 490),
    (962, 932, 1094, 1130), (1040, 828, 1084, 912),          # brinquedos do playground e bikeshare (cores parecem copas)
]

# ------------------------------------------------------------------ carros desenhados na implantacao (px, giro)
# giro 0 = eixo do carro na horizontal da planta (fileiras verticais), 90 = na vertical
_C2 = 2   # lidos na imagem a meia escala
_H = [(160, 305), (128, 365), (133, 428), (133, 535), (128, 640), (135, 743), (130, 897), (130, 925),
      (272, 449), (272, 682), (270, 742), (1025, 425), (1045, 483), (1048, 655), (1048, 768),
      (1150, 390), (1160, 433), (1160, 480), (1125, 858), (1150, 920), (1150, 980), (1145, 1100), (1150, 1195)]
_V = [(232, 270), (272, 245), (320, 245), (445, 280), (498, 280), (850, 270), (915, 245), (990, 245), (1065, 270),
      (278, 385), (357, 352), (433, 352), (433, 388), (755, 352), (770, 352), (722, 385), (785, 385), (875, 352),
      (920, 385), (965, 385), (335, 880), (345, 1030), (402, 1060), (345, 1150), (460, 1160), (785, 985),
      (807, 1060), (750, 1085), (880, 1160), (820, 1185), (985, 925)]
CARROS = [(x * _C2, y * _C2, 0) for x, y in _H] + [(x * _C2, y * _C2, 90) for x, y in _V]

# frente do condominio (gradil na divisa com a avenida), fora do acesso de veiculos e do deposito de lixo
FRENTE_GRADIL = [(194, 875), (1460, 2402)]
