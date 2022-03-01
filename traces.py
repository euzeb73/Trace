from terrain import Terrain
from queue import PriorityQueue
import numpy as np
import mayavi.mlab as ma

class Traces():
    def __init__(self,terrain : Terrain, points : list, largeurs : list):
        """ Trace attachée à terrain 
        points est une liste de (x,y) d'au moins 2 points (départ arrivée)
        largeurs est une liste de floats largeurs de longueur len(points)-1 qui représente
        la zone d'évolution autour de la droite (points[i] points[i+1]) soit
        les 2 droites parallèles à -largeur[i]/2 et + largeur[i]/2"""
        self.terrain = terrain
        self.points = points
        self.largeurs = largeurs #Pas encore implémenté
        self.ImportanceDeniv=10

    def calculate_trace(self,methode='dijkstra_fast'):
        #Dans l'idée: calculer le chemin entre chaque points de la liste self.points
        #sous traiter ce calcul à une une calsse de calculateurs avec des héritages
        #genre class Calculateur(): (il faudra lui fournir le terrain pour les conversions)
        #puis class Djikstra(Calculateur) 
        # et dans le calculateur une méthode .generate_path qui renvoie un chemin
        # dans le calculateur, il faudrait tenir compte des largeurs avec une méthode qui 
        # élimine les points hors de ces largeurs (genr en les mettant float('inf') de le terrain
        if methode=='dijkstra_fast':
            # calculateur=Dijkstra()
            pass
        elif methode=='Astar':
            # calculateur=Astar()
            pass
        #calculateur.generate_chemin()
        #calculateur.get_path() ou plutot calculateur.get_pathxyz() avec path_toxyz à adapter

        #Version provisoire
        for i in range(len(self.points)-1):
            depart=self.terrain.xyton(*self.points[i])
            arrivee=self.terrain.xyton(*self.points[i+1])
            chemin=self.dijkstra_fast(depart,arrivee)[0]
            x,y,z=self.path_to_xyz(chemin)
            if i==0:
                self.tracexyz=x,y,z
            else:
                debuttrace=self.tracexyz
                oldx,oldy,oldz=debuttrace
                self.tracexyz=np.concatenate(oldx,x),\
                              np.concatenate(oldy,y),\
                              np.concatenate(oldz,y)

    def voisins(self,n):
        """ Renvoie une liste des voisins de i,j avec les couts de déplacement
        donnés par graph. Format [[voisin1,cout1],[voisin2,cout2],...] """
        graph=self.terrain.array
        i,j=self.terrain.ntoij(n)
        N=self.terrain.N
        M=self.terrain.M
        vois=[]
        if i+1<=N-1:
            vois.append(self.terrain.ijton(i+1,j))
        if i-1>=0:
            vois.append(self.terrain.ijton(i-1,j))
        if j+1<=M-1:
            vois.append(self.terrain.ijton(i,j+1))
        if j-1>=0:
            vois.append(self.terrain.ijton(i,j-1))
        voiscouts=[]
        for voisin in vois:
            ivois,jvois=self.terrain.ntoij(voisin)
            cout=max(graph[ivois][jvois]-graph[i][j],0) #0 si plat ou descente, le deniv sinon
            penalitedistance=25
            cout=self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([voisin,cout])
        return voiscouts

    def dijkstra_fast(self,sommet_start,sommet_stop):
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
                for voisin,dist in self.voisins(sommet): 
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
        """self.tracexyz 3 listes contenant les coordonnées x,y et z de chaque poitn du chemin
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
    
    def plot3D(self,figure,Zfactor):
        """affiche la trace sur la figure (mayaplot 3D)"""
        x,y,z=self.tracexyz
        zplot=Zfactor*z.copy()
        ma.figure(figure)
        ma.plot3d(x, y, zplot, tube_radius=5,color=(1,0,1))
        ma.show()

