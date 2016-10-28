import os, os.path, datetime, string, errno
from maperipy import *
import GenIsraelHikingTiles

# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
MaperitiveDir = os.path.dirname(os.path.dirname(os.path.normpath(os.__file__)))
# App.log('MaperitiveDir: ' + MaperitiveDir)
ProgramFiles = os.path.normpath(os.path.dirname(MaperitiveDir))
# App.log('ProgramFiles: ' + ProgramFiles)
IsraelHikingDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: ' + App.script_dir)
# App.log('IsraelHikingDir: ' + IsraelHikingDir)
App.run_command('change-dir dir="' + IsraelHikingDir +'"')
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
        App.log("Warning: " + app_dir + " location not found. Could not add it to PATH.")
        return
    os.environ["PATH"] = string.join([os.environ["PATH"],full_app_dir], os.pathsep)

add_to_PATH("wget")
add_to_PATH("Mobile Atlas Creator")

phases = [
    'TileUpdate.done',
    'TileUpdate16.done',
    'LastModified.done',
    'OverlayTiles.done',
    'mtbTileUpdate.done',
    'mtbTileUpdate16.done']

def mark_done(done_file):
    open(done_file, 'a').close()

def MOBAC(map_script, map_description):
    program_line = os.path.join(ProgramFiles, "Mobile Atlas Creator", map_script)
    if os.path.exists(program_line):
        App.log("=== Launch creation of " + map_description + " ===")
        App.log('App.start_program("' + program_line + '", [])')
        App.start_program(program_line, [])

# Keep batch windows open up to 24 hours
os.environ["NOPAUSE"] = "TIMEOUT /T 86400"

gen_cmd =  GenIsraelHikingTiles.IsraelHikingTileGenCommand(BoundingBox(Srid.Wgs84LonLat, 34.00842, 29.32535, 35.92745, 33.398339999), 7, 16)

# Create a new map if all phased were done
phases_done = 0
for phase in phases:
    if os.path.exists(os.path.join(IsraelHikingDir, 'output', phase + '.done'   )):
        phases_done += 1
if phases_done == len(phases):
    for phase in phases:
        os.remove(os.path.join(IsraelHikingDir, 'output', phase + '.done'   ))
    phases_done = 0

if phases_done == 0:
    App.log("=== Update israel-and-palestine-latest.osm.pbf ===")
    # wget for Windows: http://gnuwin32.sourceforge.net/packages/wget.htm
    App.run_program('wget.exe', 1200,
                    ["--timestamping",
                     "--no-directories", "--no-verbose",
                     '--directory-prefix="' + os.path.join(IsraelHikingDir, 'Cache') + '"',
                     "http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf"])
    LastModified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-latest.osm.pbf')))
    if LastModified + datetime.timedelta(1) < datetime.datetime.today():
	    App.log("=== pbf file not updated ===");
	    App.run_command("pause 15000")
else :
    App.log('=== Continueing execution of the previous build ===')  
    App.run_command("pause 15000")

done_file = os.path.join(IsraelHikingDir, 'output', 'OverlayTiles.done')
if not os.path.exists(done_file) :
    App.log("=== Create Trails Overlay tiles ===")
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelHikingOverlay.mscript"))
    gen_cmd.GenToDirectory(7, 16, os.path.join(IsraelHikingDir, 'Site', 'OverlayTiles'))
    MOBAC("All IsraelHikingOverlay Maps.bat", "All Israel Hiking Overlay Maps")
    mark_done(done_file)
else :
    App.log('Skipped: ' + done_file + ' already exists.')

done_file = os.path.join(IsraelHikingDir, 'output', 'TileUpdate.done')
if not os.path.exists(done_file) :
    App.log('=== creating Israel Hiking zoom levels up to 15 ===')  
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelHiking.mscript"))
    App.log('=== creating tiles for Israel Hiking zoom levels up to 15 ===')  
    gen_cmd.GenToDirectory(7, 15, os.path.join(IsraelHikingDir, 'Site', 'Tiles'))

    MOBAC("Create Israel Hiking.bat", "Oruxmap Israel Hiking map")

    mark_done(done_file)
else :
    App.log('Skipped: ' + done_file + ' already exists.')

done_file = os.path.join(IsraelHikingDir, 'output', 'TileUpdate16.done')
if not os.path.exists(done_file) :
    App.log('=== creating Israel Hiking zoom level 16 ===')  
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelHiking.mscript"))
    App.log("=== Create tiles for Israel Hiking zoom 16 ===")
    gen_cmd.GenToDirectory(16, 16, os.path.join(IsraelHikingDir, 'Site', 'Tiles'))
    MOBAC("Create Israel Hiking 16.bat", "Oruxmap Israel Hiking detailed map")
    mark_done(done_file)
else :
    App.log('Skipped: ' + done_file + ' already exists.')

done_file = os.path.join(IsraelHikingDir, 'output', 'mtbTileUpdate.done')
if not os.path.exists(done_file) :
    App.log('=== creating Israel MTB zoom levels up to 15 ===')  
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelMTB.mscript"))
    App.log('=== creating tiles for Israel MTB zoom levels up to 15 ===')  
    gen_cmd.GenToDirectory(7, 15, os.path.join(IsraelHikingDir, 'Site', 'mtbTiles'))
    MOBAC("Create Israel MTB.bat", "Oruxmaps Israel MTB map")
    mark_done(done_file)
else :
    App.log('Skipped: ' + done_file + ' already exists.')

done_file = os.path.join(IsraelHikingDir, 'output', 'mtbTileUpdate16.done')
if not os.path.exists(done_file) :
    App.log('=== creating Israel MTB zoom level 16 ===')  
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelMTB.mscript"))
    App.log("=== Create tiles for Israel MTB zoom 16 ===")
    gen_cmd.GenToDirectory(16, 16, os.path.join(IsraelHikingDir, 'Site', 'mtbTiles'))
    MOBAC("Create Israel MTB 16.bat", "Oruxmaps Israel MTB detailed map")
    mark_done(done_file)
else :
    App.log('Skipped: ' + done_file + ' already exists.')

done_file = os.path.join(IsraelHikingDir, 'output', 'LastModified.done')
if not os.path.exists(done_file):
    # Create LastModified.js file and add it to done file
    LastModified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-latest.osm.pbf')))
    App.log("=== Create Last Update info:" + LastModified.strftime("%d-%m-%Y") + " ===")
    mkdir_p(os.path.join(IsraelHikingDir, 'Site', 'Tiles'))   # For initial creation of LastModified.js
    jsFile = open(os.path.join(IsraelHikingDir, 'Site', 'Tiles', 'LastModified.js'), 'w')
    jsFile.write("function getLastModifiedDate() { return '"
                 + LastModified.strftime("%d-%m-%Y")
                 + "'; }")
    jsFile.close()

App.run_command("exit")

# vim: shiftwidth=4 expandtab
