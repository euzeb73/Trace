import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import mayavi.mlab as ma
from position import Angle, Position
import glob


class JeuDeDonnees():
    def __init__(self, dir):
        """dir est le chemin d'accès au répertoire contenant les fichiers des donnees"""
        self.dir: str = dir
        self.filelist: list[str] = glob.glob("{}/*.asc".format(self.dir))
        self.tuiles: list[Terrain] = []
        #Liste des fichier convertie en liste de terrains
        for file in self.filelist:
            terrain = Terrain()
            terrain.loadasc(file, onlyinfo=True)
            self.tuiles.append(terrain)
        #on récupère les données dans une liste de terrains ordonnés
        #Les données ne sont pas lues à ce stade
        self.organise_data()

    def organise_data(self):
        """
        Va récupérer toutes les tuiles et les ranger par y decroissants puis x croissants
        et les retourner dans une liste de Terrains (pour l'instant seulement onlyinfo)
        """
        #fonction de tri
        def tri_selon_attribut(liste : list, attribut: str, croissant=True):
            """Tri des listes de tuiles selon attribut (en format str) (tri par sélection simple)
            Croissant par défaut. Metttre croisant=False pour décroissant
            tri en place + renvoie la liste triée"""
            for i in range(len(liste)):
                terrainymini = liste[i].__dict__[attribut]
                jmini = i
                for j in range(i, len(liste)):
                    if croissant:
                        if liste[j].__dict__[attribut] < terrainymini:
                            terrainymini = liste[j].__dict__[attribut]
                            jmini = j
                    else:
                        if liste[j].__dict__[attribut] > terrainymini:
                            terrainymini = liste[j].__dict__[attribut]
                            jmini = j
                liste[jmini], liste[i] = liste[i], liste[jmini]
            return liste

        #Tri selon ymax
        tri_selon_attribut(self.tuiles, 'ymax', croissant=False)
        #reperage des groupes de ymax + tri selon xmax
        ymax = self.tuiles[0].ymax
        ideb = 0
        for i in range(len(self.tuiles)):
            if self.tuiles[i].ymax != ymax:
                ifin = i
                self.tuiles[ideb:ifin] = tri_selon_attribut(
                    self.tuiles[ideb:ifin], 'xmax')
                ideb = ifin
                ymax = self.tuiles[i].ymax
        ifin = len(self.tuiles)
        self.tuiles[ideb:ifin] = tri_selon_attribut(
            self.tuiles[ideb:ifin], 'xmax')


class Zone():
    def __init__(self, position : Position =Position(45, 5), deltax=1, deltay=1):
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

    def set_rectangle(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.center = 0.5*(xmin+xmax), 0.5*(ymin+ymax)
        self.deltax = xmax-xmin
        self.deltay = ymax-ymin

    def get_rectangle(self):
        """Renvoie le rectangle de la zone dans un tuple
        ordre: xmin, xmax, ymin, ymax"""
        return self.xmin, self.xmax, self.ymin, self.ymax

    def generate_terrain(self, dataset: JeuDeDonnees):
        """Renvoie un Terrain construit à partir de la zone définie par le rectangle
        en prenant les données dans dataset
        La zone peut recouvrir plusieurs tuiles ou être à l'intérieur d'une seule tuile
        """

        #Vérification que la zone ne dépasse pas du dataset
        # considère qu'il n'y a pas de trou de tuile
        # Teste pour les 4 coins de la zone si il y a une tuile qui le contient
        # Peut etre ecrire une méthode de JeuDeDonnees is indataset(x,y)
        #                  TODO

        liste_terrains = []  # les terrains pris vont ici
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
            prendretuile = True
            if bordinf and bordsup and bordgauche and borddroit:  # zone dans tuile
                tocrop=(self.xmin,self.xmax,self.ymin,self.ymax)
            elif bordsup and bordgauche:  # coin haut gauche
                tocrop=(self.xmin,terrain.xmax,terrain.ymin,self.ymax)
            elif bordsup and milieuhoriz:  # bord supérieur, largeur entière
                tocrop=(terrain.xmin,terrain.xmax,terrain.ymin,self.ymax)
            elif bordsup and borddroit:  # coin haut droit
                tocrop=(terrain.xmin,self.xmax,terrain.ymin,self.ymax)
            elif milieuvert and bordgauche:  # bord gauche, hauteur entière
                tocrop=(self.xmin,terrain.xmax,terrain.ymin,terrain.ymax)
            elif milieuvert and milieuhoriz:  # tuile entière
                tocrop=(terrain.xmin,terrain.xmax,terrain.ymin,terrain.ymax) # c'est juste qu'il ne faut rien faire
            elif milieuvert and borddroit:  # bord droit, hauteur entière
                tocrop=(terrain.xmin,self.xmax,terrain.ymin,terrain.ymax)
            elif bordinf and bordgauche:  # coin bas gauche
                tocrop=(self.xmin,terrain.xmax,self.ymin,terrain.ymax)
            elif bordinf and milieuhoriz:  # bord inférieur, largeur entière
                tocrop=(terrain.xmin,terrain.xmax,self.ymin,terrain.ymax)
            elif bordinf and borddroit:  # coin bas droite
                tocrop=(terrain.xmin,self.xmax,self.ymin,terrain.ymax)
            else:
                prendretuile = False #LA tuile ne contient pas de données de la zone

            if prendretuile:
                terrain.loadasc(terrain.path)
                terrain.crop(*tocrop)
                liste_terrains.append(terrain)

        #Maintenant on parcourt la liste de terrains et on fusionne par ligne
        if len(liste_terrains) == 1:  # cas un seul morceau de tuile
            return liste_terrains[0]
        else:
            hmax = liste_terrains[0].ymax
            liste_lignes = []
            terrain_ligne = liste_terrains[0]
            for i in range(1, len(liste_terrains)):
                terrain = liste_terrains[i]
                if terrain.ymax == hmax: #Si on est toujours sur la même ligne
                    terrain_ligne = terrain_ligne.concatenate(
                        terrain, bordure='verticale')
                else: #on change de ligne
                    liste_lignes.append(terrain_ligne.copy())
                    terrain_ligne = liste_terrains[i]
                    hmax=liste_terrains[i].ymax
        # On va maintenant fusionner les lignes pour former le terrain final:
        terrain_final = liste_lignes[0]
        for i in range(1, len(liste_lignes)):
            terrain = liste_lignes[i]
            terrain_final=terrain_final.concatenate(terrain, bordure='horizontale')
        return terrain_final


class Terrain():
    def __init__(self, tableau=[[1, 1], [2, 1]]):
        """ Classe Terrain pour contenir des tableaux d'altitude en fonction de x et y
        à construire à partir de Terrain.loadasc"""
        self.array: np.ndarray = np.array(tableau)
        #Valeurs arbitraires
        self.N, self.M = self.array.shape
        self.xmin = -100
        self.xmax = 100
        self.ymin = -100
        self.ymax = 100
        self.cellsize = 1

    def loadasc(self, path, onlyinfo=False):
        self.path=path
        file = open(path)
        #Header
        self.M = int(file.readline()[13:])  # nb colonnes
        self.N = int(file.readline()[13:])  # nb lignes
        self.xmin = float(file.readline()[13:])  # en m
        self.ymin = float(file.readline()[13:])  # en m
        self.cellsize = float(file.readline()[13:])  # pas des données
        self.xmax = self.xmin+self.M*self.cellsize
        self.ymax = self.ymin+self.N*self.cellsize
        file.readline()
        if not onlyinfo:
            #tableau des altitudes
            alti = -1000*np.ones((self.N, self.M))
            i = 0  # la ligne
            for line in file:
                line = line[1:]
                liste = line.split(' ')
                for j in range(len(liste)):  # la colonne
                    alti[i][j] = float(liste[j])
                i += 1
            file.close()
            self.array = alti

    def writeasc(self, path='./newasc.asc'):
        """
        fabrique un fichier asc avec chemin d'accès path à partir des attributs
        self.array doit contenit le tableau des altitudes à écrire.
        """
        header = 'ncols'+8*' '+str(self.M)+'\n'
        header = header+'nrows'+8*' '+str(self.N)+'\n'
        header = header+'xllcorner'+4*' '+'{:f}'.format(self.xmin)+'\n'
        header = header+'yllcorner'+4*' '+'{:f}'.format(self.ymin)+'\n'
        header = header+'cellsize'+5*' '+'{:f}'.format(self.cellsize)+'\n'
        header = header+'NODATA_value  -99999.00\n'
        fich = open(path, 'w')
        fich.write(header)
        for i in range(self.N):  # lignes
            for j in range(self.M):
                fich.write(' {:.2f}'.format(self.array[i][j]))
            fich.write('\n')
        fich.close()

    def plot(self, show=True):
        fig = plt.figure()
        axes = plt.axes(xlim=(self.xmin, self.xmax),
                        ylim=(self.ymin, self.ymax))
        axes.imshow(self.array, aspect='auto', extent=(self.xmin, self.xmax, self.ymin, self.ymax), alpha=1,
                    zorder=0, origin='upper', cmap=cm.terrain)
        axes.axis('equal')
        if show:
            plt.show()
        return fig

    def plot3D(self, Zfactor=3, show=True):
        """le Zfactor, c'est pour mieux voir le relief
        Zfactor=1 réalité
        par défaut Zfactor = 3"""
        X = self.xmin+self.cellsize*np.arange(self.M)
        Y = self.ymin+self.cellsize*np.arange(self.N)
        X, Y = np.meshgrid(X, Y)
        X = X.transpose()  # là y'a transposition d'après le manuel.
        Y = Y.transpose()
        fig = ma.figure()
        ma.surf(X, Y, self.array*Zfactor, colormap='gist_earth')
        if show:
            ma.show()
        return fig

    def xtoj(self, x):
        """Renvoie la coordonnée j (colonne) correspondant à la position x
        (arrondi avec round)"""
        assert self.xmin <= x <= self.xmax
        return int(round((x-self.xmin)/self.cellsize))

    def ytoi(self, y):
        """Renvoie la coordonnée i (ligne) correspondant à la position y
        (arrondi avec round)"""
        assert self.ymin <= y <= self.ymax
        return int(round((self.ymax-y)/self.cellsize))

    def isinTerrain(self, x, y):
        return self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax

    def crop(self, xmin, xmax, ymin, ymax):
        """
        Rétrécit le terrain à la taille du rectangle xmin,xmax,ymin,ymax
        """
        assert self.isinTerrain(xmin, ymin) and self.isinTerrain(xmax, ymax)
        jmin = self.xtoj(xmin)
        jmax = self.xtoj(xmax)
        imin = self.ytoi(ymax)  # coin en haut (ymax)
        imax = self.ytoi(ymin)  # coin en bas (ymin)
        self.array = self.array[imin:imax+1,jmin:jmax+1]
        self.N, self.M = self.array.shape
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.cropwarning = True #le path ne veut plus dire grand chose par exemple

    def concatenate(self, other, bordure='verticale'):
        """concatene 2 terrains le long de leur bordure: 'verticale' ou 'horizontale'
        renvoie le terrain concatené
        le terrain qui appelle la méthode est au dessus/à gauche du terrain en paramètre
        """
        if bordure == 'verticale':
            assert self.N == other.N  # même nb de lignes si on veut concaténer
            assert self.ymin == other.ymin  # et aussi alignés
            # self à gauche, other à droite
            tab = np.concatenate((self.array, other.array), axis=1)
            fusion = Terrain(tab)
            fusion.xmin = self.xmin
            fusion.xmax = other.xmax
            fusion.ymin = self.ymin
            fusion.ymax = self.ymax
            fusion.cellsize = self.cellsize
        else:
            assert self.M == other.M  # même nb de colonnes si on veut concaténer
            assert self.xmin == other.xmin  # et aussi alignés
            # self en haut, other en bas
            tab = np.concatenate((self.array, other.array), axis=0)
            fusion = Terrain(tab)
            fusion.xmin = self.xmin
            fusion.xmax = self.xmax
            fusion.ymax = self.ymax
            fusion.ymin = other.ymin
            fusion.cellsize = self.cellsize
        return fusion

    def copy(self):
        """Renvoie une copy du terrain
        """
        copie=Terrain()
        copie.__dict__=self.__dict__
        copie.array=self.array.copy()
        return copie
