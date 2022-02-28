import imp
from position import Angle,Position
from terrain import Terrain
from dataset import JeuDeDonnees
from zone import Zone
import matplotlib.pyplot as plt
# point=Position(47.565943,6.725231)
# pttest=point.get_xy()
# print(pttest)

# carte=Terrain()
# carte.loadasc('../Cartes/carte_test.asc')
# carte.writeasc()
# fig=carte.plot(False)
# axes=fig.gca()
# x,y=pttest
# axes.scatter(x,y)
# plt.show()
# carte.plot3D()

belfort=JeuDeDonnees('../Belfort/')
point=Position(47.71057 , 6.930424)
# large=Zone(point,deltax=10.5e3,deltay=12e3)
large=Zone(point,deltax=1e3,deltay=3e3)
# petite=Zone(point,deltax=1.34434e3,deltay=2.3242e3)
# carte=petite.generate_terrain(belfort)
carte=large.generate_terrain(belfort)
print(carte.xmax-carte.xmin,carte.ymax-carte.ymin)
print(carte.M,carte.N)
carte.plot3D()
carte.plot()