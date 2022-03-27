
from typing import Tuple
from rectgle import Rectgle
from terrain import Terrain
from math import tan, sqrt
from queue import PriorityQueue
import numpy as np

RACINEDEDEUX = sqrt(2)


class Calculateur():
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        """calcule la trace entre depart et arrivee dans le rectangle, sur le terrain"""
        self.rectangle = rectangle
        self.terrain = terrain
        self.depart = depart
        self.departn = self.terrain.xyton(*self.depart)
        self.arrivee = arrivee
        self.arriveen = self.terrain.xyton(*self.arrivee)

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
        return [],[],[]


class Dijkstra(Calculateur):
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        super().__init__(depart, arrivee, rectangle, terrain)
        self.ImportanceDeniv = 10

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
            if abs(i-ivois)+abs(j-jvois) == 1:
                penalitedistance = self.terrain.cellsize
            else:
                penalitedistance = self.terrain.cellsize*RACINEDEDEUX
            cout = self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([self.terrain.ijton(*voisin), cout])
        return voiscouts

    def dijkstra(self,sommet_start,sommet_stop):
        graph=self.terrain.array
        #Init de la file d'attente
        attente=PriorityQueue()
        attente.put((0,sommet_start))
        #couplée avec une table des valeurs pour connaitre les valeurs des voisins
        attenteval={}
        attenteval[sommet_start]=0
        #Table des distances
        Ndeux=graph.shape[0]*graph.shape[1]
        table_dists=[float('inf') for i in range(Ndeux)]
        # table_dists[sommet_start]=0
        previous=dict() #Un dictionnaire avec le sommet précédent pour reconstruire le chemin
        visite=[] #Liste pour tous les sommets visités
        while table_dists[sommet_stop]==float('inf'):
            dist_sommet,sommet=attente.get() #on récupère le sommet qui est prioritaire dans la file
            if table_dists[sommet]==float('inf'): #Si le sommet n'a jamais été visité (normalement ne doit pas arriver mais à cause de la non suppression de la file ça arrive)
                for voisin,dist in self.voisins_couts(sommet): 
                    if table_dists[voisin]==float('inf'):#Si on n'a pas encore visité le voisin
                        if voisin not in attenteval.keys(): #Voisin pas encore en attente de visite
                            attenteval[voisin]=dist_sommet+dist #on donne la valeur
                            attente.put((dist_sommet+dist,voisin))
                            previous[voisin]=sommet #Et on change de prédécesseur
                        elif dist_sommet+dist<attenteval[voisin]:
                            attenteval[voisin]=dist_sommet+dist #on remplace si c'est plus court
                            attente.put((dist_sommet+dist,voisin))
                            previous[voisin]=sommet #Et on change de prédécesseur
                table_dists[sommet]=dist_sommet #le sommet qui a été choisi
                # del(attenteval[sommet])
                visite.append(sommet)
        #Reconstruire le chemin avec les listes des précédents:
        chemin=[]
        sommet=sommet_stop
        while sommet!=sommet_start:
            chemin.append(sommet)
            sommet=previous[sommet]
        chemin.append(sommet_start)
        chemin.reverse() #pour le mettre dans l'ordre
        return chemin,visite,table_dists[sommet_stop]

    def path_to_xyz(self,chemin):
        """self.tracexyz 3 listes contenant les coordonnées x,y et z de chaque poinnt du chemin
        point indice i de chemin(liste de points sur le array) de coordonnées x[i],  y[i] , z[i]"""
        xchem=[]
        ychem=[]
        zchem=[]
        for pointn in chemin:
            i,j=self.terrain.ntoij(pointn)
            x,y=self.terrain.ijtoxy(i,j)
            z=self.terrain.altipointxy(x,y)
            xchem.append(x)
            ychem.append(y)
            zchem.append(z)
        #self.tracexyz = np.array(xchem),np.array(ychem),np.array(zchem)
        return np.array(xchem),np.array(ychem),np.array(zchem)

    def calculate_path(self):
        chemin=self.dijkstra(self.departn,self.arriveen)[0]
        x,y,z=self.path_to_xyz(chemin)
        return x,y,z