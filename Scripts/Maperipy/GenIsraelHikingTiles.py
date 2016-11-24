"""Restrict the tile generation to the israel-and-palestine.poly from GEOfabric
http://download.geofabrik.de/asia/israel-and-palestine.poly with a reduced sea area

Author: Zeev Stadler
License: public domain
"""

# import os
from maperipy import *
# from maperipy.webmaps import Tile
# from maperipy.tilegen import TileGenCommand
from PolygonTileGenCommand import PolygonTileGenCommand

class IsraelHikingTileGenCommand(PolygonTileGenCommand):
  def __new__(cls, *args):
    # DEBUG print "IsraelHikingTileGenCommand.__new__()" 
    israel_and_palestine = Polygon((  # Modifications from Geofabrik's poly file:
	(3.465362E+01, 3.208569E+01), # Closer to the Haifa Coast. Replaces (3.464563E+01, 3.292073E+01)
	(3.498374E+01, 3.313352E+01),
	(3.515662E+01, 3.309994E+01),
	(3.531781E+01, 3.311463E+01),
	(3.536541E+01, 3.306285E+01),
	(3.546229E+01, 3.309994E+01),
	(3.551741E+01, 3.312652E+01),
	(3.552660E+01, 3.321531E+01),
	(3.553893E+01, 3.325442E+01),
	(3.556446E+01, 3.329690E+01),
	(3.561264E+01, 3.327918E+01),
	(3.567429E+01, 3.330627E+01),
	(3.570785E+01, 3.334269E+01),
	(3.575363E+01, 3.335091E+01),
	(3.581509E+01, 3.333920E+01),
	(3.591531E+01, 3.294060E+01),
	(3.580834E+01, 3.277200E+01),
	(3.577835E+01, 3.272446E+01),
	(3.559491E+01, 3.262828E+01),
	(3.557290E+01, 3.236541E+01),
	(3.559461E+01, 3.221856E+01),
	(3.555452E+01, 3.202901E+01),
	(3.557225E+01, 3.175415E+01),
	(3.548771E+01, 3.141951E+01),
	(3.542090E+01, 3.125116E+01),
	(3.547936E+01, 3.117830E+01),
	(3.542771E+01, 3.095172E+01),
	(3.533210E+01, 3.077107E+01),
	(3.520709E+01, 3.053307E+01),
	(3.517202E+01, 3.011204E+01),
	(3.507514E+01, 2.983713E+01),
	(3.502336E+01, 2.964569E+01),
	(3.493992E+01, 2.939946E+01),
	(3.489517E+01, 2.937711E+01),
	(3.484785E+01, 2.959084E+01),
	(3.469667E+01, 3.010714E+01),
	(3.452423E+01, 3.040912E+01),
	(3.448879E+01, 3.064515E+01),
	(3.415870E+01, 3.135333E+01), # Closer to the Gaza Coast.  Replaces (3.407929E+01, 3.152265E+01),
	(3.465362E+01, 3.208569E+01)  # Closer to the Haifa Coast. Replaces (3.464563E+01, 3.292073E+01)
      ))
    cmd = PolygonTileGenCommand.__new__(cls, israel_and_palestine)
    return cmd

  def __init__(self):
    PolygonTileGenCommand.__init__(self)
    # DEBUG print "IsraelHikingTileGenCommand.__init__()" 
    self.subpixel_precision = 2
    self.use_fingerprint = True
    self.clean_tiles = True  # Remove all skipped tiles

    ## DEBUG ##
    # self.visualize = True
    # self.verbose = True

# vim: sw=2
