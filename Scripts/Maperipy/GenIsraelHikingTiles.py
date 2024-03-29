"""Tile generation setup for IsraelHiking.osm.org.il maps

- Zoom levels 7 to 16
- Tile generation restriction within a polygon
- Integrated with tile generation optimization based on an OSM change file
- Add configurable tile batch post-processing
- Add copyright to tile's meta data using batch post-processing

If run directly by the 'run-python' command, the script will generate tiles of
the current layers, using the default settings, to the Output\Tiles directory.
Copyright notice is not added.

Author: Zeev Stadler
License: public domain
"""

import time
import os.path
import re
from maperipy import *
from OsmChangeTileGenCommand import OsmChangeTileGenCommand
from PolygonTileGenCommand import pretty_timer

class IsraelHikingTileGenCommand(OsmChangeTileGenCommand):
    def __new__(cls, *args):
        # israel_and_palestine polygon defined using
        # http://download.geofabrik.de/asia/israel-and-palestine.poly
        # with a reduced sea area.
        israel_and_palestine = Polygon((  # Modifications from Geofabrik's poly file:
            (34.65362, 32.08569), # Closer to the Tel-Aviv Coast. Replaces (34.64563, 32.92073)
            (34.98374, 33.13352),
            (35.15662, 33.09994),
            (35.31781, 33.11463),
            (35.36541, 33.06285),
            (35.46229, 33.09994),
            (35.51741, 33.12652),
            (35.52660, 33.21531),
            (35.53893, 33.25442),
            (35.56446, 33.29690),
            (35.61264, 33.27918),
            (35.67429, 33.30627),
            (35.70785, 33.34269),
            (35.75363, 33.35091),
            (35.81509, 33.33920),
            (35.91531, 32.94060),
            (35.80834, 32.77200),
            (35.77835, 32.72446),
            (35.59491, 32.62828),
            (35.57290, 32.36541),
            (35.59461, 32.21856),
            (35.55452, 32.02901),
            (35.57225, 31.75415),
            (35.48771, 31.41951),
            (35.42090, 31.25116),
            (35.47936, 31.17830),
            (35.42771, 30.95172),
            (35.33210, 30.77107),
            (35.20709, 30.53307),
            (35.17202, 30.11204),
            (35.07514, 29.83713),
            (35.02336, 29.64569),
            (34.93992, 29.39946),
            (34.89517, 29.37711),
            (34.84785, 29.59084),
            (34.69667, 30.10714),
            (34.52423, 30.40912),
            (34.48879, 30.64515),
            (34.15870, 31.35333), # Closer to the Gaza Coast. Replaces (34.07929, 31.52265)
            (34.65362, 32.08569)  # Closer to the Tel-Aviv Coast. Replaces (34.64563, 32.92073)
            ))
        cmd = OsmChangeTileGenCommand.__new__(cls, israel_and_palestine, 7, 16)
        return cmd

    def __init__(self):
        OsmChangeTileGenCommand.__init__(self)
        self.after_tile_save = self.collect_tiles
        self.post_process_tiles = self.add_copyright
        self.tiles_to_post_process = []
        self.len_tiles_to_post_process = 0
        self.subpixel_precision = 2
        self.use_fingerprint = True
        self.min_tile_file_size = 385  # No transparent tiles

    def rel_to_fill(self, relation):
        return (
            relation.has_tag("type") and relation.get_tag("type") == "multipolygon"
                and (set(relation.tags.keys())
                    & {"landuse", "natural", "waterway", "military", "building", "boundary", "leisure"})
            or 
            relation.has_tag("boundary")
            and (
                relation.get_tag("boundary") in ("national_park", "protected_area")
                or
                relation.has_tag("name:en") and re.match("Area [AB]$", relation.get_tag("name:en"))
            )
        )

    def execute(self):
        timer = time.time()
        OsmChangeTileGenCommand.execute(self)
        if self.post_process_tiles:
            self.post_process_tiles()
        timer = time.time() - timer
        print pretty_timer("   Tile generation time:", timer)

    def osmChangeRead(self, *args):
        timer = time.time()
        OsmChangeTileGenCommand.osmChangeRead(self, *args)
        timer = time.time() - timer
        print pretty_timer("   Osm Change analysis time:", timer)

    def collect_tiles(self, file_name):
        self.tiles_to_post_process.append(file_name)
        self.len_tiles_to_post_process += len(file_name) + 3
        if self.post_process_tiles:
            if self.len_tiles_to_post_process >= 7500:
                self.post_process_tiles()

    def add_copyright(self):
        if self.tiles_to_post_process == []:
            return
        # Add Copyright property
        # args = ['/C' , 'START', '', '/MIN', 'mogrify', '-set', 'Copyright','"Israel Hiking, CC-BY-NC-SA 3.0"']
        # args.extend(self.tiles_to_post_process)
        # Avoid copyright post-processing in development mode
        # App.start_program('cmd.exe', args)
        del self.tiles_to_post_process[:]
        self.len_tiles_to_post_process = 0

if __name__ == '<module>':
    ProjectDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
    base_map =  IsraelHikingTileGenCommand()
    base_map.post_process_tiles = None
    # Alternatively:
    # base_map.after_tile_save = lambda x : None
    base_map.GenToDirectory(7, 16, os.path.join(ProjectDir, 'Output', 'Tiles'))

# vim: set shiftwidth=4 expandtab textwidth=0:
