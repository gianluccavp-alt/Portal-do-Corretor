# ipi_luzes.py -- iluminacao do condominio a noite (etapa 2). Postes de rua com luminaria de topo, postes de jardim
# com globo no lazer, balizadores nos caminhos dos halls e a poca de luz no chao de cada um (material luz_chao: a
# cena soma a textura radial so a noite; de dia nao aparece). As fontes (luz_poste) acendem pela cena.
# Posicoes em px em ipi_planta.py (POSTES_RUA, POSTES_JARDIM, BALIZADORES). Executado por ipi_modelo.py.

Z_POCA = 0.14          # acima do passeio (0,06) e da calcada (0,12); no deck da piscina usa Z_DECK + 0.03


def materiais_luzes():
    mat('luz_poste', '#fff1cc', 0.4)
    mat('luz_chao', '#ffffff', 1.0, img='luz_radial.jpg')
    mat('poste_grafite', '#34363a', 0.5, metal=0.4)


def poca(g, x, y, r, z=Z_POCA):
    g.tapete(x - r, x + r, y - r, y + r, z, 'luz_chao', (0, 0, 1, 1))


def poste_rua(g, x, y, h=4.8, r_poca=7.5):
    """Poste conico grafite com luminaria LED de topo (disco achatado, face de baixo acesa)."""
    g.cil(x, y, 0.16, 0, 0.35, 'concreto', seg=10)
    g.cil(x, y, 0.07, 0.35, h, 'poste_grafite', seg=10, r2=0.045)
    g.cil(x, y, 0.32, h, h + 0.1, 'poste_grafite', seg=16, r2=0.22)
    g.cil(x, y, 0.3, h - 0.005, h, 'luz_poste', seg=16, tampa=False, base=True)
    poca(g, x, y, r_poca)


def poste_jardim(g, x, y, h=3.2, z=0.0, r_poca=3.4):
    """Poste baixo do jardim com globo leitoso aceso a noite (como no Alta Vista)."""
    g.cil(x, y, 0.05, z, z + h, 'poste_grafite', seg=8)
    g.elipsoide(x, y, z + h + 0.15, 0.17, 0.17, 0.17, 'luz_poste', seg=10, aneis=6)
    poca(g, x, y, r_poca, max(Z_POCA, z + 0.03))


def balizador(g, x, y, z=0.0, h=0.7, r_poca=1.3):
    g.cil(x, y, 0.08, z, z + h, 'poste_grafite', seg=10)
    g.cil(x, y, 0.082, z + h - 0.16, z + h - 0.04, 'luz_poste', seg=10, tampa=False)
    poca(g, x, y, r_poca, max(Z_POCA, z + 0.03))


def luzes(g):
    for px, py in PL.POSTES_RUA:
        poste_rua(g, X(px), Y(py))
    for px, py in PL.POSTES_JARDIM:
        poste_jardim(g, X(px), Y(py))
    for px, py in PL.BALIZADORES:
        balizador(g, X(px), Y(py))
