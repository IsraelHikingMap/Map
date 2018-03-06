"""Create and save the MOBAC profiles using the tile generation polygon
"""

import os.path
from GenIsraelHikingTiles import IsraelHikingTileGenCommand
from maperipy import App

gen_cmd = IsraelHikingTileGenCommand()
MOBAC_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir))),
        "Mobile Atlas Creator")
for (atlas_name,      source_suffix,    profile_suffix, max_zoom, min_zoom, map_format) in (
    ("Israel Hiking", "",               "",             15,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "",               "16",           16,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "Online",         "",             16,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "English",        "",             15,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "English",        "16",           16,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "English Online", "",             16,       7,        "OruxMapsSqlite"),
    ("Israel Hiking", "",               "TwoNav",       16,       7,        "TwoNavRMAP"),
    ("Israel MTB",    "",               "",             15,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "",               "16",           16,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "Online",         "",             16,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "English",        "",             15,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "English",        "16",           16,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "English Online", "",             16,       7,        "OruxMapsSqlite"),
    ("Israel MTB",    "",               "TwoNav",       16,       7,        "TwoNavRMAP"),
    ):
  map_source = "{} {}".format(atlas_name, source_suffix).rstrip()
  profile_name = "{} {}".format(map_source, profile_suffix).rstrip()
  gen_cmd.create_MOBAC_profile(MOBAC_dir, profile_name, atlas_name, map_source, max_zoom, min_zoom, map_format)
