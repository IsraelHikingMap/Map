# Adding length tags
# This Python file uses the following encoding: utf-8

from maperipy import *
from maperipy.osm import *
import math
import sys
import string
import os

#this function calculates the distance between two nodes
def getLength(node1, node2):
    return getLength4(node1.location.x, node1.location.y, node2.location.x, node2.location.y)

# These functions calculates the distance between two lat/lon pairs
# Earth's circumference is about 40,000 km.
# So 1 degree of longitude at the equator, or 1 degree of latitude, is about 40,000/360 = 110 km.
def getDistX(startx, starty, endx, endy):
    return 40000*(endx-startx)/360*math.cos(math.radians((starty+endy)/2))
def getDistY(starty, endy):
    return 40000*(endy-starty)/360
def getLength4(startx, starty, endx, endy):
    distx = getDistX(startx, starty, endx, endy)
    disty = getDistY(starty, endy)
    if distx == 0 :
        length = disty
    elif disty == 0 :
        length = distx
    else :
        length = math.sqrt((distx*distx)+(disty*disty))
    if length < 0 :
        length = - length
    return length
def setLengthAndDirection(way) :
    if way.nodes[0]!=way.nodes[way.nodes_count-1]:
        if not osmLayer.has_node(way.nodes[0]):
            return
        node1 = osmLayer.node(way.nodes[0])
        if not osmLayer.has_node(way.nodes[way.nodes_count-1]):
            return
        node2 = osmLayer.node(way.nodes[way.nodes_count-1])
        length = getLength(node1, node2)
        osmLayer.way(way.id).set_tag("length", str(length))
        if length > 0:
            direction = math.degrees(math.atan2(node2.location.x-node1.location.x,
                                                node2.location.y-node1.location.y))
            osmLayer.way(way.id).set_tag("direction", str(direction))

def setClockwise(osmWay) :
    if len(osmWay.nodes) > 0 :
        if osmWay.nodes[0] == osmWay.nodes[osmWay.nodes_count-1]:
            # Will not tag unclosed members
            length2 = 0.0
            if not osmLayer.has_node(osmWay.nodes[0]):
                return
            node0 = osmLayer.node(osmWay.nodes[0])
            for i in list(range(1, osmWay.nodes_count)):
                if not osmLayer.has_node(osmWay.nodes[i]):
                    return
                node1 = osmLayer.node(osmWay.nodes[i])
                length2 += node0.location.x*node1.location.y - node1.location.x*node0.location.y
                node0 = node1
            osmLayer.way(osmWay.id).set_tag("clockwise", "yes" if length2 < 0 else "no")
            # Add width of areas for label placement
            osmWayBBox= osmLayer.get_way_geometry(osmWay.id).bounding_box
            width = getLength4(osmWayBBox.min_x, (osmWayBBox.min_y+osmWayBBox.max_y)/2,
                               osmWayBBox.max_x, (osmWayBBox.min_y+osmWayBBox.max_y)/2)
            osmLayer.way(osmWay.id).set_tag("width", str(width))
    else:
        print "setClockwise: osmWay", osmWay.id, "has no nodes"

def escapeXML(text) :
    # Special Character   Escape Sequence Purpose  
    # &                   &amp;           Ampersand sign 
    # '                   &apos;          Single quote 
    # "                   &quot;          Double quote
    # >                   &gt;            Greater than 
    # <                   &lt;            Less than
    return text\
        .replace("&", "&amp;")\
        .replace("'", "&apos;")\
        .replace('"', "&quot;")\
        .replace(">", "&gt;")\
        .replace("<", "&lt;")

IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('IsraelHikingDir: '+IsraelHikingDir)
App.run_command('change-dir dir="'+IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

App.collect_garbage()

# Create an osm file with forest name info
sFileName = os.path.join(IsraelHikingDir, 'Cache', 'Forests.osm')
osmFile = open(sFileName, 'w')
iId = 0
# writing osm header
osmFile.write('<?xml version="1.0" encoding="utf-8"?>\n')
osmFile.write('<osm version="0.5" generator="AddWayLengthTags.py">\n')

osmLayer = None
# Look at all OSM map sources.
for layer in Map.layers:
    if layer.layer_type == "OsmLayer":
        osmLayer = layer.osm

        # Add length and direction to highways
        for osmWay in osmLayer.find_ways(lambda x : x.has_tag("highway")):
            setLengthAndDirection(osmWay)

        # Set clockwise and width for national parks and nature reserves 
        # 1. for ways
        for osmWay in osmLayer.find_ways(lambda x : (
                x.has_tag("boundary", "national_park")
                or x.has_tag("boundary", "protected_area")
                or x.has_tag("leisure", "nature_reserve"))):
            setClockwise(osmWay)
            # Handle as outer boundaries
            for osmTag in ("boundary", "leisure"):
                if (osmWay.has_tag(osmTag)):
                    osmWay.set_tag("outer_boundary", osmTag)
        # 2. for relation members
        for osmRelation in osmLayer.find_relations(lambda x : (
                x.has_tag("boundary", "national_park")
                or x.has_tag("boundary", "protected_area")
                or x.has_tag("leisure", "nature_reserve"))):
            for osmMember in osmRelation.members:
                if osmMember.ref_type==OsmReferenceType.WAY and osmLayer.has_way(osmMember.ref_id):
                    if not osmLayer.has_way(osmMember.ref_id):
                        break
                    osmWay = osmLayer.way(osmMember.ref_id)
                    #########################################
                    # For some unknown reason, setClockwise() cannot be called before the loop below
                    #########################################
                    # setClockwise(osmWay)

                    # Handle inner members and inner members that are also outer members of another relarion
                    for osmTag in ("boundary", "leisure"):
                        if (osmRelation.has_tag(osmTag)):
                            if ((osmMember.role == "" or osmMember.role == "outer")
                                    and not osmWay.has_tag(osmTag)):
                                osmWay.set_tag(osmTag, osmRelation.get_tag(osmTag))
                                osmWay.set_tag("outer_boundary", osmTag)
                            elif (osmMember.role == "inner"):
                                osmWay.set_tag("inner_boundary", osmTag)
                    #########################################
                    # For some unknown reason, setClockwise() needs to be called after the loop above
                    #########################################
                    setClockwise(osmWay)

        # Copy forest names from every multi-polygons to its outer ways
        for osmRelation in osmLayer.find_relations(lambda x : (
                (x.has_tag("landuse", "forest") or x.has_tag("natural", "wood"))
                and (x.has_tag("name") or x.has_tag("name:he") or x.has_tag("name:en")))):
            for osmMember in osmRelation.members:
                if osmMember.ref_type==OsmReferenceType.WAY and osmLayer.has_way(osmMember.ref_id):
                    if (osmMember.role == "" or osmMember.role == "outer"):
                        if not osmLayer.has_way(osmMember.ref_id):
                            break
                        osmWay = osmLayer.way(osmMember.ref_id)
                        for osmTag in ("name", "name:he", "name:en", "landuse", "natural", "is_in"):
                            if (osmRelation.has_tag(osmTag) and not osmWay.has_tag(osmTag)):
                                osmWay.set_tag(osmTag, osmRelation.get_tag(osmTag))

        # Write Forest label info to the osm file
        for osmWay in osmLayer.find_ways(lambda x : (
                (x.has_tag("landuse") or x.has_tag("natural"))
                and (x.has_tag("name") or x.has_tag("name:he") or x.has_tag("name:en")))):
            if (osmWay.has_tag("landuse", "forest") or osmWay.has_tag("natural", "wood")):
                wayBBox= osmLayer.get_way_geometry(osmWay.id).bounding_box
                # Label placement is done according to the shape's width
                width = getLength4(
                    wayBBox.min_x, (wayBBox.min_y+wayBBox.max_y)/2,
                    wayBBox.max_x, (wayBBox.min_y+wayBBox.max_y)/2)
                osmFile.write('  <node id="{}" visible="true" lat="{}" lon="{}">\n'.format(
                    iId, (wayBBox.min_y+wayBBox.max_y)/2, (wayBBox.min_x+wayBBox.max_x)/2))
                for osmTag in ( "landuse", "natural", "name", "name:he", "name:en", "is_in" ):
                    if (osmWay.has_tag(osmTag)):
                        try:
                            osmFile.write('    <tag k="{}" v="{}"/>\n'.format(
                                osmTag, escapeXML(osmWay.get_tag(osmTag)).encode('utf-8')))
                        except:
                            print ("Error: ", sys.exc_info()[0]," when writing ", osmTag,  "=", osmWay.get_tag(osmTag))
                            raise
                osmFile.write('    <tag k="width" v="{}"/>\n'.format(width))
                # Add OSM id for debugging
                osmFile.write('    <!-- tag k="OSM_id" v="{}" -->\n'.format(osmWay.id))
                osmFile.write('  </node>\n')
                iId += 1

# writing osm footer
osmFile.write('</osm>')
osmFile.close()

App.collect_garbage()

# If there are no OSM map sources, report an error...
if osmLayer is None:
    raise AssertionError("There are no OSM map sources.")

# osmLayer.save_xml_file("D:\Tiles\OSM\israel_and_palestine_with_lengths.osm")

# vim: set shiftwidth=4 expandtab textwidth=0:
