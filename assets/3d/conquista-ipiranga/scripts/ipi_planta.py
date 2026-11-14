# ipi_planta.py -- medidas do Conquista Clube Ipiranga lidas da implantacao do Drive
# (DIRECIONAL_785 ITAJUBA_IMPLANTACAO 01_R04.png, 4000 x 2037 px, sem legenda).
# So dados, em pixels dessa imagem (x para a direita, y para baixo).
# Escala 0,0452 m/px, conferida contra o FAQ da ficha tecnica:
#   torre de ponta a ponta 56,61 m = 1245 px (0,0455); piscina adulto 15,00 x 5,90 m = 330 x 133 px (0,0450);
#   piscina infantil 4,75 m = 104 px (0,0457); lateral T1 a lateral T3 24,29 m = ~530 px; T2 a T4 32,94 m = ~735 px.
# Usado pelo gerador (ipi_modelo.py e modulos) e por ipi_ver.py (sobreposicao na imagem, fora do Blender).

S_PX = 0.0452
ORIGEM_PX = (1900.0, 1000.0)      # perto do centro do terreno (vira a origem da cena)

# Divisa (muro). Rua Itajuba a leste (x > 3590); vizinhos nos outros lados. O lote tem a ponta oeste em cunha,
# o recorte do vizinho ao norte (x 2166..3590) e o "dente" das vagas 125 a 140 ao sul.
TERRENO = [
    (5, 497), (2166, 72), (2166, 228), (3590, 245), (3590, 1662), (2950, 1528), (2870, 1975), (2545, 1911),
    (2100, 1847), (1600, 1760), (1100, 1686), (600, 1615),
]
# Rua Itajuba: calcada do lote (3590..3650), pista (3650..3870), calcada oposta; rua lateral a leste (y 1250..1563)
RUA_X = (3650, 3870)
CALCADA_X = (3590, 3650)
CALCADA_OPOSTA = 65
RUA_LATERAL_Y = (1250, 1563)
# abertura do muro na frente: calcada em curva ate a guarita, acessos de veiculos e a guarita
FRENTE_ABERTA_Y = (790, 1360)
CURVA_CALCADA = [(3590, 790), (3600, 860), (3570, 950), (3510, 1017), (3463, 1083)]

# Torres: centro (px) e giro da planta em graus na imagem (negativo = eixo maior subindo para a direita).
# Planta local: eixo maior em x (leste), face +y (para cima na imagem) com os finais 09 08 07 | 06 05 04,
# face -y com 10 11 12 | 01 02 03. T1 e T2 alinhadas com a imagem; T3 e T4 giradas ~11,3 graus.
TORRES = {
    1: (2835.5, 845.5, 0.0),
    2: (2835.5, 436.0, 0.0),
    3: (1038.2, 920.1, -11.3),
    4: (838.5, 544.8, -11.3),
}
PAVIMENTOS = {1: 7, 2: 7, 3: 7, 4: 7}     # FAQ: terreo + 6
# espaco de uso comum no terreo, no lugar do final 12 (legenda da implantacao: 03, 04, 14, 16)
SALA_TERREO = {1: 'Espaço happy hour', 2: 'Coworking e espaço reels', 3: 'Brinquedoteca', 4: 'Mini market'}

# Contorno de 1/4 da torre (px a partir do centro; quadrante +x +y = finais 06, 05, 04), medido por perfil de cor na
# T1: nucleo 35,5; garden do 06 35,5..124,5; bloco do dormitorio 2 do 06 124,5..196,5; recuo entre 06 e 05
# 196,5..286,5; bloco do 05 286,5..354,5; gardens do 05 e do 04 354,5..534,5 (divisa em 444,5); ponta 534,5..622,5.
# Fachada saliente a 148,5 (guarda-corpo dos gardens na mesma linha), fundo dos recuos a 106,5, ponta a 142, nucleo a
# 130,5. Divisas: 06|05 em 240,5 e 05|04 em 444,5.
Q_PX = dict(nucleo=35.5, g06=124.5, b06=196.5, r=286.5, b05=354.5, g04=444.5, ponta=534.5, fim=622.5,
            y_fachada=148.5, y_fundo=106.5, y_ponta=142.0, y_nucleo=130.5, div06=240.5, div05=444.5,
            testa_recuo=18.0, testa_y=66.0)

# ------------------------------------------------------------------ chao (poligonos px, sem sobreposicao)
ASFALTO = [
    # rua principal (norte-sul do estacionamento ao portao) ate a calcada da Rua Itajuba
    [(1368, 1232), (3650, 1232), (3650, 1360), (1368, 1360)],
    # corredor norte (entre a T4 e a T2)
    [(1867, 175), (2000, 175), (2000, 1232), (1867, 1232)],
    # praca de manobra a noroeste (vagas 41 a 50)
    [(1520, 338), (1812, 275), (1828, 290), (1867, 290), (1867, 432), (1765, 432), (1730, 435), (1545, 472)],
    # corredor sudoeste, inclinado como a T3 (vagas 72 a 100)
    [(547, 1393), (1317, 1243), (1368, 1232), (1368, 1360), (1290, 1384), (643, 1509), (560, 1515)],
    # descida para as motos
    [(1290, 1384), (1368, 1360), (1368, 1470), (1393, 1500), (1393, 1565), (1390, 1565), (1320, 1535), (1311, 1492)],
    # corredor das motos
    [(968, 1603), (1320, 1535), (1390, 1565), (975, 1645)],
    # corredor sudeste, inclinado (vagas 125 a 140)
    [(2668, 1360), (2802, 1360), (2800, 1470), (2715, 1940), (2582, 1910), (2662, 1480)],
    # acesso de veiculos em frente a guarita (entrada e saida)
    [(3462, 1085), (3510, 1017), (3570, 950), (3612, 985), (3650, 985), (3650, 1232), (3462, 1232)],
]
# ilha de canteiro entre a entrada e a saida (na calcada) e as ilhas arredondadas das fileiras
ILHAS = [(3605, 1095, 3655, 1225), (1335, 1112, 1368, 1243), (1838, 1112, 1868, 1232), (2505, 1112, 2535, 1232),
         (3258, 1112, 3292, 1232)]

# Fileiras de vagas: 4 cantos (a, b = frente no corredor; c, d = fundo), numero de vagas e tipo.
# Vagas de piso drenante (faixas de concreto e grama), 2,30 m (FAQ: P 2,30 x 4,70; PcD 2,50 x 5,00).
VAGAS = [
    # rua principal, lado norte
    ([(1368, 1232), (1838, 1232), (1838, 1112), (1368, 1112)], 9, 'carro'),
    ([(2000, 1232), (2105, 1232), (2105, 1112), (2000, 1112)], 2, 'carro'),
    ([(2137, 1232), (2505, 1232), (2505, 1112), (2137, 1112)], 7, 'carro'),
    ([(2535, 1232), (2905, 1232), (2905, 1112), (2535, 1112)], 7, 'carro'),
    ([(2905, 1232), (3046, 1232), (3046, 1112), (2905, 1112)], 2, 'pcd'),
    ([(3046, 1232), (3255, 1232), (3255, 1112), (3046, 1112)], 4, 'carro'),
    # rua principal, lado sul
    ([(1368, 1360), (2105, 1360), (2105, 1470), (1368, 1470)], 14, 'carro'),
    ([(2140, 1360), (2668, 1360), (2668, 1470), (2140, 1470)], 10, 'carro'),
    ([(2802, 1360), (2908, 1360), (2908, 1470), (2802, 1470)], 2, 'carro'),
    ([(2908, 1360), (3046, 1360), (3046, 1470), (2908, 1470)], 2, 'pcd'),
    ([(3046, 1360), (3300, 1360), (3300, 1470), (3046, 1470)], 5, 'carro'),
    # corredor norte
    ([(1867, 1085), (1867, 478), (1763, 478), (1763, 1085)], 12, 'carro'),
    ([(2000, 172), (2000, 1085), (2100, 1085), (2100, 172)], 18, 'carro'),
    # praca noroeste
    ([(1520, 338), (1812, 275), (1795, 190), (1495, 242)], 6, 'carro'),
    ([(1545, 472), (1730, 435), (1750, 540), (1575, 575)], 4, 'carro'),
    # corredor sudoeste
    ([(547, 1393), (1317, 1243), (1290, 1123), (518, 1254)], 16, 'carro'),
    ([(643, 1509), (1290, 1384), (1311, 1492), (664, 1617)], 13, 'carro'),
    # corredor sudeste
    ([(2662, 1480), (2582, 1910), (2475, 1885), (2550, 1470)], 8, 'carro'),
    ([(2800, 1470), (2715, 1940), (2825, 1965), (2900, 1480)], 9, 'carro'),
    # motos (1,00 x 2,00 m)
    ([(1867, 175), (2000, 175), (2000, 120), (1867, 120)], 8, 'moto'),
    ([(1867, 165), (1867, 290), (1828, 290), (1828, 165)], 6, 'moto'),
    ([(1765, 432), (1865, 432), (1865, 475), (1765, 475)], 5, 'moto'),
    ([(968, 1603), (1320, 1535), (1311, 1492), (960, 1560)], 16, 'moto'),
    ([(975, 1645), (1390, 1565), (1398, 1608), (983, 1688)], 18, 'moto'),
]
# faixas de pedestre: (x0, y0, x1, y1, 'h' = listras ao longo de x empilhadas em y)
ZEBRAS = [(2105, 1240, 2137, 1352, 'h'), (2962, 1240, 2994, 1352, 'h'),
          (3612, 990, 3652, 1095, 'h'), (3615, 1228, 3655, 1360, 'h')]

# ------------------------------------------------------------------ passeios (paver) e pracas (concreto)
PASSEIOS = [
    # calcada do lado norte da rua principal (ao pe do jardim da T1 e do pet place)
    [(1335, 1078), (3300, 1078), (3300, 1112), (1335, 1112)],
    # passeio sul da rua principal (frente do lazer)
    [(1475, 1470), (2668, 1470), (2668, 1500), (1475, 1500)],
    # halls da T1 e da T2 ate os passeios
    [(2808, 994), (2868, 994), (2868, 1078), (2808, 1078)],
    [(2808, 584), (2868, 584), (2868, 665), (2808, 665)],
    [(2135, 640), (2808, 640), (2808, 665), (2135, 665)],
    # T4: do hall ao passeio entre as torres e ate o corredor norte
    [(838, 600), (872, 594), (890, 742), (858, 748)],
    [(858, 748), (1745, 576), (1752, 606), (864, 778)],
    # T3: do hall ao passeio atras das vagas 72 a 87
    [(1022, 990), (1058, 984), (1078, 1150), (1042, 1156)],
    [(510, 1250), (1335, 1108), (1335, 1078), (500, 1222)],
    # guarita: passeio ate a calcada em curva
    [(3292, 1080), (3462, 1080), (3462, 1232), (3292, 1232)],
]
PRACAS = [
    # bicicletario (15) entre a T4 e a T3
    [(392, 800), (850, 708), (850, 775), (400, 865)],
    # area tecnica (casa de bombas, reservatorios, lixo)
    [(3300, 1374), (3590, 1374), (3590, 1662), (3300, 1600)],
]

# ------------------------------------------------------------------ lazer e apoio (retangulos px x0, y0, x1, y1)
SOLARIUM = (2045, 1548, 2492, 1802)
PISCINA = (2158, 1565, 2486, 1698)
PISCINA_INFANTIL = (2304, 1722, 2410, 1798)
VESTIARIO = (1985, 1630, 2045, 1780)
FITNESS = (2145, 1500, 2400, 1542)
PLAYGROUND = (1853, 1505, 1975, 1755)
GOURMET = (1545, 1535, 1690, 1715)
PERGOLADO = (1475, 1525, 1545, 1715)
APOIO = (1690, 1535, 1795, 1720)
PET = (1480, 1010, 1745, 1075)
BICICLETARIO = [(410, 820), (840, 732)]        # linha dos paraciclos
GUARITA = (3367, 1080, 3460, 1232)
CASA_BOMBAS = (3315, 1365, 3390, 1452)
LIXO = (3490, 1380, 3585, 1498)
RESERVATORIOS = [(3438, 1432), (3338, 1505), (3424, 1528), (3503, 1550)]
RAIO_RESERVATORIO_PX = 38
PORTAO = ((3462, 1232), (3462, 1360))
PORTAO_PEDESTRE = ((3462, 1083), (3462, 1100))
SEBES = [(3390, 1356, 3612, 1374), (1490, 995, 1730, 1010), (2045, 1535, 2492, 1548)]

# ------------------------------------------------------------------ paisagismo (px)
# ipes roxos detectados pela cor na implantacao (copas rosa), fundidos a 45 px
IPES = [
    (1462, 247), (1481, 319), (1481, 377), (3613, 224), (3619, 298), (3626, 373), (1501, 476), (1536, 544),
    (1721, 594), (3626, 455), (3628, 530), (3631, 604), (3637, 685), (3638, 758), (675, 1196), (777, 1178),
    (881, 1168), (972, 1148), (1067, 1124), (1184, 1082), (1267, 1085), (1354, 1064), (2213, 1055), (2297, 1040),
    (2383, 1048), (2477, 1050), (2569, 1045), (2653, 1049), (2739, 1051), (2915, 1045), (3002, 1033), (3080, 1042),
    (3182, 1041), (3275, 1039), (3440, 1020), (577, 1220), (3653, 1389), (956, 1570), (1458, 1501), (3661, 1536),
    (3664, 1462), (1459, 1687), (1882, 1775), (3658, 1621), (3659, 1696), (3659, 1769), (3660, 1924), (3662, 1850),
]
# arvores de copa verde (lidas a olho)
ARVORES = [
    (2290, 190, 'verde'), (2385, 185, 'verde_clara'), (1560, 1030, 'verde'), (1715, 1045, 'verde_clara'),
    (2955, 1505, 'verde'), (2935, 1630, 'verde_clara'), (2905, 1760, 'verde'), (2880, 1885, 'verde_clara'),
    (3165, 1480, 'verde'), (3065, 1490, 'verde_clara'), (840, 1625, 'verde'), (1240, 1650, 'verde_clara'),
    (1625, 1745, 'verde'), (1760, 1760, 'verde_clara'), (2440, 1820, 'verde'),
    (1300, 1045, 'verde_clara'), (965, 670, 'verde'),
]
PALMEIRAS = [
    (3320, 1095), (3345, 1150), (3330, 1205), (2040, 1505), (2215, 1478), (2440, 1480), (2500, 1545),
    (2495, 1660), (2470, 1775), (2120, 1815), (2260, 1810), (2365, 1825), (1925, 1475), (1820, 1480),
]
# carros parados como na implantacao (px, giro em graus no Blender: 0 = eixo do carro ao longo de x, 90 = ao
# longo de y; nas fileiras inclinadas 101 = perpendicular a T3/T4 e -10 = perpendicular ao corredor sudeste)
CARROS = [
    (1495, 1175, 90), (1820, 1415, 90), (2323, 1175, 90), (2562, 1175, 90), (2880, 1175, 90),
    (1630, 268, 101), (2045, 350, 0), (2050, 600, 0), (1820, 855, 0), (904, 1265, 101), (1165, 1455, 101),
    (2820, 1660, -10), (2540, 1820, -10),
]
