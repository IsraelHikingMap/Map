#
# Perform one-time installation tasks:
# 1. Copy DEM files to Maperitive installation
# 2. Copy additional icons to the Maperitive installation
#

import os.path
from maperipy import *

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
App.log('MaperitiveDir: ' + MaperitiveDir)
IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
App.log('IsraelHikingDir: ' + IsraelHikingDir)

#
# TODO: The following was tested only on MS-Windows platforms
#
App.log("Copy missing DEM files, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Cache", "Rasters")+'"', '"'+os.path.join(MaperitiveDir, "Cache", "Rasters")+'"'])

App.log("Copy missing Icons, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Icons")+'"', '"'+os.path.join(MaperitiveDir, "icons")+'"'])

App.log("Copy missing Textures, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Textures")+'"', '"'+os.path.join(MaperitiveDir, "Textures")+'"'])
