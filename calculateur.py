
from typing import Tuple
from rectgle import Rectgle
from terrain import Terrain
from math import tan, sqrt
from queue import PriorityQueue
import numpy as np

RACINEDEDEUX = sqrt(2)


class Calculateur():
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        """calcule la trace entre depart et arrivee dans le rectangle, sur le terrain
        depart et arrivee sont deux tuple avec les coord x,y des points"""
        self.rectangle = rectangle
        self.terrain = terrain
        self.depart = depart
        self.arrivee = arrivee

    def ijisinrect(self, i, j):
        """Retourne True si le point i,j est dans self.rectangle
        False sinon"""
        x, y = self.terrain.ijtoxy(i, j)
        return self.rectangle.contains(x, y)

    def voisins(self, n):
        """renvoie une liste des voisins de n
        format liste de tuples (i,j)"""
        i, j = self.terrain.ntoij(n)
        N = self.terrain.N
        M = self.terrain.M
        vois = []
        for deltai in [-1, 0, 1]:  # les voisins diagonales comprises
            for deltaj in [-1, 0, 1]:
                ipastropgrand = i+deltai <= N-1
                ipastroppetit = i+deltai >= 0
                jpastropgrand = j+deltaj <= M-1
                jpastroppetit = j+deltaj >= 0
                pas0 = deltai != 0 or deltaj != 0  # pour enlever 0,0
                # Si le voisin est dans l'espace sélectionné
                dansrec = self.ijisinrect(i+deltai, j+deltaj)
                if ipastropgrand and ipastroppetit and jpastropgrand and jpastroppetit and pas0 and dansrec:
                    vois.append((i+deltai, j+deltaj))
        return vois

    def calculate_path(self) -> Tuple[list]:
        """ Calcule le chemin selon la méthode du calculateur entre self.depart
        et self.arrivee tout en restant dans self.rectangle
        renvoie x,y,z les 3 listes de points du chemin"""

        print("non implémenté dans la classe mère")
        return [], [], []


class Dijkstra(Calculateur):
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        super().__init__(depart, arrivee, rectangle, terrain)
        self.ImportanceDeniv = 10
        self.departn = self.terrain.xyton(*self.depart)
        self.arriveen = self.terrain.xyton(*self.arrivee)

    def horiz_penalty(self, i, j, ivois=None, jvois=None):
        """renvoie la pénalitée de distance pour un déplacement horizontal
        ajouté au cout d'un sommet en plus du dénivelé"""
        if abs(i-ivois)+abs(j-jvois) == 1:
            penalitedistance = self.terrain.cellsize
        else:
            penalitedistance = self.terrain.cellsize*RACINEDEDEUX
        return penalitedistance

    def voisins_couts(self, n):
        """ Renvoie une liste des voisins de i,j avec les couts de déplacement
        donnés par graph. Format [[voisin1,cout1],[voisin2,cout2],...] """
        graph = self.terrain.array
        i, j = self.terrain.ntoij(n)
        vois = self.voisins(n)
        voiscouts = []
        for voisin in vois:
            ivois, jvois = voisin
            # 0 si plat ou descente, le deniv sinon
            cout = max(graph[ivois][jvois]-graph[i][j], 0)

            # Pénaliser les grandes pentes
            # TODO à mettre en paramètre
            pentemax = 15
            if cout >= self.terrain.cellsize*tan(pentemax*3.14/180):
                cout = cout*10
            penalitedistance = self.horiz_penalty(i, j, ivois, jvois)
            cout = self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([self.terrain.ijton(*voisin), cout])
        return voiscouts

    def calcul_chemin(self, sommet_start, sommet_stop):
        graph = self.terrain.array
        #Init de la file d'attente
        attente = PriorityQueue()
        attente.put((0, sommet_start))
        #couplée avec une table des valeurs pour connaitre les valeurs des voisins
        attenteval = {}
        attenteval[sommet_start] = 0
        #Table des distances
        Ndeux = graph.shape[0]*graph.shape[1]
        table_dists = [float('inf') for i in range(Ndeux)]
        # table_dists[sommet_start]=0
        previous = dict()  # Un dictionnaire avec le sommet précédent pour reconstruire le chemin
        visite = []  # Liste pour tous les sommets visités
        while table_dists[sommet_stop] == float('inf'):
            # on récupère le sommet qui est prioritaire dans la file
            dist_sommet, sommet = attente.get()
            # Si le sommet n'a jamais été visité (normalement ne doit pas arriver mais à cause de la non suppression de la file ça arrive)
            if table_dists[sommet] == float('inf'):
                for voisin, dist in self.voisins_couts(sommet):
                    # Si on n'a pas encore visité le voisin
                    if table_dists[voisin] == float('inf'):
                        if voisin not in attenteval.keys():  # Voisin pas encore en attente de visite
                            attenteval[voisin] = dist_sommet + \
                                dist  # on donne la valeur
                            attente.put((dist_sommet+dist, voisin))
                            # Et on change de prédécesseur
                            previous[voisin] = sommet
                        elif dist_sommet+dist < attenteval[voisin]:
                            # on remplace si c'est plus court
                            attenteval[voisin] = dist_sommet+dist
                            attente.put((dist_sommet+dist, voisin))
                            # Et on change de prédécesseur
                            previous[voisin] = sommet
                table_dists[sommet] = dist_sommet  # le sommet qui a été choisi
                # del(attenteval[sommet])
                visite.append(sommet)
        #Reconstruire le chemin avec les listes des précédents:
        chemin = []
        sommet = sommet_stop
        while sommet != sommet_start:
            chemin.append(sommet)
            sommet = previous[sommet]
        chemin.append(sommet_start)
        chemin.reverse()  # pour le mettre dans l'ordre
        return chemin, visite, table_dists[sommet_stop]

    def path_to_xyz(self, chemin):
        """self.tracexyz 3 listes contenant les coordonnées x,y et z de chaque poinnt du chemin
        point indice i de chemin(liste de points sur le array) de coordonnées x[i],  y[i] , z[i]"""
        xchem = []
        ychem = []
        zchem = []
        for pointn in chemin:
            i, j = self.terrain.ntoij(pointn)
            x, y = self.terrain.ijtoxy(i, j)
            z = self.terrain.altipointxy(x, y)
            xchem.append(x)
            ychem.append(y)
            zchem.append(z)
        #self.tracexyz = np.array(xchem),np.array(ychem),np.array(zchem)
        return np.array(xchem), np.array(ychem), np.array(zchem)

    def calculate_path(self):
        chemin = self.calcul_chemin(self.departn, self.arriveen)[0]
        x, y, z = self.path_to_xyz(chemin)
        return x, y, z


class Astar(Dijkstra):
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        super().__init__(depart, arrivee, rectangle, terrain)
        # pour Astar on compare 1m de deniv avec 10m d'écart à vol d'oiseau ?
        self.ImportanceDeniv = 10

    def distance_eucl(self, i1, j1, i2, j2):
        """renvoie la distance euclidienne à vol d'oiseau entre
        i1,j1 et i2,j2"""
        x1, y1 = self.terrain.ijtoxy(i1, j1)
        x2, y2 = self.terrain.ijtoxy(i2, j2)
        return sqrt((x2-x1)**2+(y2-y1)**2)

    def horiz_penalty(self, i, j, ivois=None, jvois=None):
        """renvoie la pénalitée de distance  correspondant à la distance à l'arrivé
        à vol d'oiseau qui s'ajoutera au dénivelé pour le cout du sommet"""
        iarriv, jarriv = self.terrain.ntoij(self.arriveen)
        return self.distance_eucl(ivois, jvois, iarriv, jarriv)
