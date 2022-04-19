from calculateur import Astar
from position import Angle,Position
from terrain import Terrain
from dataset import JeuDeDonnees
from zone import Zone
import matplotlib.pyplot as plt
from traces import Traces
import time

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
# fig,Zfac=carte.plot3D(Zfactor=3)
# trace=Traces(carte,[(carte.xmin+5,carte.ymin+5),(carte.xmax-5,carte.ymax-5)],[])
trace=Traces(carte,[(carte.xmax-10,carte.ymax-10),(carte.xmin+10,carte.ymin+10)],[])
trace.calculate_trace()
# trace.calculate_trace('Astar')
fig,Zfac=carte.plot3D(Zfactor=3, show= False)
trace.plot3D(fig,Zfac)