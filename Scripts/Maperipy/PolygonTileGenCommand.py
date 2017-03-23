"""Tile generation restriction within a polygon

The GenToDirectory method generates tiles in a given zoom interval into a directory

Tile generation options:
  - Remove tiles outside of the polygon from disk
  - Create a Unix script to remove such tiles independently
  - Visualize the ploygon, the generated super-tiles, and the saved tiles

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
        if self.visualize and self.generation_polygon:
            # Show the Polygon on the map
            if not self.layer:
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
        n = 2.0**zoom
        lon_deg = 360.0*xtile/n - 180.0
        lat_rad = math.atan(math.sinh(math.pi*(1 - 2*ytile/n)))
        lat_deg = math.degrees(lat_rad)
        return Point(lon_deg, lat_deg)

    def deg2num(self, lat, lon, zoom):
        # Adapted from
        # http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
        lat_deg = float(lat)
        lon_deg = float(lon)
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        tile_x = int((lon_deg + 180.0) / 360.0 * n)
        tile_y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (tile_x, tile_y)

    def linear_ring_overlapps_polygon(self, geometry):
        result = False
        # Start with the geometry nodes, as it is usually a rectangle
        for point in geometry.coords:
            if GeometryUtils.is_inside_linear_ring(point, self.generation_polygon.exterior, True):
                # A geometry node is inside the polygon
                result = True
                break
        else:
            for point in self.generation_polygon.exterior.coords:
                if GeometryUtils.is_inside_linear_ring(point, geometry, True):
                    # A polygon node is inside the geometry
                    result = True
                    break
        return result

    def tiles_overlapps_polygon(self, zoom, x, y, width, height):
        if self.generation_polygon is None:
            return True
        tile_geometry = LinearRing([
            self.num2deg(x, y, zoom),  # NW
            self.num2deg(x+width, y, zoom),  # NE
            self.num2deg(x+width, y+height, zoom),  # SE
            self.num2deg(x, y+height, zoom)])  # SW
        result = self.linear_ring_overlapps_polygon(tile_geometry)
        if False and self.verbose:
            print "     overlap query bbox: ({:10.7f}, {:11.7f}, {:10.7f}, {:11.7f}), tiles {}/{} - {}/{}: {}".format(
                    tile_geometry.bounding_box.min_y, tile_geometry.bounding_box.min_x,
                    tile_geometry.bounding_box.max_y, tile_geometry.bounding_box.max_x,
                    x, y, x+width-1, y+height-1, result)
        if result:
            if self.visualize and zoom < 13:
                if not self.layer:
                    # Create a custom map layer...
                    self.layer = Map.add_custom_layer()
                    self.layer.visible = True
                # Create a polygon for the tile
                tile_polygon = Polygon(tile_geometry)
                # Create a symbol for the tile
                tile_symbol = PolygonSymbol("{}/{}/{} ({}x{} tiles)".format(
                    zoom, x, y, width, height), Srid.Wgs84LonLat)
                tile_symbol.style.pen_width = 4
                if width+height > 2:
                  # A generation bbox
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
            self.list_file.write("rm -f {}*\n".format(filename))

    def delete_tile(self, tilename):
        filename = os.path.join(self.tiles_dir, tilename)
        if os.path.exists(filename):
            os.remove(filename)

    def generation_filter (self, zoom, x, y, width, height):
        """Avoid generating tile batches outside the polygon"""
        self._progress_update(zoom, width*height)
        generate = self.tiles_overlapps_polygon(zoom, x, y, width, height)
        if self.verbose:
            print "     PolygonTileGenCommand - Generating {}x{} super-tile: {}/{}/{}: {}".format(
                width, height, zoom, x, y, generate)
        return generate

    def save_filter(self, tile):
        save = self.tiles_overlapps_polygon(tile.zoom, tile.tile_x, tile.tile_y, 1, 1)
        if self.verbose:
            print "     PolygonTileGenCommand - Saving tile: {}/{}/{}: {}".format(
                tile.zoom, tile.tile_x, tile.tile_y, save)
        return save

    def __new__(cls, *args):
        if isinstance(args[0], Polygon):
            bbox = LineSymbol("Generation filter Polygon", Srid.Wgs84LonLat, [args[0]]).bounding_box
            cmd = TileGenCommand.__new__(cls, bbox, args[1], args[2])
            cmd.generation_polygon = args[0]
        else:
            # Also allow construction with TileGenCommand's original parameters.
            cmd = TileGenCommand.__new__(cls, *args)
            cmd.generation_polygon = None
        return cmd

    def execute(self):
        self._progress_zoom = None
        try:
            TileGenCommand.execute(self)
        except BaseException as e:
            print "Exception during TileGenCommand.execute():", e
            if str(e) <> "ValueError: An item with the same key has already been added.":
                raise

    def _progress_update(self, zoom, size):
        if self._progress_zoom <> zoom:
            self._progress_zoom = zoom
            (left, bottom) = self.deg2num(self.rendering_bounds.min_y, self.rendering_bounds.min_x, zoom)
            (right, top) = self.deg2num(self.rendering_bounds.max_y, self.rendering_bounds.max_x, zoom)
            self._progress_target = (right-left+1)*(bottom-top+1)
            self._progress_count = 0
            self._progress_last_report = 0
            self._progress_report_step = max(1000, self._progress_target/10.0)
        if self._progress_count - self._progress_last_report > self._progress_report_step:
            print "     Scanned {}% of zoom {}".format(
                self._progress_count*100//self._progress_target, zoom)
            self._progress_last_report = self._progress_count
        self._progress_count += size

    def __init__(self):
        # Derived classes can overide the save_filter and generation_filter methods
        self.tile_save_filter = self.save_filter
        self.tile_generation_filter = self.generation_filter
        self.visualize = False  # Show polygon, generated and saved areas on the map?
        self.layer = None
        self.verbose = False  # Show tile generation progress?
        self.clean_tiles = False  # Remove all skipped tiles?
        self.tile_removal_script = 'Output\\rm_tiles.sh'  # Optional: tile removal script name
        self.list_file = open(os.devnull, 'w')

def pretty_timer(prefix, timer):
    days = timer // 3600*24
    if timer > 86400:
        if timer%86400 > 0:
            return pretty_timer("{} {:.0f} days".format(
                    prefix, timer//86400), timer%86400)
        else:
            return "{} {:.0f} days".format(
                    prefix, timer//86400)
    elif timer > 3600:
        if timer%60 > 0:
            return "{} {:.0f}:{:02.0f}:{:02.0f} hours".format(
                    prefix, timer//3600, (timer//60)%60, timer%60)
        elif timer%3600 > 0:
            return "{} {:.0f}:{:02.0f} hours".format(
                    prefix, timer//3600, (timer//60)%60)
        else:
            return "{} {:.0f} hours".format(
                    prefix, timer//3600)
    elif timer > 60:
        if timer%60 > 0:
            return "{} {:.0f}:{:02.0f} minutes".format(
                    prefix, timer//60, timer%60)
        else:
            return "{} {:.0f} minutes".format(
                    prefix, timer//60)
    else:
        return "{} {:.1f} seconds".format(prefix, timer)

# vim: set shiftwidth=4 expandtab textwidth=0:
