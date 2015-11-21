import os, os.path, datetime, string
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

# Keep the name of the Tile Upload command
upload_tiles = os.path.join(IsraelHikingDir, "Scripts", "Batch", "UploadTiles.bat")

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
add_to_PATH("WinSCP")

def zip_and_upload(zip_file):
    if os.path.exists(upload_tiles):
        App.log("=== Create a Zip file with new tiles ===")
        App.run_command('zip base-dir="' + os.path.join(IsraelHikingDir, 'Site') + '" zip-file="' + zip_file + '"')
        App.log("=== Upload " + zip_file + "===")
        App.log('App.start_program("' + upload_tiles + '", [' + zip_file + '])')
        App.start_program(upload_tiles, [zip_file])

gen_cmd =  GenIsraelHikingTiles.IsraelHikingTileGenCommand(BoundingBox(Srid.Wgs84LonLat, 34.00842, 29.32535, 35.92745, 33.398339999), 7, 16)

zip_file = os.path.join(IsraelHikingDir, 'output', 'mtbTileUpdate.zip')
if not os.path.exists(zip_file) :
    App.run_command("run-script file=" + os.path.join("Scripts", "Maperitive", "IsraelMTB.mscript"))
    # Map Created
    #Original# App.run_command("generate-tiles minzoom=7 maxzoom=15 subpixel=3 tilesdir=" + IsraelHikingDir + "\Site\Tiles use-fprint=true")
    gen_cmd.GenToDirectory(7, 16, os.path.join(IsraelHikingDir, 'Site', 'mtbTiles'))
    App.collect_garbage()
    zip_and_upload(zip_file)
    App.collect_garbage()
else :
    App.log('Skipped: ' + zip_file + ' already exists.')

os.chdir(MaperitiveDir)

# vim: shiftwidth=4 expandtab
