# park_chao_mao.py -- chao do Village Park desenhado a mao (px da implantacao, x para a direita, y para baixo).
# Substitui a segmentacao por cor, que confundia a vaga clara com calcada e contornava as copas e os carros
# (manchas e guias tortas). Aqui o chao e feito de poligonos limpos:
#   ASFALTO   pista, corredores e fileiras de vagas      (menos os CANTEIROS, ilhas de grama dentro do asfalto)
#   PASSEIO   calcadas levantadas (tem prioridade sobre o asfalto)
#   grama     todo o resto do terreno (fora das zonas do lazer, que sao modeladas a mao)
# e as faixas pintadas saem de FILEIRAS (retangulo + orientacao): o passo e a fase das divisorias sao medidos no
# proprio desenho e as linhas cobrem a fileira inteira, sem buracos embaixo de carro ou copa.
#
# Dois referenciais:
#   'img' : px da imagem
#   'L'   : o estacionamento sul, a torre 3 e o miolo atras dela estao girados ~4 graus no desenho. Em L, u corre ao
#           longo das fileiras (para leste) e v para o sul: (x, y) = ORIGEM_L + u * (cos, sen) + v * (-sen, cos).
# Lido por park_mapa.py (venv com numpy, pillow e shapely).
import math

INCL_L = 0.0694                        # inclinacao das fileiras do sul (dy/dx), medida em linhas de 1,3 km de vaga
ORIGEM_L = (460.0, 1858.0)             # linha norte da primeira quadra de vagas do sul, na ponta oeste
_T = math.atan(INCL_L)
_C, _S = math.cos(_T), math.sin(_T)


def L(u, v):
    return (ORIGEM_L[0] + u * _C - v * _S, ORIGEM_L[1] + u * _S + v * _C)


def L_inv(x, y):
    dx, dy = x - ORIGEM_L[0], y - ORIGEM_L[1]
    return (dx * _C + dy * _S, -dx * _S + dy * _C)


# ------------------------------------------------------------------ formas (cada uma vira poligono no build)
# ('r', x0, y0, x1, y1)              retangulo
# ('rr', x0, y0, x1, y1, raio)       retangulo de cantos arredondados (canteiro com ponta redonda)
# ('q', x0, y0, x1, y1, cx, cy, r)   retangulo cortado por um disco (ilha de canto em quarto de circulo)
# ('arco', cx, cy, r0, r1, poli)     coroa circular (r0 = 0: disco) recortada pelo poligono
# ('p', [(x, y), ...])               poligono qualquer
# Prefixo 'L' no referencial: a forma e montada em (u, v) e girada para a imagem.

ASFALTO = [
    ('img', ('r', 30, 228, 2570, 341)),                 # avenida (o resto dela vem de park_patio.avenida)
    ('img', ('r', 1050, 341, 1410, 600)),               # acesso de veiculos (menos as ilhas e os arcos)
    ('img', ('r', 241, 420, 460, 2352)),                # coluna de vagas oeste e corredor
    ('img', ('r', 241, 420, 430, 600)),
    ('img', ('r', 430, 432, 489, 600)),
    ('img', ('r', 489, 520, 505, 600)),
    ('img', ('r', 505, 455, 866, 600)),
    ('img', ('r', 866, 512, 1050, 600)),
    ('img', ('r', 1410, 518, 1805, 600)),
    ('img', ('r', 1805, 463, 2022, 600)),
    ('img', ('r', 2022, 520, 2042, 600)),
    ('img', ('r', 2042, 432, 2326, 600)),
    ('img', ('r', 241, 583, 2326, 680)),                # corredor norte
    ('img', ('r', 455, 680, 2137, 806)),                # fileira em frente as torres 1 e 2
    ('img', ('r', 455, 806, 576, 1710)),                # coluna junto da torre 2
    ('img', ('r', 2016, 806, 2133, 1770)),              # coluna junto da torre 1
    ('img', ('r', 2133, 432, 2326, 2450)),              # corredor e coluna leste
    ('img', ('r', 2016, 1700, 2219, 2450)),             # canto sudeste (encontro com as quadras giradas)
    ('L', ('r', -5, -85, 1725, 468)),                   # quadras do sul e corredores
    ('L', ('r', 89, -165, 440, -85)),                   # vagas PCD atras da churrasqueira T2
    ('L', ('r', 440, -110, 1102, -85)),                 # motos atras da torre 3
    ('L', ('r', 1102, -205, 1600, -85)),                # quadra a leste da torre 3
]

CANTEIROS = [
    # norte
    ('img', ('rr', 430, 521, 444, 590, 7)),
    ('img', ('rr', 688, 440, 700, 589, 6)),
    ('img', ('rr', 853, 440, 866, 586, 6)),
    ('img', ('rr', 940, 505, 953, 590, 6)),
    ('img', ('rr', 1487, 505, 1501, 589, 7)),
    ('img', ('rr', 1805, 440, 1817, 589, 6)),
    ('img', ('rr', 2147, 505, 2160, 590, 6)),
    ('img', ('rr', 1166, 330, 1296, 578, 40)),          # ilha da portaria (o porte fica sobre ela)
    # fileira em frente as torres
    ('img', ('q', 455, 680, 526, 755, 526, 755, 75)),   # ilha noroeste (copa branca)
    ('img', ('q', 2066, 680, 2137, 755, 2066, 755, 75)),
    ('img', ('r', 1208, 690, 1248, 806)),               # canteiro das palmeiras no eixo da portaria
    # coluna junto da torre 2
    ('img', ('rr', 452, 842, 640, 855, 6)),
    ('img', ('rr', 452, 1182, 640, 1195, 6)),
    ('img', ('q', 455, 1700, 527, 1756, 527, 1700, 72)),
    # coluna junto da torre 1
    ('img', ('rr', 1990, 1068, 2142, 1080, 6)),
    ('img', ('r', 1984, 1080, 2053, 1287)),            # gramado ao lado das vagas PCD
    # sul (referencial girado)
    ('L', ('q', -10, -5, 65, 65, 65, 65, 70)),         # ilha noroeste da 1a quadra
    ('L', ('rr', -5, 150, 15, 268, 8)),                # ponta oeste da 2a fileira
    ('L', ('rr', -8, 349, 8, 466, 7)),                 # ponta oeste da fileira junto do muro
    ('L', ('r', 65, 120, 880, 153)),                   # canteiro central da 1a quadra (com as copas)
    ('L', ('r', 880, 140, 1690, 153)),
    ('L', ('rr', 419, -5, 432, 125, 6)),               # canteiros norte-sul no meio da quadra
    ('L', ('rr', 436, 148, 450, 272, 6)),
    ('L', ('q', 1600, -5, 1690, 30, 1600, 95, 95)),    # ilha nordeste da 1a quadra
    ('L', ('rr', 1600, 30, 1625, 150, 6)),
    ('L', ('rr', 1690, 148, 1705, 268, 7)),
    ('L', ('rr', 1725, 349, 1737, 466, 6)),
    ('L', ('rr', 1250, -215, 1258, -92, 4)),           # canteiro da quadra a leste da torre 3
    ('L', ('q', 1585, -215, 1660, -100, 1585, -100, 85)),   # ilha com as copas brancas
]

# portaria: arcos das calcadas que entram do passeio da avenida; dentro deles, grama
_BOX_O = [(1000, 330), (1100, 330), (1100, 575), (1041, 575), (1041, 495), (1000, 495)]
_BOX_L = [(2 * 1231 - x, y) for x, y in _BOX_O]
ARCOS = [((944, 480), _BOX_O), ((1518, 480), _BOX_L)]
R_ARCO = (126, 140)

PASSEIO = [
    ('img', ('r', 30, 177, 2570, 228)),                 # calcada do outro lado da avenida
    ('img', ('r', 30, 341, 1000, 394)),                 # calcada do condominio
    ('img', ('r', 1462, 341, 2570, 394)),
    ('img', ('arco', 944, 480, 126, 140, _BOX_O)),
    ('img', ('arco', 1518, 480, 126, 140, _BOX_L)),
    ('img', ('r', 866, 492, 1050, 512)),                # calcada junto das vagas da portaria
    ('img', ('r', 1454, 493, 1805, 502)),
    ('img', ('r', 1532, 421, 1657, 502)),               # patio do apoio
    ('img', ('r', 1673, 434, 1760, 490)),               # reservatorio norte
    ('img', ('r', 205, 2263, 305, 2388)),               # reservatorio sul
    # miolo: calcadas em volta das torres e do lazer
    ('img', ('r', 608, 806, 1098, 818)),
    ('img', ('r', 1645, 806, 1984, 818)),
    ('img', ('r', 608, 806, 615, 1470)),
    ('img', ('r', 1977, 806, 1984, 1470)),
    ('img', ('r', 522, 975, 540, 1180)),                # passagens das vagas PCD
    ('img', ('r', 2053, 1080, 2070, 1287)),
    ('img', ('r', 522, 1157, 676, 1180)),               # caminho da coluna oeste ate a torre 2
    ('img', ('r', 1916, 1265, 2070, 1288)),             # caminho da coluna leste ate a torre 1
    ('img', ('r', 608, 1452, 1005, 1470)),              # calcada ao sul das torres 1, 2 e do lazer
    ('img', ('r', 1645, 1452, 1984, 1470)),
    ('img', ('r', 960, 1470, 972, 1700)),
    ('img', ('r', 1620, 1470, 1632, 1540)),
]

# faixas de pedestre: (referencial, retangulo, direcao das listras 'x' ou 'y' no referencial)
ZEBRAS = [
    ('img', (1222, 585, 1242, 662), 'y'),
    ('img', (1077, 540, 1162, 556), 'x'),
    ('img', (1300, 540, 1385, 556), 'x'),
    ('img', (372, 1085, 452, 1097), 'x'),
    ('img', (2136, 1200, 2216, 1213), 'x'),
    ('L', (426, -75, 440, -12), 'y'),
    ('L', (434, 280, 448, 345), 'y'),
]

# fileiras de vagas: (referencial, retangulo, eixo das divisorias, passo min, passo max)
#   eixo 'v': divisorias verticais no referencial (a fileira corre em x/u); 'h': horizontais (corre em y/v)
#   As linhas paralelas a fileira (fundo, meio, frente) sao achadas no desenho.
FILEIRAS = [
    ('img', (243, 420, 363, 2265), 'h', 27, 33),        # coluna oeste
    ('img', (2219, 432, 2326, 2448), 'h', 27, 33),      # coluna leste
    ('img', (430, 432, 488, 512), 'h', 26, 34),
    ('img', (2042, 432, 2160, 512), 'h', 26, 34),
    ('img', (505, 455, 688, 520), 'v', 27, 33),
    ('img', (505, 520, 688, 583), 'v', 27, 33),
    ('img', (700, 455, 853, 520), 'v', 27, 33),
    ('img', (700, 520, 853, 583), 'v', 27, 33),
    ('img', (866, 520, 940, 583), 'v', 26, 34),
    ('img', (1454, 520, 1487, 583), 'v', 27, 34),
    ('img', (1501, 520, 1805, 583), 'v', 27, 33),
    ('img', (1817, 463, 2022, 520), 'v', 27, 33),
    ('img', (1817, 520, 2022, 583), 'v', 27, 33),
    ('img', (2022, 520, 2147, 583), 'v', 27, 33),
    ('img', (548, 680, 1208, 806), 'v', 27, 33),        # em frente a torre 2
    ('img', (1248, 680, 1980, 806), 'v', 27, 33),       # em frente a torre 1
    ('img', (460, 855, 576, 975), 'h', 27, 33),         # coluna junto da torre 2
    ('img', (460, 975, 522, 1182), 'h', 34, 46),        # PCD
    ('img', (460, 1195, 576, 1700), 'h', 27, 33),
    ('img', (2016, 806, 2133, 1068), 'h', 27, 33),      # coluna junto da torre 1
    ('img', (2070, 1080, 2133, 1287), 'h', 34, 46),     # PCD
    ('img', (2016, 1288, 2133, 1760), 'h', 27, 33),
    ('L', (73, 0, 419, 59), 'v', 29, 33),               # 1a quadra do sul (fileira dupla, meio em v = 59 / 69)
    ('L', (73, 59, 419, 120), 'v', 29, 33),
    ('L', (432, 0, 880, 59), 'v', 29, 33),
    ('L', (432, 59, 880, 120), 'v', 29, 33),
    ('L', (880, 0, 1600, 69), 'v', 29, 33),
    ('L', (880, 69, 1600, 139), 'v', 29, 33),
    ('L', (15, 153, 436, 213), 'v', 29, 33),            # 2a fileira dupla
    ('L', (15, 213, 436, 272), 'v', 29, 33),
    ('L', (450, 153, 1690, 213), 'v', 29, 33),
    ('L', (450, 213, 1690, 272), 'v', 29, 33),
    ('L', (8, 349, 1725, 408), 'v', 29, 33),            # fileira junto do muro sul
    ('L', (8, 408, 1725, 468), 'v', 29, 33),
    ('L', (5, 65, 65, 125), 'h', 27, 34),
    ('L', (1625, 30, 1690, 150), 'h', 27, 34),
    ('L', (89, -165, 426, -85), 'v', 34, 50),           # PCD atras da churrasqueira T2
    ('L', (440, -110, 1102, -85), 'v', 10, 15),         # motos
    ('L', (1102, -205, 1250, -85), 'v', 29, 33),       # quadra a leste da torre 3 (fileira dupla)
    ('L', (1258, -205, 1600, -85), 'v', 29, 33),
]
