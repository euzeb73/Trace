from preselec import Preselc
import requests

#selec=Preselc()
# rep=selec.current_map

# filesave=open('save.jpg','wb')
# filesave.write(rep.content)
# filesave.close()
xmin=993150.7914940799
xmax=994948.0921845281
ymin=6497809.3394231405
ymax=6498637.739536691
rep=requests.get(f'https://wxs.ign.fr/altimetrie/geoportail/r/wms?LAYERS=ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES&EXCEPTIONS=text/xml&FORMAT=text/asc&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:2154&BBOX={xmin},{ymin},{xmax},{ymax}&WIDTH={(xmax-xmin)}&HEIGHT={ymax-ymin}')
alts=rep.text
#print(alts)