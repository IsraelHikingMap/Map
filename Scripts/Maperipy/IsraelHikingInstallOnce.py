#
# Perform one-time installation tasks:
# 1. Copy DEM files to Maperitive installation
# 2. Copy additional icons to the Maperitive installation
# 3. Set map decoration defaults
# 4. Update Mobile Atlas Creator files, including ajdusting local map sources path
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
App.log("Copy new DEM files, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Cache", "Rasters")+'"', '"'+os.path.join(MaperitiveDir, "Cache", "Rasters")+'"'])

App.log("Copy new Icons, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Icons")+'"', '"'+os.path.join(MaperitiveDir, "icons")+'"'])

App.log("Copy new Textures, if any, to the Maperitive Installation")
App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+os.path.join(IsraelHikingDir, "Textures")+'"', '"'+os.path.join(MaperitiveDir, "Textures")+'"'])

App.run_command("set-setting name=map.decoration.grid value=False")
App.run_command("set-setting name=map.decoration.scale value=False")
App.run_command("set-setting name=map.decoration.attribution value=False")

mobacSourceDir = os.path.join(IsraelHikingDir, "Mobile Atlas Creator", "mapsources")
mobacTargetDir = os.path.join(os.path.dirname(MaperitiveDir), "Mobile Atlas Creator", "mapsources")
if os.path.isdir(mobacTargetDir):
    App.log("Copy ajdusted new map sources, if any, to the Mobile Atlas Creator Installation")
    numFiles=0
    for fileName in os.listdir(mobacSourceDir):
        sourceFile = os.path.join(mobacSourceDir, fileName)
        targetFile = os.path.join(mobacTargetDir, fileName)
        if (not os.path.exists(targetFile)
                or os.path.getmtime(sourceFile) > os.path.getmtime(targetFile)):
            with open(sourceFile, "r") as fin:
                with open(targetFile, "w") as fout:
                    for line in fin:
                        fout.write(line.replace(
                            "C:\Users\yourself\Documents\GitHub\IsraelHikingMap\Map",
                            IsraelHikingDir))
            App.log("{} -> {}".format(sourceFile, targetFile))
            numFiles += 1
    App.log("{} File(s) copied.".format(numFiles))

    mobacSourceDir = os.path.dirname(mobacSourceDir)
    mobacTargetDir = os.path.dirname(mobacTargetDir)
    App.log("Copy other new files, if any, to the Mobile Atlas Creator Installation")
    App.run_program('xcopy.exe', 1200, ["/S/I/D/F/R/Y", '"'+mobacSourceDir+'"', '"'+mobacTargetDir+'"'])

# vim: set shiftwidth=4 expandtab textwidth=0:
