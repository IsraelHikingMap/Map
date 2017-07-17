"""Find and tag highways in Urban areas

Author: Zeev Stadler
License: CC BY-NC-SA 3.0 

https://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from maperipy import *
from maperipy.osm import *

def getBoundingBox(osmObject, osmData) :
    bbox = BoundingBox(0)
    try :
        if (isinstance(osmObject, OsmNode)) :
           bbox = osmObject.location.bounding_box
        elif (isinstance(osmObject, OsmWay)) :
            # osmData.get_way_geometry().geom_type is in ['LineString', 'LinearRing']
            bbox = osmData.get_way_geometry(osmObject.id).bounding_box
        elif (isinstance(osmObject, OsmRelation)) :
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

def isBoundingBoxWithin(external, internal) :
    # In an empty BoundingBox max_* < min_*
    return (external.max_x >= max(internal.max_x, internal.min_x)
            and external.min_x <= min(internal.min_x, internal.max_x)
            and external.max_y >= max(internal.max_y, internal.min_y)
            and external.min_y <= min(internal.min_y, internal.max_y))

App.collect_garbage()

# Unfortunately, could not find a way for Meperitive to accept Hebrew strings in this file
placeNames = [
        "Tel Aviv-Yafo"
        ];

osmData = None
# Look at all OSM map sources.
for layer in Map.layers:
    if layer.layer_type == "OsmLayer":
        osmData = layer.osm
        bboxes = []
        for place in placeNames:
            for osmRelation in osmData.find_relations(lambda x : (
                    x.has_tag("place") and x.has_tag("name:en", place))):
                bboxes.append(getBoundingBox(osmRelation, osmData))

        for osmNode in osmData.find_nodes(lambda x : (
                x.has_tag("amenity") or x.has_tag("barrier")
                or x.has_tag("building") or x.has_tag("construction")
                or x.has_tag("highway") or x.has_tag("historic")
                or x.has_tag("landuse"))) :
            elementBoundingBox = getBoundingBox(osmNode, osmData)
            for external in bboxes:
                if isBoundingBoxWithin(external, elementBoundingBox) :
                    osmNode.set_tag("_urban", "yes")
                    break

        for osmWay in osmData.find_ways(lambda x : (
                x.has_tag("amenity") or x.has_tag("barrier")
                or x.has_tag("building") or x.has_tag("construction")
                or x.has_tag("highway") or x.has_tag("historic")
                or x.has_tag("landuse"))) :
            elementBoundingBox = getBoundingBox(osmWay, osmData)
            for external in bboxes:
                if isBoundingBoxWithin(external, elementBoundingBox) :
                    osmWay.set_tag("_urban", "yes")
                    break

        for osmRelation in osmData.find_relations(lambda x : (
                x.has_tag("amenity") or x.has_tag("barrier")
                or x.has_tag("building") or x.has_tag("construction")
                or x.has_tag("highway") or x.has_tag("historic")
                or x.has_tag("landuse"))) :
            elementBoundingBox = getBoundingBox(osmRelation, osmData)
            for external in bboxes:
                if isBoundingBoxWithin(external, elementBoundingBox) :
                    osmRelation.set_tag("_urban", "yes")
                    break

App.collect_garbage()

# If there are no OSM map sources, report an error...
if osmData is None:
    raise AssertionError("There are no OSM map sources.")
