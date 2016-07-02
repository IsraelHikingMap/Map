# This is sqlite3.py for Maperipy
import os
import clr
# Maperipy installation directory found based on
# http://stackoverflow.com/questions/749711/how-to-get-the-python-exe-location-programmatically
clr.AddReferenceToFileAndPath(
	os.path.join(
	    os.path.dirname(os.path.dirname(
		    os.path.normpath(os.__file__))),
	    'IronPython.SQLite.dll'))
from _sqlite3 import *
