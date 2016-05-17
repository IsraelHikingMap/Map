# Adding size=* tag to natural/landuse/place areas
# This Python file uses the following encoding: utf-8

from maperipy import *
from maperipy.osm import *
import math
import sys
import string

osmLayer = None
try:
	# Look at all OSM map sources.
	for layer in Map.layers:
		if layer.layer_type == "OsmLayer":
			osmLayer = layer.osm

			# Calculate size of area based on bounding box
			for way in osmLayer.find_ways(lambda x : ( (x.has_tag("landuse") or x.has_tag("natural") or x.has_tag("leisure") or x.has_tag("place")) and x.has_tag("name"))):
				wayBBox= osmLayer.get_way_geometry(way.id).bounding_box
				size = ((wayBBox.max_x - wayBBox.min_x)*1 + (wayBBox.max_y - wayBBox.min_y)*2)*20
				way.set_tag("size", str(size))

			for osmRelation in osmLayer.find_relations(lambda x : ( (x.has_tag("landuse") or x.has_tag("natural") or x.has_tag("leisure") or x.has_tag("place")) and x.has_tag("name"))):
				xmin = 180
				xmax = -180
				ymin = 90
				ymax = -90
				for osmMember in osmRelation.members:
					try:
						if osmMember.ref_type==OsmReferenceType.WAY and (osmMember.role == "" or osmMember.role == "outer"):
							osmWay = osmLayer.way(osmMember.ref_id)
							wayBBox = osmLayer.get_way_geometry(osmWay.id).bounding_box
							min_x = wayBBox.min_x
							max_x = wayBBox.max_x
							min_y = wayBBox.min_y
							max_y = wayBBox.max_y
							if min_x < xmin:
								xmin = min_x
							if max_x > xmax:
								xmax = max_x
							if min_y < ymin:
								ymin = min_y
							if max_y > ymax:
								ymax = max_y
					# Using except pass in case way belonging to relation hasn't been loaded because outside bounds
					except:
						pass
				relationsize = ((xmax - xmin)*1 + (ymax - ymin)*2)*20
				osmRelation.set_tag("size", str(relationsize))
#				osmRelation.set_tag(str(xmin) + " " +str(xmax) + " " + str(ymin) + " " + str(ymax))
except:
    print "Unexpected error:", sys.exc_info()[0]

App.collect_garbage()

# If there are no OSM map sources, report an error...
if osmLayer is None:
    raise AssertionError("There are no OSM map sources.")

###############
