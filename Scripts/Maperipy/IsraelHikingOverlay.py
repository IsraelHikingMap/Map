from maperipy import App
import os.path

App.log('script-dir: ' + App.script_dir)
App.run_command('change-dir dir="' + App.script_dir +'"')

ProgramFiles = os.path.dirname(os.path.dirname(App.script_dir))

App.log("=== Create Trails Overlay tiles ===")
App.run_command("run-script file=IsraelHikingOverlay.mscript")
if os.path.exists(App.script_dir + "\UploadTiles.bat"):
    App.log("=== Upload Trails Overlay tiles ===")
    App.log('App.start_program("' + App.script_dir + '\UploadTiles.bat", "OverlayTiles.zip"])')
    App.start_program(App.script_dir + "\UploadTiles.bat", ["OverlayTiles.zip"])
if os.path.exists(ProgramFiles + "\Mobile Atlas Creator\All IsraelHikingOverlay Maps.bat"):
    App.log("=== Launch creation of All IsraelHikingOverlay Maps ===")
    App.log('App.start_program(ProgramFiles + "\Mobile Atlas Creator\All IsraelHikingOverlay Maps.bat", [])')
    App.start_program(ProgramFiles + "\Mobile Atlas Creator\All IsraelHikingOverlay Maps.bat", [])

App.collect_garbage()

# vim: shiftwidth=4 expandtab
