from position import Angle,Position
from terrain import Terrain,JeuDeDonnees, Zone
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
large=Zone(point,deltax=10.5e3,deltay=12e3)
# petite=Zone(point,deltax=100,deltay=350)
# carte=petite.generate_terrain(belfort)
carte=large.generate_terrain(belfort)
carte.plot()
