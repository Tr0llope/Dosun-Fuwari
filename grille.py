from tkinter import Canvas
import pycosat as sat

from modelisation import modeliser

class grid(Canvas):
    """
    Classe définissant une grille de Dosun Fuwari intéractive.
    """

    cell_width = 50
    border_width = 5
    border_colour = "#964B00"
    selection_colour = "#b3e5fc"

    def __init__(self, x, y, solvable_textvar, noir=[], subdivisions=[], master=None):
        """
        Initialisation automatique à la création d'une grille
        Arguments:
          - x : largeur de la grille
          - y : hauteur de la grille
          - solvable_textvar: TextVar contenant le message de satisfaisabilité
                              de la grille (à mettre à jour après résolution
                              de la grille)
          - noir (optionnel): Liste des cases noires de la grille
                                préexistante à afficher
          - subdivisions (optionnel): Liste des subdivisions de la grille préexistante à
                               afficher
          - master (optionnel): Element Tk dans lequel dessiner la grille
        """
        # Initialiser les variables d'instance
        self.master = master
        self.dimensions = (x, y)
        self.black_cells = noir
        self.subdivisions = subdivisions
        self.solvable_textvar = solvable_textvar

        # Initialiser le canvas
        super().__init__(
            master,
            width=x * self.cell_width,
            height=y * self.cell_width,
        )
        # Dessiner la grille vide
        self.draw()

        # Dessiner la grille fournie (si fournie)
        if subdivisions != [] or noir != []:
            self.load_grid(subdivisions, noir)

    def draw(self):
        """
        Dessiner une grille vide
        """
        # Dessiner les cases
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                self.create_rectangle(
                    x * self.cell_width + self.border_width,
                    y * self.cell_width + self.border_width,
                    (x + 1) * self.cell_width,
                    (y + 1) * self.cell_width,
                    fill="white",
                    width=0.0,
                    tags="cell x" + str(x) + " y" + str(y) + " blank",
                    # le tag "blank" sert à vérifier à la fin que toutes les
                    # cases soient soit dans une subdivision, soit noires
                )
        # Assigner à chaque case l'action casSelectiones
        self.tag_bind("cell", "<ButtonPress-1>", self.casSelectiones)

        # Dessiner les bordures horizontales
        for y in range(self.dimensions[1] + 1):
            for x in range(self.dimensions[0] + 1):
                self.create_rectangle(
                    x * self.cell_width,
                    y * self.cell_width,
                    (x + 1) * self.cell_width + 2 * self.border_width,
                    y * self.cell_width + self.border_width,
                    fill=self.border_colour,
                    width=0.0,
                    tags="border horizontal x" + str(x) + " y" + str(y),
                )
        # Dessiner les bordures verticales
        for y in range(self.dimensions[1] + 1):
            for x in range(self.dimensions[0] + 1):
                self.create_rectangle(
                    x * self.cell_width,
                    y * self.cell_width,
                    x * self.cell_width + self.border_width,
                    (y + 1) * self.cell_width + self.border_width,
                    fill=self.border_colour,
                    width=0.0,
                    tags="border vertical x" + str(x) + " y" + str(y),
                )

    def TrouverVoisinsSelectiones(self, cell, found):
        """
        Trouver les voisins sélectionnés de la case donnée en argument,
        ainsi que les voisins sélectionnés de chacun d'entre eux etc
        récursivement.
        Arguments:
          - cell: case à partir de laquelle on cherche les voisins
          - found: ensemble des voisins connus. Nécessaire pour ne
                   pas revenir en arrière lors de la récursion.
                   Initialement devrait être vide.
        """
        # vérifier que cell est bien sélectionnée
        tags = self.gettags(cell)
        if "selected" in tags:
            # l'ajouter à l'ensemble
            found.add(cell)
            # trouver ses coordonnées pour trouver tous ses voisins
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            voisins = self.TrouverVoisins(x, y)
            # ne garder que les voisins sélectionnés et tous leurs voisins
            # sélectionnés
            for ncell in voisins:
                if voisins[ncell] not in found:
                    for u in self.TrouverVoisinsSelectiones(voisins[ncell], found):
                        found.add(u)
        return found

    def casSelectiones(self, event):
        """
        Ajoute la case sur laquelle l'utilisateur a cliqué à la sélection. Si
        la case était déjà sélectionnée, on la déselectionne à la place. Si
        la déselectionner couperait la sélection en deux subdivisions séparées, on
        désélectionne tout (par sécurité).
        """
        # Trouver les coordonnées de la case cliquée
        tags = self.gettags("current")
        x = int(tags[1][1:])
        y = int(tags[2][1:])

        # Si elle était déja sélectionnée, la déselectionner
        if "selected" in tags:
            self.dtag("current", "selected")
            # la recolorer de la bonne facon
            if "solid" in tags:
                self.itemconfig("current", fill="#000000")
            else:
                self.itemconfig("current", fill="#ffffff")

            # Vérifier si la sélection a été coupée en deux subdivisions distinctes
            
            # On compare la sélection entière avec l'ensemble des cases
            # sélectionnées qui sont en contact avec la case de
            # la sélection. Si les deux ensembles ne sont pas égaux, alors
            # la sélection a été coupée
            # sélection entière
            selection = self.find_withtag("selected")
            # Si la sélection est vide ca sert à rien
            if len(selection) > 0:
                # partie de la sélection en contact avec le 1e élement de la
                # liste précédente
                selection_contiguous = self.TrouverVoisinsSelectiones(selection[0], set())
                # si les deux ensembles sont différents, tout désélectionner
                if set(selection) != selection_contiguous:
                    self.itemconfig("selected", fill="#ffffff")
                    self.itemconfig("solid", fill="#000000")
                    self.dtag("selected", "selected")

        # Sinon ajouter la case cliquée à la sélection (si c'est autorisé)
        else:
            # vérifier si elle partage une bordure avec la sélection existante
            # trouver ses voisins, vérifier si l'un d'entre eux est sélectionné
            voisins = self.TrouverVoisins(x, y)
            has_selected_neighbour = False
            for cell in voisins:
                if "selected" in self.gettags(voisins[cell]):
                    has_selected_neighbour = True
                    break

            # Si non, tout déselectionner et garder que la nouvelle case
            if not has_selected_neighbour:
                self.itemconfig("selected", fill="#ffffff")
                self.itemconfig("solid", fill="#000000")
                self.dtag("selected", "selected")

            # Sélectionner la case et la colorer en bleu
            self.addtag_withtag("selected", "current")
            self.itemconfig("selected", fill=self.selection_colour)

    def TrouverVoisins(self, x, y):
        """
        Trouve les cases voisines de la case (x,y)
        Renvoie un dictionaire des éléments Tk des voisins
        Format:
        {
            "up": id de l'élément du canvas (entier),
            "down": id de l'élément du canvas (entier),
            "left": id de l'élément du canvas (entier),
            "right": id de l'élément du canvas (entier)
        }
        """
        # Trouver toutes les cases
        cells = self.find_withtag("cell")
        voisins = {}
        # Pour chaque case de la grille, si la case a les bonnes coordonnées,
        # l'ajouter au dict
        for cell in cells:
            cell_tags = self.gettags(cell)
            # Voisin gauche
            if "x" + str(x - 1) in cell_tags and "y" + str(y) in cell_tags:
                voisins["left"] = cell
            # Voisin supérieur
            if "x" + str(x) in cell_tags and "y" + str(y - 1) in cell_tags:
                voisins["up"] = cell
            # Voisin droit
            if "x" + str(x + 1) in cell_tags and "y" + str(y) in cell_tags:
                voisins["right"] = cell
            # Voisin inférieur
            if "x" + str(x) in cell_tags and "y" + str(y + 1) in cell_tags:
                voisins["down"] = cell
        return voisins

    def faire_subdivision(self):
        """
        Créé une subdivision à partir de la sélection courante.
        """
        # Commencer par enlever le tag "blank" à toutes les cases sélectionnées
        self.dtag("selected", "blank")

        # Trouver les cases sélectionnées
        selection = self.find_withtag("selected")
        borders = self.find_withtag("border")
        # Ajouter une subdivision dans la liste
        self.subdivisions.append([])
        for item in selection:
            # Trouver les coordonnées de la case courante
            tags = self.gettags(item)
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            if "solid" in tags:
                self.dtag(item, "solid")
                self.black_cells.remove([x, y])
            # Trouver ses voisins
            voisins = self.TrouverVoisins(x, y)
            # Ne garder que ceux qui sont sélectionnés
            for cell in list(voisins):
                tags = self.gettags(voisins[cell])
                if "selected" not in tags:
                    del voisins[cell]
            # Colorier ses bordures
            for border in borders:
                border_tags = self.gettags(border)
                # bordure gauche
                if (
                    "x" + str(x) in border_tags
                    and "y" + str(y) in border_tags
                    and "vertical" in border_tags
                ):
                    if "left" not in voisins.keys():
                        self.itemconfig(border, fill="#964B00")
                    else:
                        self.itemconfig(border, fill="#ebebeb")
                # bordure supérieure
                elif (
                    "x" + str(x) in border_tags
                    and "y" + str(y) in border_tags
                    and "horizontal" in border_tags
                ):
                    if "up" not in voisins.keys():
                        self.itemconfig(border, fill="#964B00")
                    else:
                        self.itemconfig(border, fill="#ebebeb")
                # bordure droite
                elif (
                    "x" + str(x + 1) in border_tags
                    and "y" + str(y) in border_tags
                    and "vertical" in border_tags
                ):
                    if "right" not in voisins.keys():
                        self.itemconfig(border, fill="#964B00")
                    else:
                        self.itemconfig(border, fill="#ebebeb")
                # bordure inférieure
                elif (
                    "x" + str(x) in border_tags
                    and "y" + str(y + 1) in border_tags
                    and "horizontal" in border_tags
                ):
                    if "down" not in voisins.keys():
                        self.itemconfig(border, fill="#964B00")
                    else:
                        self.itemconfig(border, fill="#ebebeb")

            # Retirer l'item de toute autre subdivision
            for subdivision in self.subdivisions:
                if [x, y] in subdivision:
                    subdivision.remove([x, y])
            # L'ajouter à la nouvelle subdivision
            self.subdivisions[-1].append([x, y])
            # Retirer les subdivisions vides
            for subdivision in self.subdivisions:
                if subdivision == []:
                    self.subdivisions.remove(subdivision)
        # désélectionner les cases
        self.itemconfig("selected", fill="#ffffff")
        self.itemconfig("solid", fill="#000000")
        self.dtag("selected", "selected")

    def rendSolides(self):
        """
        Rend solide toutes les cases sélectionnées
        """
        # trouver toutes les cases sélectionnées
        selection = self.find_withtag("selected")
        for cell in selection:
            # vérifier si la case est déjà solide
            tags = self.gettags(cell)
            if "solid" in tags:
                # Si oui, la remettre vide
                self.black_cells.remove([int(tags[1][1:]), int(tags[2][1:])])
                self.dtag(cell, "solid")
                self.itemconfig(cell, fill="#ffffff")
                self.addtag_withtag("blank", cell) # lui remettre le tag "blank"
            else:
                # Sinon la rendre solide
                self.dtag(cell, "blank") # lui retirer le tag "blank"
                self.black_cells.append([int(tags[1][1:]), int(tags[2][1:])])
                self.addtag_withtag("solid", cell)
                self.itemconfig(cell, fill="#000000")

        # Tout déselectionner
        self.dtag("selected", "selected")

    def solve(self):
        """
        Résoudre la grille, dessiner la solution et afficher le résultat dans
        le champs de texte prévu pour. 
        """
        # Rendre la grille non modifiable une fois qu'elle a été résolue
        self.tag_unbind("cell", "<ButtonPress-1>")
        # Afficher un message des fois que la recherche d'une solution mette
        # un peu de temps
        self.solvable_textvar.set("Chercher une solution...")
        # rendre solides toutes les cases qui ne sont pas dans une subdivision ou solides
        self.dtag("selected", "selected")
        self.addtag_withtag("selected", "blank")
        self.rendSolides()

        # Générer les clauses
        formule = modeliser(
            self.dimensions[0], self.dimensions[1], self.subdivisions, self.black_cells
        )
        # Trouver une solution
        solution = sat.solve(formule)
        # Si une solution a été trouvée, l'afficher et mettre à jour le texte
        if not (solution == "UNSAT" or solution == "UNKNOWN"):
            self.AfficheSolution(solution)
            self.solvable_textvar.set("Solution trouvée!")
        # Sinon, juste mettre a jour le texte
        else:
            self.solvable_textvar.set("Aucune solution trouvée!")

    def get_grid(self):
        """
        Renvoyer le dictionnaire définissant les propriétés de la grille.
        Format du dictionnaire renvoyé:
        {
            "width": largeur de la grille (entier),
            "height": hauteur de la grille (entier),
            "subdivisions" : [
                [[x1, y1], [x2, y2], ...], les coordonnées des cellules de la subdivision 1
                [[x3, y3], [x4, y4], ...], les coordonnées des cellules de la subdivision 2
                ...
            ],
            "noir": [[x1, y1], [x2, y2], ...] les coordonnées des cellules noires
        }
        """
        grid = {
            "width": self.dimensions[0],
            "height": self.dimensions[1],
            "subdivisions": self.subdivisions,
            "noir": self.black_cells,
        }
        return grid

    def AfficheSolution(self, solution):
        """
        Dessiner la solution de la grille: les pierres sont symbolisées par
        des cercles noirs, les ballons par des cercles blancs.
        Format attendu de la solution: liste d'entiers telle que renvoyée par
        pycosat.
        """
        # Parcourir la clause en ignorant les variables en dehors de la grille
        # servant uniquement pour résoudre le problème
        x = 0  # colonne courante
        y = 0  # ligne courante
        # La première variable dans la grille (la case en haut à gauche) est
        # précédée par une ligne entière de variables
        i = self.dimensions[0] * 3
        # On ne sait pas combien de variables le satsolver a rajouté dans la
        # clause pour résoudre le problème, on doit donc compter les lignes pour
        # savoir où s'arrêter
        while y < self.dimensions[1]:
            if solution[i] > 0:
                # Dessiner un ballon
                self.create_oval(
                    self.cell_width * x + 5,
                    self.cell_width * y + 5,
                    self.cell_width * (x + 1) - 5,
                    self.cell_width * (y + 1) - 5,
                    fill="white",
                    width=2.0,
                )
            elif solution[i + 1] > 0:
                # Dessiner une pierre
                self.create_oval(
                    self.cell_width * x + 5,
                    self.cell_width * y + 5,
                    self.cell_width * (x + 1) - 5,
                    self.cell_width * (y + 1) - 5,
                    fill="black",
                    width=2.0,
                )

            i += 3 # passer au groupe de variables suivante
            x += 1 # passer à la colonne suivante

            if x >= self.dimensions[0]:
                # si on est arrivé en bout de ligne, repasser à la première
                # colonne et passer à la ligne suivante
                x = 0
                y += 1

    def load_grid(self, subdivisions, noir):
        """
        Charger les subdivisions et les cases noires fournies en argument
        """
        # récupérer la liste des cases de la grille
        cells = self.find_withtag("cell")

        # dessiner les cases noires: les sélectionner toutes, les rendre noires
        # et les désélectionner
        for cell in noir:
            for id in cells:
                tags = self.gettags(id)
                if ("x{}".format(cell[0]) in tags) and ("y{}".format(cell[1]) in tags):
                    self.addtag_withtag("selected", id)
        self.rendSolides()
        self.dtag("selected", "selected")

        # dessiner les subdivisions: sélectionner chaque subdivision puis appeller la
        # fonction faire_subdivion()
        for subdivision in list(subdivisions):
            # list() est nécessaire parce que la subdivisions se fait modifier en
            # cours de route: en appelant list() dessus on force une copie de
            # la liste qui ne se fait donc pas modifier
            for cell in subdivision:
                for id in cells:
                    tags = self.gettags(id)
                    if ("x{}".format(cell[0]) in tags) and (
                        "y{}".format(cell[1]) in tags
                    ):
                        self.addtag_withtag("selected", id)
            self.faire_subdivision()
            # la fonction désélectionne toute seule la subdivision à la fin: pas
            # besoin de le faire ici
