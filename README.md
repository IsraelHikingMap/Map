# Israel Hiking Map
This Repository is part of the Israel Hiking Map project, and it holds all the file and instructions needed to create the tiles and offline copies of the Israel Hiking Map - a topographic map with style similar to Israel Trails Committee (ITC).

The output of the map can be [seen here](https://IsraelHiking.osm.org.il/).

## Contents
* [Ready-to-use maps](#ready-to-use-maps)
  * [Android supported applications](#android-supported-applications)
  * [Galileo for iOS](#galileo-for-ios)
  * [Marble](#marble)
* [Tile Access](#tile-access)
  * [Tile URLs](#tile-urls)
  * [QGIS Integration](#qgis-integration)
  * [Tile Mirroring](#tile-mirroring)
* [Prepare a map for offline use](#prepare-a-map-for-offline-use)
* [Building the map](#building-the-map)

## Ready-to-use maps

For offline use of the maps on android devices follow the instructions in the [download dialog](https://israelhiking.osm.org.il/#!/?download).
      
### Android supported applications
  * The map is available for Online use as part of OruxMaps built-in maps.
    * Select the map using  _"Maps &rarr; Switch map &rarr; ONLINE &rarr; Israel Hiking"_

### [Galileo for iOS](https://itunes.apple.com/us/app/galileo-offline-maps/id321745474?mt=8)
This is the only app for iOS that we know is supported, please consult [this pdf file](https://github.com/IsraelHikingMap/Map/files/618705/IHM.iOS.pdf) in order to use it.

### [Marble](https://marble.kde.org/install.php)
Marble is available for various Linux Desktop distributions, Windows Desktop. The Mac OS X version may require compilation.
Setup instructions:
  * Maps folder location is
    * Windows: `%programfiles%\Marble\data\maps\earth\`
    * Linux  : `/usr/share/apps/marble/data/maps/earth/`
  * Copy the [osm.org.il folder](https://github.com/shtrb/marble/tree/master/earth/osm.org.il) to maps folder
  * Copy the [mtb folder](https://github.com/shtrb/marble/tree/master/earth/mtb) to maps folder
  * Copy the [routes folder](https://github.com/shtrb/marble/tree/master/earth/routes) to maps folder
  * Select _"osm.org.il"_ in the available maps

## Tile Access
The tiles on the the [Israel Hiking server](http://IsraelHiking.OSM.org.il) are available according to the [Licence terms](LICENSE.md).  
The URLs are following the [Slippy map tilenames](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) naming conventions.  
Please avoid overloading the server and use [Tile Mirroring](#tile-mirroring) where possible to minimize the the load.

### Tile URLs
The following tile sources are currently available for zoom levels 7 to 16:

#### Hebrew Base Maps
* Israel Hiking Map: `https://israelhiking.osm.org.il/Hebrew/Tiles/{z}/{x}/{y}.png`
* Israel MTB Map: `https://israelhiking.osm.org.il/Hebrew/mtbTiles/{z}/{x}/{y}.png`

#### English Base Maps
* Israel Hiking Map (English): `https://israelhiking.osm.org.il/English/Tiles/{z}/{x}/{y}.png`
* Israel MTB Map (English): `https://israelhiking.osm.org.il/English/mtbTiles/{z}/{x}/{y}.png`

#### Trails Overlays
* Hiking Trails Overlay with roads and elevation countours: `https://israelhiking.osm.org.il/OverlayTiles/{z}/{x}/{y}.png`
* MTB Trails Overlay with roads and elevation countours: `https://israelhiking.osm.org.il/OverlayMTB/{z}/{x}/{y}.png`

### QGIS Integration
The maps can be added to QGIS, by by the following steps:

1. Install the "QuickMapServices" plug-in into QGIS
2. Click on the QuickMapServices icon

   <img width="110" alt="createservice" src="https://cloud.githubusercontent.com/assets/1304610/20640313/e45942ba-b3e2-11e6-8cc3-7d9e09c3105c.png">
3. Choose "Settings" 
4. Open the "Add/Edit/Remove" tab
5. Under "My services", create a new service by clicking the "+" button

   <img width="330" alt="createservice" src="https://cloud.githubusercontent.com/assets/1304610/20640842/36f86144-b3f3-11e6-930d-3f074c2644fa.png">
6. Fill the form in the "General" tab

   <img width="300" alt="createservice" src="https://cloud.githubusercontent.com/assets/1304610/20642358/550f7236-b415-11e6-8dcf-9af256f8099d.png">

   Note: The <img width="16" alt="favicon-32x32" src="https://github.com/IsraelHikingMap/Site/blob/master/IsraelHiking.Web/sources/content/favicons/favicon-32x32.png"> icon can be downloaded from [here](https://github.com/IsraelHikingMap/Site/blob/master/IsraelHiking.Web/sources/content/favicons/favicon-32x32.png)
7. Open the "TMS" tab and fill the form with one of the [Tile URLs](#tile-urls)

   <img width="300" alt="tms" src="https://cloud.githubusercontent.com/assets/1304610/20642389/5b10fc26-b416-11e6-9226-08cc705224b6.png">

   Fill the other values as shown above.
8. Click "OK"
9. Click "Save"

The new map is now available in the OSM group under the QuickMapServices button
### Tile Mirroring
Sites and application owners are encouraged to create a mirror of latest tiles on their servers.

We have found that wget is a simple and effective tool to create such a mirror mechanism. For example:
```bash
cd public_html/IsraelHiking
wget --recursive --timestamping --accept=png --no-parent --no-host-directories --no-verbose --limit-rate=200k http://israelhiking.osm.org.il/Tiles/ http://israelhiking.osm.org.il/OverlayTiles/ http://israelhiking.osm.org.il/mtbTiles/ > temp/wget_tiles.log 2>&1 
```

wget comes pre-installed with most Unix/Linux distributions.
A free MS-windows version of wget is available for download [online](https://eternallybored.org/misc/wget/).

A daily task for refreshing the mirror tiles can be created:
* MS-Windows: [Windows' Task Scheduler](https://technet.microsoft.com/en-us/library/cc748993(v=ws.11).aspx)
* Unix/Linux: the [cron](https://help.ubuntu.com/community/CronHowto) utility. 

## Prepare a map for offline use

[MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is used to create offline maps for  for [many navigation applications](http://mobac.sourceforge.net/#features), including OruxMaps. It is a JAVA program that runs on Windows, Linux, MAC, and more.

iPhone and iOS users can find instructions for using MOBAC to create offline maps for
[Galileo](https://galileo-app.com/manual.html#offline_maps)
and
[Looking4Cache](https://www.looking4cache.com/manual/create-offline-maps-with-mobac).

1. Download [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/).
2. Download [`Israel Hiking Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking%20Online.xml) to the `{MOBAC installtion folder}\mapsources` folder.
3. Open MOBAC (it takes some time since it runs on Java) and choose _"oruxmaps sqlite"_ or any other atlas format, as accepted by the map application.
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


## Building the map

Follow the process below if you want to create your own tiles or modify the map style.
[Maperitive](http://maperitive.net/) is used to create the map tiles and it runs on Windows, Linux and MAC.
Note that this might be tricky on PCs that has windows 32bit and less than 8GB RAM).

### One-time setup for Maperitive and the Israel Hiking Map generation:

1. Download the [latest Maperitive version](http://maperitive.net/download/Maperitive-latest.zip) from the [Maperitive site](http://maperitive.net/)
2. Extract the contents of the zip file to a desired location. 
   * If you have Administrator permission for your Windows machine, you can unzip to the `Program Files` folder, but this is not a requirement.
   * If MOBAC will be used for creation of offline maps, the two installation directories need to have the same parent directory or the MOBAC directory needs to be added to the `PATH` environment variable.
   * On Linux and MacOS, Maperitive requires the use of [Mono](http://www.mono-project.com/Main_Page).
3. Download the [Israel Hiking Map zip file](https://github.com/IsraelHikingMap/Map/archive/master.zip) from the [IsraelHikingMap/Map on GitHub](https://github.com/IsraelHikingMap/Map) site (this site if you read this file in GitHub).
4. Choose a location on a disk with no less than 10GB of free space. Our favorite locations are in the Maperitive Install folder, or within the Documents folders hierarchy.
5. Unzip the zip file to chosen location.
6. Rename the top `Map-master` folder to `IsraelHikingMap`.
7. Download the [wget zip file](https://eternallybored.org/misc/wget/releases/wget-1.18-win32.zip).
6. Create a `wget` directory in the same parent directory as the Maperitive installation directory. Alternatively, place the wget directory elsewhere and add it to the `PATH` environment variable.
7. Extract the contents of the zip file to the wget directory.

### Map tiles generation:

1. Ensure you have Internet connection to enable downloading of the latest OpenStreetMap data.
2. Double-click on the `IsraelHikingMap\Scripts\Maperipy\CreateOruxMap.py` script file.
3. If asked how to open the file, please choose `maperitive.exe` from the Maperitive installation folder. 

This should generate 256x256 png tile files inside the `IsraelHikingMap\Site\Tiles` folder and would take several hours.
You may choose to do it overnight, but you need to make sure you don't get out of memory.

### Preparing locally generated map for offline use

This is an optional stage in case you want to make the locally generated tiles available for offline use.

1. Follow the instructions to [prepare a map for offline use](#prepare-a-map-for-offline-use), and exit MOBAC. 
2. Download [`Israel Hiking.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking.xml) to the `{MOBAC installtion folder}\mapsources` folder.
3. Edit the `IsraelHiking.xml` file and change the `\<sourceFolder\>` tag to the full path of the directory were the tiles were created, such as `...\{IsraelHikingMap Install folder}\Site\Tiles`.
4. Run MOBAC
5. On the left side under _"Map Source"_ choose _"Isreal Hiking Local"_.
6. Re-create the atlas using your locally generated map.

-------------------------
Created by Harel Mazor and Zeev Stadler 31-Mar-13.

<!-- vim: set autoindent shiftwidth=2: -->
