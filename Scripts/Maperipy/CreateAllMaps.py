import os, os.path, datetime, string, errno
from maperipy import *
import GenIsraelHikingTiles

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
    'IsraelHiking16',
    'IsraelMTB15',
    'IsraelMTB16',
    'LastModified']
remainingPhases = []

def done_file(phase):
    return os.path.join(IsraelHikingDir, 'output', phase+'.done')

def mark_done(phase):
    open(done_file(phase), 'a').close()
    App.log(phase+' phase is done.')

def MOBAC(map_script, map_description):
    program_line = os.path.join(ProgramFiles, "Mobile Atlas Creator", map_script)
    if os.path.exists(program_line):
        App.log("=== Launch creation of "+map_description+" ===")
        App.log('App.start_program("'+program_line+'", [])')
        App.start_program(program_line, [])

# Keep batch windows open up to 24 hours
os.environ["NOPAUSE"] = "TIMEOUT /T 86400"

gen_cmd =  GenIsraelHikingTiles.IsraelHikingTileGenCommand(BoundingBox(Srid.Wgs84LonLat, 34.00842, 29.32535, 35.92745, 33.398339999), 7, 16)

# Create a new map if all phased were done
phases_done = 0
for phase in phases:
    if not os.path.exists(done_file(phase)):
        remainingPhases.append(phase)
App.log('Remaining phases: '+', '.join(remainingPhases))

if remainingPhases == []:
    for phase in phases:
        os.remove(done_file(phase))

if remainingPhases == phases or remainingPhases == []:
    App.log("=== Update israel-and-palestine-latest.osm.pbf ===")
    # wget for Windows: http://gnuwin32.sourceforge.net/packages/wget.htm
    App.run_program('wget.exe', 1200,
                    ["--timestamping",
                     "--no-directories", "--no-verbose",
                     '--directory-prefix="'+os.path.join(IsraelHikingDir, 'Cache')+'"',
                     "http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf"])
    LastModified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-latest.osm.pbf')))
    if remainingPhases == [] and LastModified+datetime.timedelta(1) < datetime.datetime.today():
        App.log("=== pbf file is up-to-date - doing nothing ===");
        App.run_command("pause 15000")
        # Nothing to do, exiting
        App.run_command("exit")
    else:
        remainingPhases = phases
else:
    App.log('=== Continueing execution of the previous build ===')  
    App.run_command("pause 15000")

phase = 'OverlayTiles'
if phase in remainingPhases:
    App.log("=== Create Trails Overlay tiles ===")
    App.run_command("run-script file="+os.path.join("Scripts", "Maperitive", "IsraelHikingOverlay.mscript"))
    gen_cmd.GenToDirectory(7, 16, os.path.join(IsraelHikingDir, 'Site', 'OverlayTiles'))
    MOBAC("All IsraelHikingOverlay Maps.bat", "All Israel Hiking Overlay Maps")
    mark_done(phase)
else:
    App.log(phase+' phase skipped.')

if [val for val in ['IsraelHiking15', 'IsraelHiking16', 'IsraelMTB15', 'IsraelMTB16']
        if val in remainingPhases]:
    App.run_command("run-script file="+os.path.join("Scripts", "Maperitive", "IsraelMap.mscript"))

    if [val for val in ['IsraelHiking15', 'IsraelHiking16']
            if val in remainingPhases]:
        App.log('Updating the Israel Hiking Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "IsraelHiking.mrules"))
        App.run_command("apply-ruleset")

        phase = 'IsraelHiking15'
        if phase in remainingPhases:
            App.log('=== creating tiles for Israel Hiking zoom levels up to 15 ===')  
            gen_cmd.GenToDirectory(7, 15, os.path.join(IsraelHikingDir, 'Site', 'Tiles'))
            MOBAC("Create Israel Hiking.bat", "Oruxmap Israel Hiking map")
            mark_done(phase)
        else:
            App.log(phase+' phase skipped.')

        phase = 'IsraelHiking16'
        if phase in remainingPhases:
            App.log("=== Create tiles for Israel Hiking zoom level 16 ===")
            gen_cmd.GenToDirectory(16, 16, os.path.join(IsraelHikingDir, 'Site', 'Tiles'))
            MOBAC("Create Israel Hiking 16.bat", "Oruxmap Israel Hiking detailed map")
            mark_done(phase)
        else:
            App.log(phase+' phase skipped.')

    if [val for val in ['IsraelMTB15', 'IsraelMTB16']
            if val in remainingPhases]:
        App.log('Updating the Israel MTB Map')
        App.run_command("use-ruleset "+os.path.join("Rules", "mtbmap.mrules"))
        App.run_command("apply-ruleset")

        phase = 'IsraelMTB15'
        if phase in remainingPhases:
            App.log('=== creating tiles for Israel MTB zoom levels up to 15 ===')  
            gen_cmd.GenToDirectory(7, 15, os.path.join(IsraelHikingDir, 'Site', 'mtbTiles'))
            MOBAC("Create Israel MTB.bat", "Oruxmaps Israel MTB map")
            mark_done(phase)
        else:
            App.log(phase+' phase skipped.')

        phase = 'IsraelMTB16'
        if phase in remainingPhases:
            App.log('=== creating Israel MTB zoom level 16 ===')  
            gen_cmd.GenToDirectory(16, 16, os.path.join(IsraelHikingDir, 'Site', 'mtbTiles'))
            MOBAC("Create Israel MTB 16.bat", "Oruxmaps Israel MTB detailed map")
            mark_done(phase)
        else:
            App.log(phase+' phase skipped.')

phase = 'LastModified'
if phase in remainingPhases:
    # Create LastModified.js file and add it to done file
    LastModified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(IsraelHikingDir, 'Cache', 'israel-and-palestine-latest.osm.pbf')))
    App.log("=== Create Last Update info:"+LastModified.strftime("%d-%m-%Y")+" ===")
    mkdir_p(os.path.join(IsraelHikingDir, 'Site', 'Tiles'))   # For initial creation of LastModified.js
    jsFile = open(os.path.join(IsraelHikingDir, 'Site', 'Tiles', 'LastModified.js'), 'w')
    jsFile.write("function getLastModifiedDate() { return '"
                 + LastModified.strftime("%d-%m-%Y")
                 + "'; }")
    jsFile.close()

App.run_command("exit")

# vim: shiftwidth=4 expandtab
