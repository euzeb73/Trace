import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import mayavi.mlab as ma
from position import Angle, Position
import glob


class Terrain():
    def __init__(self, tableau=[[1, 1], [2, 1]]):
        """ Classe Terrain pour contenir des tableaux d'altitude en fonction de x et y
        à construire à partir de Terrain.loadasc"""
        self.array: np.ndarray = np.array(tableau)
        # Valeurs arbitraires
        self.N, self.M = self.array.shape
        self.xmin = -100
        self.xmax = 100
        self.ymin = -100
        self.ymax = 100
        self.cellsize = 1

    def loadasc(self, path, onlyinfo=False):
        self.path = path
        file = open(path)
        # Header
        self.M = int(file.readline()[13:])  # nb colonnes
        self.N = int(file.readline()[13:])  # nb lignes
        self.xmin = float(file.readline()[13:])  # en m
        self.ymin = float(file.readline()[13:])  # en m
        self.cellsize = float(file.readline()[13:])  # pas des données
        self.xmax = self.xmin+self.M*self.cellsize
        self.ymax = self.ymin+self.N*self.cellsize
        file.readline()
        if not onlyinfo:
            # tableau des altitudes
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
        # pour que ça colle transposition+renversement des 2 axes
        tabalti = np.flip(self.array.transpose(), 1)*Zfactor
        ma.surf(X, Y, tabalti, colormap='gist_earth')
        if show:
            ma.show()
        return fig, Zfactor

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

    def xytoij(self, x, y):
        return self.ytoi(y), self.xtoj(x)

    def ijton(self,i,j):
        return i*self.M+j
    
    def xyton(self, x, y):
        """Renvoie la coordonnée n=i*M+j correspondant à la position x,y"""
        i, j = self.xytoij(x, y)
        return self.ijton(i,j)

    def ntoij(self, n):
        """renvoie les coordonnées i,j correspondant à n=i*M+j"""
        return n//self.M, n % self.M

    def ijtoxy(self, i, j):
        """renvoie les coordonnées géographiques quand on donne les indices du tableau
        tuple x,y"""
        x = j*self.cellsize+self.xmin
        y = self.ymax-i*self.cellsize
        return x, y

    def altipointxy(self,x,y):
        """renvoie l'altitude du point de coordonnées x,y"""
        assert self.xmin<=x<=self.xmax and self.ymin<=y<=self.ymax #dans le terrain
        i,j=self.xytoij(x,y)
        return self.array[i,j]

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
        self.array = self.array[imin:imax+1, jmin:jmax+1]
        self.N, self.M = self.array.shape
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.cropwarning = True  # le path ne veut plus dire grand chose par exemple

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
        copie = Terrain()
        copie.__dict__ = self.__dict__
        copie.array = self.array.copy()
        return copie
