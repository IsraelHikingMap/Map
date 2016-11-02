# SRTM_bathimetry.py: Remove bathimetry information from SRTM HGT files
# Overides underwater and shoreline elevations to the higher 10-meter value

import os
import os.path
import math
import array
import struct
from maperipy import App
from maperipy import Map
# import sys

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(
        os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: '+MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: '+ProgramFiles)
IsraelHikingDir = os.path.dirname(os.path.dirname(
            os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('IsraelHikingDir: '+IsraelHikingDir)

HGTDir = 'ASTER'
os.chdir(os.path.join(IsraelHikingDir, 'Cache', 'Rasters', HGTDir))
App.run_command('change-dir dir="'
                + os.path.join(IsraelHikingDir, 'Cache', 'Rasters', HGTDir)
                + '"')

# Set bounds to match
# http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf
App.run_command("set-geo-bounds 34.07929,29.37711,35.91531,33.35091");

# Geo bounds in integer degrees
MinLon = int(Map.geo_bounds.min_x)
MaxLon = int(math.ceil(Map.geo_bounds.max_x))

MinLat = int(Map.geo_bounds.min_y)
MaxLat = int(math.ceil(Map.geo_bounds.max_y))

# Loop throu HGT files
# TODO: add support for South and West hemisphares
# if False: # 
for baseLat in range (MinLat, MaxLat, 1):
    for baseLon in range (MinLon, MaxLon, 1):
        fileName = "N{:02}E{:03}.hgt".format(baseLat, baseLon)
        # Determine number of 2-byte cells in the 1-degree square
        numCells = os.path.getsize(fileName)//2
        if numCells <> 3601*3601 and numCells <> 1201*1201:
            App.log("Unknown edge length: {}. File {} skipped," \
                    .format(edgeLen, fileName))
            continue
        # Number of cells on each edge of the square
        edgeLen = int(math.sqrt(numCells))
        App.log("Removing bathimetry in "+fileName)
        fileContent = array.array('h')
        with open(fileName, mode='rb') as file:
            # Read all cells to an array
            fileContent.fromfile(file, numCells)
            # Convert to little endian
            fileContent.byteswap()
            file.close()
            maxEle = -32768
            minEle = 32767
            for i in range(numCells):
                # Cells are arranged in rows from North to South
                # Each row is arranged West to East
                # All edge cells have integer lat and/or lon
                lat = baseLat + 1 - (i//edgeLen)/(edgeLen-1.0)
                lon = baseLon + (i%edgeLen)/(edgeLen-1.0)
                ele = fileContent[i]
                if ele == -32768:  # Keep voids as-is
                    pass
                # set minimum elevation, if needed
                elif fileName == "N32E035.hgt":
                    if lon < 35.2:
                        # Mediterranean Sea
                        if ele < 10:
                            ele = 10
                    elif lat > 32.7:
                        # Sea of Galilee
                        if ele < -200:
                            ele = -200
                elif fileName in ["N30E035.hgt", "N31E035.hgt"]:
                    # Dead Sea
                    if ele < -380:
                        ele = -380
                elif fileName == "N33E035.hgt":
                    if lon < 35.2:
                        # Mediterranean Sea
                        if ele < 10:
                            ele = 10
                else:
                    if ele < 10:
                        ele = 10
                if ele > maxEle:
                    maxEle = ele
                if ele < minEle:
                    minEle = ele
                # update elevation
                fileContent[i] = ele
        # Write file from buffer
        with open(fileName, mode='wb') as file:
            # Convert to big endian
            fileContent.byteswap()
            # Write the updated array back to the file
            fileContent.tofile(file)
            file.close()
        App.log("{}m to {}m".format(minEle, maxEle))

os.chdir(IsraelHikingDir)
App.run_command('change-dir dir="'+IsraelHikingDir+'"')

# vim: shiftwidth=4 expandtab
