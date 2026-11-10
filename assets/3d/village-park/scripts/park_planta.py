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
# gardens do terreo (linhas finas em volta das torres na implantacao), em metros na planta local da torre:
# muro externo, divisorias entre quintais e passagens (hall no recorte central da face -x)
GARDEN_MEIA = (9.7, 23.3)
GARDEN_DIV_Y = 11.8
# andares por torre (FAQ: T1 e T2 terreo ao 19, T3 terreo ao 18)
PAVIMENTOS = {1: 20, 2: 20, 3: 19}

# ------------------------------------------------------------------ lazer (retangulos x0, y0, x1, y1 em px)
DECK_PISCINA = (1108, 838, 1452, 1070)
# piscina adulto 20 x 7,5 m = 257 x 101 px: retangulo com floreira no meio da borda sul e prainha a leste
PISCINA = [(1164, 861, 1421, 932), (1164, 932, 1231, 962), (1352, 932, 1421, 962)]
FLOREIRA_PISCINA = (1231, 932, 1352, 962)
PISCINA_INFANTIL = (1268, 969, 1317, 1018)                       # 3,5 x 3,5 m
VESTIARIOS = (1139, 1026, 1225, 1062)
QUADRA_LAJE = (1118, 1080, 1340, 1232)
QUADRA = (1127, 1099, 1330, 1213)                                 # 16 x 9 m
BEACH = (1378, 1112, 1618, 1250)                                   # areia; quadra 18,6 x 10,6 m
PLAYGROUND = (960, 930, 1095, 1220)
BIKESHARE = (1045, 830, 1080, 910)
BLOCO_LAZER = (1035, 1275, 1470, 1390)                             # salao, brinquedoteca, academia, pub, market, cowork, beauty
CHURRASQUEIRA_T1 = (1550, 930, 1620, 1025)
DECK_CHURRASQUEIRA_T1 = (1520, 910, 1640, 1065)
CHURRASQUEIRA_T2 = (825, 1530, 900, 1610)
DECK_CHURRASQUEIRA_T2 = (790, 1480, 950, 1630)
PET = (600, 1480, 740, 1630)
CLUB_DECK = (1680, 1545, 1885, 1705)
CLUB_PISCINA = (1815, 1570, 1875, 1670)
CLUB_SALAO = (1665, 1615, 1780, 1685)

# ------------------------------------------------------------------ entrada e apoio
LIXO = (875, 392, 1040, 478)
GUARITA = (1200, 475, 1250, 530)
PORTICO = (1185, 460, 1275, 560)
PORTOES = [(1060, 478, 1185, 492), (1275, 478, 1420, 492)]
APOIO = (1545, 435, 1640, 480)
RESERVATORIOS = [(1717, 460, 25), (268, 2325, 28)]                 # (cx, cy, raio) px

# zonas onde a segmentacao nao entra (modelado a mao) e onde nao se procuram copas automaticamente
ZONAS_A_MAO = []
SEM_ARVORE_AUTO = [
    (1100, 830, 1460, 1075), BLOCO_LAZER, (1500, 900, 1650, 1075), (780, 1475, 960, 1640), (1655, 1540, 1890, 1710),
    (660, 870, 860, 1425), (1735, 870, 1935, 1425), (1030, 1540, 1580, 1735), LIXO, PORTICO, APOIO, (1665, 430, 1770, 490),
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
