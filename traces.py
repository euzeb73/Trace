import time
from rectgle import Rectgle
from terrain import Terrain
from queue import PriorityQueue
import numpy as np
import mayavi.mlab as ma
import matplotlib.pyplot as plt
from math import tan,sqrt

RACINEDEDEUX=sqrt(2)

class Traces():
    def __init__(self,terrain : Terrain, points : list, largeurs : list=[]):
        """ Trace attachée à terrain 
        points est une liste de (x,y) d'au moins 2 points (départ arrivée)
        largeurs est une liste de floats largeurs de longueur len(points)-1 qui représente
        la zone d'évolution autour de la droite (points[i] points[i+1]) soit
        les 2 droites parallèles à -largeur[i]/2 et + largeur[i]/2
        
        
        REpenser le truc à partir de liste de points et de rectangles ?
        
        
        """
        self.terrain = terrain
        self.points = points
        if largeurs == [] :
            self.largeurs=[250 for i in range(len(self.points)-1)]    #par défaut 250 m de large
        else:
            self.largeurs = largeurs
        assert len(self.largeurs)==len(self.points)-1 
        self.generate_rects()
        self.ImportanceDeniv=10

    def set_rects(self,rectangles):
        self.rects : list[Rectgle] = rectangles

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
            self.rects.append(Rectgle(self.points[i],self.points[i+1],self.largeurs[i],self.terrain.cellsize))

    # def isinrect(self,x,y,rect : Rectgle):
    #     """Retourne True si le points x,y est dans rect défini par les coordonnées de A,B et D
    #     False sinon"""
    #     A,B,D=rect.ABD
    #     M=np.array((x,y))
    #     vecAM=M-A
    #     vecAB=B-A
    #     AB=np.linalg.norm(vecAB)
    #     vecAD=D-A
    #     AD=np.linalg.norm(vecAD)
    #     return 0<=vecAM.dot(vecAB)<=AB**2 and 0<=vecAM.dot(vecAD)<=AD**2

    def ijisinrect(self,i,j,rect : Rectgle):
        """Retourne True si le points i,j est dans rect défini par les coordonnées de A,B et D
        False sinon"""
        x,y=self.terrain.ijtoxy(i,j)
        return rect.contains(x,y)



    def calculate_trace(self,methode='Dijkstra'):
        #Dans l'idée: calculer le chemin entre chaque points de la liste self.points
        #sous traiter ce calcul à une une calsse de calculateurs avec des héritages
        #genre class Calculateur(): (il faudra lui fournir le terrain pour les conversions)
        #puis class Djikstra(Calculateur) 
        # et dans le calculateur une méthode .generate_path qui renvoie un chemin
        # dans le calculateur, il faudrait tenir compte des largeurs avec une méthode qui 
        # élimine les points hors de ces largeurs (genr en les mettant float('inf') de le terrain
        self.methode=methode
        if methode=='Dijkstra':
            # calculateur=Dijkstra()
            pass
        elif methode=='A*':
            # calculateur=Astar()
            pass
        #calculateur.generate_chemin()
        #calculateur.get_path() ou plutot calculateur.get_pathxyz() avec path_toxyz à adapter

        #Version provisoire
        print('Calcul de la Trace')
        t1=time.perf_counter()
        for i in range(len(self.points)-1):
            depart=self.terrain.xyton(*self.points[i])
            arrivee=self.terrain.xyton(*self.points[i+1])
            self.current_rec=self.rects[i]
            chemin=self.dijkstra(depart,arrivee)[0]
            x,y,z=self.path_to_xyz(chemin)
            if i==0:
                self.tracexyz=x,y,z
            else:
                debuttrace=self.tracexyz
                oldx,oldy,oldz=debuttrace
                self.tracexyz=np.concatenate((oldx,x)),\
                              np.concatenate((oldy,y)),\
                              np.concatenate((oldz,z))
        t2=time.perf_counter()
        print('Calcul fini en {:.2f}s'.format(t2-t1) )
    def voisins(self,n):
        """renvoie une liste des voisins de n
        format liste de tuples (i,j)"""
        i,j=self.terrain.ntoij(n)
        N=self.terrain.N
        M=self.terrain.M
        vois=[]
        for deltai in [-1,0,1]: #les voisins diagonales comprises
            for deltaj in [-1,0,1]:
                ipastropgrand = i+deltai<=N-1
                ipastroppetit = i+deltai>=0
                jpastropgrand = j+deltaj<=M-1
                jpastroppetit = j+deltaj>=0
                pas0 = deltai!=0 or deltaj!=0 #pour enlever 0,0
                dansrec=self.ijisinrect(i+deltai,j+deltaj,self.current_rec) #Si le voisin est dans l'espace sélectionné
                if ipastropgrand and ipastroppetit and jpastropgrand and jpastroppetit and pas0 and dansrec:
                    vois.append((i+deltai,j+deltaj))
        return vois
        
    def voisins_couts(self,n):
        """ Renvoie une liste des voisins de i,j avec les couts de déplacement
        donnés par graph. Format [[voisin1,cout1],[voisin2,cout2],...] """
        graph=self.terrain.array
        i,j=self.terrain.ntoij(n)
        vois=self.voisins(n)
        voiscouts=[]
        for voisin in vois:
            ivois,jvois=voisin
            cout=max(graph[ivois][jvois]-graph[i][j],0) #0 si plat ou descente, le deniv sinon
            
            # Pénaliser les grandes pentes
            # TODO à mettre en paramètre
            pentemax=15
            if cout>=tan(pentemax*3.14/180):
                cout=cout*10
            if abs(i-ivois)+abs(j-jvois)==1:
                penalitedistance=self.terrain.cellsize
            else:
                penalitedistance=self.terrain.cellsize*RACINEDEDEUX
            cout=self.ImportanceDeniv*cout+penalitedistance
            voiscouts.append([self.terrain.ijton(*voisin),cout])
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
    
    def plot3D(self,figure,Zfactor):
        """affiche la trace sur la figure (mayaplot 3D)"""
        x,y,z=self.tracexyz
        zplot=Zfactor*z.copy()
        ma.figure(figure)
        ma.plot3d(x, y, zplot, tube_radius=1,color=(1,0,1),figure=figure)
        ma.text3d(x[0],y[0],zplot[0]+Zfactor*10,'Depart',figure=figure,scale=(20,20,20),color=(1,0,0))
        fin=len(x)-1
        ma.text3d(x[fin],y[fin],zplot[fin]+Zfactor*10,'Arrivee',figure=figure,scale=(20,20,20),color=(1,0,0))
        ma.show()

    def plot2D(self,axes):
        """affiche la trace sur la figure (2D)"""
        x,y,z=self.tracexyz
        axes.plot(x,y,color=(1,0,1))
        # plt.show()

    #TODO AJOUTER une visu de Trace en 2D avc points et rectangles.
