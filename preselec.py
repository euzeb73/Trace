from zone import Zone
from position import Position
from selecteur import Selecteur
from dataset import JeuDeDonnees
import matplotlib.pyplot as plt
import requests
from PIL import Image
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
from rectgle import Rectgle


class Preselec():
    def __init__(self) -> None:
        self.dataset = JeuDeDonnees('../Savoie/')
        self.reset(None)

        #TODO BOuton retour zoom arrière facile avec une liste de box

        #Bouton effacer
        axeffacer = self.figure.add_axes([0.04, 0.5, 0.12, 0.08])
        self.bouton_effacer = Button(axeffacer, 'Effacer')
        self.cid_effacer = self.bouton_effacer.on_clicked(self.effacer)
        #Bouton Reset
        axereset = self.figure.add_axes([0.04, 0.6, 0.12, 0.08])
        self.bouton_reset = Button(axereset, 'Reset !')
        self.cid_reset = self.bouton_reset.on_clicked(self.reset)
        #Bouton Zoom
        axezoom = self.figure.add_axes([0.04, 0.4, 0.12, 0.08])
        self.bouton_zoom = Button(axezoom, 'Zoom')
        self.cid_zoom = self.bouton_zoom.on_clicked(self.zoom)
        #Bouton valider
        axevalider = self.figure.add_axes([0.02, 0.3, 0.16, 0.08])
        self.bouton_valider = Button(axevalider, 'Valider la zone')
        self.cid_valider = self.bouton_valider.on_clicked(self.valider)
        plt.show()

    def reset(self, event):
        #requete pour la France
        xmin, ymin = Position(41.169545, -5.04875).get_xy()
        xmax, ymax = Position(51.239222, 11.055755).get_xy()
        #requete pour la Savoie
        xmin, ymin = Position(45.18468, 5.713331).get_xy()
        xmax, ymax = Position(45.865632, 7.249164).get_xy()
        self.box = xmin, ymin, xmax, ymax
        self.set_map(*self.box)
        self.plot_map()
        self.newbox = None
        self.rectangle = None
        self.canvas.draw()

    def valider(self, event):
        plt.close(self.figure)
        #Si rien de sélectionné: toute la zone est prise
        if self.newbox is None:
            self.newbox = self.box
        zone = Zone()
        zone.set_rectangle(*self.newbox)
        terrain = zone.generate_terrain(self.dataset)
        Selecteur(terrain)

    def effacer(self, event):
        """Quand on annule"""
        self.newbox = None
        self.rectangle.remove()
        self.rectangle = None
        self.canvas.draw()
        # #Effacer les rectangle
        # list_artist = self.axes.get_children()
        # for artist in list_artist:
        #     if isinstance(artist, Line2D):
        #         artist.remove()

    def zoom(self, event):
        """Quand la zone est choisie et qu'on charge une nouvelle zone"""
        self.box = self.newbox
        self.set_map(*self.box)
        self.plot_map()
        self.effacer(None)

    def click(self, event):
        self.xclick, self.yclick = event.xdata, event.ydata
        xmin, ymin, xmax, ymax = self.box
        onmap = xmin <= self.xclick <= xmax and ymin <= self.yclick <= ymax
        if event.inaxes != self.axes or not onmap:
            return
        #On active le mouvement de la souris
        self.cid_move = self.canvas.mpl_connect(
            'motion_notify_event', self.drawrect)
        #On active la détection du relachement de la souris
        self.cid_release = self.canvas.mpl_connect(
            'button_release_event', self.release)

    def release(self, event):
        #On arrête de regarder la souris qui bouge
        self.canvas.mpl_disconnect(self.cid_move)
        #On arrête de détecter le relachement du bouton de la souris
        self.cid_release = self.canvas.mpl_disconnect(self.cid_release)
        # x2,y2=event.xdata, event.ydata

    def drawrect(self, event):
        x1, y1 = self.xclick, self.yclick
        x2, y2 = event.xdata, event.ydata
        self.newbox = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        xmin, ymin, xmax, ymax = self.newbox
        if self.rectangle is None:
            self.rectangle = Rectangle(
                (xmin, ymin), xmax-xmin, ymax-ymin, alpha=0.2, edgecolor='r', facecolor='b')
            self.axes.add_artist(self.rectangle)
        else:
            self.rectangle.set(xy=(xmin, ymin), width=xmax -
                               xmin, height=ymax-ymin)
        self.canvas.draw()

    def plot_map(self):
        #Fenêtre matplotlib
        xmin, ymin, xmax, ymax = self.box
        self.figure = plt.gcf()
        self.axes = plt.axes(xlim=(xmin, xmax),
                             ylim=(ymin, ymax))
        self.figure.subplots_adjust(left=0.2)
        self.canvas = self.figure.canvas
        carte = Image.open(self.current_map_path)
        self.axes.imshow(carte, aspect='auto', extent=(xmin, xmax, ymin, ymax), alpha=1,
                         zorder=0, origin='upper')
        self.axes.axis('equal')
        self.axes.xaxis.set_ticklabels([])
        self.axes.yaxis.set_ticklabels([])
        self.axes.set_title("Sélectionner la zone à valider ou à zoomer")
        self.cid = self.canvas.mpl_connect('button_press_event', self.click)
        # plt.show()

    def set_map(self, xmin, ymin, xmax, ymax):
        self.box = xmin, ymin, xmax, ymax
        self.current_map = self.request_map(*self.box)
        self.current_map_path = self.temp_file(self.current_map)

    def request_map(self, xmin, ymin, xmax, ymax):
        #renvoie le binary correspondant à la carte
        height = ymax-ymin
        width = xmax-xmin
        long_dim, short_dim = width, height
        ldim = 'width'
        if height > width:
            long_dim, short_dim = height, width
            ldim = 'height'
        ratio = long_dim/short_dim
        pixel_width = 1024
        if ldim == 'width':
            pixel_height = round(1024/ratio)
        else:
            pixel_height = 1024
            pixel_width = round(1024/ratio)

        rep = requests.get(
            f'https://wxs.ign.fr/cartes/geoportail/r/wms?LAYERS=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:2154&BBOX={xmin},{ymin},{xmax},{ymax}&WIDTH={pixel_width}&HEIGHT={pixel_height}')
        if rep:
            return rep.content
        else:
            print('Pas de réponse, vérifier la connection internet')
            print(f'Erreur {rep.status_code}')

    def temp_file(self, binary, path='temp.jpg'):
        tempfile = open(path, 'wb')
        tempfile.write(binary)
        return path
