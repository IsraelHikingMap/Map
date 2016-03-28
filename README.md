#Israel Hiking Map
This Repository is part of the IsraelHikingMap project, and it holds all the file and instructions needed to create the tiles and offline copies of the Israel Hiking Map - a topographic map with style similar to Israel Trails Committee (ITC).

The output of the map can be [seen here](http://IsraelHiking.osm.org.il/).


###Ready-to-use maps

* [OruxMaps](http://www.oruxmaps.com/index_en.html): 
  * The map is available for Online use as part of OruxMaps builtin maps.
    * Select the map using  _"Maps &rarr; Switch map &rarr; ONLINE &rarr; Israel Hiking"_
  * For offline use:
    * download the ["Israel Hiking" folder](https://googledrive.com/host/0B-qrsEBJWXhQUGVBM3lHZTF2eXc/) with both files in it.
    * Place the directory under the oruxmaps/mapfiles directory on your device.
    * Refresh the offline map list using _"Maps &rarr; Switch map &rarr; OFFLINE &rarr; Refresh (the counter-clockwise arrow)"_
* [OpenMaps for iOS](http://izeize.com/openmaps/) (this is a guess since we don't have an iOS device)
  * Select "Settings" from the menu.
  * Select "Type" under "Map".
  * Select "Edit".
  * Scroll down.
  * Select "add new type".
  * Define a name for it (i.e Israel Hiking).
  * Enter the this URL: `http://IsraelHiking.osm.org.il/Tiles/<zoom>/<x>/<y>.png`.
  * Select "Save".
* [Marble](https://marble.kde.org/install.php) (source files)
  * Maps directory
    * Windows: `%programfiles%\Marble\data\maps\earth\`
    * Linux  : `/usr/share/apps/marble/data/maps/earth/`
  * Copy osm.org.il [directory](https://github.com/shtrb/marble/tree/master/earth/osm.org.il) to maps directory
  * Copy mtb [directory](https://github.com/shtrb/marble/tree/master/earth/mtb) to maps directory
  * Copy routes [directory](https://github.com/shtrb/marble/tree/master/earth/routes) to maps directory
  * Select osm.org.il in the available maps


###Building the map yourself
Building the map is composed of two steps:
* Optional: Creating the map tiles. You can create tiles using the Israel hiking style map (256x256 PNG tiles). While doing do, you may create additional zoom levels, make changes to the map style, etc.
Note that this might be tricky on PCs that has 32-bit windows or less than 6GB RAM.
* Preparing offline maps for OruxMaps and other navigation software. The second part of the following manual will explain how to convert the map for offline use on an android device.


###Optional: Creating the map tiles

Prerequisites:
* [Maperitive](http://maperitive.net/) is used to create the map tiles and it runs on Windows, Linux and MAC.
* [wget](https://www.gnu.org/software/wget/) is used to download the latest OpenStreetMaps data for Israel. 
One-time setup for Maperitive and the IsraelHiking Map generation:

1. Download the [latest Maperitive version](http://maperitive.net/download/Maperitive-latest.zip) from the [Maperitive site](http://maperitive.net/)
2. Extract the contents of the zip file to a desired location. If you have Administrator permission for your Windows machine, you can unzip to the "Program Files" directory, but this is not a requirement.
...On Linux and MacOS, Maperitive requires the use of [Mono](http://www.mono-project.com/Main_Page).
3. Download the [latest version of wget](https://eternallybored.org/misc/wget/current/wget.exe) from the (Windows binaries of GNU Wget)[https://eternallybored.org/misc/wget/] site. 
4. Move the program to `\Program files\wget\wget.exe` in the same drive as the Israel Hiking project. Alternatively, you may add your installation directory to the PATH environment variable.
5. Download the [Israel Hiking Map zip file](https://github.com/IsraelHikingMap/Map/archive/master.zip) from the [IsraelHikingMap/Map on GitHub](https://github.com/IsraelHikingMap/Map) site (this site if you read this file in github).
6. Choose a location on a disk with no less than 10GB of free space. Our favorite locations are in the Maperitive Install folder, or within the Documents folders hierarchy.
7. Unzip the zip file to chosen location.
8. Rename the top `Map-master` directory to `IsraelHikingMap`.

Map tiles generation:

1. Ensure you have Internet connection to enable downloading of the latest OpenStreetMap data.
2. Double-click on the `IsraelHikingMap\Scripts\Maperipy\CreateOruxMap.py` script file.
3. If asked how to open the file, please choose `maperitive.exe` from the Maperitive instalation directory. 

This should generate 256x256 png tile files inside the `IsraelHikingMap\Site\Tiles` directory and would take several hours.
You may choose to do it overnight, but you need to make sure you don't get out of memory.

###Preparing offline maps for OruxMaps and other navigation software

Prerequisite:
* [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is used to create offline maps. It creates maps for use by [http://mobac.sourceforge.net/#features](many offline navigation applications). MOBAC is a JAVA program that runs on Windows, Linux, MAC, and more. 

[Oruxmaps](http://www.oruxmaps.com/index_en.html)is an offline and online navigation application for Android. You may install OruxMaps on your Androis device from the [play store](https://play.google.com/store/apps/details?id=com.orux.oruxmaps). Oruxmaps is free of charge and does not have ads. It was not created by any of us, yet we recommend you buy the [donate version](https://play.google.com/store/apps/details?id=com.orux.oruxmapsDonate).

1. Download and install [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/). If possible, use the same parent directory for the Maperitive installation and Mobile Atlas Creator instalation.
2. Copy all files and directories from the _"Mobile Atlas Creator"_ directory of this repository to the above Mobile Atlas Creator installtion folder.
3. If you created your own tiles, edit `{MOBAC installtion folder}\mapsources\Israel Hiking.xml` file and change the `\<sourceFolder\>` tag to where the tiles were created (...\{IsraelHikingMAp Install folder}\Site\Tiles - full path).

Offline maps can also be created from the online map available at the [Israel Hiking site](http://IsraelHiking.osm.org.il). The _"Israel Hiking Online"_ saved profile can be used to generate the same map as available online. Alternatively, you can create a different map:

1. Run Mobile Atlas Creator.
2. If you created your own tiles, select _"Israel Hiking"_ as the map source. To use the online tiles, select _"Israel Hiking Online"_ as the map source.
3. Choose _"oruxmaps sqlite"_ as the atlas format.
4. Click _"Settings"_. Choose _"Map size"_ tab and set the Maximum size of rectangular maps to 1048575. 
...You may also chage the Output Atlas Directory in the _"Directories"_ tab.
5. Move zoom on the top of the screen to 7 and by mouse drag select the whole country (the selected area should be red)
   * Alternatively, you can select the required area using a polygon and avoid spending disk space for the Mediterranean Sea and foreign countries.
6. Under _"Zoom levels"_ choose 7,8,...,15
...You may also choose to add zoom level 16, but because of size limitation, the map area cannot contain all of Israel.
7. Under _"Atlas Content"_ set name to _"Israel Hiking"_ and click on _"Add Selection"_.
...this should result in adding the name to the tree, opening the tree should show the selected zoom levels (7 - 15).
8. Click _"Create Atlas"_.
9. A window will pop up with progress indecators. The operation should take about 20 Minutes, depending on the power of the PC.
...When using an online map source, please make sure to check "ignore download errors".
10. Once finished you should be able to find an _"Israel Hiking"_ folder under _"{MOBAC installation folder}\atlases\Israel Hiking\{Creation Date}"_.
11. Copy the inner _"Israel Hiking"_ folder (not _"Israel Hiking\{Creation Date}"_) to your android device under oruxmaps/mapfiles

For your reference, there are 2 saved profiles: _"Israel Hiking"_ and _"Israel Hiking Online"_. Both create Oruxmaps sqlite map for zoom levels 7-15. If MOBAC is installed, with the same parent ditrectory as Maperitive, the map generation script will to build an offline map using the _"Israel Hiking"_. To create a different map, save your preferred profile as _"Israel Hiking"_. Technical details are available in the `Create Israel Hiking.bat` file.

Enjoy, open a OSM account and add trails to make this map better :-)

-------------------------
Created by Harel Mazor and Zeev Stadler 31.3.13. Last Updated: 13.02.16
