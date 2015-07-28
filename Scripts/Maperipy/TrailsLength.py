# Measure length of Israel Hiking trails
# This Python file uses the following encoding: utf-8

from maperipy import *
from maperipy.osm import *
import math
import sys
import string

from collections import defaultdict
routeLength = defaultdict(lambda : defaultdict(int))

# The wayLength function calculates the total length of a way
def wayLength(way):
    if way.has_tag("length"):
        try: 
            length = float(way.get_tag("length"))
            if length > 0:
                return length
        except:
            print "unexpected error: ", sys.exc_info()
            print 'way.get_tag("length"): ', way.get_tag("length")
    length = 0.0
    for i in list(range(len(way.nodes)-1)):
            length += getLength(osmLayer.node(way.nodes[i]), osmLayer.node(way.nodes[i+1]))
    way.set_tag("length", str(length))
    return length

# The getLength function calculates the distance between two nodes
def getLength(node1, node2):
    return getLength4(node1.location.x, node1.location.y, node2.location.x, node2.location.y)

# These functions calculate the distance between two lat/lon pairs
    # Earth's circumference is about 40,000 km.
    # So 1 degree of longitude at the equator, or 1 degree of latitude, is about 40,000/360 = 110 km.
def getDistX(startx, starty, endx, endy):
    return 40000*(endx-startx)/360 * math.cos(math.radians((starty+endy)/2))
def getDistY(starty, endy):
    return 40000*(endy-starty)/360
def getLength4(startx, starty, endx, endy):
    distx = getDistX(startx, starty, endx, endy)
    disty = getDistY(starty, endy)
    if distx == 0 :
        length = disty
    elif disty == 0 :
        length = distx
    else:
        length = math.sqrt((distx*distx)+(disty*disty))
    if length < 0 :
        length = - length
    return length

trails_length = 0

try:
    # Look at all OSM map sources.
    for layer in Map.layers:
        if layer.layer_type == "OsmLayer":
            osmLayer = layer.osm

            # Accumulating length of all coloured trails
            for way in osmLayer.find_ways(lambda x : x.has_tag("highway") and x.has_tag("colour")):
                trails_length += wayLength(way)

            # Copy forest names from every multi-polygons to its outer ways
            for osmRelation in osmLayer.find_relations(lambda x : ( (x.has_tag("landuse", "forest") or x.has_tag("natural", "wood")) and (x.has_tag("name") or x.has_tag("name:he") or x.has_tag("name:en")))):
                for osmMember in osmRelation.members:
                    if osmMember.ref_type==OsmReferenceType.WAY and osmLayer.has_way(osmMember.ref_id):
                        osmWay = osmLayer.way(osmMember.ref_id)
                        if (osmMember.role == "" or osmMember.role == "outer"):
                            for osmTag in ("name", "name:he", "name:en", "landuse", "natural", "is_in"):
                                if (osmRelation.has_tag(osmTag) and not osmWay.has_tag(osmTag)):
                                    osmWay.set_tag(osmTag, osmRelation.get_tag(osmTag))

            # Set length for Hiking, bicycle, and mtb routes
            for osmRelation in osmLayer.find_relations(lambda x : (x.has_tag("route", "hiking") or x.has_tag("route", "bicycle") or x.has_tag("route", "mtb"))):
                length = 0.0
                for osmMember in osmRelation.members:
                    if osmMember.ref_type==OsmReferenceType.WAY and osmLayer.has_way(osmMember.ref_id):
                        length += wayLength(osmLayer.way(osmMember.ref_id))
                routeLength[osmRelation.get_tag("operator") if osmRelation.has_tag("operator") else "none"][osmRelation.get_tag("osmc:symbol") if osmRelation.has_tag("osmc:symbol") else "none"] += length

    print "======"
    print "Trail length Summary"
    print "Operator\tosmc:symbol\tlength"
    total = 0.0
    for operator, symbols in routeLength.iteritems():
        sum = 0.0
        for (symbol, length) in symbols.iteritems():
            sum += length
            print operator+"\t"+symbol+"\t"+format(length, ".1f")
        print operator+"\ttotal\t"+format(sum, ".1f")
        total += sum
    print "Total\t"+format(total, ".1f")
    print "======"

except:
    print "unexpected error:", sys.exc_info()
    print "wayLength(way): ", str(wayLength(way))
else:
    print "Total length of Israel Hiking Trails is", format(trails_length, ".1f"), "km"

# If there are no OSM map sources, report an error...
if osmLayer == None:
    raise AssertionError("There are no OSM map sources.")

# vim: set shiftwidth=4 expandtab textwidth=0:
