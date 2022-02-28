from terrain import Terrain
import glob



class JeuDeDonnees():
    def __init__(self, dir):
        """dir est le chemin d'accès au répertoire contenant les fichiers des donnees"""
        self.dir: str = dir
        self.filelist: list[str] = glob.glob("{}/*.asc".format(self.dir))
        self.tuiles: list[Terrain] = []
        #Liste des fichier convertie en liste de terrains
        for file in self.filelist:
            terrain = Terrain()
            terrain.loadasc(file, onlyinfo=True)
            self.tuiles.append(terrain)
        #on récupère les données dans une liste de terrains ordonnés
        #Les données ne sont pas lues à ce stade
        self.organise_data()

    def organise_data(self):
        """
        Va récupérer toutes les tuiles et les ranger par y decroissants puis x croissants
        et les retourner dans une liste de Terrains (pour l'instant seulement onlyinfo)
        """
        #fonction de tri
        def tri_selon_attribut(liste : list, attribut: str, croissant=True):
            """Tri des listes de tuiles selon attribut (en format str) (tri par sélection simple)
            Croissant par défaut. Metttre croisant=False pour décroissant
            tri en place + renvoie la liste triée"""
            for i in range(len(liste)):
                terrainymini = liste[i].__dict__[attribut]
                jmini = i
                for j in range(i, len(liste)):
                    if croissant:
                        if liste[j].__dict__[attribut] < terrainymini:
                            terrainymini = liste[j].__dict__[attribut]
                            jmini = j
                    else:
                        if liste[j].__dict__[attribut] > terrainymini:
                            terrainymini = liste[j].__dict__[attribut]
                            jmini = j
                liste[jmini], liste[i] = liste[i], liste[jmini]
            return liste

        #Tri selon ymax
        tri_selon_attribut(self.tuiles, 'ymax', croissant=False)
        #reperage des groupes de ymax + tri selon xmax
        ymax = self.tuiles[0].ymax
        ideb = 0
        for i in range(len(self.tuiles)):
            if self.tuiles[i].ymax != ymax:
                ifin = i
                self.tuiles[ideb:ifin] = tri_selon_attribut(
                    self.tuiles[ideb:ifin], 'xmax')
                ideb = ifin
                ymax = self.tuiles[i].ymax
        ifin = len(self.tuiles)
        self.tuiles[ideb:ifin] = tri_selon_attribut(
            self.tuiles[ideb:ifin], 'xmax')

