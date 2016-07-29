import os.path
import math
import sqlite3
from maperipy import App
from maperipy import Map
import sys

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: ' + MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: ' + ProgramFiles)
IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: ' + App.script_dir)
# App.log('IsraelHikingDir: ' + IsraelHikingDir)
App.run_command('change-dir dir="' + IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

# Set bounds to match
# http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf
App.run_command("set-geo-bounds 34.07929,29.37711,35.91531,33.35091");

# Geo bounds in integer degrees
MinLon=int(Map.geo_bounds.min_x)
MaxLon=int(math.ceil(Map.geo_bounds.max_x))

MinLat=int(Map.geo_bounds.min_y)
MaxLat=int(math.ceil(Map.geo_bounds.max_y))

App.run_command('set-dem-source ASTER')
App.run_command('set-setting name=scripts.completion-signal.min-duration-sec value=99999')

App.log("Generating contours "+str(MinLon)+'-'+str(MinLat)+" to "+str(MaxLon)+'-'+str(MaxLat) )

for Lat in range (MinLat, MaxLat, 1) :
  for Lon in range (MinLon, MaxLon, 1) :
    App.run_command('generate-contours interval=10 min-ele=-380 bounds='+str(Lon)+','+str(Lat)+ ',' +str(Lon+1)+','+str(Lat+1))
    Quad = str(Lon)+'-'+str(Lat)
    Contours = os.path.join('Cache', 'ASTER-'+Quad+'.contours')
    App.run_command('save-source ' + Contours)
    App.run_command('remove-source')

    # Remove shore and off-shore contour lines
    try:
      Conn = None
      Conn = sqlite3.connect(Contours)
      App.log("Analysing the contours of " + Contours)
      Cur = Conn.cursor()
      if Quad == "35-32":
	# Sea of Galilee
	Cur.execute("DELETE FROM Contours WHERE Elevation <= -210 AND MinY>32.7;")
	App.log("Removed "+str(Cur.rowcount)+" shore and off-shore contour lines")
      elif Quad in set(["35-30", "35-31"]):
	# Jordan Valley
	App.log("Removed "+str(Cur.rowcount)+" shore and off-shore contour lines")
      else:
	# Elsewhere
	Cur.execute("DELETE FROM Contours WHERE Elevation <= 0;")
	App.log("Removed "+str(Cur.rowcount)+" shore and off-shore contour lines")
      Conn.commit()
      Cur.close()
      App.log("Changes comitted")
    except sqlite3.Error, e:
      print "Error %s:" % e.args[0]
      sys.exit(1)

# App.run_command('save-map-script file=' + os.path.join('Scripts', 'Contours.mscript'))
