from terrain import Terrain
from position import Position
from dataset import JeuDeDonnees


class Zone():
    def __init__(self, position: Position = Position(45, 5), deltax=1, deltay=1):
        """Définit une zone d'étude centrée sur position (type Position)
        et de taille deltax par deltay (en m)"""
        self.position: Position = position
        self.center: tuple(float) = position.get_xy()
        self.deltax = deltax
        self.deltay = deltay
        # Calcul du Rectangle correspondant
        xcenter, ycenter = self.center
        self.xmin = xcenter-0.5*deltax
        self.xmax = xcenter+0.5*deltax
        self.ymin = ycenter-0.5*deltay
        self.ymax = ycenter+0.5*deltay

    def set_rectangle(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.center = 0.5*(xmin+xmax), 0.5*(ymin+ymax)
        self.deltax = xmax-xmin
        self.deltay = ymax-ymin

    def get_rectangle(self):
        """Renvoie le rectangle de la zone dans un tuple
        ordre: xmin, ymin, xmax, ymax"""
        return self.xmin, self.ymin, self.xmax, self.ymax

    def generate_terrain(self, dataset: JeuDeDonnees) -> Terrain:
        """Renvoie un Terrain construit à partir de la zone définie par le rectangle
        en prenant les données dans dataset
        La zone peut recouvrir plusieurs tuiles ou être à l'intérieur d'une seule tuile
        """

        #Vérification que la zone ne dépasse pas du dataset
        # considère qu'il n'y a pas de trou de tuile
        # Teste pour les 4 coins de la zone si il y a une tuile qui le contient
        # Peut etre ecrire une méthode de JeuDeDonnees is indataset(x,y)
        #                  TODO

        liste_terrains: list[Terrain] = []  # les terrains pris vont ici
        for terrain in dataset.tuiles:
            bordsup = terrain.ymin <= self.ymax <= terrain.ymax  # bord sup zone intersect tuile
            bordinf = terrain.ymin <= self.ymin <= terrain.ymax  # bord inf zone intersect tuile
            # tuile dans la zone en vert
            milieuvert = self.ymin <= terrain.ymin and self.ymax >= terrain.ymax
            # bord droit zone intersect tuile
            borddroit = terrain.xmin <= self.xmax <= terrain.xmax
            # bord gauche zone intersect tuile
            bordgauche = terrain.xmin <= self.xmin <= terrain.xmax
            # tuile dans la zone en horiz
            milieuhoriz = self.xmin <= terrain.xmin and self.xmax >= terrain.xmax

            # il y en a au moins 2 de vrais
            if int(bordsup or bordinf)+int(milieuvert) + int(milieuhoriz)+int(borddroit or bordgauche) >= 2:
                prendretuile = True
                tocrop = [terrain.xmin, terrain.xmax,
                          terrain.ymin, terrain.ymax]
                if bordsup:
                    tocrop[3] = self.ymax
                if bordinf:
                    tocrop[2] = self.ymin
                if bordgauche:
                    tocrop[0] = self.xmin
                if borddroit:
                    tocrop[1] = self.xmax
            else:
                prendretuile = False

            if prendretuile:
                terrain.loadasc(terrain.path)
                terrain.crop(*tocrop)
                liste_terrains.append(terrain)

        #Maintenant on parcourt la liste de terrains et on fusionne par ligne
        if len(liste_terrains) == 1:  # cas un seul morceau de tuile
            return liste_terrains[0]
        else:
            epsilon = liste_terrains[0].cellsize  # pour comparer des longueurs
            hmax = liste_terrains[0].ymax
            liste_lignes = []
            terrain_ligne = liste_terrains[0]
            for i in range(1, len(liste_terrains)):
                terrain = liste_terrains[i]
                if abs(terrain.ymax - hmax) < epsilon:  # Si on est toujours sur la même ligne
                    terrain_ligne = terrain_ligne.concatenate(
                        terrain, bordure='verticale')
                else:  # on change de ligne
                    liste_lignes.append(terrain_ligne.copy())
                    terrain_ligne = liste_terrains[i]
                    hmax = liste_terrains[i].ymax
            liste_lignes.append(terrain_ligne)
        # On va maintenant fusionner les lignes pour former le terrain final:
        if len(liste_lignes) >= 2:  # il faut au moins 2 lignes pour fusionner
            terrain_final: Terrain = liste_lignes[0]
            for i in range(1, len(liste_lignes)):
                terrain = liste_lignes[i]
                terrain_final: Terrain = terrain_final.concatenate(
                    terrain, bordure='horizontale')
        else:
            terrain_final = terrain_ligne
        return terrain_final
