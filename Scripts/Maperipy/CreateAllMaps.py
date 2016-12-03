import os
import os.path
from datetime import *
import string
import errno
from maperipy import *
from maperipy.osm import *
from GenIsraelHikingTiles import IsraelHikingTileGenCommand

start_time = datetime.now()

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: '+MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: '+ProgramFiles)
IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('IsraelHikingDir: '+IsraelHikingDir)
App.run_command('change-dir dir="'+IsraelHikingDir +'"')
os.chdir(IsraelHikingDir)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def add_to_PATH(app_dir):
    full_app_dir=os.path.join(ProgramFiles, app_dir)
    for path_dir in (string.split(os.environ["PATH"], os.pathsep)):
        if os.path.basename(path_dir) == app_dir:
            # Application already found in PATH
            return
    if not os.path.isdir(full_app_dir):
        # Application not a sibling of Maperitive
        App.log("Warning: "+app_dir+" location not found. Could not add it to PATH.")
        return
    os.environ["PATH"] = string.join([os.environ["PATH"],full_app_dir], os.pathsep)

add_to_PATH("wget")
add_to_PATH("Mobile Atlas Creator")

phases = [
    'OverlayTiles',
    'IsraelHiking15',
    'IsraelMTB15',
    'IsraelHiking16',
    'IsraelMTB16',
    'LastModified']
remainingPhases = []

def done_file(phase):
    return os.path.join(IsraelHikingDir, 'output', phase+'.done')

def mark_done(phase):
    open(done_file(phase), 'a').close()
    App.log(phase+' phase is done.')
    gen_cmd.print_timer("Current duration:", (datetime.now()-start_time).total_seconds())

def MOBAC(map_script, map_description):
    program_line = os.path.join(ProgramFiles, "Mobile Atlas Creator", map_script)
    if os.path.exists(program_line):
        App.log("=== Launch creation of "+map_description+" ===")
        App.log('App.start_program("'+program_line+'", [])')
        App.start_program(program_line, [])

# Keep batch windows open up to 24 hours
os.environ["NOPAUSE"] = "TIMEOUT /T 86400"

gen_cmd =  IsraelHikingTileGenCommand()

# Create a new map if all phased were done
phases_done = 0
for phase in phases:
    if not os.path.exists(done_file(phase)):
        remainingPhases.append(phase)

if remainingPhases == []:
    for phase in phases:
        os.remove(done_file(phase))

# TODO openstreetmap.fr's israel minutely updates
# The OSM data used by the latest tile generation
latest = os.path.join(IsraelHikingDir, 'Cache', 'israel-latest.osm.pbf')
# URL for downloading the above
latest_url = "http://download.openstreetmap.fr/extracts/asia/israel-latest.osm.pbf"
# The changes since then
osm_change = os.path.join(IsraelHikingDir, 'Cache', 'israel-update.osc')
# The updated OSM data for this tile generation
updated = os.path.join(IsraelHikingDir, 'Cache', 'israel-updated.osm.pbf')
# Source of the OSM diff files
base_url = "download.openstreetmap.fr/replication/asia/israel"
change_resolution = "--minute"

# Geofaprik's israel-and-palestine daily updates
# The OSM data used by the latest tile generation
latest = os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-latest.osm.pbf')
# URL for downloading the above
latest_url = "http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf"
# The changes since then
osm_change = os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-update.osc')
# The updated OSM data for this tile generation
updated = os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-updated.osm.pbf')
# Source of the OSM diff files
base_url = "download.geofabrik.de/asia/israel-and-palestine-updates"
change_resolution = "--sporadic"

# Output directory for the tiles of all maps
site_dir = os.path.join(IsraelHikingDir, 'Site')

if os.path.exists(latest):
    if remainingPhases == phases or remainingPhases == []:
        App.log("=== Downloading map changes ===")
        exit_code = App.run_program("osmup.exe", 7200, [
            latest, osm_change, "--base-url="+base_url, change_resolution])
        gen_cmd.print_timer("Current duration:", (datetime.now()-start_time).total_seconds())
        if exit_code == 21:
            # osmupdate: Your OSM file is already up-to-date
            App.log("=== No changes found, map update completed ===")
            remainingPhases = []
        else:
            App.log("=== Creating updated map data ===")
            App.run_program("osmconvert.exe", 300, [latest, osm_change, "-o="+updated])
            remainingPhases = phases
            gen_cmd.print_timer("Current duration:", (datetime.now()-start_time).total_seconds())
    else:
        App.log('=== Continueing execution of the previous tile generation ===')  
        App.log('Remaining phases: '+', '.join(remainingPhases))
        App.run_command("pause 15000")

    if remainingPhases:
        # Osm Change analysis
        App.run_command("use-ruleset location="+os.path.join("Rules", "empty.mrules"))
        App.log("=== Analyzing map changes ===")
        gen_cmd.osmChangeRead(osm_change, latest, updated)
        (changed, guard) = gen_cmd.statistics()
        if not changed:
            remainingPhases = ["LastModified"]
        gen_cmd.print_timer("Current duration:", (datetime.now()-start_time).total_seconds())
else:
    # Create base map if latest does not exist
    App.log("=== Downloading the latest.osm.pbf ===")
    App.log("=== No Incremental Tile Generation ===")
    # wget for Windows: http://gnuwin32.sourceforge.net/packages/wget.htm
    App.run_program('wget.exe', 1200,
                    ["--timestamping",
                     "--no-directories", "--no-verbose",
                     '--directory-prefix="'+os.path.join(IsraelHikingDir, 'Cache')+'"',
                     latest_url])
    gen_cmd.timestamp = datetime.fromtimestamp(os.path.getmtime(latest))
    OsmData.load_pbf_file(latest)
    remainingPhases = phases

if remainingPhases:
    # Tile generation
    phase = 'OverlayTiles'
    if phase in remainingPhases:
        App.log("=== Create Trails Overlay tiles ===")
        App.run_command("set-setting name=map.coastline.mode value=ignore")
        App.run_command("use-ruleset location="+os.path.join("Rules", "IsraelHikingOverlay.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        gen_cmd.GenToDirectory(7, 16, os.path.join(site_dir, 'OverlayTiles'))
        MOBAC("All IsraelHikingOverlay Maps.bat", "All Israel Hiking Overlay Maps")
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    if [val for val in ['IsraelHiking15', 'IsraelMTB15', 'IsraelHiking16', 'IsraelMTB16']
            if val in remainingPhases]:
        App.run_command("run-script file="+os.path.join("Scripts", "Maperitive", "IsraelDecoration.mscript"))

    phase = 'IsraelHiking15'
    if phase in remainingPhases:
        App.log('Updating the Israel Hiking Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== creating tiles for Israel Hiking zoom levels up to 15 ===')  
        gen_cmd.GenToDirectory(7, 15, os.path.join(site_dir, 'Tiles'))
        MOBAC("Create Israel Hiking.bat", "Oruxmap Israel Hiking map")
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelMTB15'
    if phase in remainingPhases:
        App.log('Updating the Israel MTB Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== creating tiles for Israel MTB zoom levels up to 15 ===')  
        gen_cmd.GenToDirectory(7, 15, os.path.join(site_dir, 'mtbTiles'))
        MOBAC("Create Israel MTB.bat", "Oruxmaps Israel MTB map")
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelHiking16'
    if phase in remainingPhases:
        App.log('Updating the Israel Hiking Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log("=== Create tiles for Israel Hiking zoom level 16 ===")
        gen_cmd.GenToDirectory(16, 16, os.path.join(site_dir, 'Tiles'))
        MOBAC("Create Israel Hiking 16.bat", "Oruxmap Israel Hiking detailed map")
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'IsraelMTB16'
    if phase in remainingPhases:
        App.log('Updating the Israel MTB Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
        App.run_command("apply-ruleset")
        App.collect_garbage()
        App.log('=== creating Israel MTB zoom level 16 ===')  
        gen_cmd.GenToDirectory(16, 16, os.path.join(site_dir, 'mtbTiles'))
        MOBAC("Create Israel MTB 16.bat", "Oruxmaps Israel MTB detailed map")
        mark_done(phase)
    else:
        App.log(phase+' phase skipped.')

    phase = 'LastModified'
    if phase in remainingPhases:
        # Create LastModified.js file and add it to done file
        last_modified = gen_cmd.timestamp.strftime("%d-%m-%Y")
        App.log("=== Create Last Update info: "+last_modified+" ===")
        mkdir_p(os.path.join(site_dir, 'Tiles'))   # For initial creation of LastModified.js
        with open(os.path.join(site_dir, 'Tiles', 'LastModified.js'), 'w') as jsFile:
            jsFile.write("function getLastModifiedDate(){return '"+last_modified+"';}")
        mark_done(phase)

    for phase in phases:
        try:
            os.remove(done_file(phase))
        except:
            pass

    # Don't loose the original latest pbf if something goes wrong
    if os.path.exists(updated):
        os.rename(latest, latest+".old")
        os.rename(updated, latest)
        os.remove(latest+".old")
    Map.clear()

duration = datetime.now()-start_time
gen_cmd.print_timer("Total time:", duration.total_seconds())

App.run_command("exit")

Map.clear()  # DEBUG
App.collect_garbage()  # DEBUG

# vim: shiftwidth=4 expandtab
