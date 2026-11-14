# avm_planta.py -- medidas do Alta Vista Mangara lidas da implantacao (adesivo de implantacao do Drive,
# 4724 x 2362 px; no repo: assets/img/alta-vista/plantas/implantacao.jpg, a mesma imagem em 3840 x 1920).
# So dados, em pixels da imagem de 4724 px (x para a direita, y para baixo).
# Escala 0,05288 m/px, conferida contra o FAQ da ficha tecnica:
#   torre de ponta a ponta 37,70 m = 713 px; T1-T2 20,45 m = 387 px (20,46 m);
#   vaga M 2,50 x 4,50 m: fileira do deck com 43 vagas em 2051 px (2,52 m) e 90 px de fundo (4,76 m com as faixas).
# Usado pelo gerador (avm_modelo.py e modulos) e por avm_ver.py (sobreposicao na imagem, fora do Blender).

S_PX = 0.05288
ORIGEM_PX = (1615.0, 1170.0)      # centro do terreno (vira a origem da cena)
IMG_REPO = 3840 / 4724            # px desta planta -> px de assets/img/alta-vista/plantas/implantacao.jpg

# Muro de divisa: Rua Joao Francisco Lisboa a oeste, Av. Graca Aranha na diagonal sul, Rua 2 a leste e o lote
# vizinho ao norte. A calcada fica entre o muro e o meio-fio (~4 m na avenida, ~5 m na Rua 2).
TERRENO = [
    (330, 398), (2900, 398), (2900, 1700), (2898, 1810), (2880, 1880), (2845, 1925), (2790, 1942),
    (470, 1195), (430, 1170), (380, 1128), (345, 1070), (330, 1000),
]
# meio-fio das ruas (lado do lote), na mesma ordem de cima para baixo
MEIO_FIO = [
    (255, 330), (255, 1090), (285, 1190), (360, 1258), (500, 1283), (2780, 2022), (2860, 2010), (2940, 1980),
    (2985, 1930), (3005, 1850), (3005, 330),
]
LARGURA_RUA_M = {'jfl': 10.0, 'graca_aranha': 14.0, 'rua2': 12.0}

# Torres: centro (px). Planta local: eixo maior em x; face +y (para cima na imagem) com os finais 6, 5, 4 e 3
# (da esquerda para a direita), face -y com 7, 8, 1 e 2. As duas torres sem giro em relacao a imagem.
TORRES = {
    1: (2162.0, 923.0),
    2: (1060.0, 940.0),
}
# contorno de 1/4 da torre (m, quadrante +x +y, finais 4 e 3), medido na implantacao (18,91 px/m) e nas plantas
# tipo: fachada 37,70 m, pontas com 5,82 m ate o eixo, saliencia do dormitorio do meio ate 6,80 m, recorte da testa
# (laje tecnica e janela do dormitorio 2 da ponta) com 2,27 m de fundo e 4,76 m de largura
TORRE_Q = [(0.0, 5.82), (3.12, 5.82), (3.12, 6.80), (5.30, 6.80), (5.30, 5.82), (18.85, 5.82), (18.85, 2.38),
           (16.58, 2.38), (16.58, 0.0)]
# FAQ: terreo ao 18o pavimento nas duas torres (19 pavimentos); terreo com 6 gardens (sem os finais 1 e 8)
PAVIMENTOS = {1: 19, 2: 19}

# ------------------------------------------------------------------ edificio garagem (deck)
# Faixa norte: terreo coberto (sobressolo, entrada pelo leste) e o 1o pavimento descoberto com vagas, com rampa
# saindo da rua interna entre as torres ("acesso ao 1o pavimento do edificio garagem").
DECK = (375, 455, 2426, 730)
DECK_Z = 3.0
RAMPA_DECK = (1565, 730, 1660, 1110)          # sobe de y=1110 (chao) ate y=730 (deck)
ESCADA_DECK = (1200, 648, 1300, 740)          # nucleo de escada do edificio garagem

# ------------------------------------------------------------------ chao (retangulos x0, y0, x1, y1 em px)
# Asfalto do terreo (o resto do lote e grama). O chao sob o deck tambem e asfalto.
ASFALTO = [
    (375, 455, 2426, 730),       # sob o deck
    (2426, 444, 2847, 730),      # leste do deck (vagas 16 a 24, 109 a 111 e a entrada do sobressolo)
    (375, 730, 640, 1105),       # coluna oeste (vagas 207 a 225)
    (465, 1105, 560, 1182),      # vagas 215 e 216
    (1485, 730, 1740, 1150),     # rua entre as torres
    (910, 1150, 2560, 1412),     # faixa sul (fileiras 256 a 270 e 271 a 304)
    (2547, 730, 2847, 1412),     # faixa leste
    (2560, 1412, 2765, 1853),    # rotativas 305 a 315 e a pista de saida
    (2765, 1500, 2847, 1853),    # motos
    (2847, 1265, 3005, 1540),    # entrada de veiculos (Rua 2), com as vagas de acumulacao antes do portao
    (2835, 1641, 3005, 1700),    # saida de veiculos
]
# gardens das torres (grama cercada por cerca viva baixa)
JARDIM_TORRE = {1: (1740, 730, 2547, 1134), 2: (640, 730, 1485, 1105)}
# lazer (sul, entre a fileira 271-304 e a avenida): grama com os decks e volumes
LAZER_Y0 = 1412

# fileiras de vagas: (x0, y0, x1, y1, 'h' = vagas lado a lado ao longo de x | 'v' = ao longo de y, largura m)
# a largura vem do FAQ: M 2,50, P 2,20, PcD 2,50 (+1,20 de faixa), rotativa 2,20, moto 1,00
VAGAS = [
    # deck (1o pavimento do edificio garagem)
    (375, 455, 2426, 545, 'h', 2.50, 'deck'),
    (565, 648, 1185, 730, 'h', 2.20, 'deck'),
    (1315, 648, 1485, 730, 'h', 2.20, 'deck'),
    (1739, 646, 2426, 730, 'h', 2.50, 'deck'),
    # terreo
    (2426, 444, 2847, 523, 'h', 2.50, 'chao'),
    (2426, 655, 2568, 730, 'h', 2.50, 'chao'),
    (375, 740, 455, 1100, 'v', 2.50, 'chao'),
    (560, 735, 640, 1100, 'v', 2.20, 'chao'),
    (465, 1105, 550, 1180, 'h', 2.20, 'chao'),
    (1485, 740, 1560, 1110, 'v', 2.20, 'chao'),
    (1665, 740, 1740, 1110, 'v', 2.20, 'chao'),
    (910, 1150, 1560, 1220, 'h', 2.20, 'chao'),
    (1665, 1134, 2547, 1225, 'h', 2.50, 'chao'),
    (1170, 1340, 2547, 1412, 'h', 2.20, 'chao'),
    (2568, 670, 2653, 1223, 'v', 2.50, 'chao'),
    (2758, 628, 2847, 1397, 'v', 2.50, 'chao'),
    (2576, 1347, 2653, 1841, 'v', 2.20, 'chao'),
    (2765, 1541, 2835, 1853, 'v', 1.00, 'chao'),
]
# faixas de pedestre (zebras)
ZEBRAS = [(1540, 1120, 1665, 1150, 'v'), (2600, 1260, 2645, 1330, 'h'), (2770, 1575, 2850, 1600, 'v')]

# ------------------------------------------------------------------ lazer e apoio (retangulos px)
# Etapa 2: posicoes lidas na vista de cima do lazer (perspectiva 782-...-VOO, 2560 x 1024), alinhada a implantacao
# pela quadra de areia e pela piscina infantil: impl_x = 2015 + (x_voo/1,4222 - 905) * 0,594, idem em y a partir
# de 1498 (topo do bloco do salao). Confere com a implantacao em ~3 px.
PISCINA_DECK = (2330, 1461, 2526, 1758)
PISCINA = [(2434, 1472, 2510, 1746), (2391, 1472, 2434, 1574)]     # adulto: raia funda + deck molhado (raso)
DECK_MOLHADO = (2391, 1472, 2434, 1574)
PISCINA_INFANTIL = (2369, 1664, 2412, 1739)
EDIF_SALAO = (2019, 1498, 2303, 1636)                  # bloco sem teto: academia | salao de festas | copa e WCs
ACADEMIA_X = (2019, 2101)
SALAO_X = (2101, 2235)
WC_X = (2235, 2303)
DECK_GOURMET = (2107, 1642, 2184, 1710)                # 09 lounge gourmet (deck de madeira)
LOUNGE_ACADEMIA = (2019, 1636, 2104, 1662)             # 11 lounge academia (faixa em frente a academia)
WINE_LOUNGE = (2187, 1642, 2306, 1722)                 # 25 wine lounge (gramado com poltronas e fogo)
PLAYGROUND = (1920, 1520, 2015, 1639)
QUADRA_AREIA = (1761, 1499, 1916, 1582)
CHURRASQUEIRA = (1656, 1432, 1754, 1517)               # 15 churrasqueira sem teto (copa + WC)
LOUNGE_CHURRASQUEIRA = (1611, 1432, 1656, 1517)        # 16 lounge com pergolado de madeira
PIQUENIQUE = (1530, 1432, 1606, 1517)                  # 17 piquenique (gramado com 2 mesas)
MESAS_PIQUENIQUE = [(1559, 1449, 0), (1580, 1493, 25)]
PRACA = (1754, 1413, 2018, 1499)                       # 13 praca de convivio (paver com arvores)
PASSEIO_LAZER = (2018, 1430, 2330, 1498)               # paver ao norte do bloco do salao
PORTARIA = (2835, 1541, 2906, 1641)
MARQUISE_PORTARIA = (2828, 1440, 2915, 1641)           # laje plana que cobre a guarita e o portao de entrada
TOTEM = (2955, 1508)
LIXO = (2841, 1735, 2906, 1829)
PET = (2780, 1858, 2860, 1905)
CASA_BOMBAS = (755, 1125, 835, 1185)
BIKE = (840, 1135, 910, 1215)
RESERVATORIOS = [(580, 1150), (635, 1176), (690, 1200), (745, 1226), (800, 1250)]
RAIO_RESERVATORIO_PX = 28
PORTAO_ENTRADA = ((2860, 1265), (2860, 1540))     # recuado: as vagas de acumulacao ficam antes dele
PORTAO_SAIDA = ((2906, 1641), (2906, 1700))
MURO_ABERTO_Y = (1265, 1700)     # sem muro no leste entre esses y (entrada, portaria e saida)

# ------------------------------------------------------------------ paisagismo (px)
ARVORES = [
    # faixa norte (junto ao muro) e faixa leste (junto a Rua 2)
    *[(x, 425, 'verde') for x in range(420, 2850, 150)],
    *[(2875, y, 'verde') for y in range(760, 1240, 95)],
    # gardens das torres (fila norte)
    (760, 765, 'verde'), (880, 765, 'verde_clara'), (990, 765, 'verde'), (1100, 765, 'verde_clara'),
    (1230, 765, 'verde'), (1345, 765, 'verde_clara'),
    (1795, 755, 'verde'), (1921, 755, 'verde_clara'), (2037, 755, 'verde'), (2147, 755, 'verde_clara'),
    (2268, 755, 'verde'), (2384, 755, 'verde_clara'),
    # lazer (praca de convivio e canto do piquenique)
    (1783, 1455, 'ipe_amarelo'), (1878, 1446, 'verde'), (1959, 1446, 'ipe_amarelo'), (2040, 1448, 'verde'),
    (1700, 1540, 'verde'), (1645, 1545, 'verde_clara'), (2010, 1660, 'verde_clara'), (2860, 1780, 'verde'),
    # ipes roxos na calcada da avenida e da Rua Joao Francisco Lisboa
    (300, 1160, 'roxa'), (480, 1255, 'roxa'), (710, 1335, 'roxa'), (955, 1410, 'roxa'), (1329, 1535, 'roxa'),
    (1512, 1595, 'roxa'), (1665, 1645, 'roxa'), (1841, 1705, 'roxa'), (2006, 1755, 'roxa'), (2165, 1805, 'roxa'),
    (2353, 1860, 'roxa'), (2571, 1930, 'roxa'), (2788, 1990, 'roxa'),
    *[(285, y, 'roxa') for y in (520, 760, 1000)],
    *[(2955, y, 'verde') for y in (520, 800, 1080, 1400, 1700)],
]
PALMEIRAS = [
    (720, 1085), (790, 1090), (1395, 1085), (1450, 1080),             # pe da torre 2
    (1765, 1110), (1830, 1110), (2470, 1110), (2520, 1105),           # pe da torre 1
    (2196, 1431), (2255, 1431), (2318, 1700), (2318, 1730),           # lazer (entrada do bloco e lateral da piscina)
]
# cercas vivas (sebes baixas) em volta dos gardens das torres e do lazer
SEBES = [
    (640, 1095, 1485, 1110), (1740, 1125, 2547, 1140), (1170, 1412, 2560, 1428),
    (2333, 1800, 2556, 1812),
]

# carros parados (px, giro: 0 = eixo do carro ao longo de x, 90 = ao longo de y), em vagas das fileiras
CARROS = [
    (470, 500, 90), (660, 500, 90), (1040, 500, 90), (1230, 500, 90), (1700, 500, 90), (2080, 500, 90), (2330, 500, 90),
    (640, 690, 90), (900, 690, 90), (1360, 690, 90), (1900, 690, 90), (2210, 690, 90),
    (2480, 484, 90), (2700, 484, 90), (2500, 692, 90),
    (415, 800, 0), (415, 960, 0), (600, 860, 0), (600, 1040, 0),
    (1522, 820, 0), (1522, 1010, 0), (1702, 900, 0),
    (1000, 1185, 90), (1250, 1185, 90), (1420, 1185, 90), (1820, 1180, 90), (2200, 1180, 90), (2420, 1180, 90),
    (1260, 1376, 90), (1520, 1376, 90), (1720, 1376, 90), (1980, 1376, 90), (2310, 1376, 90),
    (2610, 760, 0), (2610, 1000, 0), (2802, 700, 0), (2802, 900, 0), (2802, 1250, 0), (2614, 1500, 0),
]
