import os.path
import math
from maperipy import App
from maperipy import Map

# Geo bounds in integer degrees
MinLon=int(Map.geo_bounds.min_x)
MaxLon=int(math.ceil(Map.geo_bounds.max_x))

MinLat=int(Map.geo_bounds.min_y)
MaxLat=int(math.ceil(Map.geo_bounds.max_y))

App.run_command('set-dem-source ASTER')

for Lon in range (MinLon, MaxLon, 1) :
  for Lat in range (MinLat, MaxLat, 1) :
    App.run_command('generate-contours interval=10 bounds='+str(Lon)+','+str(Lat)+ ',' +str(Lon+1)+','+str(Lat+1))
    App.run_command('save-source ' + os.path.join('Cache', 'ASTER-'+str(Lon)+'-'+str(Lat)+'.contours'))

# App.run_command('save-map-script file=' + os.path.join('Scripts', 'Contours.mscript'))
