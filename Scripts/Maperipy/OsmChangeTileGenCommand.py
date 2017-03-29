"""Tile generation restriction by an Osm Change file and a polygon.

Read a compressed or uncompressed Osm Change file
Analyze the tiles that were modified at a given range of zoom levels.
Potentially perform the analysis on additional Osm Change files.
Restrict the tile generation within a polygon to changed tiles and their adjecent tiles.

Inputs for each analysis:
- Osm Change file
- Base and new OSM maps, each as either a pbf file or an existing map layer
"""

# TODO:
# - mark center of rel_bbox for relations using members_bbox?
# - Check the removal of the guardband given the "map.rendering.tiles.rendering-bounds-buffer"
#   settings which "specifies the additional buffer around the tile rendering bounds to prevent 
#   labels being cut off at neighboring tiles. Specified as percentage of value, the default is 10%"

# import string
import math
import os
from datetime import *
from time import sleep
from System.IO import TextReader
from maperipy import *
from maperipy.osm import *
from PolygonTileGenCommand import PolygonTileGenCommand
import gzip  # https://bitbucket.org/jdhardy/ironpythonzlib/src/tip/tests/gzip.py
import clr
clr.AddReference('System.Xml')
from System.Xml import *

class OsmChangeTileGenCommand(PolygonTileGenCommand):
    """Analyse an OsmChange file and find all tiles to be updated

    Changed tiles are stored in a dictionary of dictionaries:
    self.changed[zoom][(tile_x, tile_y)]
    Changed tiles are added at max_zoom and propagated to lower zoom levels if needed.

    Tiles to be updated are either changed or adjecant to changed tiles.
    self.guard[zoom][(tile_x, tile_y)] is a cache for the tiles to be updated
    """

    def generation_filter(self, zoom, x, y, width, height):
        """Filter rendering of the map in a super-tile"""
        # DEBUG EXAMPLE
        # self.verbose = ((zoom == 13) and (x <= 4899) and (4899 <= (x+width-1)) and (y <= 3327) and (3327 <= (y+height-1)))
        if self.changed is None:
            # Change analysis is not used
            return PolygonTileGenCommand.generation_filter(self, zoom, x, y, width, height)
        self._progress_update(zoom, width*height)
        generate = self.updated(zoom, x, y, width, height)
        if self.verbose:
            print "     OsmChangeTileGenCommand - Generating {}x{} super-tile: {}/{}/{}: {}".format(
                    width, height, zoom, x, y, generate)
        return generate

    def save_filter(self, tile):
        """Filter the saving to disk of individual tiles in the super tile"""
        # DEBUG EXAMPLE
        # self.verbose = ((tile.zoom == 13) and (tile.tile_x == 4899) and (tile.tile_y == 3327))
        if self.changed is None:
            # Change analysis is not used
            return PolygonTileGenCommand.save_filter(self, tile)
        save = self.updated(tile.zoom, tile.tile_x, tile.tile_y, 1, 1)
        if self.verbose:
            reason = "Changed" if (tile.tile_x, tile.tile_y) in self.changed[tile.zoom] else ("Guard band" if save else "Skipped")
            # TODO # self.reason[reason] += 1
            App.log("     OsmChangeTileGenCommand - Saving tile: {}/{}/{}: {}".format(
                    tile.zoom, tile.tile_x, tile.tile_y, reason))
        return save

    def osmChangeRead(self, change_file, base_map, new_map):
        """Analyze which tiles require an update by using a change file with base and new maps.

        The base pbf file is added to the map as an invisible layer and removed after the analysis
        The new pbf file is added to the map.

        Inputs: File names of the change file, base map, and new map
        The base map is used for locating tiles with deleted and changed objects.
        The new map is used for locating tiles with new and changed objects.
        """

        App.collect_garbage()
        if self.changed == None:
            self.changed = {x:{} for x in range(self.min_zoom, self.max_zoom+1)}
        # Initialize the guard zone tiles
        self.guard = None
        if self.verbose:
            print "     Reading change file", change_file, "..."
        osmChange = XmlDocument()
        osmChange.Load(osmChangeReader(change_file))
        for element in osmChange.SelectNodes("./osmChange"):
            if not element.HasChildNodes:
                return
        if self.verbose:
            print "     Reading base OSM map from", base_map, "..."
        sleep(10)  # Try to avoid CommandExecutionException
        App.run_command('load-source file="{}"'.format(base_map))
        sleep(10)  # Try to avoid CommandExecutionException
        base_index = len(Map.layers)
        Map.layers[base_index-1].visible = False
        baseOsm = Map.layers[base_index-1].osm
        App.collect_garbage()
        if self.verbose:
            App.log("     Reading new OSM map from {} ...".format(new_map))
        App.run_command('load-source file="{}"'.format(new_map))
        sleep(10)  # Try to avoid CommandExecutionException
        new_index = len(Map.layers)
        App.collect_garbage()
        newOsm = Map.layers[new_index-1].osm
        if self.verbose:
            print "     Analyzing change file ..."
        sum = {key : 0 for key in ("node", "way", "relation")}
        for element in osmChange.SelectNodes("./osmChange/*/*"):
            action = element.ParentNode.Name  # "delete", "modify", or "create"`
            element_type = element.Name  # "node", "way", or "relation"
            element_id = long(element.Attributes.GetNamedItem("id").Value)
            # DEBUG EXAMPLE
            # self.verbose = ((element_type == "relation") and (element_id == 3791784))
            sum[element_type] += 1
            if self.verbose:
                print "     {} {} id={}:".format(action, element_type, element_id)
            try:
                if action in ("delete", "modify"):
                    for bbox in self.bboxes(baseOsm, element_type, element_id):
                            self.mark_bbox(bbox)
                if action in ("create", "modify"):
                    for bbox in self.bboxes(newOsm, element_type, element_id):
                        self.mark_bbox(bbox)
            except KeyError:
                # An element does bot exist in the map,
                # no need to redraw its position
                pass
        App.collect_garbage()
        if self.verbose:
            print "     Analyzed {} nodes, {} ways, and {} relations.".format(
                    sum["node"], sum["way"], sum["relation"])
        App.run_command('remove-source index="{}"'.format(base_index))

    def __init__(self, *args):
        PolygonTileGenCommand.__init__(self)
        self.changed = None
        self.guard = None

    def execute(self):
        if self.changed is not None:
            if self.changed[min(self.changed)]:
                self.update_guard()
            else:
                # Change analysis was done, but nothing was changed
                return
        PolygonTileGenCommand.execute(self)

    def updated(self, zoom, x, y, width, height):
        if self.verbose:
            App.log("updated({}, {}, {}, {}, {})".format(zoom, x, y, width, height))
        try:
            # Leverage the guard to check every 3rd row and column inside the super-tile
            # Note: This is for safety. We did not see width or height values larger than 3.
            for tile_x in range(x, x+width, 3) + [x+width-1]:
                for tile_y in range(y, y+width, 3) + [y+width-1]:
                    if self.verbose:
                        App.log("({}, {}) {} in self.guard[{}]".format(
                            tile_x, tile_y,
                            "" if (tile_x, tile_y) in self.guard[zoom] else "not ",
                            zoom))
                    if (tile_x, tile_y) in self.guard[zoom]:
                        return True
            return False
        # Handle rare scenarios through exceptions
        except TypeError:
            if self.guard is None:
                # Guard is not updated
                self.update_guard()
                return self.updated(zoom, x, y, width, height)
            else:
                raise
        except KeyError:
            # Zoom levels during tile generation may differ from analyzed zoom levels
            if zoom > max(self.changed):
                # Look for a tile at zoom == max(self.changed) that covers this tile
                return self.updated(zoom-1, x//2, y//2)
            elif zoom < min(self.changed):
                # Look for a tile at zoom == min(self.changed) that is covered by this tile
                zoom += 1
                x *= 2
                y *= 2
                return (self.updated(zoom, x, y)
                        or self.updated(zoom, x+1, y+1)
                        or self.updated(zoom, x, y+1)
                        or self.updated(zoom, x+1, y))
            else:
                raise

    def new_tile_upwards(self, x, y, zoom):
        if self.verbose:
            App.log("     New tile upwards {}, {}, zoom {}".format(x, y, zoom))
        if zoom > max(self.changed) or self.new_tile(x, y, zoom):
            self.new_tile_upwards(x//2, y//2, zoom-1)

    def new_tile(self, x, y, zoom):
        tile = (x, y)
        if zoom not in self.changed or tile in self.changed[zoom]:
            if self.verbose:
                if zoom not in self.changed:
                    App.log("     No new tile {}/{}/{}, zoom not in self.changed".format(zoom, x, y))
                if tile in self.changed[zoom]:
                    App.log("     No new tile {}/{}/{}, already there".format(zoom, x, y))
            return False
        else:
            self.changed[zoom][tile] = True
            if self.verbose:
                App.log("     New tile {}/{}/{}".format(zoom, x, y))
            return True

    def update_guard(self):
        """If needed, update the cache of tiles to be rendered
        by adding a guard of one tile around each changed tile.
        Avoid adding tiles outside the polygon.
        """
        if self.guard is not None:
            return
        self.guard={}
        tile_checked = {}
        for zoom in sorted(self.changed):
            self.guard[zoom] = {}
            tile_checked[zoom] = {}
            for (x, y) in self.changed[zoom]:
                for x_guard in range(x-1, x+2):
                    for y_guard in range(y-1, y+2):
                        if (x_guard, y_guard) not in tile_checked[zoom]:
                            # Check each tile once
                            tile_checked[zoom][(x_guard, y_guard)] = True
                            if ((zoom == min(self.changed) or (x_guard//2, y_guard//2) in self.guard[zoom-1])
                                    and self.tiles_overlapps_polygon(zoom, x_guard, y_guard, 1, 1)):
                                # Included in guard of lower zoom, if exists, and in the polygon 
                                self.guard[zoom][(x_guard, y_guard)] = True

    def statistics(self):
        self.update_guard()
        sum_changed = 0
        sum_guard = 0
        for zoom in self.changed:
            cur_changed = len(self.changed[zoom])
            cur_guard = len(self.guard[zoom])
            sum_changed += cur_changed
            sum_guard += cur_guard
            print "     zoom {:2} has {:6} changed tiles, {:6} update tiles".format(
                    zoom, cur_changed, cur_guard)
        print "     Total of    {:6} changed tiles, {:6} update tiles".format(
                sum_changed, sum_guard)
        return (sum_changed, sum_guard)

    def mark_bbox(self, bbox):
        # Update all tiles covering the bounding box
        if not self.linear_ring_overlapps_polygon(bbox.polygon.exterior):
            # Ignore changes outside the generation polygon
            return
        zoom = max(self.changed)
        (left, top) = self.deg2num(bbox.max_y, bbox.min_x, zoom)
        (right, bottom) = self.deg2num(bbox.min_y, bbox.max_x, zoom)
        if self.visualize:
            if not self.layer:
                # Create a custom map layer...
                self.layer = Map.add_custom_layer()
                self.layer.visible = True
            # Create a symbol for the Polygon
            bbox_title = "{0}/{1}/{2} ({3}x{4} tiles)".format(
                zoom, left, top, right-left+1, bottom-top+1)
            if self.verbose:
                App.log("mark_bbox: {}".format(bbox_title))
            tile_symbol = PolygonSymbol(bbox_title, Srid.Wgs84LonLat)
            tile_symbol.style.pen_width = 2
            tile_symbol.style.pen_color = Color("blue")
            tile_symbol.style.pen_opacity = 0.5
            tile_symbol.style.fill_opacity = 0
            # Add the plygon of the tiles to the visualization layer
            self.layer.add_symbol(tile_symbol.add(Polygon(LinearRing([
                self.num2deg(left, top, zoom),  # NW of NW tile
                self.num2deg(right+1, top, zoom),  # NE of NE tile
                self.num2deg(right+1, bottom+1, zoom),  # SE of SE tile
                self.num2deg(left, bottom+1, zoom),  # SW of SW tile
                self.num2deg(left, top, zoom)  # NW of NW tile
                ]))))
        if self.verbose:
            App.log("     mark_bbox for x in range ({}, {}):".format(left, right+1))
            App.log("     mark_bbox     for y in range ({}, {}):".format(top, bottom+1))
        for x in range (left, right+1):
            for y in range(top, bottom+1):
                self.new_tile_upwards(x, y, zoom)
                if self.verbose:
                    App.log("     mark_bbox        new_tile_upwards(({}, {}), {})".format(x, y, zoom))

    def rel_members_bbox(self, relation):
        return not (relation.has_tag("type") and relation.get_tag("type") == "multipolygon")

    def bboxes(self, osm_data, element_type, element_id):
        if self.verbose:
            App.log("     finding bboxes of {} {}".format(element_type, element_id))
        if element_type == "node":
            yield osm_data.node(element_id).location.bounding_box
        elif element_type == "way":
            yield osm_data.get_way_geometry(element_id).bounding_box
        elif element_type == "relation":
            relation = osm_data.relation(element_id) 
            members_bbox = self.rel_members_bbox(relation) # Yield each member's bbox?
            rel_bbox = BoundingBox(Srid.Wgs84LonLat)  # Members bboxes accumulator, if needed
            for member in relation.members:
                member_type = None
                if member.ref_type==OsmReferenceType.NODE and osm_data.has_node(member.ref_id):
                    member_type = "node"
                elif member.ref_type==OsmReferenceType.WAY and osm_data.has_way(member.ref_id):
                    member_type = "way"
                elif member.ref_type==OsmReferenceType.RELATION and osm_data.has_relation(member.ref_id):
                    member_type = "relation"
                for bbox in self.bboxes(osm_data, member_type, member.ref_id):
                    if members_bbox:
                        # Yield each member's bbox
                        yield bbox
                    else:
                        rel_bbox.extend_with(bbox)
                if not members_bbox:
                    # Yield the accumulated bbox of all members
                    yield rel_bbox

class osmChangeReader(TextReader):
    def __init__(self, filename):
        if filename[-3:] == ".gz":
            self.f = gzip.open(filename)
        else:
            self.f = open(filename)
    def Read(self, buffer, index, count):
        chars = self.f.read(count).ToCharArray()
        chars.CopyTo(buffer, index)
        return len(chars)

# vim: set shiftwidth=4 expandtab textwidth=0:
