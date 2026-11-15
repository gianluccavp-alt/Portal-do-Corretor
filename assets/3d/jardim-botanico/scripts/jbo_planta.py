# jbo_planta.py -- medidas do Reserva Direcional Jardim Botanico lidas no Drive do produto. So dados.
#
# IMPLANTACAO: GUI_M01_Implantacao_REV_05_00a.jpg (PLANTAS E IMPLANTACAO, 14003 x 1991 px), em pixels dessa imagem
# (x para a direita, y para baixo). Lote comprido no sentido x: edificio-garagem na ponta esquerda, Av. Guilhermina
# Cunha Coelho na direita (entrada). Escala 36,5 px/m (0,0274 m/px), conferida contra as plantas tipo (ver
# jbo_torre.py), a vaga de 2,40 m (87 px), a rua interna de 7,0 m (258 px) e a area do terreno da ficha (14.444 m2:
# lote de ~366 x 40 m).
# Usado pelo gerador (jbo_modelo.py e modulos) e por jbo_ver.py (sobreposicao na imagem, fora do Blender).

S_PX = 1 / 36.5
ORIGEM_PX = (7000.0, 1000.0)      # perto do centro do lote (vira a origem da cena)

# Norte da rosa dos ventos da implantacao: ~43 graus a direita do "para cima" da imagem.
NORTE_GRAUS = 43.0

# Centro de cada torre (as tres tem a mesma forma e nao sao giradas): meio das testas e dos blocos dos quartos.
TORRES = {1: (11436.5, 903.0), 2: (8793.5, 867.0), 3: (5275.0, 844.0)}


def topo(x):
    """Muro de cima (divisa norte), reto e levemente inclinado: y = 263 em x = 350 e 410 em x = 13000."""
    return 263.0 + 0.01162 * (x - 350.0)


Y_BAIXO = 1757.0                  # muro de baixo
X_OESTE = 300.0                   # muro da ponta do edificio-garagem
# frente na avenida: calcada publica em curva; o lote fecha no gradil da entrada
FRENTE = [(13715, topo(13715)), (13633, 627), (13520, 747), (13413, 795), (13030, 800)]
PORTAO = ((12960, 1007), (12960, 1267))      # portoes de veiculos (entrada e saida) na linha da guarita
CANTO_SE = [(12960, 1267), (13107, 1273), (13160, 1460), (13160, Y_BAIXO)]

# ------------------------------------------------------------------ rua interna e entrada
RUA_Y = (1274, 1534)              # rua interna de asfalto (o desenho do chao vem do raster; aqui so as guias)
# faixas de pedestre: (x0, y0, x1, y1, 'h' = listras ao longo de x empilhadas em y, 'v' = ao longo de y)
ZEBRAS = [(9788, 1276, 9825, 1532, 'h'), (10010, 1276, 10047, 1532, 'h'), (10235, 1276, 10275, 1532, 'h'),
          (12907, 1007, 12947, 1253, 'h')]
# faixa de pedestre diagonal na avenida, em frente a entrada: (eixo de, eixo ate, largura px)
ZEBRA_AVENIDA = ((13467, 1000), (13240, 1460), 33)

# ------------------------------------------------------------------ vagas
# Fileiras: 4 cantos (a, b = frente no corredor; c, d = fundo), numero de vagas e tipo:
#   'dren' = piso drenante (trilhos de concreto e grama), 'asf' = asfalto com faixas, 'moto', 'deck' = cobertura do
#   edificio-garagem. Vaga 2,40 x 5,0 m (implantacao).
def _fil(x0, x1, yf, yb, n, tipo):
    return ([(x0, yf), (x1, yf), (x1, yb), (x0, yb)], n, tipo)


def _col(xf, xb, y0, y1, n, tipo):
    """fileira vertical: frente no corredor em x = xf, fundo em xb"""
    return ([(xf, y0), (xf, y1), (xb, y1), (xb, y0)], n, tipo)


VAGAS = [
    # fileira de baixo, ao longo do muro sul (drenante): da garagem ate as PcD e depois da faixa de ipes ate a entrada
    _fil(1990, 9690, 1545, 1730, 89, 'dren'),
    _fil(10375, 10535, 1545, 1730, 2, 'dren'),
    _fil(11500, 12720, 1545, 1730, 14, 'dren'),
    # estacionamento oeste: quatro ilhas com duas fileiras (cara a cara) e uma fileira junto a torre 3
    _col(2096, 2276, 364, 1319, 11, 'dren'), _col(2457, 2277, 364, 1319, 11, 'dren'),
    _col(2639, 2819, 364, 1319, 11, 'dren'), _col(3000, 2820, 364, 1319, 11, 'dren'),
    _col(3181, 3362, 364, 1319, 11, 'dren'), _col(3543, 3363, 364, 1319, 11, 'dren'),
    _col(3724, 3894, 364, 1319, 11, 'dren'), _col(4064, 3895, 364, 1319, 11, 'dren'),
    _col(4228, 4395, 407, 1136, 8, 'dren'),
    _fil(4228, 4893, 1319, 1150, 8, 'dren'),
    # motos e duas vagas paralelas na frente da torre 3; motos na frente da torre 2
    _fil(4893, 5343, 1268, 1200, 12, 'moto'), _fil(5357, 5786, 1268, 1180, 2, 'asf'),
    _fil(5800, 6087, 1268, 1200, 8, 'moto'), _fil(8443, 9163, 1268, 1198, 19, 'moto'),
    # lado de cima da rua, na frente do lazer (drenante)
    _fil(6120, 7800, 1272, 1077, 19, 'dren'),
    # entrada: tres vagas ao lado da faixa de pedestres
    _col(12720, 12907, 1295, 1527, 3, 'dren'),
    # cobertura do edificio-garagem
    _fil(367, 1207, 297, 469, 10, 'deck'), _fil(1490, 1733, 297, 469, 3, 'deck'),
    _col(1911, 1740, 479, 1643, 14, 'deck'),
    _col(733, 903, 647, 1643, 12, 'deck'), _col(1073, 904, 647, 1643, 12, 'deck'),
    _col(1236, 1406, 647, 1643, 12, 'deck'), _col(1577, 1407, 647, 1643, 12, 'deck'),
    _col(567, 400, 1143, 1643, 6, 'deck'),
]
# vagas PcD e as faixas zebradas entre elas (asfalto, junto as quadras), lado de baixo e de cima da rua:
# (x0, x1, y_frente, y_fundo, pcd?)
VAGAS_PCD = [
    (9690, 9788, 1545, 1730, True), (9825, 9915, 1545, 1730, False), (9915, 10010, 1545, 1730, True),
    (10047, 10140, 1545, 1730, False), (10140, 10235, 1545, 1730, True), (10275, 10375, 1545, 1730, True),
    (9690, 9788, 1272, 1095, True), (9825, 9915, 1272, 1095, True), (9915, 10010, 1272, 1095, False),
    (10047, 10140, 1272, 1095, True), (10140, 10235, 1272, 1095, False), (10275, 10375, 1272, 1095, True),
    (10375, 10535, 1272, 1095, False),
]
ZEBRAS_PCD = [(9788, 9825), (10010, 10047), (10235, 10275)]

# ------------------------------------------------------------------ edificio-garagem (terreo + cobertura)
GARAGEM = (367, 290, 1913, 1645)
RAMPA_GARAGEM = (367, 683, 567, 1143)        # rampa da cobertura para o terreo (desce para o norte)
NUCLEO_GARAGEM = (1241, 297, 1467, 483)      # escada/elevador, bike sharing e oficina de bike (18)

# ------------------------------------------------------------------ lazer (retangulos px x0, y0, x1, y1)
ACADEMIA = (6171, 634, 6351, 953)            # 15, fechada e climatizada (telha metalica)
FITNESS = (6360, 440, 6490, 820)             # 14, fitness cross
PET = (6173, 517, 6257, 623)                 # 16
DECK_PISCINA = (6583, 441, 7229, 1031)       # 12, solarium (piso de concreto)
PISCINA = (6633, 463, 7177, 645)             # 11, adulto 14,9 x 5,0 m
PISCINA_INFANTIL = (6633, 898, 6817, 1005)   # 13, infantil 5,0 x 2,9 m
CABANAS = [(6744, 773, 6807, 850), (6991, 773, 7053, 850)]
GUARDA_SOIS = [(7080, 908, 1.0), (6990, 991, 1.0)]
ESPREGUICADEIRAS = [(x, 610) for x in (6656, 6708, 6760, 6812, 6862)] + [(x, 645) for x in (6970, 7022, 7068, 7108)]
CASA_MAQ = [(7151, 885, 7229, 950), (7044, 950, 7153, 1031)]
PLAYGROUND = (7316, 497, 7577, 710)          # 10
HAPPY_HOUR = (7633, 497, 7780, 710)          # 9, mesas sob pergolados
SALAO = (7300, 746, 7764, 997)               # 8, salao de festas
QUADRA = (9678, 485, 9928, 1015)             # 7, quadra recreativa
CHURRASQUEIRA = (10015, 593, 10150, 912)     # 6, cobertura da churrasqueira (no meio da faixa laranja)
BEACH = (10201, 478, 10484, 1015)            # 5, beach tennis / volei de praia
PRACA = (12373, 627, 12800, 973)             # 4, praca de convivencia
PERGOLA_PRACA = (12470, 838, 12700, 940)
GUARITA = (12960, 873, 13087, 993)           # 3
LIXO = (13013, 464, 13207, 740)              # abrigo de lixo e gas (telhado em duas aguas)
RESERVATORIO = (13323, 535, 110)             # cisterna redonda: centro e raio px
MEDIDORES = (13253, 671, 13360, 777)
COBERTURA_SE = (12880, 1560, 13160, 1747)    # cobertura metalica junto a entrada (motos)

# ------------------------------------------------------------------ paisagismo (px)
IPES = [  # ipes roxos
    (4050, 1707), (4386, 1729), (4736, 1721), (5100, 1736), (5450, 1729), (5786, 1736), (7524, 676),
    (7767, 583), (7787, 917), (9671, 1088), (10150, 1066), (10451, 1081), (11091, 1221), (11444, 1228),
    (11753, 1206), (10650, 1647), (10878, 1647), (11113, 1647), (11356, 1647), (11503, 1743), (11826, 1743),
    (12187, 1720), (12560, 1733), (12827, 1707), (13013, 1467), (4290, 1014), (8000, 1606), (8700, 1618),
    (5655, 1622), (2424, 584), (2424, 1278), (2964, 1572),
]
FLORIDAS = [  # copas verde-amareladas (estacionamento e lazer)
    (2293, 529), (2814, 564), (3357, 500), (3893, 543), (2286, 914), (2829, 864), (3364, 900), (3900, 921),
    (2286, 1236), (2829, 1207), (3350, 1200), (3893, 1214), (1957, 1729), (2329, 1750), (2629, 1714),
    (2993, 1700), (3364, 1714), (3707, 1707), (6327, 1037), (6687, 1037), (7060, 1063), (7420, 1043),
    (7720, 1083), (6153, 1757), (6507, 1743), (6820, 1723), (7187, 1757), (7520, 1710), (8024, 1250),
    (8207, 1250), (8391, 1235), (9229, 1228), (9413, 1228), (9568, 1250), (7847, 1713), (8200, 1700),
    (8546, 1700), (8891, 1700), (9274, 1700), (9641, 1713), (10003, 1713), (10474, 1743), (12587, 787),
    (6420, 700),
]
ARVORES = [  # copas verdes escuras (frente das torres, praca)
    (4414, 479, 'verde'), (4400, 800, 'verde_clara'), (4393, 1021, 'verde'), (4643, 486, 'verde_clara'),
    (4929, 493, 'verde'), (5193, 486, 'verde_clara'), (5443, 486, 'verde'), (4936, 1164, 'verde'),
    (5129, 1179, 'verde_clara'), (5314, 1164, 'verde'), (6133, 410, 'verde'), (8112, 537, 'verde'),
    (8399, 522, 'verde_clara'), (8751, 537, 'verde'), (8943, 522, 'verde_clara'), (9229, 537, 'verde'),
    (9516, 537, 'verde_clara'), (11032, 559, 'verde'), (11187, 537, 'verde_clara'), (11356, 515, 'verde'),
    (11613, 537, 'verde_clara'), (11760, 559, 'verde'), (11951, 596, 'verde_clara'), (12200, 527, 'verde'),
    (12673, 460, 'verde_clara'), (12860, 553, 'verde'), (12453, 687, 'verde'), (12740, 687, 'verde_clara'),
    (12427, 907, 'verde_clara'), (12747, 907, 'verde'), (12867, 800, 'verde'), (12773, 1573, 'verde'),
]
PALMEIRAS = [(7333, 377), (7460, 377), (7607, 377), (7713, 377), (6656, 817), (6887, 817), (7160, 813),
             (13000, 1333), (13067, 1413), (13147, 1467)]
