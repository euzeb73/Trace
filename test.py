import imp
from position import Angle,Position
from terrain import Terrain
from dataset import JeuDeDonnees
from zone import Zone
import matplotlib.pyplot as plt
from traces import Traces
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
# large=Zone(point,deltax=1e3,deltay=3e3)
petite=Zone(point,deltax=0.34434e3,deltay=0.7242e3)
carte=petite.generate_terrain(belfort)
# carte=large.generate_terrain(belfort)
print(carte.xmax-carte.xmin,carte.ymax-carte.ymin)
print(carte.M,carte.N)
trace=Traces(carte,[(carte.xmin+5,carte.ymin+5),(carte.xmax-5,carte.ymax-5)],[])
trace.calculate_trace()
fig,Zfac=carte.plot3D(Zfactor=3, show= False)
trace.plot3D(fig,Zfac)

