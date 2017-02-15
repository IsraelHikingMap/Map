import re
from maperipy import *

def MIRROR(name):
    return name[::-1]

def RTL(name):
    if name[-1] == "'":
        return "'"+name[:-1]
    return name

def FindName(e):
    language = "Hebrew"
    if DataStore.has_data("Language"):
        language = DataStore.get_data("Language")
    if language == "Hebrew":
        for set in e.tagSets:
            if set.hasTag('name:he'):
                return set['name:he']
            if set.hasTag('name') and re.search("[א-ת]", set['name']):
                return set['name']
            if set.hasTag('name:en'):
                return set['name:en']
            if set.hasTag('name'):
                return set['name']
    if language == "English":
        for set in e.tagSets:
            if set.hasTag('name:en'):
                return set['name:en']
            if set.hasTag('name') and re.search("[A-Za-z]", set['name']):
                return set['name']
            if set.hasTag('name:he'):
                return set['name:he']
            if set.hasTag('name'):
                return set['name']
    return('')

def NodeName(e):
    name = FindName(e);
    if re.search("[א-ת؀-ۿݐ-ݿ]", name):
        return RTL(name)
    return name

def WayName(e):
    name = FindName(e);
    if re.search("[א-ת؀-ۿݐ-ݿ]", name):
        return RTL(MIRROR(name))
    return name

# vim: set shiftwidth=4 expandtab textwidth=0:
