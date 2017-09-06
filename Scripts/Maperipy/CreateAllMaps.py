"""Create all Israel Hiking and Biking maps

This is the main script used to build the maps.

The map creation is done in phases. The first phase creates the trails overlay map.
Each of the following phases updates the tiles for the Hiking and MTB maps where
zoom 16 tiles are created after both maps are updated upto zoom 15.

Progress is tracked by creating "phase done" files. 
An incomplete map creation will be resumes at the first incomplete phase.
"""

import os
import os.path
from datetime import *
import string
import errno
from maperipy import *
from maperipy.osm import *
from GenIsraelHikingTiles import IsraelHikingTileGenCommand
from OsmChangeSource import *
from PolygonTileGenCommand import pretty_timer

start_time = datetime.now()
App.run_command('clear-map')

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: '+MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: '+ProgramFiles)
ProjectDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('ProjectDir: '+ProjectDir)
App.run_command('change-dir dir="'+ProjectDir +'"')
os.chdir(ProjectDir)

def mkdir_p(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)

def silent_remove(filename):
    # https://www.python.org/dev/peps/pep-3151/#lack-of-fine-grained-exceptions
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def silent_rename(filename, new_filename):
    silent_remove(new_filename)
    try:
        os.rename(filename, new_filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def safe_rename(filename, new_filename):
    silent_remove(new_filename+".old")
    silent_rename(new_filename, new_filename+".old")
    try:
        os.rename(filename, new_filename)
        silent_remove(new_filename+".old")
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def add_to_PATH(app_name):
    for path_dir in string.split(os.environ["PATH"], os.pathsep):
        for ext in string.split(os.pathsep+os.environ["PATHEXT"], os.pathsep):
            if os.path.exists(os.path.join(path_dir, app_name+ext)):
                # Application already found in PATH
                return
    full_app_name=os.path.join(ProgramFiles, app_name)
    if not os.path.isdir(full_app_name):
        # Application not a sibling of Maperitive
        App.log("Warning: "+app_name+" location not found. Could not add it to PATH.")
        return
    os.environ["PATH"] = string.join([os.environ["PATH"],full_app_name], os.pathsep)

def cache_file(filename):
    if filename:
        return os.path.join(ProjectDir, 'Cache', language, filename)
    return os.path.join(ProjectDir, 'Cache', language)

add_to_PATH("wget")

language = "Hebrew"
if DataStore.has_data("Language"):
    language = DataStore.get_data("Language")
# Output directory for the tiles of all maps
site_dir = os.path.join(ProjectDir, language)
mkdir_p(os.path.join(site_dir, "Oruxmaps"))
mkdir_p(cache_file(''))

#
# Map sources
#
base_map =  IsraelHikingTileGenCommand()
if language == "Hebrew":
    # Minute updates from openstreetmap.fr
    osm_source = openstreetmap_fr(
            cache_file('israel-and-palestine-latest.osm.pbf'),
            cache_file('israel-and-palestine-update.osc'),
            cache_file('israel-and-palestine-updated.osm.pbf'),
            os.path.join(ProjectDir, 'Cache', 'openstreetmap_fr'),
            "asia/israel_and_palestine")
    # Improve performance with prefetch
    osm_source.osmupdate_params = ["--trust-tempfiles"]
    # DEBUG # osm_source.osmupdate_params = ["--keep-tempfiles", "--verbose", "--trust-tempfiles"]
else:
    # Daily updated from geofabric
    osm_source = geofabric(
            cache_file('israel-and-palestine-latest.osm.pbf'),
            cache_file('israel-and-palestine-update.osc'),
            cache_file('israel-and-palestine-updated.osm.pbf'),
            os.path.join(ProjectDir, 'Cache', 'geofabrik'),
            "asia/israel-and-palestine")

trails_overlay =  IsraelHikingTileGenCommand()
osm_trails = osmChangeOverlyFilterSource(
        cache_file('israel-and-palestine-trails-latest.osm.pbf'),
        cache_file('israel-and-palestine-trails-update.osc'),
        cache_file('israel-and-palestine-trails-updated.osm.pbf'),
        "hiking trails",
        os.path.join('Filters', 'trails_filter.txt'),
        osm_source)

#
# Map creation phases
#
phases = [
    'IsraelHiking15',
    'IsraelMTB15',
    'IsraelHiking16',
    'IsraelMTB16']
if language == "Hebrew":
    phases += [
            'OverlayTiles',
            'OverlayMTB']

def done_file(phase):
    return cache_file(phase+'.done')

def mark_done(phase):
    open(done_file(phase), 'a').close()
    App.log(phase+' phase is done.')
    print pretty_timer("Current duration:", (datetime.now()-start_time).total_seconds())

# Create a new map if all phased were done
remainingPhases = []
for phase in phases:
    if not os.path.exists(done_file(phase)):
        remainingPhases.append(phase)

if remainingPhases == []:
    osm_source.advance()
    if "OverlayTiles" in phases:
        osm_trails.advance()
    for phase in phases:
        os.remove(done_file(phase))
    remainingPhases = phases

#
# Assess map creation mode and completion of previous execution
#
App.run_command("use-ruleset location="+os.path.join("Rules", "empty.mrules"))

if osm_source.status() in ("non-incremental", "incremental"):
    # Continue an incomplete run
    App.log('=== Continuing execution of the previous tile generation ===')  
    App.log('Remaining phases: '+', '.join(remainingPhases))
    App.run_command("pause 15000")
else:
    exit_code = osm_source.downloadMap()
    if exit_code == 21:
        remainingPhases = []
    elif exit_code == 0:
        pass
    else:
        raise RuntimeError
    print pretty_timer("Current duration:", (datetime.now()-start_time).total_seconds())

# Incremental tile generation?
if os.path.exists(osm_source.changes):
    if "timestamp max" not in osm_source.statistics(osm_source.changes):
        App.log("=== No map changes ===")
        remainingPhases = []
    else:
        # Osm Change analysis
        base_time = osm_source.timestamp(osm_source.base)
        updated_time = osm_source.timestamp(osm_source.updated)
        change_span = pretty_timer("from {}Z to {}Z -".format(
            base_time.isoformat(),
            updated_time.isoformat()),
            (updated_time-base_time).total_seconds())
        App.log("=== Analyzing map changes {} ===".format(change_span))
        App.collect_garbage()
        base_map.osmChangeRead(osm_source.changes, osm_source.base, osm_source.updated)
        (changed, guard) = base_map.statistics()
        if changed:
            with open(cache_file("Change Analysis.log"), 'a') as journal:
                journal.write("Changes {}\n".format(change_span))
        else:
            remainingPhases = []
        App.collect_garbage()
        print pretty_timer("Current duration:", (datetime.now()-start_time).total_seconds())
elif remainingPhases:
    # 
    updated_time = "map dated {}Z".format(
            osm_source.timestamp(osm_source.updated).isoformat())
    App.log("=== Loading the {} ===".format(updated_time))
    with open(cache_file("Change Analysis.log"), 'a') as journal:
        journal.write("Base {}\n".format(updated_time))
    Map.add_osm_source(osm_source.updated)
    print pretty_timer("Current duration:", (datetime.now()-start_time).total_seconds())

#
# Execute map generation by phases
#
if remainingPhases:
    App.log("=== Executing Phases: {} ===".format(remainingPhases))
    if language == "Hebrew":
        App.log("=== Updating the site's search and routing DBs ===")
        # Update the site's search and routing DBs
        try:
            App.start_program("UpdateDB.bat",[osm_source.updated])
        except:
            pass

    # Tile generation
    if [val for val in ('IsraelHiking15', 'IsraelMTB15', 'IsraelHiking16', 'IsraelMTB16')
            if val in remainingPhases]:
        App.run_command("run-script file="+os.path.join("Scripts", "Maperitive", "IsraelDecoration.mscript"))

    phase = 'IsraelHiking15'
    if phase in remainingPhases:
        App.log('Updating the Israel Hiking Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== Creating Israel Hiking tiles up to zoom 15 ===')  
        base_map.GenToDirectory(7, 15, os.path.join(site_dir, 'Tiles'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelMTB15'
    if phase in remainingPhases:
        App.log('Updating the Israel MTB Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== Creating Israel MTB tiles up to zoom 15 ===')  
        base_map.GenToDirectory(7, 15, os.path.join(site_dir, 'mtbTiles'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelHiking16'
    if phase in remainingPhases:
        App.log('Updating the Israel Hiking Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log("=== Creating Israel Hiking zoom 16 tiles ===")
        base_map.GenToDirectory(16, 16, os.path.join(site_dir, 'Tiles'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelMTB16'
    if phase in remainingPhases:
        App.log('Updating the Israel MTB Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== Creating Israel MTB zoom 16 tiles ===')  
        base_map.GenToDirectory(16, 16, os.path.join(site_dir, 'mtbTiles'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    # Overlay generation
    if [val for val in ('OverlayTiles', 'OverlayMTB')
            if val in remainingPhases]:
        App.log("=== Preparing Overlay tiles ===")
        App.run_command("clear-map")
        App.run_command("use-ruleset location="+os.path.join("Rules", "empty.mrules"))
        if osm_trails.status() in ("uninitialized", "base"):
            # Not continuing execution of the previous tile generation 
            if osm_trails.downloadMap():
                raise RuntimeError
        if osm_trails.status() == "non-incremental":
            Map.add_osm_source(osm_trails.updated)
            changed = True
        else:
            trails_overlay.osmChangeRead(osm_trails.changes, osm_trails.base, osm_trails.updated)
            (changed, guard) = trails_overlay.statistics()
        App.collect_garbage()
        if changed:
            App.run_command("run-script file="+os.path.join(
                "Scripts", "Maperitive", "IsraelMinimalDecoration.mscript"))

    phase = 'OverlayTiles'
    if phase in remainingPhases:
        App.log("=== Creating Trails Overlay tiles ===")
        if changed:
            App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
            App.run_command("apply-ruleset")
            trails_overlay.GenToDirectory(7, 16, os.path.join(site_dir, 'OverlayTiles'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'OverlayMTB'
    if phase in remainingPhases:
        App.log("=== Creating MTB Overlay tiles ===")
        if changed:
            App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
            App.run_command("apply-ruleset")
            trails_overlay.GenToDirectory(7, 16, os.path.join(site_dir, 'OverlayMTB'))
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    with open(cache_file("Change Analysis.log"), 'a') as journal:
        journal.write("{}\n".format(pretty_timer(
            "Execution time:",
            (datetime.now()-start_time).total_seconds())))

#
# Cleanup and prepare for next execution
#
Map.clear()  # DEBUG
App.collect_garbage()  # DEBUG

osm_trails.advance()
osm_source.advance()

for phase in phases:
    silent_remove(done_file(phase))

print pretty_timer("Total time:", (datetime.now()-start_time).total_seconds())

# vim: shiftwidth=4 expandtab
