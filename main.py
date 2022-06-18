#!venv/bin/python
# importer les éléments Tk que l'on utilise pour le GUI
from tkinter import *
from tkinter.ttk import Button, Label, Frame, Entry
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno

# Classe de la grille de Dosun Fuwari (basée sur un tkinter.Canvas)
from grille import grid
# Fonctions de résolution de grid
from modelisation import modeliser

def save_dimacs(formule, filename):
        """
        Enregistre les clauses fournies en 1e argument dans le fichier fourni en
        2e argument au format DIMACS.
         Format de clauses attendu: liste d'entiers (format dimacs compatible avec
        pycosat)
        """
        #Initialisation du nombre de clause
        nb_clauses = 0
        #Initialisation d'une liste pour chercher le nombre de variables de la formule
        listeVar=[]

        for clause in formule:
            # incrémenter le nombre de clauses
            nb_clauses+=1
            # Pour chaque variable, si elle n'est pas dans listeVar, incrementer
            # le compteur du nombre de variable et l'ajouter dans listeVar
            for variable in clause:
                if not(variable in listeVar) and not(-variable in listeVar):
                    listeVar.append(variable)
    
        #Ecriture du le fichier au format DIMACS
        with open(filename, "w") as fichier:
            # En-tête
            fichier.write("c Fichier DIMACS\n")
            fichier.write("p cnf ")
            fichier.write(str(len(listeVar)))
            fichier.write(" ")
            fichier.write(str(nb_clauses))
            fichier.write("\n")
            # Clauses
            for clause in formule:
                i = 1
                for variable in clause:
                    fichier.write(str(variable))
                    fichier.write(" ")
                    if i == len(clause):
                        fichier.write("0")
                    i += 1
                fichier.write("\n")
                

def quit():
    """
    Détruit l'objet principal Tk, le global root. Termine l'execution du
    programme.
    """
    global root
    root.destroy()


class Editor_Frame(Frame):
    """
    Fenêtre d'édition de grille de Dosun Fuwari. Permet de créer une nouvelle
    grille puis de la
    résoudre avec pycosat, d'exporter
    la formule de solvabilité dans un fichier DIMACS.
    """

    # Variables de classe contenant les chaines statiques à afficher
    TITLE = "Dosun-Fuwari Solveur"
    

    def __init__(self, grid_w, grid_h, grid, master=None):
        """
        Initialisation automatique à la création de la fenêtre d'édition.
        Arguments:
          - grid_w: largeur de la grille
          - grid_h: hauteur de la grille
          - grid: dictionnaire contenant la liste des cases noires et la liste
                  des subdivisions de la grille. Format: {"noir": [], "subdivisions": []}
          - master (optional): objet Tk parent
        """
        super().__init__(master)
        # assigner les variables d'instance
        self.master = master
        self.grid_dimensions = (grid_w, grid_h)  # dimensions de la grille
        # StringVar qui contiendra le résultat du satsolver à afficher
        self.solvable = StringVar()
        self.grid = grid

        # création des éléments à afficher
        self.CreerWidgets()

    def CreerWidgets(self):
        """
        Créé et affiche tous les éléments de la fenêtre d'édition de grid
        """
        # Créer trois conteneurs
        aligneGauche = Frame(self, padding=(10, 10, 10, 10))
        aligneGauche.columnconfigure(0, weight=1)
        aligneGauche.grid(row=0, column=0, sticky=N + S + W)

        # Ajouter deux subdivisions de texte dans la barre de gauche
        # Titre principal
        Label(
            aligneGauche, text=self.TITLE, font=("Times New Roman", 18), padding=(0, 0, 0, 10)
        ).grid(row=0, column=0, sticky=N)
        # Créer trois conteneurs
        left_bar = Frame(self, padding=(30, 30, 30, 30))
        left_bar.columnconfigure(0, weight=20)
        left_bar.grid(row=0, column=0, sticky=N + S + W)

        mid_bar = Frame(self)
        mid_bar.columnconfigure(0, weight=20)
        mid_bar.grid(row=0, column=1, sticky=N + S + W + E)

        right_bar = Frame(self, padding=(30, 30, 30, 30))
        right_bar.columnconfigure(0, weight=20)
        right_bar.grid(row=0, column=2, sticky=N + S + W)
        # Créer une nouvelle grille vide avec les bonnes dimensions
        self.dosun_grid = grid(
            self.grid_dimensions[0],
            self.grid_dimensions[1],
            self.solvable,
            self.grid["noir"],
            self.grid["subdivisions"],
            master=aligneGauche,
        )
        self.dosun_grid.grid(row=1, column=0, sticky=N)

        # Ajouter les boutons
        Button(
            aligneGauche,
            text="Créer une subdivision",
            command=self.dosun_grid.faire_subdivision,
        ).grid(row=2, column=0, sticky=N)
        Button(
            aligneGauche,
            text="Rendre la cellule sélectionnée solide",
            command=self.dosun_grid.rendSolides,
        ).grid(row=3, column=0, sticky=N)
        Button(aligneGauche, text="Résoudre!", command=self.dosun_grid.solve).grid(
            row=4, column=0, sticky=N
        )
        # Dessiner la subdivision de texte associée au StringVar self.solvable
        Label(aligneGauche, textvariable=self.solvable, font=("Helvetica", 12)).grid(
            row=5, column=0, sticky=S, pady=(10, 10)
        )

   
    def export_dimacsSAT(self):
        """
        Exporte le fichier DIMACS associé à la grille.
        """
        filename = asksaveasfilename(
            initialdir=".",
            filetypes=(("DIMACS File", "*.cnf"), ("All Files", "*.*")),
            title="Sauvegarder sous format DIMACS",
        )
        if filename:
            grid = self.dosun_grid.get_grid()
            sat = modeliser(grid["width"], grid["height"], grid["subdivisions"], grid["noir"])
            save_dimacs(sat, filename)

    
    def NouvelleGrille(self):
        """
        Ferme la fenêtre d'édition et retourne à la fenêtre de choix de
        dimensions afin de créer une nouvelle grille.
        """
        self.destroy()
        self.master.change(InitFrame, [])

    def CreerMenu(self, root):
        """
        Dessine le "menu" - la barre d'options en haut de la fenêtre.
        """
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Nouvelle grille", command=self.NouvelleGrille)
        fileMenu.add_command(label="Exporter en format DIMACS", command=self.export_dimacsSAT)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quitter", command=quit)
        menubar.add_cascade(label="Menu", menu=fileMenu)
        return menubar


class InitFrame(Frame):
    """
    Fenêtre initiale. Demande à l'utilisateur d'entrer les dimensions de la
    grille à créer.
    """

    TITLE = "Dosun Fuwari Solveur"
    HELPTEXT = "Entrer les dimensions de la grille"

    def __init__(self, master=None):
        """
        Initialisation automatique à la création de la fenêtre d'initialisation
        """
        super().__init__(master, padding=(50, 50, 50, 50))
        # assigner les variables d'instance
        self.master = master
        # variables Tk qui contiendront les valeurs entrées dans les deux champs de
        # texte
        self.x = IntVar()
        self.y = IntVar()
        # Les initialiser à des valeurs cohérentes
        self.x.set(3)
        self.y.set(3)
        # Dessiner la fenêtre
        self.CreerWidgets()

    def CreerWidgets(self):
        """
        Affiche le formulaire de démarrage.
        """
        # Titre
        Label(
            self,
            text=self.TITLE,
            font=("Times New Roman", 18),
            anchor=N,
            padding=(0, 0, 0, 10),
        ).grid(row=0, column=0, columnspan=4, sticky=W + E + N)
        # Texte d'indication
        Label(
            self,
            text=self.HELPTEXT,
            wraplength=300,
            font=("Arial", 10),
            anchor=N,
            justify=LEFT,
            padding=(0, 0, 0, 10),
        ).grid(row=1, column=0, columnspan=4, sticky=W + E)



        # Commande de validation des entrées
        # Source: https://stackoverflow.com/a/31048136
        # Empêche la création de grilles de dimensions non-validés
        vcmd = (self.register(self.validate), "%d", "%P", "%S")

        # Formulaire d'entrée de la largeur de la grille
        Label(self, text="Largeur:").grid(row=2, column=0)
        x_entry = Entry(self, textvariable=self.x, validate="key", validatecommand=vcmd)
        x_entry.grid(row=2, column=1, sticky=W + E)
        # Formulaire d'entrée de la hauteur de la grille
        Label(self, text="Hauteur:").grid(row=3, column=0)
        y_entry = Entry(self, textvariable=self.y, validate="key", validatecommand=vcmd)
        y_entry.grid(row=3, column=1, sticky=W + E)

        # Bouton Start
        sub_btn = Button(
            self,
            text="Commencer",
            command=lambda: self.changeFenetre(int(x_entry.get()), int(y_entry.get())),
        )
        
        sub_btn.grid(row=4, column=1, rowspan=2)
        # Bouton Quit
        sub_btn = Button(
            self,
            text="Quitter",
            command=quit)
        sub_btn.grid(row=6, column=1, rowspan=3)
        
    def validate(self, action, value_if_allowed, text):
        """
        Renvoie True ssi la valeur fournie dans text est convertissable en
        entier et a une valeur autorisée ( > 0 et <= 20)
        Source: https://stackoverflow.com/a/31048136
        """
        # Ne vérifier l'entrée que si on insère un caractère
        if action == "1":
            # N'autoriser que des chiffres
            if text in "0123456789":
                try:
                    # Vérifier que la valeur saisie est un entier et est entre
                    # les bornes choisies
                    return 0 < int(value_if_allowed) <= 20
                except ValueError:
                    # La valeur n'était pas un entier: enpêcher la saisie
                    return False
            else:
                # La valeur n'était pas un chiffre
                return False
        else:
            # Sinon on s'en fout (on n'empêche pas de supprimer, sélectionner
            # comme on veut)
            return True

    def changeFenetre(self, x, y, event=None):
        """
        Détruit la fenêtre initiale et ouvre une fenêtre d'édition avec une
        grid de la taille choisie par l'utilisateur
        """
        self.destroy()
        self.master.change(Editor_Frame, [x, y, {"noir": [], "subdivisions": []}])



    def CreerMenu(self, root):
        """
        Dessine le "menu" - la barre d'options en haut de la fenêtre.
        """
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        return menubar


class Fenetre(Tk):
    """
    Conteneur Tk dans lequel on dessine les différentes fenêtres
    """

    def __init__(self):
        """
        Initialisation automatique de l'instance
        """
        super().__init__()

        # cacher la fenêtre, dessiner la fenêtre et le menu, puis re-afficher
        # la fenêtre
        self.withdraw()

        # Empêcher le redimentionnement de la fenêtre
        self.resizable(False, False)

        # Charger la fenêtre initiale
        self.frame = InitFrame(self)
        menubar = self.frame.CreerMenu(self)
        self.configure(menu=menubar)
        self.frame.pack(expand=1)
        self.deiconify()

    def change(self, frame, args=None):
        """
        Changer la fenêtre affichée à l'écran.
        Arguments:
          - frame: classe de la fenêtre à créer
          - args: liste des arguments à fournir à la classe lors de son
                  instanciation
        """
        # cacher la fenêtre, dessiner la nouvelle fenêtre et le menu, puis
        # re-afficher la fenêtre
        self.withdraw()
        # instancier la nouvelle fenêtre avec les bons arguments
        if len(args) > 0:
            self.frame = frame(*args, master=self)
        else:
            self.frame = frame(master=self)
        menubar = self.frame.CreerMenu(self)
        self.configure(menu=menubar)
        self.update_idletasks()  # vérifier que la fenêtre a bien été mise à jour
        self.frame.pack(expand=1)  # dessiner la nouvelle fenêtre
        self.deiconify()


if __name__ == "__main__":
    root = Fenetre()
    root.title("Dosun-Fuwari Solveur")
    root.mainloop()
