#!venv/bin/python
import itertools
import pycosat as sat



def clauseSubdivision(subdivision, gridWidth, mode):
    #mode=0: chaque case peut être un ballon
    #mode=1: chaque case peut être une pierre
    clause = []
    # chaque case pourrait être le ballon
    for i in range(len(subdivision)):
        j = 3 * gridWidth * (1 + subdivision[i][1]) + 1 + 3 * subdivision[i][0] + mode
        clause.append(j)
    yield clause

    # si la case de l est le ballon, alors les cases de k ne peuvent pas
    # l'être, et ce pour tout k > l
    for i in range(len(subdivision) - 1):
        # l est positif
        l = 3 * gridWidth * (1 + subdivision[i][1]) + 1 + 3 * subdivision[i][0] + mode
        # chaque k est négatif
        for k in range(i + 1, len(subdivision)):
            clause = []
            j = 3 * gridWidth * (1 + subdivision[k][1]) + 1 + 3 * subdivision[k][0] + mode
            clause.append(-l)
            clause.append(-j)
            yield clause

#-----------------------FONCTION PRINCIPALE-------------------------------------
def modeliser(width, height, subdivisions, noir):
    formule = []

    # Clauses pour les cases en dehors de la grille
    # ---------------Cases au dessus----------------
    for i in range(1, 1 + 3 * width - 1, 3):
        formule.append([-i])  # les cases au dessus ne peuvent pas contenir de ballon
        formule.append([-(i + 1)])  # elles ne peuvent pas non plus contenir de pierre
        formule.append([i + 2])  # Mais elles sont considérées noires
    # Cases en dessous: règles identiques que pour au dessus
    for i in range(
        3 * width * height + 3 * width + 1,                  # debut
        3 * width * height + 3 * width + 1 + 3 * width - 1,  # fin
        3,                                                   # pas
    ):
        formule.append([-i])
        formule.append([-(i + 1)])
        formule.append([i + 2])

    # ----------------------Clauses définissant les cases noires---------------
    i = 1 + 3 * width
    for y in range(height):
        for x in range(width):
            if [x, y] in noir:
                formule.append([i + 2])     # (x,y) est noire
                formule.append([-i])        # (x,y) ne peut pas contenir un ballon
                formule.append([-(i + 1)])  # (x,y) ne peut pas contenir une pierre
            else:
                formule.append([-(i + 2)]) # (x,y) n'est pas noire donc il peut contenir un ballon ou un pierre
            i += 3

    # ----Une case ne peut pas contenir à la fois un ballon et une pierre----------
    for i in range(1 + 3 * width, 3 * width * height + 3 * width + 1, 3):
        formule.append(
            [-i, -(i + 1)]
        )  # ¬(estBallon ∧ estPierre) = ¬estBallon ∨ ¬estPierre

    # -----------------Conditions de position des pierres------------
    # On s'arrête à la ligne height-1 vu que qu'une pierre dans la ligne du
    # bas repose forcément sur le bas de la grille: c'est donc forcément légal
    i = 1 + 3 * width
    for _ in range(0, height - 1):
        for _ in range(0, width):
            formule.append([-(i + 1), (i + 1) + 3 * width, (i + 1) + 3 * width + 1])
             # ¬ estPierre(x,y) ∨ estPierre(x,y+1) ∨ estNoir(x,y+1)
            i += 3
    # ---------------Conditions de position des ballons-------------
    # On commence à la ligne 1 (2e ligne) vu que qu'un ballon dans la ligne du
    # haut repose forcément contre le haut de la grille: c'est donc forcément
    # légal
    i = 1 + 3 * width * 2
    for _ in range(0, height - 1):
        for _ in range(0, width):
            formule.append([-i, i - 3 * width, i - 3 * width + 2])
            # ¬ estBallon(x,y) ∨ estBallon(x,y-1) ∨ estNoir(x,y-1)
            i += 3
    # --------------------Clauses pour les cases dans les subdivisions-----------------
    for subdivision in subdivisions:
        # Chaque case de la subdivision pourrait être un ballon
        for clause in clauseSubdivision(subdivision, width, 0): #0 =ballon
            formule.append(list(clause))
        # Chaque case de la subdivision pourrait être une pierre
        for clause in clauseSubdivision(subdivision, width, 1): #1 =pierre
            formule.append(list(clause))
    return formule
