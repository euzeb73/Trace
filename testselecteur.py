from position import Angle,Position
from terrain import Terrain
from dataset import JeuDeDonnees
from zone import Zone
import matplotlib.pyplot as plt
from traces import Traces
import time
from selecteur import Selecteur
from rectgle import Rectgle

# fig,ax=plt.subplots()
# test=Rectgle((0,3),(0,4),2)
# ax.plot([0,5], [0,6])
# ax.add_artist(test)
# test.remove()
# plt.show()

t1=time.perf_counter()
belfort=JeuDeDonnees('../Belfort/')
t2=time.perf_counter()
print('Cartes lues et triées en {:.4f} s'.format((t2-t1)))
point=Position(47.75057 , 6.930424)
large=Zone(point,deltax=2.5e3,deltay=2e3)
# large=Zone(point,deltax=150,deltay=300)
petite=Zone(point,deltax=0.5e3,deltay=0.9e3)
# carte=petite.generate_terrain(belfort)
carte=large.generate_terrain(belfort)
Selecteur(carte)
