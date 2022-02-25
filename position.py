from math import pi, log, cos, sin, tan, sqrt
import numpy as np


class Angle():
    def __init__(self, angle):
        self.rad = angle*pi/180
        self.deg = angle

    def __add__(self, other):
        return Angle(self.deg+other.deg)

    def __sub__(self, other):
        return Angle(self.deg-other.deg)

    def __mul__(self, cte):
        return Angle(cte*self.deg)

    def __rmul__(self, cte):
        return Angle(cte*self.deg)

    def __str__(self):
        return str(self.deg)


class Position():
    def __init__(self, lat, lon):
        """ lat et lon sont les latitude et longitude en DEGRES
        """
        self.lat = Angle(lat)  # latitude
        self.lon = Angle(lon)  # longitude
        # Caracteristiques de la Terre https://fr.wikipedia.org/wiki/Terre (rayon)
        a = 6378.137e3
        b = 6356.752e3
        self.e = sqrt(a**2-b**2)/a  # excentricité de l'ellipsoide
        phi1 = Angle(44)  # phi1 (première sec)
        phi2 = Angle(49)  # phi2 (2eme sec)
        #Calculs des termes utiles dans la projection
        numerateur = log(cos(phi2.rad)/cos(phi1.rad)) + \
            0.5*log((1-self.e**2*sin(phi1.rad)**2) /
                    (1-self.e**2*sin(phi2.rad)**2))
        denominateur = log((tan(phi1.rad/2+pi/4)*(1-self.e*sin(phi1.rad))**(self.e/2)*(1+self.e*sin(phi2.rad))**(self.e/2)) /
                           (tan(phi2.rad/2+pi/4)*(1+self.e*sin(phi1.rad))**(self.e/2)*(1-self.e*sin(phi2.rad))**(self.e/2)))
        self.n = numerateur/denominateur
        terme1 = a*cos(phi1.rad)/(self.n*sqrt(1-(self.e*sin(phi1.rad))**2))
        terme2 = (tan(phi1.rad/2+pi/4)*((1-self.e*sin(phi1.rad)) /
                  (1+self.e*sin(phi1.rad)))**(self.e/2))**self.n
        self.rhode0 = terme1*terme2

    def rho(self, phi:Angle):
        rhodephi = self.rhode0*((1+self.e*sin(phi.rad))/(1-self.e*sin(phi.rad))
                                )**(self.n*self.e/2)/(tan(phi.rad/2+pi/4))**self.n
        return rhodephi

    def get_xy(self):
        """ Renvoie la position en coordonnées cartésiennes selon la projection
        de Lambert 93 (RGF 93)
        https://fr.wikipedia.org/wiki/Projection_conique_conforme_de_Lambert#Projections_officielles_en_France_m%C3%A9tropolitaine
        """
        lon0 = Angle(3)  # lambda0
        lat0 = Angle(46.5)  # phi0
        X0 = 700e3
        Y0 = 6600e3
        theta = self.n*(self.lon-lon0)
        rho = self.rho(self.lat)
        rho0 = self.rho(lat0)
        x = X0+rho*sin(theta.rad)
        y = Y0+rho0-rho*cos(theta.rad)
        return x, y
