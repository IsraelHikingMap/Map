# -*- coding: utf-8 -*-

# Use Contour tiles from Cache/WebTiles/ContourTiles in Maperitive's installation directory

from maperipy import Map
from maperipy.webmaps import WebMapLayer

contours_overlay = WebMapLayer.create_offline("ContourTiles")
contours_overlay.draw_in_background = True
# Now we add that layer to the map.
Map.add_layer(contours_overlay)
