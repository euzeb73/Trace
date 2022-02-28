from terrain import Terrain
from queue import PriorityQueue
import numpy as np

class Trace():
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
    def voisins(self,n,graph):
        """ Renvoie une liste des voisins de i,j avec les couts de déplacement
        donnés par graph. Format [[voisin1,cout1],[voisin2,cout2],...] """
        i,j=self.terrain.n2ij(n)
        N=self.terrain.N
        M=self.terrain.M
        vois=[]
        if i+1<=N-1:
            vois.append(self.terrain.ij2n(i+1,j))
        if i-1>=0:
            vois.append(self.terrain.ij2n(i-1,j))
        if j+1<=M-1:
            vois.append(self.terrain.ij2n(i,j+1))
        if j-1>=0:
            vois.append(self.terrain.ij2n(i,j-1))
        voiscouts=[]
        for voisin in vois:
            ivois,jvois=self.terrain.n2ij(voisin)
            cout=max(graph[ivois][jvois]-graph[i][j],0) #0 si plat ou descente, le deniv sinon
            penalitedistance=25
            cout=self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([voisin,cout])
        return voiscouts

    def dijkstra_fast(self,graph,sommet_start,sommet_stop):
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
                for voisin,dist in self.voisins(sommet,graph): 
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
    
    def path_to_plot(self,chemin):
        x=[]
        y=[]
        for pointn in chemin:
            i,j=self.terrain.n2ij(pointn)
            y.append(i)
            x.append(j)
        return x,y

    def path_to_mayaplot(self,chemin):
        x,y=self.path_to_plot(chemin)
        z=[]
        map3D=self.terrain.array
        N=map3D.shape[0]
        for i in range(len(x)):
            # x[i],y[i]=x[i],y[i]
            z.append(map3D[y[i],x[i]]) #transposition
            xi,yi=x[i],y[i]
            x[i]=25*yi #tuile de 25m x 25m + transposition
            y[i]=25*xi
        return np.array(x),np.array(y),np.array(z)


    
