import time
from rectgle import Rectgle
from terrain import Terrain
from queue import PriorityQueue
import numpy as np
import mayavi.mlab as ma
import matplotlib.pyplot as plt
from math import tan, sqrt
from calculateur import Astar, Calculateur, Dijkstra

RACINEDEDEUX = sqrt(2)


class Traces():
    def __init__(self, terrain: Terrain, points: list, largeurs: list = []):
        """ Trace attachée à terrain 
        points est une liste de (x,y) d'au moins 2 points (départ arrivée)
        largeurs est une liste de floats largeurs de longueur len(points)-1 qui représente
        la zone d'évolution autour de la droite (points[i] points[i+1]) soit
        les 2 droites parallèles à -largeur[i]/2 et + largeur[i]/2    
        
        Pour définir la trace à partir de rectangles utiliser set_rects
        """
        self.terrain = terrain
        self.points = points
        largeurmax = RACINEDEDEUX * \
            max(self.terrain.ymax-self.terrain.ymin,
                self.terrain.xmax-self.terrain.xmin)
        if largeurs == []:
            self.largeurs = [largeurmax for i in range(
                len(self.points)-1)]  # par défaut tout le terrain
        else:
            self.largeurs = largeurs
        assert len(self.largeurs) == len(self.points)-1
        self.generate_rects()

    def set_rects(self, rectangles):
        self.rects: list[Rectgle] = rectangles

    def generate_rects(self):
        """calcule les rectangles d'évolution de la trace
        il y en a len(self.points) -1 = len(largeurs)
        le self.rects[i] a la largeur self.largeur[i] et contient self.points[i] et self.points[i+1]
        le rectangle est donné par 3 de ses points A,B,D. C (non donné est tel que vec AC=vec AB+vec AD)
        on rajoute une marge en longueur de self.cellsize pour avoir l'arrivée tjs dans le rectangle 
        même après approximation
        """
        self.rects = []
        for i in range(len(self.points)-1):
            self.rects.append(Rectgle(
                self.points[i], self.points[i+1], self.largeurs[i], self.terrain.cellsize))

    def ijisinrect(self, i, j, rect: Rectgle):
        """Retourne True si le points i,j est dans rect défini par les coordonnées de A,B et D
        False sinon"""
        x, y = self.terrain.ijtoxy(i, j)
        return rect.contains(x, y)

    def calculate_trace(self, methode='Dijkstra'):
        #Dans l'idée: calculer le chemin entre chaque points de la liste self.points
        #sous traiter ce calcul à une une calsse de calculateurs avec des héritages
        #genre class Calculateur(): (il faudra lui fournir le terrain pour les conversions)
        #puis class Djikstra(Calculateur)
        # et dans le calculateur une méthode .generate_path qui renvoie un chemin
        # dans le calculateur, il faudrait tenir compte des largeurs avec une méthode qui
        # élimine les points hors de ces largeurs (genr en les mettant float('inf') de le terrain
        args = 0, 0, 0, 0
        # dictionnaire avec les calculateurs
        calcdict = {'Dijkstra': Dijkstra, 'Astar': Astar, 'A*': Astar}
        if methode not in calcdict:
            print('méthode de calcul non supportée méthode supportées:\n')
            print(calcdict.keys())
            return

        print('Calcul de la Trace')
        t1 = time.perf_counter()
        for i in range(len(self.points)-1):
            depart = self.points[i]
            arrivee = self.points[i+1]
            rectangle = self.rects[i]
            terrain = self.terrain
            args = depart, arrivee, rectangle, terrain
            calculateur = calcdict[methode](*args)
            x, y, z = calculateur.calculate_path()
            if i == 0:
                self.tracexyz = x, y, z
            else:
                debuttrace = self.tracexyz
                oldx, oldy, oldz = debuttrace
                self.tracexyz = np.concatenate((oldx, x)),\
                    np.concatenate((oldy, y)),\
                    np.concatenate((oldz, z))
        t2 = time.perf_counter()
        print('Calcul fini en {:.2f}s'.format(t2-t1))

    def plot3D(self, figure, Zfactor):
        """affiche la trace sur la figure (mayaplot 3D)
        
        TODO faire un affichage des rectangles:
        -Avec une surface calculée à plot avec de l'alpha (lent ?)
        -Faire un cadre avec des lignes plot3d
        ------
        |    |      de alt 0 à 5000 ou zmin à zmax
        ------
        ou
        ------
        |////|      de alt 0 à 5000 ou zmin à zmax
        ------
        """

        x, y, z = self.tracexyz
        zplot = Zfactor*z.copy()
        ma.figure(figure)
        ma.plot3d(x, y, zplot, tube_radius=1, color=(1, 0, 1), figure=figure)
        ma.text3d(x[0], y[0], zplot[0]+Zfactor*10, 'Depart',
                  figure=figure, scale=(20, 20, 20), color=(1, 0, 0))
        fin = len(x)-1
        ma.text3d(x[fin], y[fin], zplot[fin]+Zfactor*10, 'Arrivee',
                  figure=figure, scale=(20, 20, 20), color=(1, 0, 0))
        ma.show()

    def plot2D(self, axes):
        """affiche la trace sur la figure (2D)"""
        x, y, z = self.tracexyz
        axes.plot(x, y, color=(1, 0, 1))
        # plt.show()
