"""Create the English versions of the Israel Hiking and Biking maps
"""

import os.path
from maperipy import *

ProjectDir = os.path.dirname(os.path.dirname(os.path.normpath(App.script_dir)))
# App.log('App.script_dir: '+App.script_dir)
# App.log('ProjectDir: '+ProjectDir)
App.run_command('change-dir dir="'+ProjectDir +'"')
os.chdir(ProjectDir)

import English
import CreateAllMaps

if __name__ == '<module>':
    App.run_command("exit")

# vim: shiftwidth=4 expandtab
