# -*- coding: utf-8 -*-

# Creates a bounding Polygon for Israel Hiking Map
# Modified from the israel-and-palestine.poly from GEOfabric
# http://download.geofabrik.de/asia/israel-and-palestine.poly

# Author: Zeev Stadler
# License: public domain

import math
import os
from maperipy import *
from maperipy.webmaps import Tile
from maperipy.tilegen import TileGenCommand

IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('APP.script_dir: ' + App.script_dir + ', IsraelHikingDir: ' + IsraelHikingDir)

class IsraelHikingTileGenCommand(TileGenCommand):

  israel_and_palestine = Polygon(LinearRing.from_coords(( \
      (3.465362E+01, 3.208569E+01), # Haifa Coast: (3.464563E+01, 3.292073E+01) \
      (3.498374E+01, 3.313352E+01), \
      (3.515662E+01, 3.309994E+01), \
      (3.531781E+01, 3.311463E+01), \
      (3.536541E+01, 3.306285E+01), \
      (3.546229E+01, 3.309994E+01), \
      (3.551741E+01, 3.312652E+01), \
      (3.552660E+01, 3.321531E+01), \
      (3.553893E+01, 3.325442E+01), \
      (3.556446E+01, 3.329690E+01), \
      (3.561264E+01, 3.327918E+01), \
      (3.567429E+01, 3.330627E+01), \
      (3.570785E+01, 3.334269E+01), \
      (3.575363E+01, 3.335091E+01), \
      (3.581509E+01, 3.333920E+01), \
      (3.591531E+01, 3.294060E+01), \
      (3.580834E+01, 3.277200E+01), \
      (3.577835E+01, 3.272446E+01), \
      (3.559491E+01, 3.262828E+01), \
      (3.557290E+01, 3.236541E+01), \
      (3.559461E+01, 3.221856E+01), \
      (3.555452E+01, 3.202901E+01), \
      (3.557225E+01, 3.175415E+01), \
      (3.548771E+01, 3.141951E+01), \
      (3.542090E+01, 3.125116E+01), \
      (3.547936E+01, 3.117830E+01), \
      (3.542771E+01, 3.095172E+01), \
      (3.533210E+01, 3.077107E+01), \
      (3.520709E+01, 3.053307E+01), \
      (3.517202E+01, 3.011204E+01), \
      (3.507514E+01, 2.983713E+01), \
      (3.502336E+01, 2.964569E+01), \
      (3.493992E+01, 2.939946E+01), \
      (3.489517E+01, 2.937711E+01), \
      (3.484785E+01, 2.959084E+01), \
      (3.469667E+01, 3.010714E+01), \
      (3.452423E+01, 3.040912E+01), \
      (3.448879E+01, 3.064515E+01), \
      (3.415870E+01, 3.135333E+01), # Gaza Coast:  (3.407929E+01, 3.152265E+01), \
      (3.465362E+01, 3.208569E+01)  # Haifa Coast: (3.464563E+01, 3.292073E+01) \
    )))

  #print "israel_and_palestine.exterior: {0}" \
  #    .format(israel_and_palestine.exterior.coords)

  #print "Point(30.7513, 35.1563): {0}" \
  #    .format(Point(30.7513, 35.1563))

  #print "Point(30.7513, 35.1563) is in Israel_and_palestine: {0}" \
  #    .format(GeometryUtils.is_inside_linear_ring((Point(35.0, 32.0)), \
  #	  israel_and_palestine.exterior, True))

  def GenToDirectory(self, min_zoom, max_zoom, tiles_dir):
    App.collect_garbage()
    self.tiles_dir = tiles_dir
    self.min_zoom = min_zoom
    self.max_zoom = max_zoom
    self.gen_list_file = True
    if self.gen_clean_file:
      self.list_file = open(self.sFileName, 'w')
    self.execute()
    if self.gen_clean_file:
      self.list_file.close()
    App.collect_garbage()

  def num2deg(self, xtile, ytile, zoom):
    # This returns the NW-corner of the square. Use the function with xtile+1
    # and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it
    # will return the center of the tile.
    # 
    # Based on code from
    # http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2
    # 
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
#    print "num2deg({0}, {1}, {2}) = ({3}, {4})" \
#	.format(xtile, ytile, zoom, lat_deg, lon_deg)
    return Point(lon_deg, lat_deg)

  def tile_in_polygon(self, zoom, x, y, width, height, poly):
    self.nw_point = self.num2deg(x, y, zoom)
    self.se_point = self.num2deg(x+width, y+height, zoom)
    self.ne_point = self.num2deg(x+width, y, zoom)
    self.sw_point = self.num2deg(x, y+height, zoom)
    self.gen_polygon = Polygon(LinearRing([self.nw_point, self.ne_point, self.se_point, self.sw_point, self.nw_point]))
    result = \
        GeometryUtils.is_inside_linear_ring(self.nw_point, poly.exterior, True) or \
        GeometryUtils.is_inside_linear_ring(self.se_point, poly.exterior, True) or \
        GeometryUtils.is_inside_linear_ring(self.ne_point, poly.exterior, True) or \
        GeometryUtils.is_inside_linear_ring(self.sw_point, poly.exterior, True)
    if self.visualize and not result and zoom < 13:
      # Create a symbol for the Polygon
      self.polygon = PolygonSymbol("{0}/{1}/{2} ({3}x{4} tiles)" \
          .format(zoom, x, y, width, height), Srid.Wgs84LonLat)
      self.polygon.style.pen_width = 4
      self.polygon.style.pen_color = Color("green")
      self.polygon.style.pen_opacity = 0.5
      self.polygon.style.fill_opacity = 0
      # Add the plygon to the layer
      self.layer.add_symbol(self.polygon.add(self.gen_polygon))
    if not result:
      for xshift in xrange(width):
	for yshift in xrange(height):
	  self.skip_tile(zoom, x+xshift, y+yshift)
    return result

  def skip_tile(self, zoom, x, y):
    filename = "{0}/{1}/{2}.png".format(zoom, x, y)
    self.delete_tile(filename)
    self.delete_tile(filename+".finger")
    if self.gen_clean_file:
      self.list_file.write("rm -f " + filename + "*\n")

  def delete_tile(self, tilename):
    filename = os.path.join(self.tiles_dir, tilename)
    if os.path.exists(filename):
      os.remove(filename)

  def generation_filter (self, zoom, x, y, width, height):
    # Avoid generating tiles outside the polygon
    # Note: In Zoom 10 and below, the polygon can overlap a tile
    # with no tile corner inside the israel-and-palestine polygon
    generate = \
        zoom < 11 or \
        self.tile_in_polygon( \
          zoom, x, y, width, height, self.israel_and_palestine)
    if self.verbose:
      print "Generating tile batch: {0}/{1}/{2} ({3}x{4} tiles): {5}" \
          .format(zoom, x, y, width, height, generate)
    return generate

  def save_filter(self, tile):
    # In Zoom 10 and below, the polygon can overlap a tile
    # with no tile corner in the israel-and-palestine polygon
    save = \
        tile.zoom < 11 or \
        self.tile_in_polygon( \
            tile.zoom, tile.tile_x, tile.tile_y, 1, 1, self.israel_and_palestine)
    if self.verbose:
      print "Saving tile: {0}/{1}/{2}: {3}" \
          .format(tile.zoom, tile.tile_x, tile.tile_y, save)
    return save

  def __init__(self, print_bounds, min_zoom, max_zoom):
    # super(IsraelHikingTileGenCommand, self).__init__(BoundingBox(Srid.Wgs84LonLat, 34.00842, 29.32535, 35.92745, 33.398339999), 7, 16)
        # israel_and_palestine.bounding_box, min_zoom, max_zoom)
    self.visualize = False	# Show polygon and skipped areas on the map
    self.verbose = False	# Show tile generation progress
    self.gen_clean_file = False	# Create a sh file that removes all skipped tiles
    self.subpixel_precision = 3
    self.use_fingerprint = True
    self.tile_save_filter = self.save_filter
    self.tile_generation_filter = self.generation_filter
    if self.gen_clean_file:
      self.sFileName = 'Cache\\rm_tiles.sh'
      self.list_file = open(os.devnull, 'w')
    if self.visualize:
      # Show the Polygon on the map
      # Create a custom map layer...
      self.layer = Map.add_custom_layer()
      self.layer.visible = True
      # Create a symbol for the Polygon
      self.polygon = PolygonSymbol("israel_and_palestine", Srid.Wgs84LonLat)
      self.polygon.style.pen_width = 8
      self.polygon.style.pen_color = Color("blue")
      self.polygon.style.pen_opacity = 0.5
      self.polygon.style.fill_opacity = 0
      # Add the plygon to the layer
      self.layer.add_symbol(self.polygon.add(self.israel_and_palestine))
      Map.zoom_area(self.rendering_bounds)

Map.clear()
cmd =  IsraelHikingTileGenCommand(BoundingBox(Srid.Wgs84LonLat, 34.00842, 29.32535, 35.92745, 33.398339999), 7, 16)
# cmd.GenToDirectory(7, 16, "F:\Temp\Tiles2")

  # vim: sw=2
