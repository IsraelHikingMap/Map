#Israel Hiking Map
This Repository is part of the IsraelHikingMap project, and it holds all the file and instructions needed to create the tiles and offline copies of the Israel Hiking Map - a topographic map with style similar to Israel Trails Committee (ITC).

The output of the map can be [seen here](http://IsraelHiking.osm.org.il/).

## Contents
* [Ready-to-use maps](#ready-to-use-maps)
  * [Oruxmaps](#oruxmaps)
  * [OpenMaps for iOS](#openmaps-for-ios)
  * [Marble](#marble)
* [Prepare a map for offline use](#prepare-a-map-for-offline-use)
* [Building the map](#building-the-map)

##Ready-to-use maps

###[OruxMaps](http://www.oruxmaps.com/index_en.html): 
  * The map is available for Online use as part of OruxMaps builtin maps.
    * Select the map using  _"Maps &rarr; Switch map &rarr; ONLINE &rarr; Israel Hiking"_
  * For offline use:
    * Create an `Israel Hiking` folder under the `oruxmaps/mapfiles` folder on your Android device.
    * Download both `Israel Hiking.otrk2.xml` and `OruxMapsImages.db` files from one of the following locations:
      * [Google Drive](https://googledrive.com/host/0B-qrsEBJWXhQUGVBM3lHZTF2eXc/Israel Hiking/) (mirror, usually faster).
      * [IsraelHiking.osm.org.il](http://IsraelHiking.osm.org.il/Oruxmaps/mapfiles/Israel Hiking/) (origin).
    * Place both files in the "Israel Hiking" folder on your device.
    * Open OruxMaps and refresh the offline map list using _"Maps &rarr; Switch map &rarr; OFFLINE &rarr; Refresh (the counter-clockwise arrow)"_

To update the offline maps, just re-download the two files.

###[OpenMaps for iOS](http://izeize.com/openmaps/)
This is a guess since we don't have an iOS device
  * Select "Settings" from the menu.
  * Select "Type" under "Map".
  * Select "Edit".
  * Scroll down.
  * Select "Add new type".
  * Define a name for it (i.e Israel Hiking).
  * Enter this URL: `http://IsraelHiking.osm.org.il/Tiles/<zoom>/<x>/<y>.png`.
  * Select "Save".

###[Marble](https://marble.kde.org/install.php)
Marble is available for various Linux Desktop distributions, Windows Desktop. The Mac OS X version may require compilation.
Setup instructions:
  * Maps folder location is
    * Windows: `%programfiles%\Marble\data\maps\earth\`
    * Linux  : `/usr/share/apps/marble/data/maps/earth/`
  * Copy the [osm.org.il folder](https://github.com/shtrb/marble/tree/master/earth/osm.org.il) to maps folder
  * Copy the [mtb folder](https://github.com/shtrb/marble/tree/master/earth/mtb) to maps folder
  * Copy the [routes folder](https://github.com/shtrb/marble/tree/master/earth/routes) to maps folder
  * Select _"osm.org.il"_ in the available maps


##Prepare a map for offline use

[MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is used to create offline maps for  for [many navigation applications](http://mobac.sourceforge.net/#features), including OruxMaps. It is a JAVA program that runs on Windows, Linux, MAC, and more.

iPhone and iOS users can find instructions for using MOBAC to create offline maps for
[Galileo](https://galileo-app.com/manual.html#offline_maps)
and
[Looking4Cache](https://www.looking4cache.com/manual/create-offline-maps-with-mobac).

1. Download [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/).
2. Download [`Israel Hiking Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking%20Online.xml) to the `{MOBAC installtion folder}\mapsources` folder.
3. Open MOBAC (it takes some time since it runs on java) and choose _"oruxmaps sqlite"_ or any other atlas format, as accepted by the map application.
4. On the left side under _"Map Source"_ choose _"Isreal Hiking Online"_.
5. Move zoom on the top of the screen to 7 and by mouse drag select the whole country (the selected area should be red)
   * Alternatively, you can select the required area using a polygon and avoid spending disk space for the Mediterranean Sea and foreign countries.
6. Under _"Zoom levels"_ choose 7,8,...,15
...You may also choose to add zoom level 16, but because of size limitation, the map area cannot contain all of Israel.
7. Click _"Settings"_. Choose _"Map size"_ tab and change the Maximum size of rectangular maps to 1048575 if needed.
8. Under _"Atlas Content"_ set name to _"Israel Hiking"_ and click on _"Add Selection"_.
...this should result in adding the name to the tree, opening the tree should show the selected zoom levels (7 - 15).
9. Click _"Create Atlas"_. An "Atlas" is the map prepared for offline use. 
10. A window should pop up with progress, make sure to check "ignore download errors", the operation should take about 20 Minutes, depending on the polygon selection, zoom levels selected, your Internet speed and the power of your PC.
11. Once finished you should be able to find the atlas at the `{MOBAC installation folder}\atlases\Israel Hiking\{Creation Date}\Israel Hiking` folder.
12. Copy the inner `Israel Hiking` folder (__not `{MOBAC installation folder}\atlases\Israel Hiking`!__) into the `oruxmaps/mapfiles` folder on your Android device or follow the installation instructions of your map application.
13. Enjoy, open a OSM account and add trails to make this map better :-)


##Building the map

Follow the process below if you want to create your own tiles or modify the map style.
[Maperitive](http://maperitive.net/) is used to create the map tiles and it runs on Windows, Linux and MAC.
Note that this might be tricky on PCs that has windows 32bit and less than 8GB RAM).

###One-time setup for Maperitive and the IsraelHiking Map generation:

1. Download the [latest Maperitive version](http://maperitive.net/download/Maperitive-latest.zip) from the [Maperitive site](http://maperitive.net/)
2. Extract the contents of the zip file to a desired location.
...If you have Administrator permission for your Windows machine, you can unzip to the `Program Files` folder, but this is not a requirement.
...On Linux and MacOS, Maperitive requires the use of [Mono](http://www.mono-project.com/Main_Page).
3. Download the [Israel Hiking Map zip file](https://github.com/IsraelHikingMap/Map/archive/master.zip) from the [IsraelHikingMap/Map on GitHub](https://github.com/IsraelHikingMap/Map) site (this site if you read this file in github).
4. Choose a location on a disk with no less than 10GB of free space. Our favorite locations are in the Maperitive Install folder, or within the Documents folders hierarchy.
5. Unzip the zip file to chosen location.
6. Rename the top `Map-master` folder to `IsraelHikingMap`.

###Map tiles generation:

1. Ensure you have Internet connection to enable downloading of the latest OpenStreetMap data.
2. Double-click on the `IsraelHikingMap\Scripts\Maperipy\CreateOruxMap.py` script file.
3. If asked how to open the file, please choose `maperitive.exe` from the Maperitive instalation folder. 

This should generate 256x256 png tile files inside the `IsraelHikingMap\Site\Tiles` folder and would take several hours.
You may choose to do it overnight, but you need to make sure you don't get out of memory.

###Preparing locally generated map for offline use

This is an optional stage in case you want to make the locally generated tiles available for offline use.

1. Follow the instructions to [prepare a map for offline use](#prepare-a-map-for-offline-use), and exit MOBAC. 
2. Download [`Israel Hiking.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking.xml) to the `{MOBAC installtion folder}\mapsources` folder.
3. Edit the `IsraelHiking.xml` file and change the `\<sourceFolder\>` tag to the full path of the dircetory were the tiles were created, such as `...\{IsraelHikingMap Install folder}\Site\Tiles`.
4. Run MOBAC
5. On the left side under _"Map Source"_ choose _"Isreal Hiking Local"_.
6. Re-create the atlas using your locally generated map.

-------------------------
Created by Harel Mazor and Zeev Stadler 31-Mar-13. Last Updated: 5-May-16
