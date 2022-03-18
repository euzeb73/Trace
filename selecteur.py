# from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from terrain import Terrain
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from rectgle import Rectgle

class Selecteur():
    def __init__(self,terrain:Terrain) -> None:
        self.terrain=terrain
        self.figure=self.terrain.plot(False) #affiche le terrain
        self.figure.subplots_adjust(left=0.25)
        self.axes=self.figure.gca()
        self.canvas=self.figure.canvas
        #Bouton effacer
        axeffacer=self.figure.add_axes([0.05,0.5,0.1,0.08])
        self.bouton_effacer=Button(axeffacer,'Effacer')
        self.cid_effacer=self.bouton_effacer.on_clicked(self.effacer)
        #Bouton valider
        axevalider=self.figure.add_axes([0.05,0.3,0.1,0.08])
        self.bouton_valider=Button(axevalider,'Fin nouveaux points')
        self.cid_valider=self.bouton_valider.on_clicked(self.valider)
        #Slider largeur
        axeslider=self.figure.add_axes([0.1,0.6,0.05,0.3])
        self.slider_largeur=Slider(ax=axeslider,label='Largeur',valmin=0,valmax= 5000,valinit=200,orientation='vertical')
        self.slider_largeur.on_changed(self.change_largeur)
        self.connect()
        plt.show()
    def change_largeur(self,val):
        """ changer pour current rect"""
        pass
    def connect(self):
        self.points=[]
        self.largeurs=[]
        self.rectangles : list[Rectgle] =[] #les rectangles
        self.currentpoint=-1
        self.line,=self.axes.plot([],[],'.r')
        self.axes.set_title("Sélectionner les points de passage dans l'ordre ")
        self.cid=self.canvas.mpl_connect('button_press_event',self.click)
        self.part2=False  # première partie de sélection des points

    def click(self,event):
        print('click')
        if event.inaxes != self.axes: #si on clique en dehors
            return 
        x,y=event.xdata,event.ydata
        self.points.append((x,y))#on ajoute le point cliqué à la liste des points
        xpts=[point[0] for point in self.points]
        ypts=[point[1] for point in self.points]
        self.line.set_data(xpts,ypts)
        if len(self.points)>1: #si on a au moins 2 points il faut ajouter un rectangle
            self.largeurs.append(self.slider_largeur.val)
            self.rectangles.append(Rectgle(self.points[-2],self.points[-1],self.largeurs[-1]))
        self.draw()
    
    def draw_rectangles(self):
        """affiche les rectangles
        
        faire une patch collection ?
        https://matplotlib.org/stable/gallery/statistics/errorbars_and_boxes.html

        """
        for rectangle in self.rectangles:
            if rectangle.axes is not None:
                rectangle.remove()
        for rectangle in self.rectangles:
            rectangle.set(facecolor='r',edgecolor='none', alpha=0.5)
        if self.currentpoint > 0 : #on a sélectionné un rectangle
            if self.currentpoint==len(self.currentpoint)-1:
                currentrec=self.currentpoint-1
            else:
                currentrec=self.currentpoint
            self.rectangles[currentrec].set(edgecolor='b')
        for rectangle in self.rectangles:
            # rectangle.set(figure=self.figure)
            self.axes.add_artist(rectangle)

    def draw(self):
        self.draw_rectangles()
        self.canvas.draw()
    def effacer(self,event):
        if len(self.points)>0: #au mloins un point
            self.points.pop() #on l'enlève
            xpts=[point[0] for point in self.points]
            ypts=[point[1] for point in self.points]
            self.line.set_data(xpts,ypts)
            if len(self.points)>0: # il y avait au moins 2 points donc au moins un rectangle
                self.largeurs.pop()
                self.rectangles.pop().remove()
        self.draw()
    def connect_part2(self):
        self.part2=True
        pass
    def valider(self,event):
        self.canvas.mpl_disconnect(self.cid)
        self.bouton_effacer.disconnect(self.cid_effacer)
        self.axes.set_title('Vous pouver ajuster les points et les largeurs')
        self.connect_part2()