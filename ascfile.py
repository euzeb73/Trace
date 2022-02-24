import numpy as np

class Ascfile():
    def __init__(self,path):
        self.path=path
        self.read_info()
        self.array=None #pas la peine d'encombrer la mémoire
    def read_info(self):
        file = open(self.path)
        #Header
        self.M = int(file.readline()[13:])  # nb colonnes
        self.N = int(file.readline()[13:])  # nb lignes
        self.xmin = float(file.readline()[13:])  # en m
        self.ymax = float(file.readline()[13:])  # en m
        self.cellsize = float(file.readline()[13:])  # pas des données
        self.xmax = self.xmin+self.M*self.cellsize
        self.ymin = self.ymax-self.N*self.cellsize
        file.readline()
        file.close()
    def get_data(self):
        """Lit les altitudes et renvoie un array contenant les altitudes"""
        file = open(self.path)
        #Header
        for i in range(6):
            file.readline()
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
        return alti
    def save_array(self):
        """ Lit le tableau dans le asc et le stocke dans self.array"""
        self.array=self.get_data()
    def make_file(self,path='./newasc.asc'):
        """
        fabrique un fichir asc avec chemin d'accès path à partir des attributs
        self.array doit contenit le tableau des altitudes à écrire.

        A FAIRE....

        """
