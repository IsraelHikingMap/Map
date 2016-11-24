"""Restrict the tile generation according to a polygon

- GenToDirectory method to generate tiles in a given zoom interval
- Optionally, remove tiles outside of the polygon
- Optionally, create a Unix script to remove the tiles
- Optionally, visualize the ploygon, the generated area, and the saved tiles

Author: Zeev Stadler
License: public domain
"""

import os
import math
from maperipy import *
from maperipy.tilegen import TileGenCommand

class PolygonTileGenCommand(TileGenCommand):
  def GenToDirectory(self, min_zoom, max_zoom, tiles_dir):
    """Generate a given range of zoom levels into a target tiles directory"""
    App.collect_garbage()
    self.tiles_dir = tiles_dir
    self.min_zoom = min_zoom
    self.max_zoom = max_zoom
    if self.clean_tiles and self.tile_removal_script:
      self.list_file.close()
      self.list_file = open(self.tile_removal_script, 'w')
    if self.visualize:
      # Show the Polygon on the map
      # Create a custom map layer...
      self.layer = Map.add_custom_layer()
      self.layer.visible = True
      # Create a symbol for the Polygon
      self.polygon = PolygonSymbol("GenerationPolygon", Srid.Wgs84LonLat)
      self.polygon.style.pen_width = 8
      self.polygon.style.pen_color = Color("blue")
      self.polygon.style.pen_opacity = 0.5
      self.polygon.style.fill_opacity = 0
      # Add the plygon to the layer
      self.layer.add_symbol(self.polygon.add(self.generation_polygon))
      Map.zoom_area(self.rendering_bounds)
    self.execute()
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
#    print "numdeg({}, {}, {}) = ({}, {})" \
#	.format(xtile, ytile, zoom, lat_deg, lon_deg)
    return Point(lon_deg, lat_deg)

  def tile_overlapps_polygon(self, zoom, x, y, width, height, poly):
    tile_geometry = LinearRing([
      self.num2deg(x, y, zoom),  # SW
      self.num2deg(x+width, y, zoom),  # SE
      self.num2deg(x+width, y+height, zoom),  # NE
      self.num2deg(x, y+height, zoom)])  # NW
    result = (
	# A tile corner is inside the polygon
	reduce(
	  lambda x, y: x or y,
	  map(
	    lambda point: GeometryUtils.is_inside_linear_ring(point, poly.exterior, True),
	    tile_geometry.coords))
	# Or a polygon node is inside the tile
	or reduce(
	  lambda x, y: x or y,
	  map(
	    lambda point: GeometryUtils.is_inside_linear_ring(point, tile_geometry, True),
	    poly.exterior.coords)))
    if result:
      if self.visualize and zoom < 13:
	# Create a polygon for the tile
	tile_polygon = Polygon(tile_geometry)
	# Create a symbol for the tile
	tile_symbol = PolygonSymbol("{}/{}/{} ({}x{} tiles)" \
	    .format(zoom, x, y, width, height), Srid.Wgs84LonLat)
	tile_symbol.style.pen_width = 4
	if width + height > 2:
	  tile_symbol.style.pen_color = Color("orange")
	else:
	  tile_symbol.style.pen_color = Color("green")
	tile_symbol.style.pen_opacity = 0.5
	tile_symbol.style.fill_opacity = 0
	# Add the polygon to the layer
	self.layer.add_symbol(tile_symbol.add(tile_polygon))
    elif self.clean_tiles:
      for xshift in xrange(width):
	for yshift in xrange(height):
	  self.clean_tile(zoom, x+xshift, y+yshift)
    return result

  def clean_tile(self, zoom, x, y):
    filename = "{}/{}/{}.png".format(zoom, x, y)
    self.delete_tile(filename)
    self.delete_tile(filename+".finger")
    if self.tile_removal_script:
      self.list_file.write("rm -f " + filename + "*\n")

  def delete_tile(self, tilename):
    filename = os.path.join(self.tiles_dir, tilename)
    if os.path.exists(filename):
      os.remove(filename)

  def generation_filter (self, zoom, x, y, width, height):
    # Avoid generating tile batches outside the polygon
    generate = self.tile_overlapps_polygon(
          zoom, x, y, width, height, self.generation_polygon)
    if self.verbose:
      print "Generating tile batch: {}/{}/{} ({}x{} tiles): {}".format(
	  zoom, x, y, width, height, generate)
    return generate

  def save_filter(self, tile):
    save = self.tile_overlapps_polygon(
            tile.zoom, tile.tile_x, tile.tile_y, 1, 1, self.generation_polygon)
    if self.verbose:
      print "Saving tile: {}/{}/{}: {}".format(
	  tile.zoom, tile.tile_x, tile.tile_y, save)
    return save

  def __new__(cls, *args):
    # DEBUG print "PolygonTileGenCommand.__new__()" 
    # TODO: 
    # Allow construction with TileGenCommand's original parameters.
    # Requires:
    # - Method for setting the polygon and updating the bbox accordingly
    # - Handling on a None polygon
    bbox = LineSymbol("Generation filter Polygon", Srid.Wgs84LonLat, [args[0]]).bounding_box
    cmd = TileGenCommand.__new__(cls, bbox, 7, 16)
    cmd.generation_polygon = args[0]
    Map.print_bounds = Map.create_print_bounds(bbox)
    return cmd

  def __init__(self):
    # DEBUG print "PolygonTileGenCommand.__init__()" 
    self.tile_save_filter = self.save_filter
    self.tile_generation_filter = self.generation_filter
    self.visualize = False  # Show polygon and skipped areas on the map?
    self.verbose = False  # Show tile generation progress?
    self.clean_tiles = False  # Remove all skipped tiles?
    self.tile_removal_script = 'Output\\rm_tiles.sh'  # Optional: tile removal script name
    self.list_file = open(os.devnull, 'w')

# vim: sw=2
