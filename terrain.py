import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import mayavi.mlab as ma
from position import Angle, Position
import glob

class Ascfile():
    def __init__(self,path):
        self.path=path
        self.read_info()
    def read_info(self):
        file = open(self.path)
        #Header
        self.M = int(file.readline()[13:])  # nb colonnes
        self.N = int(file.readline()[13:])  # nb lignes
        self.xmin = float(file.readline()[13:])  # en m
        self.ymax = float(file.readline()[13:])  # en m
        self.cellsize = float(file.readline()[13:])  # pas des données
        self.xmax = self.xmin+self.M*self.cellsize
        self.ymin = self.ymax-self.N*self.cellsize
        file.readline()
        file.close()
    def get_data(self):
        """Lit les altitudes et renvoie un array contenant les altitudes"""
        file = open(self.path)
        #Header
        for i in range(6):
            file.readline()
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
        return alti


class JeuDeDonnees():
    def __init__(self, dir):
        """dir est le chemin d'accès au répertoire contenant les fichiers des donnees"""
        self.dir=dir
        filelist=glob.glob("{}/*.asc".format(self.dir))
        self.filelist=[Ascfile(file) for file in filelist]
    def scrap_data(self):
        same=True
        cellsize=self.filelist[0].cellsize
        for file in self.filelist:
            if file.cellsize != cellsize:
                same=False
        print(same)

class Zone():
    def __init__(self, position=Position(45,5), deltax=1, deltay=1):
        """Définit une zone d'étude centrée sur position (type Position)
        et de taille deltax par deltay (en m)"""
        self.position = position
        self.center = position.get_xy()
        self.deltax = deltax
        self.deltay = deltay
        # Calcul du Rectangle correspondant
        xcenter,ycenter=self.center
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
        return self.xmin,self.xmax,self.ymin,self.ymax
    


class Terrain():
    def __init__(self, tableau=[[1, 1], [2, 1]]):
        """ Classe Terrain pour contenir des tableaux d'altitude en fonction de x et y
        à construire à partir de Terrain.loadasc"""
        self.array = np.array(tableau)
        #Valeurs arbitraires
        self.N, self.M = self.array.shape
        self.xmin = -100
        self.xmax = 100
        self.ymin = -100
        self.ymax = 100
        self.cellsize = 1

    def loadasc(self, path):
        file=Ascfile(path)
        self.M = file.M  # nb colonnes
        self.N = file.N  # nb lignes
        self.xmin = file.xmin  # en m
        self.ymax = file.ymax  # en m
        self.cellsize = file.cellsize  # pas des données
        self.xmax = self.xmin+self.M*self.cellsize
        self.ymin = self.ymax-self.N*self.cellsize
        self.array = file.get_data()
        # file = open(path)
        # #Header
        # self.M = int(file.readline()[13:])  # nb colonnes
        # self.N = int(file.readline()[13:])  # nb lignes
        # self.xmin = float(file.readline()[13:])  # en m
        # self.ymax = float(file.readline()[13:])  # en m
        # self.cellsize = float(file.readline()[13:])  # pas des données
        # self.xmax = self.xmin+self.M*self.cellsize
        # self.ymin = self.ymax-self.N*self.cellsize
        # file.readline()
        # #tableau des altitudes
        # alti = -1000*np.ones((self.N, self.M))
        # i = 0  # la ligne
        # for line in file:
        #     line = line[1:]
        #     liste = line.split(' ')
        #     for j in range(len(liste)):  # la colonne
        #         alti[i][j] = float(liste[j])
        #     i += 1
        # file.close()
        # self.array = alti

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

    def select_points(self):
        fig = self.plot()
        axes = 0
