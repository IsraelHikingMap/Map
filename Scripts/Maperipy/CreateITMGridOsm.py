'''Create OSM file with horizontal and vertical "ways" (lines) according to ITM.
The lines are based on a fixed-distance lattice. 
Each line and node has labels to asist in renderingg the ITM grid.
'''

from maperipy import *
from maperipy.osm import *
import os

from System.Collections.Generic import List
import clr
clr.AddReference('GeoAPI')
clr.AddReference('ProjNet')
from GeoAPI.Geometries import *
from GeoAPI.CoordinateSystems import *
from ProjNet.CoordinateSystems import *
from ProjNet.CoordinateSystems.Transformations import *

'''Grid creation boundries - in meters
'''
iGridStartN = 375000
iGridEndN = 805000
iGridStartE = 120000
iGridEndE = 285000
iGridStep = 1000

sFileName = 'Cache\ITMGrid.osm'

coordinateSystemFactory = CoordinateSystemFactory()

itmDatum = coordinateSystemFactory.CreateHorizontalDatum(
        "Isreal 1993", 
        DatumType.HD_Geocentric, 
        Ellipsoid.GRS80, 
        Wgs84ConversionInfo(-24.0024, -17.1032, -17.8444, -0.33077, -1.85269, 1.66969, 5.4248))

itmGeo = coordinateSystemFactory.CreateGeographicCoordinateSystem(
        "ITM", 
        AngularUnit.Degrees, 
        itmDatum, 
        PrimeMeridian.Greenwich,
        AxisInfo("East", AxisOrientationEnum.East),
        AxisInfo("North", AxisOrientationEnum.North))

itmParameters = List[ProjectionParameter]([
        ProjectionParameter("latitude_of_origin", 31 + (44 + 03.8170/60)/60),
        ProjectionParameter("central_meridian", 35 + (12 + 16.2610/60)/60),
        ProjectionParameter("false_northing", 626907.390),
        ProjectionParameter("false_easting", 219529.584),
        ProjectionParameter("scale_factor", 1.0000067)
        ])

itmProjection = coordinateSystemFactory.CreateProjection(
        "Transverse_Mercator", 
        "Transverse_Mercator", 
        itmParameters)

ITM = coordinateSystemFactory.CreateProjectedCoordinateSystem(
        "ITM", 
        itmGeo, 
        itmProjection, 
        LinearUnit.Metre,
        AxisInfo("East", AxisOrientationEnum.East), 
        AxisInfo("North", AxisOrientationEnum.North))

WGS84 = GeographicCoordinateSystem.WGS84

Transformation = CoordinateTransformationFactory().CreateFromCoordinateSystems(ITM, WGS84).MathTransform

'''Israel New Grid (ITM) to WGS84 conversion
'''
def ITM2WGS84(N, E) :
    point = Transformation.Transform(Coordinate(E,N))
    return (point.Y, point.X)

'''Create the osm file with the lattice nodesand the grid ways
'''

IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: ' + App.script_dir)
# App.log('IsraelHikingDir: ' + IsraelHikingDir)
App.run_command('change-dir dir="' + IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

osmFile = open(sFileName, 'w')
iId = 0
# writing osm header
osmFile.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
osmFile.write('<osm version="0.5" generator="CreateITMGridOsm.py">' + "\n")

# Adding all the junction nodes
for iN in range(iGridStartN, iGridEndN + iGridStep, iGridStep) :
    for iE in range(iGridStartE, iGridEndE + iGridStep, iGridStep) :
	(dbLat,dbLon) = ITM2WGS84(iN, iE)
	osmFile.write('  <node id="' + str(iId) + '" visible="true" lat="' + str(dbLat) + '" lon="' + str(dbLon) + '">' + "\n")
	osmFile.write('    <tag k="grid" v="ITM"/>' + "\n")
	osmFile.write('    <tag k="east" v="' +  str(iE / 1000) + '"/>' + "\n")
	osmFile.write('    <tag k="north" v="' +  str(iN / 1000) + '"/>' + "\n")
	osmFile.write('  </node>' + "\n")
	iId = iId + 1

# Adding horizontal lines
for iN in range(iGridStartN, iGridEndN + iGridStep, iGridStep) :
    osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
    iId = iId + 1
    for iE in range(iGridStartE, iGridEndE + iGridStep, iGridStep) :
	iNodeId = ((iE - iGridStartE) + (iN - iGridStartN) * (1 + (iGridEndE - iGridStartE)/ iGridStep)) / iGridStep
	osmFile.write('    <nd ref="' + str(iNodeId) + '"/>' + "\n")
    osmFile.write('    <tag k="grid" v="ITM"/>' + "\n")
    osmFile.write('    <tag k="name" v="' +  str(iN / 1000) + '"/>' + "\n")
    osmFile.write('  </way>' + "\n")
    
# Adding vertical lines
for iE in range(iGridStartE, iGridEndE + iGridStep, iGridStep) :
    osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
    iId = iId + 1
    for iN in range(iGridStartN, iGridEndN + iGridStep, iGridStep) :
	iNodeId = ((iE - iGridStartE) + (iN - iGridStartN) * (1 + (iGridEndE - iGridStartE)/ iGridStep)) / iGridStep
	osmFile.write('    <nd ref="' + str(iNodeId) + '"/>' + "\n")
    osmFile.write('    <tag k="grid" v="ITM"/>' + "\n")
    osmFile.write('    <tag k="name" v="' +  str(iE / 1000) + '"/>' + "\n")
    osmFile.write('  </way>' + "\n")

# writing osm fotter
osmFile.write('</osm>')
osmFile.close()

# vim: shiftwidth=4 expandtab ai
