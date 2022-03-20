from position import Angle,Position
from terrain import Terrain
from dataset import JeuDeDonnees
from zone import Zone
import matplotlib.pyplot as plt
from traces import Traces
import time
from selecteur import Selecteur

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

"""
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
"""
chalet=Position(45.524949 , 6.791012)

t1=time.perf_counter()
savoie=JeuDeDonnees('../Savoie/')
t2=time.perf_counter()
print('Cartes lues et triées en {:.4f} s'.format((t2-t1)))
#zone=Zone(chalet,deltax=4e3,deltay=4e3)
xmin,ymax=Position(45.524444 , 6.756787).get_xy()
xmax,ymin=Position(45.516221 , 6.779277).get_xy()
bosse_etroit=Zone()
bosse_etroit.set_rectangle(xmin-2000,xmax+2000,ymin-2000,ymax+2000)
t1=time.perf_counter()
carte=bosse_etroit.generate_terrain(savoie)
t2=time.perf_counter()
print('Terrain construit à partir des cartes en {:.4f} s'.format((t2-t1)))

sortie_foret=Position(45.521279 , 6.77825).get_xy()
sommet_bosse=Position(45.518665 , 6.76557).get_xy()
fin_descente=Position(45.524455 , 6.762408).get_xy()
col_bosse=Position(45.521172 , 6.765767).get_xy()
replat_chamois=Position(45.521462 , 6.772941).get_xy()
avant_pleinest=Position(45.519639 , 6.773636).get_xy()

Selecteur(carte)

# # trace=Traces(carte,[sortie_foret,replat_chamois,sommet_bosse],[])
# # trace=Traces(carte,[sortie_foret,sommet_bosse],[25])
# trace=Traces(carte,[sortie_foret,avant_pleinest,replat_chamois,sommet_bosse],[100,50,200])
# # trace=Traces(carte,[fin_descente,col_bosse],[])
# t1=time.perf_counter()
# trace.calculate_trace()
# t2=time.perf_counter()
# print('Trace calculée en {:.4f} s'.format((t2-t1)))
# fig,zfac=carte.plot3D(Zfactor=1,show=False)
# trace.plot3D(fig,zfac)