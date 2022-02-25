from position import Angle,Position
from terrain import Terrain,JeuDeDonnees
import matplotlib.pyplot as plt

# pttest=Position(47.565943,6.725231).get_xy()
# print(pttest)

carte=Terrain()
carte.loadasc('../Cartes/carte_test.asc')
carte.writeasc()
# fig=carte.plot(False)
# axes=fig.gca()
# x,y=pttest
# axes.scatter(x,y)
# plt.show()
# carte.plot3D()

# belfort=JeuDeDonnees('../Belfort/')
# print(belfort.filelist)
# belfort.scrap_data()