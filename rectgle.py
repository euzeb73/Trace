import numpy as np
from math import pi
from matplotlib.patches import Rectangle

class Rectgle(Rectangle):
    def __init__(self,point1,point2,largeur,cellsize=0) -> None:
        """cellsize est la marge à prendre pour être sûr que le rectangle contienne
         point1 et surtout point2 dans le système de coordonnées i,j
         Fabrique un patch matplotlib avec d'autres attributs pour les utilisations ailleurs
         """
        self.point1=point1
        self.point2=point2
        self.largeur=largeur
        self.marge=cellsize
        self.calc_coords()
        super().__init__(*self.get_matplotlibrec())

    def calc_coords(self):
        I=np.array(self.point1) #les milieux des côtés
        J=np.array(self.point2)
        vecIJ=J-I
        IJ=np.linalg.norm(vecIJ)
        normalIJ=np.array((vecIJ[1],-vecIJ[0]))
        vecIA=0.5*self.largeur*normalIJ/IJ
        A=I+vecIA #vecteurs: OA=OI+IA
        B=I-vecIA #vecteurs: OB=OI-IA     AB est la largeur du rectangle
        D=A+(IJ+self.marge)*vecIJ/IJ #vecteurs: OD=OA+IJ On ajoute une cellule dans cette direction pour avoir le point d'arrivée même avec les arrondis
        self.ABD=(A,B,D) #les coodonnées de A,B et D 

    def get_matplotlibrec(self):
        """"""
        A,B,D=self.ABD
        xy=A   #coin A
        height=self.largeur # largeur de A à B
        vecAD=D-A
        width=np.linalg.norm(vecAD) #longueur AD
        angle=180*np.arctan2(vecAD[1],vecAD[0])/pi
        return xy,width,height,angle

    def set_frommatplotlib(rec : Rectangle):
        """pour importé un rectangle à partir d'un objet Rectangle de Matplotlib
        
        PAS UTILE ?

        """

    def contains(self,x,y):
        """Retourne True si le points x,y est dans self
        False sinon"""
        A,B,D=self.ABD
        M=np.array((x,y))
        vecAM=M-A
        vecAB=B-A
        AB=np.linalg.norm(vecAB)
        vecAD=D-A
        AD=np.linalg.norm(vecAD)
        return 0<=vecAM.dot(vecAB)<=AB**2 and 0<=vecAM.dot(vecAD)<=AD**2
