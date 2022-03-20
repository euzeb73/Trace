# from matplotlib.collections import PatchCollection
from aiohttp import TraceRequestExceptionParams
from matplotlib.patches import Rectangle
from terrain import Terrain
from traces import Traces
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button, Slider, RadioButtons
from rectgle import Rectgle
from matplotlib.patches import Rectangle

class Selecteur():
    def __init__(self,terrain:Terrain) -> None:
        self.terrain=terrain
        self.figure,self.axes=self.terrain.plot(False) #affiche le terrain
        self.map_artists=self.axes.get_children()
        self.figure.subplots_adjust(left=0.2)
        self.canvas=self.figure.canvas
        #Bouton effacer
        axeffacer=self.figure.add_axes([0.05,0.5,0.12,0.08])
        self.bouton_effacer=Button(axeffacer,'Effacer')
        self.cid_effacer=self.bouton_effacer.on_clicked(self.effacer)
        #Bouton Reset
        axereset=self.figure.add_axes([0.05,0.4,0.12,0.08])
        self.bouton_reset=Button(axereset,'Reset !')
        self.cid_reset=self.bouton_reset.on_clicked(self.connect)
        #Bouton valider
        axevalider=self.figure.add_axes([0.05,0.3,0.12,0.08])
        self.bouton_valider=Button(axevalider,'Tracer !')
        self.cid_valider=self.bouton_valider.on_clicked(self.valider)
        #Slider largeur
        axeslider=self.figure.add_axes([0.05,0.65,0.02,0.3])
        self.slider_largeur=Slider(ax=axeslider,label='Largeur',valmin=5,valmax= 5000,valinit=200,orientation='vertical')
        self.slider_largeur.on_changed(self.change_largeur)
        #Bouton choix de trace
        axechoix=self.figure.add_axes([0.05,0.05,0.12,0.2])
        self.bouton_choix=RadioButtons(axechoix,['Djikstra','A*','montée'])
        #Bouton choix du rendu
        axechoixplot=self.figure.add_axes([0.1,0.72,0.07,0.15])
        self.bouton_choix_plot=RadioButtons(axechoixplot,['2D','3D'])
        self.rectangles : list[Rectgle] =[] #les rectangles utile pour 1er appel à connect
        self.connect()
        plt.show()

    def change_largeur(self,val):
        """ changer pour current rect"""
        if len(self.largeurs)>0:
            self.largeurs[-1]=val
            self.rectangles[-1].remove() #l'enlever du canvas
            self.rectangles[-1]=Rectgle(self.points[-2],self.points[-1],self.largeurs[-1],self.terrain.cellsize) #actualiser le rectangle
        self.draw_rectangles()

    def connect(self,event=None):
        #Nettoyage des rectangles
        for rectangle in self.rectangles:
            rectangle.remove()
        #Nettoyage des traces
        list_artist=self.axes.get_children()
        for artist in list_artist:
            if isinstance(artist,Line2D):
                artist.remove()
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
        x,y=event.xdata,event.ydata
        if event.inaxes != self.axes or not self.terrain.isinTerrain(x,y): #si on clique en dehors
            return 
        self.points.append((x,y))#on ajoute le point cliqué à la liste des points
        xpts=[point[0] for point in self.points]
        ypts=[point[1] for point in self.points]
        self.line.set_data(xpts,ypts)
        if len(self.points)>1: #si on a au moins 2 points il faut ajouter un rectangle
            self.largeurs.append(self.slider_largeur.val)
            #on ajoute le rectangle avec une marge cellsize pour avoir l'arrivée dedans à coup sûr.
            self.rectangles.append(Rectgle(self.points[-2],self.points[-1],self.largeurs[-1],self.terrain.cellsize))
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
            rectangle.set(facecolor='r',edgecolor='none', alpha=0.3)
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
        # self.bouton_valider.active=False
        # self.bouton_effacer.disconnect(self.cid_effacer)
        tracetoplot=Traces(self.terrain,self.points)
        tracetoplot.set_rects(self.rectangles)
        tracetoplot.calculate_trace(self.bouton_choix.value_selected)
        if self.bouton_choix_plot.value_selected=='2D':
            tracetoplot.plot2D(self.axes)
        else:
            fig,zfact=self.terrain.plot3D(Zfactor=1,show=False)
            tracetoplot.plot3D(fig,zfact)
        # self.bouton_valider.active=True
        # self.axes.set_title('Vous pouver ajuster les points et les largeurs')
        # self.connect_part2()