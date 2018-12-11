# This Python file uses the following encoding: utf-8
"""Add computed tags for OSM layers

Add tags to existing elements
Add new elements by creating a new OSM file and then loading it

Author: Zeev Stadler
License: CC BY-NC-SA 3.0 

https://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from maperipy import *
from maperipy.osm import *
import math
import sys
import string
import os

def getLength(node1, node2):
    """Calculate the distance between two nodes."""
    return getLength4(node1.location.x, node1.location.y, node2.location.x, node2.location.y)

def getDistX(startx, starty, endx, endy):
    """Calculate the horizontal distance between two locations."""
    # Earth's circumference is about 40,000 km.
    return 40000*(endx-startx)/360*math.cos(math.radians((starty+endy)/2))
def getDistY(starty, endy):
    """Calculate the vertical distance between two locations."""
    # Earth's circumference is about 40,000 km.
    return 40000*(endy-starty)/360
def getLength4(startx, starty, endx, endy):
    """Calculate the distance between two locations."""
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

def setWayLengthAndDirection(way, osmData):
    """Set the length and direction tags for a way."""
    if way.nodes[0]!=way.nodes[way.nodes_count-1]:
        if not osmData.has_node(way.nodes[0]):
            return
        node1 = osmData.node(way.nodes[0])
        if not osmData.has_node(way.nodes[way.nodes_count-1]):
            return
        node2 = osmData.node(way.nodes[way.nodes_count-1])
        length = getLength(node1, node2)
        osmData.way(way.id).set_tag("length", str(length))
        if length > 0:
            direction = math.degrees(math.atan2(node2.location.x-node1.location.x,
                                                node2.location.y-node1.location.y))
            osmData.way(way.id).set_tag("direction", str(direction))

def setClockwise(osmWay, osmData):
    """Set the clockwise and width tags for a way."""
    if len(osmWay.nodes) > 0 :
        if osmWay.nodes[0] == osmWay.nodes[osmWay.nodes_count-1]:
            # Will not tag unclosed members
            length2 = 0.0
            if not osmData.has_node(osmWay.nodes[0]):
                return
            node0 = osmData.node(osmWay.nodes[0])
            for i in list(range(1, osmWay.nodes_count)):
                if not osmData.has_node(osmWay.nodes[i]):
                    return
                node1 = osmData.node(osmWay.nodes[i])
                length2 += node0.location.x*node1.location.y - node1.location.x*node0.location.y
                node0 = node1
            osmData.way(osmWay.id).set_tag("clockwise", "yes" if length2 < 0 else "no")
            # Add width of areas for label placement
            osmWayBBox= osmData.get_way_geometry(osmWay.id).bounding_box
            width = getLength4(osmWayBBox.min_x, (osmWayBBox.min_y+osmWayBBox.max_y)/2,
                               osmWayBBox.max_x, (osmWayBBox.min_y+osmWayBBox.max_y)/2)
            osmData.way(osmWay.id).set_tag("width", str(width))
    else:
        print "setClockwise: osmWay", osmWay.id, "has no nodes"

def escapeXML(text):
    """Convert a string to use XML escape sequences."""
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
        .replace("<", "&lt;")\
        .encode('utf-8')

def analyzeWays(osmData):
    """Set the length and direction tag to highways, ridges, and valleys."""
    for osmWay in osmData.find_ways(lambda x: (
            x.has_tag("highway")
            or x.has_tag("natural", "ridge")
            or x.has_tag("natural", "valley"))):
        setWayLengthAndDirection(osmWay, osmData)

def analyzeAreas(osmData):
    """Set the clockwise and width tags for national parks and nature reserves."""
    # 1. for ways
    for osmWay in osmData.find_ways(lambda x : (
            x.has_tag("boundary", "national_park")
            or x.has_tag("boundary", "protected_area")
            or x.has_tag("leisure", "nature_reserve"))):
        setClockwise(osmWay, osmData)
        # Handle as outer boundaries
        for osmTag in ("boundary", "leisure"):
            if (osmWay.has_tag(osmTag)):
                osmWay.set_tag("outer_boundary", osmTag)
    # 2. for relation members
    for osmRelation in osmData.find_relations(lambda x : (
            x.has_tag("boundary", "national_park")
            or x.has_tag("boundary", "protected_area")
            or x.has_tag("leisure", "nature_reserve"))):
        for osmMember in osmRelation.members:
            if osmMember.ref_type==OsmReferenceType.WAY and osmData.has_way(osmMember.ref_id):
                if not osmData.has_way(osmMember.ref_id):
                    continue
                osmWay = osmData.way(osmMember.ref_id)
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
                setClockwise(osmWay, osmData)

def analyzeForests(osmData):
    """Create an OSM file for forest labels.
    
    New nodes are placed in the center of each way's bounding box.
    The node has a new width tag and copies of name, name:he, and name:en tags.
    Outer members of multipolygons inherit the name tags from the relation.
    """
    # Copy forest names from every multi-polygons to its outer ways
    for osmRelation in osmData.find_relations(lambda x : (
            (x.has_tag("landuse", "forest") or x.has_tag("natural", "wood"))
            and (x.has_tag("name") or x.has_tag("name:he") or x.has_tag("name:en")))):
        for osmMember in osmRelation.members:
            if osmMember.ref_type==OsmReferenceType.WAY and osmData.has_way(osmMember.ref_id):
                if (osmMember.role == "" or osmMember.role == "outer"):
                    if not osmData.has_way(osmMember.ref_id):
                        continue
                    osmWay = osmData.way(osmMember.ref_id)
                    for osmTag in ("name", "name:he", "name:en", "landuse", "natural", "is_in"):
                        if (osmRelation.has_tag(osmTag) and not osmWay.has_tag(osmTag)):
                            osmWay.set_tag(osmTag, osmRelation.get_tag(osmTag))

    # Write Forest label info to the osm file
    for osmWay in osmData.find_ways(lambda x : (
            (x.has_tag("landuse") or x.has_tag("natural"))
            and (x.has_tag("name") or x.has_tag("name:he") or x.has_tag("name:en")))):
        if (osmWay.has_tag("landuse", "forest") or osmWay.has_tag("natural", "wood")):
            try:
                wayBBox= osmData.get_way_geometry(osmWay.id).bounding_box
            except KeyError:
                # Way has incomplete geometry
                continue
            # Label placement is done according to the shape's width
            width = getLength4(
                wayBBox.min_x, (wayBBox.min_y+wayBBox.max_y)/2,
                wayBBox.max_x, (wayBBox.min_y+wayBBox.max_y)/2)
            osmFile.write(
                '  <node id="{}" visible="true" lat="{}" lon="{}">\n'
                '    <!-- tag k="_OSM_id" v="{}" -->\n'
                .format(
                    analyzeForests.iId,
                    (wayBBox.min_y+wayBBox.max_y)/2,
                    (wayBBox.min_x+wayBBox.max_x)/2,
                    osmWay.id))
            analyzeForests.iId += 1
            for osmTag in ( "landuse", "natural", "name", "name:he", "name:en", "is_in" ):
                if (osmWay.has_tag(osmTag)):
                    try:
                        osmFile.write(
                            '    <tag k="{}" v="{}"/>\n'
                            .format(
                                osmTag,
                                escapeXML(osmWay.get_tag(osmTag))))
                    except:
                        print ("Error: {} when writing {}={}"
                                .format(sys.exc_info()[0], osmTag, osmWay.get_tag(osmTag)))
                        raise
            osmFile.write(
                '    <tag k="width" v="{}"/>\n'
                '  </node>\n'
                .format(width))

def getBoundingBox(osmObject, osmData):
    """Return a BoundingBox for an OSM object
    
    A relation's BoundingBox contains all members' bounding boxes.
    """
    bbox = BoundingBox(0)
    try :
        if (isinstance(osmObject, OsmNode)):
           bbox = osmObject.location.bounding_box
        elif (isinstance(osmObject, OsmWay)):
            # osmData.get_way_geometry().geom_type is in ['LineString', 'LinearRing']
            bbox = osmData.get_way_geometry(osmObject.id).bounding_box
        elif (isinstance(osmObject, OsmRelation)):
            for osmMember in osmObject.members :
                osmMemberObject = None
                if osmMember.ref_type==OsmReferenceType.NODE and osmData.has_node(osmMember.ref_id):
                    osmMemberObject = osmData.node(osmMember.ref_id)
                elif osmMember.ref_type==OsmReferenceType.WAY and osmData.has_way(osmMember.ref_id):
                    osmMemberObject = osmData.way(osmMember.ref_id)
                elif osmMember.ref_type==OsmReferenceType.RELATION and osmData.has_relation(osmMember.ref_id):
                    osmMemberObject = osmData.relation(osmMember.ref_id)
                bbox.extend_with(getBoundingBox(osmMemberObject, osmData))
    except KeyError:
        # An element does not exist in the map
        pass
    return bbox

def isBoundingBoxWithin(external, internal):
    """Check the inclusion of one Bouunding Box within another."""
    # In an empty BoundingBox max_* < min_*
    return (external.max_x >= max(internal.max_x, internal.min_x)
            and external.min_x <= min(internal.min_x, internal.max_x)
            and external.max_y >= max(internal.max_y, internal.min_y)
            and external.min_y <= min(internal.min_y, internal.max_y))

def analyzeUrban(osmData):
    """Add _urban=yes tags to certain elements located in urban areas."""
    # Unfortunately, could not find a way for Meperitive to accept Hebrew strings in this file
    placeNames = ["Acre", "Afula", "Ashdod", "Ashkelon", "Bat Yam", "Be'er Sheva", "Bnei Brak", "Carmiel", "Daliyat al-Karmel", "Eilat", "Givatyim", "Hadera", "Haifa", "Herzliya", "Holon", "Jerusalem", "Kfar Sava", "Modiin-Maccabim-Reut", "Nazareth", "Nahariyya", "Nes Ziona", "Netanya", "Petah Tikva", "Raanana", "Ramat Gan", "Ramat HaSharon", "Rehovot", "Rishon LeZion", "Safed", "Tel Aviv-Yafo"
        ];
    placeBboxes = []
    for place in placeNames:
        for osmRelation in osmData.find_relations(lambda x : (
                x.has_tag("place") and x.has_tag("name:en", place))):
            placeBboxes.append(getBoundingBox(osmRelation, osmData))
    analyzeUrbanNodes(osmData, placeBboxes)
    analyzeUrbanWays(osmData, placeBboxes)
    analyzeUrbanRelations(osmData, placeBboxes)

def analyzeUrbanNodes(osmData, placeBboxes):
    """Add _urban=yes tags to certain nodes located in urban areas."""
    for osmNode in osmData.find_nodes(lambda x : (
            x.has_tag("amenity") or x.has_tag("barrier")
            or x.has_tag("building") or x.has_tag("construction")
            or x.has_tag("highway") or x.has_tag("historic") or x.has_tag("tourism") or x.has_tag("natural") or x.has_tag("shop")
            or x.has_tag("landuse"))):
        elementBoundingBox = getBoundingBox(osmNode, osmData)
        for external in placeBboxes:
            if isBoundingBoxWithin(external, elementBoundingBox):
                osmNode.set_tag("_urban", "yes")
                break

def analyzeUrbanWays(osmData, placeBboxes):
    """Add _urban=yes tags to certain ways located in urban areas."""
    for osmWay in osmData.find_ways(lambda x : (
            x.has_tag("amenity") or x.has_tag("barrier")
            or x.has_tag("building") or x.has_tag("construction")
            or x.has_tag("highway") or x.has_tag("historic") or x.has_tag("shop") or x.has_tag("tourism") 
            or x.has_tag("landuse"))):
        elementBoundingBox = getBoundingBox(osmWay, osmData)
        for external in placeBboxes:
            if isBoundingBoxWithin(external, elementBoundingBox):
                osmWay.set_tag("_urban", "yes")
                break

def analyzeUrbanRelations(osmData, placeBboxes):
    """Add _urban=yes tags to certain relations located in urban areas."""
    for osmRelation in osmData.find_relations(lambda x : (
            x.has_tag("amenity") or x.has_tag("barrier")
            or x.has_tag("building") or x.has_tag("construction")
            or x.has_tag("highway") or x.has_tag("historic")
            or x.has_tag("landuse"))):
        elementBoundingBox = getBoundingBox(osmRelation, osmData)
        for external in placeBboxes:
            if isBoundingBoxWithin(external, elementBoundingBox):
                osmRelation.set_tag("_urban", "yes")
                break

IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
App.run_command('change-dir dir="'+IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

App.collect_garbage()

# Create an osm file with forest name info
ForestsFileName = os.path.join(IsraelHikingDir, 'Cache', 'Forests.osm')
osmFile = open(ForestsFileName, 'w')
osmFile.write('<?xml version="1.0" encoding="utf-8"?>\n'
'<osm version="0.5" generator="AddOsmTags.py">\n')

analyzeForests.iId = 1
osmData = None
# Look at all OSM map sources.
for layer in Map.layers:
    if layer.layer_type == "OsmLayer":
        osmData = layer.osm
        analyzeWays(osmData)
        analyzeAreas(osmData)
        analyzeForests(osmData)
        analyzeUrban(osmData)

# writing osm footer
osmFile.write('</osm>\n')
osmFile.close()

App.collect_garbage()

# If there are no OSM map sources, report an error...
if osmData is None:
    raise AssertionError("There are no OSM map sources.")

Map.add_osm_source(ForestsFileName)

# vim: set shiftwidth=4 expandtab textwidth=0:
