#Israel Hiking Map
This Repository is part of the IsraelHikingMap project, and it holds all the file and instructions needed to create the tiles and offline copies of the Israel Hiking Map - a topographic map with style similar to Israel Trails Committee (ITC).

The output of the map can be [seen here](http://osm.org.il/IsraelHiking/).


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
    * Enter the this URL: `http://osm.org.il/IsraelHiking/Tiles/<zoom>/<x>/<y>.png`.
    * Select "Save".
* [Marble](https://marble.kde.org/install.php) on Linux (compressed form)
    * Download the osm.org.il [archive file](https://github.com/shtrb/marble/blob/master/archive/osm.org.il.tar.bz2)
    * unpack archive in /usr/share/apps/marble/data/maps/
    * Select osm.org.il in the available maps
* [Marble](https://marble.kde.org/install.php) on Linux (source files)
    * copy osm.org.il [directory](https://github.com/shtrb/marble/tree/master/earth/osm.org.il) to /usr/share/apps/marble/data/maps/earth/
    * copy mtb [directory](https://github.com/shtrb/marble/tree/master/earth/mtb) to /usr/share/apps/marble/data/maps/earth/
    * copy routes [directory](https://github.com/shtrb/marble/tree/master/earth/routes) to /usr/share/apps/marble/data/maps/earth/
    * Select osm.org.il in the available maps
* [Marble](https://marble.kde.org/install.php) on windows (compressed form)
    * Download the osm.org.il [archive file](https://github.com/shtrb/marble/blob/master/archive/osm.org.il.tar.bz2)
    * unpack archive in %programfiles%\Marble\data\maps\
    * Select osm.org.il in the available maps
* [Marble](https://marble.kde.org/install.php) on Windows (source files)
    * copy osm.org.il [directory](https://github.com/shtrb/marble/tree/master/earth/osm.org.il) to %programfiles%\Marble\data\maps\earth\
    * copy mtb [directory](https://github.com/shtrb/marble/tree/master/earth/mtb) to %programfiles%\Marble\data\maps\earth\
    * copy routes [directory](https://github.com/shtrb/marble/tree/master/earth/routes) to %programfiles%\Marble\data\maps\earth\
    * Select osm.org.il in the available maps


###Abstract
Building the map is composed of two steps:
* Maperitive: The first part of following manual will explain how to create an Israel hiking style map (256x256 PNG tiles).
Note that this might be tricky on PCs that has windows 32bit and less than 8GB RAM).
* MOBAC: The second part of the following manual will explain how to convert the map for offline use on an android device.


##Maperitive

[Maperitive](http://maperitive.net/) is used to create the map tiles and it runs on Windows, Linux and MAC.

One-time setup for Maperitive and the IsraelHiking Map generation:
1. Download the [latest Maperitive version](http://maperitive.net/download/Maperitive-latest.zip) from the [Maperitive site](http://maperitive.net/)
2. Extract the contents of the zip file to a desired location. If you have Administrator permission for your Windows machine, you can unzip to the "Program Files" directory, but this is not a requirement.
...On Linux and MacOS, Maperitive requires the use of [Mono](http://www.mono-project.com/Main_Page).
3. Download the [Israel Hiking Map zip file](https://github.com/IsraelHikingMap/Map/archive/master.zip) from the [IsraelHikingMap/Map on GitHub](https://github.com/IsraelHikingMap/Map) site (this site if you read this file in github).
4. Choose a location on a disk with no less than 10GB of free space. Our favorite locations are in the Maperitive Install folder, or within the Documents folders hierarchy.
5. Unzip the zip file to chosen location.
6. Rename the top `Map-master` directory to `IsraelHikingMap`.

Map tiles generation:
1. Ensure you have Internet connection to enable downloading of the latest OpenStreetMap data.
2. Double-click on the `IsraelHikingMap\Scripts\Maperipy\CreateOruxMap.py` script file.
3. If asked how to open the file, please choose `maperitive.exe` from the Maperitive instalation directory. 

This should generate 256x256 png tile files inside the IsraelHikingMap\Site\Tiles directory and would take several hours.
You may choose to do it overnight, but you need to make sure you don't get out of memory.

##MOBAC and OruxMaps

[Oruxmaps](http://www.oruxmaps.com/index_en.html) is an offline and online navigation application for Android.
[MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is used to create offline maps for use by OruxMaps and other applications

[MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is a JAVA program that runs on Windows, Linux, MAC, and more. It creates offline maps for [http://mobac.sourceforge.net/#features](many navigation applications).

1. In order to use an offline version of this map in an android device first install [Oruxmaps](http://www.oruxmaps.com/index_en.html) from the [play store](https://play.google.com/store/apps/details?id=com.orux.oruxmaps). Oruxmaps is free of charge and does not have ads. It was not created by any of us, yet we recommend you buy the [donate version](https://play.google.com/store/apps/details?id=com.orux.oruxmapsDonate).
2. Download [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/).
3. Open IsraelHiking.xml file and change the \<sourceFolder\> tag to where the tiles were created (...\{IsraelHikingMAp Install folder}\Site\Tiles - full path).
4. Place the _"IsraelHiking.xml"_ file in the _"{MOBAC installtion folder}\mapsources"_ folder.
5. Open MOBAC (it takes some time since it runs on java) and choose _"oruxmaps sqlite"_ as the atlas format.
6. On the left side under _"Map Source"_ choose _"Isreal Hiking"_.
7. Move zoom on the top of the screen to 7 and by mouse drag select the whole country (the selected area should be red)
   * Alternatively, you can select the required area using a polygon and avoid spending disk space for the Mediterranean Sea and foreign countries.
8. Under _"Zoom levels"_ choose 7,8,...,15
...You may also choose to add zoom level 16, but because of size limitation, the map area cannot contain all of Israel.
9. Click _"Settings"_. Choose _"Map size"_ tab and change the Maximum size of rectangular maps to 1048575 if needed.
10. Under _"Atlas Content"_ set name to _"Israel Hiking"_ and click on _"Add Selection"_.
...this should result in adding the name to the tree, opening the tree should show the selected zoom levels (7 - 15).
11. Click _"Create Atlas"_.
12. A window should pop up with progress, make sure to check "ignore download errors", the operation should take about 20 Minutes.
13. Once finished you should be able to find an _"Israel Hiking"_ folder under _"{MOBAC installation folder}\atlases\Israel Hiking\{Creation Date}"_.
14. Copy the inner _"Israel Hiking"_ folder (not _"Israel Hiking\{Creation Date}"_) to your android device under oruxmaps/mapfiles
15. Enjoy, open a OSM account and add trails to make this map better :-)

-------------------------
Created by Harel Mazor and Zeev Stadler 31.3.13. Last Updated: 28.7.15
