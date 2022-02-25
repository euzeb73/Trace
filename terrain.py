from distutils import filelist
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import mayavi.mlab as ma
from position import Angle, Position
import glob


class JeuDeDonnees():
    def __init__(self, dir):
        """dir est le chemin d'accès au répertoire contenant les fichiers des donnees"""
        self.dir=dir
        self.filelist=glob.glob("{}/*.asc".format(self.dir))
        self.terrainlist=[]
        for file in filelist:
            terrain=Terrain()
            terrain.loadasc(file,onlyinfo = True)
            self.terrainlist.append(terrain)
    def scrap_data(self):
        same=True
        cellsize=self.terrainlist[0].cellsize
        for terrain in self.terrainlist:
            if terrain.cellsize != cellsize:
                same=False
        print(same)

class Zone():
    def __init__(self, dataset:JeuDeDonnees,position=(45,5), deltax=1, deltay=1):
        """Définit une zone d'étude centrée sur position (type Position)
        et de taille deltax par deltay (en m)"""
        self.position = Position(position)
        self.center = position.get_xy()
        self.deltax = deltax
        self.deltay = deltay
        # Calcul du Rectangle correspondant
        xcenter,ycenter=self.center
        self.xmin = xcenter-0.5*deltax
        self.xmax = xcenter+0.5*deltax
        self.ymin = ycenter-0.5*deltay
        self.ymax = ycenter+0.5*deltay
        self.dataset= dataset
    def set_rectangle(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.center = 0.5*(xmin+xmax), 0.5*(ymin+ymax)
        self.deltax = xmax-xmin
        self.deltay = ymax-ymin
    def set_dataset(self,dataset):
        """Associe un jeu de données dataset à la zone (dataset de type JeuDeDonnees)
        Nécessaire si on veut extraire les données de la zone"""
        self.dataset=dataset
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

    def loadasc(self, path,onlyinfo=False):
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
        header='ncols'+8*' '+str(self.M)+'\n'
        header=header+'nrows'+8*' '+str(self.N)+'\n'
        header=header+'xllcorner'+4*' '+'{:f}'.format(self.xmin)+'\n'
        header=header+'yllcorner'+4*' '+'{:f}'.format(self.ymin)+'\n'
        header=header+'cellsize'+5*' '+'{:f}'.format(self.cellsize)+'\n'
        header=header+'NODATA_value  -99999.00\n'
        fich=open(path,'w')
        fich.write(header)
        for i in range(self.N): #lignes
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

    def select_points(self):
        fig = self.plot()
        axes = 0
