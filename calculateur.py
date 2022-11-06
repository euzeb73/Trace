from operator import ne
from turtle import pos
from typing import Tuple
from rectgle import Rectgle
from terrain import Terrain
from math import tan, sqrt, pi, cos, sin
from queue import PriorityQueue
import numpy as np
#DEbug
import matplotlib.pyplot as plt


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

    def path_to_xyz(self, chemin):
        """Chaque point n du chemin est converti en un point x,y,z
        Renvoie un tuple de array avec listes de x,y,z
        un point indice i de chemin(liste de points sur le array) 
        a pour coordonnées x[i],  y[i] , z[i]"""
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
            # TODO utiliser self.pente_trace
            pentemax = 15
            if cout >= self.terrain.cellsize*tan(pentemax*3.14/180):
                cout = cout*10
            penalitedistance = self.horiz_penalty(i, j, ivois, jvois)
            cout = self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([self.terrain.ijton(*voisin), cout])
        return voiscouts

    def heuristique(self, sommet):
        return 0

    def calcul_chemin(self, sommet_start, sommet_stop):
        graph = self.terrain.array
        #Init de la file d'attente
        attente = PriorityQueue()
        attente.put((0, sommet_start))
        #Table des distances
        Ndeux = graph.shape[0]*graph.shape[1]
        table_dists = [float('inf') for i in range(Ndeux)]
        #liste des sommets deja visite
        dejavisite = [False for i in range(Ndeux)]
        # table_dists[sommet_start]=0
        previous = dict()  # Un dictionnaire avec le sommet précédent pour reconstruire le chemin
        visite = []  # Liste pour tous les sommets visités
        while table_dists[sommet_stop] == float('inf'):
            # on récupère le sommet qui est prioritaire dans la file
            dist_sommet, sommet = attente.get()
            # Si le sommet n'a jamais été visité (normalement ne doit pas arriver mais à cause de la non suppression de la file ça arrive)
            if not dejavisite[sommet]:
                for voisin, dist in self.voisins_couts(sommet):
                    if dist_sommet+dist < table_dists[voisin]:
                        attente.put(
                            (dist_sommet+dist+self.heuristique(voisin), voisin))
                        # Et on change de prédécesseur
                        previous[voisin] = sommet
                        table_dists[voisin] = dist_sommet + dist
                visite.append(sommet)
                dejavisite[sommet] = True
        #Reconstruire le chemin avec les listes des précédents:
        chemin = []
        sommet = sommet_stop
        while sommet != sommet_start:
            chemin.append(sommet)
            sommet = previous[sommet]
        chemin.append(sommet_start)
        chemin.reverse()  # pour le mettre dans l'ordre
        return chemin, visite, table_dists[sommet_stop]

    """
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
                            attente.put((dist_sommet+dist+self.heuristique(voisin), voisin))
                            # Et on change de prédécesseur
                            previous[voisin] = sommet
                        elif dist_sommet+dist < attenteval[voisin]:
                            # on remplace si c'est plus court
                            attenteval[voisin] = dist_sommet+dist
                            attente.put((dist_sommet+dist+self.heuristique(voisin), voisin))
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
    """

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

    def heuristique(self, sommet):
        i, j = self.terrain.ntoij(sommet)
        iarriv, jarriv = self.terrain.ntoij(self.arriveen)
        idep, jdep = self.terrain.ntoij(self.departn)
        #Changer le coeff devant mon heuristique normalisée ?
        #Ajouter une variation de dénivelé à l'heuristique ?
        # return 50*self.distance_eucl(i, j, iarriv, jarriv) / \
        #     self.distance_eucl(idep, jdep, iarriv, jarriv)
        return self.distance_eucl(i, j, iarriv, jarriv)
    '''
    def horiz_penalty(self, i, j, ivois=None, jvois=None):
        """renvoie la pénalitée de distance  correspondant à la distance à l'arrivé
        à vol d'oiseau qui s'ajoutera au dénivelé pour le cout du sommet"""
        iarriv, jarriv = self.terrain.ntoij(self.arriveen)
        return self.distance_eucl(ivois, jvois, iarriv, jarriv)
    '''


class Skieur(Calculateur):
    def __init__(self, depart, arrivee, rectangle: Rectgle, terrain: Terrain):
        super().__init__(depart, arrivee, rectangle, terrain)
        self.depart = np.array(depart)
        #DEbug
        # self.depart = self.depart+[50, 50]
        # self.departn = self.terrain.xyton(*self.depart)
        #End Debug
        self.arrivee = np.array(arrivee)
        # on calcule la direction de la trace sur cette échelle (en nb de cellsize)
        self.dmoy = 10
        self.angle = 45  # 0° on monte droit dans la pente, 90° on se déplace sur ligne de niveau
        self.pentemax = 5 * pi/180 #Pente max tolérée par le skieur

    def calc_next_step(self, i, j):
        """renvoie le prochain i,j"""
        # grad = self.gradient(i, j)
        # angle_grad = np.arctan2(grad[1], grad[0])
        # #Angle de la trace par rapport au gradient
        # angle_OM = angle_grad-self.angle*pi/180
        # #Direction "tout droit"
        # toutdroit=self.direction_but(i,j)
        # angle_toutdroit=np.arctan2(toutdroit[1], toutdroit[0])
        # pasraide=not(angle_grad-abs(self.angle)*pi/180 < angle_toutdroit < angle_grad+abs(self.angle)*pi/180)
        # if pasraide:
        #     u_dOM=toutdroit
        # else:
        #     u_dOM = np.array([cos(angle_OM), sin(angle_OM)])
        
        taille_deplacement=self.dmoy*self.terrain.cellsize
        
        toutdroit=self.direction_but(i,j)*taille_deplacement
        pente_toutdroit=self.pente_direction(i,j,toutdroit)
        if pente_toutdroit<self.pentemax: #pas raide
            direction = toutdroit
        else:
            #aller vers le haut avec
            # un angle constant par rapport à la 
            # ligne de niveau (perpendiculaire au gradient)
            grad=self.gradient(i,j)
            direction_plusgdpente=taille_deplacement* grad/np.linalg.norm(grad) #pas utile ?
            angle_plusdgpente = np.arctan2(direction_plusgdpente[1], direction_plusgdpente[0])
            angle_ligneniveau = angle_plusdgpente - pi/2 

            #Recherche de l'angle/direction pour avoir self.pentemax comme pente
            theta=angle_ligneniveau
            N=1000 #pas de la recherche
            dtheta=(angle_plusdgpente-angle_ligneniveau)/N
            pente=0
            while pente<=self.pentemax:
                theta+=dtheta
                direction=taille_deplacement*np.array([cos(theta),sin(theta)])
                pente=self.pente_direction(i,j,direction)
            
        #DEbug:
        # print(
        #     f'Angle grad {angle_grad*180/pi:f},Angle OM {angle_OM*180/pi:f} ')

        return self.next_ij(i, j, direction)

    def pente_direction(self, i, j, direction):
        """renvoie la pente en i,j si on va dans la direction direction
        pas de test pour vérifier qu'on est encore dans le terrain quand 
        on se déplace de direction
        """
        x,y=self.terrain.ijtoxy(i,j)

        # TODO Tester si on est encore dans le terrain avec déplacement de direction.
        # Si non alors on renvoie un valeur spéciale

        inext,jnext=self.terrain.xytoij(x+direction[0],y+direction[1])
        di,dj=inext-i,jnext-j
        diffalt=(self.terrain.array[i+di,j+dj]-self.terrain.array[i,j])
        disthoriz=np.linalg.norm(direction)
        return np.arctan2(diffalt, disthoriz)

    def convertion(self):
        """changement de direction"""
        self.angle = -self.angle

    def calculate_path(self) -> Tuple[list]:
        position = self.terrain.xytoij(*self.depart)
        chemin = [self.terrain.ijton(*position)]
        next_pos = self.calc_next_step(*position)
        xnext, ynext = self.terrain.ijtoxy(*next_pos)
        #Debug
        maxturn = 10000
        turn = 0
        for i in range(10):  # on verra
            while self.ijisinrect(*next_pos) and self.terrain.isinTerrain(xnext, ynext) and turn < maxturn:
                position = next_pos
                chemin.append(self.terrain.ijton(*position))
                next_pos = self.calc_next_step(*position)
                xnext, ynext = self.terrain.ijtoxy(*next_pos)
                turn += 1
            self.convertion()
            next_pos = self.calc_next_step(*position)
            xnext, ynext = self.terrain.ijtoxy(*next_pos)
        return self.path_to_xyz(chemin)

    def direction_but(self, i, j):
        x, y = self.terrain.ijtoxy(i, j)
        position = np.array([x, y])
        vecteur = self.arrivee-position
        return (self.arrivee-position)/np.linalg.norm(vecteur)

    def terrain_autour(self, i, j, taille=5):
        """renvoie un array contenant les altitudes autour de x,y
        tableau de dim 2 taille+1 x 2 taille +1
        x,y au centre du tableau: coordonnées len()//2,len()//2
        si des points sont hors rectangle ou hors terrain, ils ont une altitude 10000"""
        # i,j=self.terrain.xytoij(x,y)
        tableau = 10000*np.ones((2*taille+1, 2*taille+1))
        for k in range(-taille, taille+1):
            for l in range(-taille, taille+1):
                itest, jtest = i+k, j+l
                interrain = 0 <= i < self.terrain.N and 0 <= j < self.terrain.M
                if self.ijisinrect(itest, jtest) and interrain:
                    tableau[k+taille, l+taille] = self.terrain.array[itest, jtest]
        return tableau

    def direction_dOM(self, i, j, inext, jnext):
        """renvoie le vecteur déplacement élémentaire de i,j à inext,jnext"""
        x, y = self.terrain.ijtoxy(i, j)
        xnext, ynext = self.terrain.ijtoxy(inext, jnext)
        return np.array(xnext-x, ynext-y)

    def gradient(self, i, j):
        """renvoie un vecteur gradient qui pointe vers le haut"""
        # autour = self.terrain_autour(i, j)
        # tab = np.gradient(autour, self.terrain.cellsize, self.terrain.cellsize)
        # centre = len(autour)//2, len(autour)//2
        # gradx = tab[1][centre]
        # grady = -tab[0][centre]

        #Gradient maison sur un point

        #Moyenne autour du point pour calculer le gradient
        #zone de self.dmoy x self.dmoy cellules

        #TODO Gérer les cas près du bord.
        delta=self.dmoy//2
        gradx=0
        for di in [-delta,delta]:
            gradx += (self.terrain.array[i+di, j+delta] -
                self.terrain.array[i+di, j-delta])/self.terrain.cellsize    
        gradx=gradx/(2*delta)

        grady=0
        for dj in [-delta,delta]:
            grady += (self.terrain.array[i+delta, j+dj] -
                self.terrain.array[i-delta, j+dj])/self.terrain.cellsize    
        grady=grady/(2*delta)

        # for delta in [-1, 1]:
        #     itest = i+delta
        #     jtest = j
        #     interrain = 0 <= itest < self.terrain.N and 0 <= jtest < self.terrain.M
        #     if self.ijisinrect(itest, jtest) and interrain:
        #         deltai = delta
        # for delta in [-1, 1]:
        #     itest = i
        #     jtest = j+delta
        #     interrain = 0 <= itest < self.terrain.N and 0 <= jtest < self.terrain.M
        #     if self.ijisinrect(itest, jtest) and interrain:
        #         deltaj = delta
        # gradx = deltaj * \
        #     (self.terrain.array[i, j+delta] -
        #      self.terrain.array[i, j])/self.terrain.cellsize
        # grady = -deltai * \
        #     (self.terrain.array[i+delta, j] -
        #      self.terrain.array[i, j])/self.terrain.cellsize

        return np.array([gradx, grady])

    def next_ij(self, i, j, dOM):
        """renvoie les coordonnées inext,jnext du prochain point dans la direction
        dOM depuis i,j"""
        # deltai,deltaj=self.terrain.xytoij(*dOM)
        # deltai,deltaj=round(deltai/self.dmoy),round(deltaj/self.dmoy) #pour ramener à 0 ou +-1
        x, y = dOM/np.linalg.norm(dOM)
        # les coordonnées sont inversées plus i croit quend y décroit
        deltai, deltaj = -round(y), round(x)
        return i+deltai, j+deltaj

    def angle(self, vec1, vec2):
        """renvoie l'angle entre vec1 et vec2"""
        # prodnormes=(np.linalg.norm(vec1)*np.linalg.norm(vec1))
        cosalpha = np.dot(vec1, vec2)  # /prodnormes
        sinalpha = np.cross(vec1, vec2)  # /prodnormes
        return np.arctan2(sinalpha, cosalpha)
