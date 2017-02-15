import os.path
import math
import sqlite3
from maperipy import App
from maperipy import Map
import sys

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: '+MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: '+ProgramFiles)
IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('IsraelHikingDir: '+IsraelHikingDir)
App.run_command('change-dir dir="'+IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

# Set bounds to match
# http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf
App.run_command("set-geo-bounds 34.07929,29.37711,35.91531,33.35091");

# Geo bounds in integer degrees
MinLon=Map.geo_bounds.min_x
MaxLon=Map.geo_bounds.max_x

MinLat=int(Map.geo_bounds.min_y)
MaxLat=int(math.ceil(Map.geo_bounds.max_y))

HGTDir = 'ASTER'

App.run_command('set-dem-source '+HGTDir)
App.run_command('set-setting name=scripts.completion-signal.min-duration-sec value=99999')

App.log("Generating contours {}-{} to {}-{}".format(MinLon, MinLat, MaxLon, MaxLat))

for Lat in range (MinLat, MaxLat, 1) :
#  for Lon in range (MinLon, MaxLon, 1) :
    App.run_command('clear-map')
    App.run_command('generate-contours interval=10 bounds={},{},{},{}'
                    .format(MinLon, max(Lat, Map.geo_bounds.min_y),
                            MaxLon, min(Lat+1, Map.geo_bounds.max_y)))
    App.run_command('save-source ' 
                    + os.path.join('Cache', '{}-N{}.contours'.format(HGTDir, Lat)))

# vim: shiftwidth=4 expandtab
