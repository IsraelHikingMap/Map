# Israel Hiking Map
This Repository is part of the Israel Hiking Map project. It contains all the files and instructions needed to create the tiles and offline copies of the Israel Hiking Map - a topographic map with style similar to trail maps published by the Israel Trails Committee and the Israel MTB Map - a topographic map for MTB trails and urban bike lanes.

The maps can be seen at [IsraelHiking.osm.org.il](https://IsraelHiking.osm.org.il/). The site has additional facilities including customized trip planning and sharing, points of interest, trails, and route upload and download.

Please see the [Licence terms](LICENSE.md) for using the repository and any tiles created using it.

Enjoy, open a OSM account, and add trails to make these map even better :-)

## Contents
* [Online maps](#online-maps)
  * [OruxMaps](#oruxmaps)
  * [Off-Road](#off-road)
  * [Locus Map](#locus-map)
  * [QGIS](#qgis)
  * [Marble](#marble)
* [Offline maps](#offline-maps)
  * [Ready to download](ready-to-download)
  * [Preparing offline maps](#preparing-offline-maps)
* [Tile Access](#tile-access)
  * [Tile URLs](#tile-urls)
  * [Tile Mirroring](#tile-mirroring)
* [Building the map](#building-the-map)
 * [Minimal recommended configuration](#minimal-recommended-configuration)
 * [One-time setup](#one-time-setup)
 * [Map tiles generation](#map-tiles-generation)

## Online maps
The maps are available for online use with several applications:

### [OruxMaps](http://www.oruxmaps.com/cs/en)
The map is available for Online use as part of OruxMaps' built-in maps.    
Selected the maps using _Maps &rarr; Switch map &rarr; ONLINE_

For online use please refer to [this onlinemapsources.xml file](https://lookaside.fbsbx.com/file/onlinemapsources.xml?token=AWxzCQ3s-4Bwhn8z8Y90nwVTEJJTbGK4XRZmwOvc8aYKJvlZctKnysqBKKDsrwBotyz_MzOZwYZ1QSDtaG94Rg7uimKVKC0xzGEedO1k5JUllXLSDW8hEuP2MJm-KSzwVj1hhIo99-MQWrZUJ2-pXLvIFuUvBBuGFMKssNraJZGM8af1-VYpWuDTGLXa2r9Baz8u3cyl_nszIse8jekTD04r). Replace it with onlinemapsources.xml in oruxsmaps/mapfiles folder in your Android device. This xml will gain you access to many more web services.


### [Off-Road](http://off-road.io/)
Off-Road is available for Android and iOS devices. Selected the maps for online and offline viewing from the "Maps" menu.

### [Locus Map](http://www.locusmap.eu/)
Add the maps using _Maps &rarr; ONLINE &rarr; "+"_

### [QGIS](http://qgis.org)
The maps can be added to QGIS as a tiles layer.

1. Install the "QuickMapServices" plug-in into QGIS.
2. Click on the Search QMS icon.    
   <img width="22" alt="Search QMS icon" src="https://user-images.githubusercontent.com/1304610/32561290-a5639d7e-c4b4-11e7-99e6-0643ecfd395c.png">
3. Type the word "Israel" in the search box and wait for the search results.    
   <img width="326" alt="search resulls" src="https://user-images.githubusercontent.com/1304610/32561610-556ce360-c4b5-11e7-9569-16e831dbfbe4.png">
4. Click "Add" next to the required map.

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

## Offline maps
### Ready to download
#### OroxMaps, Off-Road, and Lucus Map    
Please open the [download dialog](https://israelhiking.osm.org.il/#!/?download) from your Android device and follow the instructions.

_Notes:_
* [Off-Road](#off-road) allows offline use of the maps on both iOS and Android.
* [Locus Map](#locus-map) allows the use of OruxMaps offline maps using:
   * _Maps &rarr; Offline &rarr; "+" &rarr; External maps &rarr; "+"_
   * _Menu &rarr; Local drives_
   * Navigate to the `oruxmaps` &gt; `mapfiles` folder
   * Approve

#### [Galileo for iOS](https://itunes.apple.com/us/app/galileo-offline-maps/id321745474?mt=8)    
Please consult [this pdf file](https://github.com/IsraelHikingMap/Map/files/618705/IHM.iOS.pdf).


### Preparing offline maps

[MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/) is used to create offline maps for many [navigation applications](http://mobac.sourceforge.net/#features). It is a JAVA program that runs on Windows, Linux, macOS, and more.

1. Download [MOBAC - MOBile Atlas Creator](http://mobac.sourceforge.net/).
2. Download the [`Israel Hiking Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking%20Online.xml)
or [`Israel MTB Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20MTB%20Online.xml)
map source to the `{MOBAC installation folder}\mapsources` folder.    
Other [`*Online.xml` _map sources_](https://github.com/IsraelHikingMap/Map/tree/master/Mobile%20Atlas%20Creator/mapsources) can also be used.
3. Download the [`mobac-profile-Israel Hiking Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mobac-profile-Israel%20Hiking%20Online.xml)
or [`mobac-profile-Israel MTB Online.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/blob/master/Mobile%20Atlas%20Creator/mobac-profile-Israel%20MTB%20English%20Online.xml)
profile to the `{MOBAC installation folder}` folder.    
Other [`*Online.xml` _profiles_](https://github.com/IsraelHikingMap/Map/tree/master/Mobile%20Atlas%20Creator) can also be downloaded using the `RAW` button.
4. Open MOBAC. It takes some time since it runs on Java.
5. Move the map by **right-click and drag** in order to show Israel and then use the mouse scroll or the zoom slide to reach a zoom between 7 and 16.
6. Choose your preferred _"Map Source"_ on the left pane and verify that you see the desired map.
7. Choose one of the _"Saved Profiles"_ on the left pane and _"Load"_ it.
8. Use _Atlas &rarr; Convert Atlas Format_ to select the atlas format accepted by the target map application.
9. Expand the _"Atlas Content"_ and delete unrequired zoom levels, if any.
10. Click _"Create Atlas"_. An "Atlas" is the map prepared for offline use. 
11. A window should pop up with progress, make sure to check "ignore download errors", the operation should take about 20 Minutes, depending on the zoom levels selected, your Internet speed, and the performance of your PC.
12. Once finished, click _"Open Atlas Folder"_, look for a folder named _`{Atlas Name}_{Date}_{Time}`_ and copy __its contents__ (not the folder) to the application.

iPhone and iOS users can find instructions for using MOBAC to create and install offline maps for
[Galileo](https://galileo-app.com/manual.html#offline_maps)
and
[Looking4Cache](https://www.looking4cache.com/manual/create-offline-maps-with-mobac).

## Tile Access
The tiles on the the [Israel Hiking server](https://IsraelHiking.OSM.org.il) are available according to the [Licence terms](LICENSE.md).  
The URLs are following the [Slippy map tilenames](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) naming conventions.  
Please avoid overloading the server and use [Tile Mirroring](#tile-mirroring) where possible to minimize the the load.

### Tile URLs
The following tile sources are currently available for zoom levels 7 to 16.    
The trails overlays also include roads and elevation countours.

_Note:_ Different applications and sites may use different syntax for specifying the `{x}`, `{y}`, and `{z}` parts of the URL. Please modify the URL below accordingly.

| Israel Hiking         | URL                                                             |
|:----------------------|:----------------------------------------------------------------|
| Hebrew Base Map       | `https://israelhiking.osm.org.il/Hebrew/Tiles/{z}/{x}/{y}.png`  |
| English Base Map      | `https://israelhiking.osm.org.il/English/Tiles/{z}/{x}/{y}.png` |
| Hiking Trails Overlay | `https://israelhiking.osm.org.il/OverlayTiles/{z}/{x}/{y}.png`  |

| Israel MTB            | URL                                                                |
|:----------------------|:-------------------------------------------------------------------|
| Hebrew Base Map       | `https://israelhiking.osm.org.il/Hebrew/mtbTiles/{z}/{x}/{y}.png`  |
| English Base Map      | `https://israelhiking.osm.org.il/English/mtbTiles/{z}/{x}/{y}.png` |
| MTB Trails Overlay    | `https://israelhiking.osm.org.il/OverlayMTB/{z}/{x}/{y}.png`       |

### Tile Mirroring
Sites and application owners are encouraged to create a mirror of latest tiles on their servers.

We have found that wget is a simple and effective tool to maintain a tile mirror for a site. For example:
```bash
cd IsraelHiking
wget --recursive --timestamping --accept=png --no-parent --no-host-directories --no-verbose --limit-rate=200k http://israelhiking.osm.org.il/Hebrew/Tiles/ http://israelhiking.osm.org.il/Hebrew/mtbTiles/ > temp/wget_tiles.log 2>&1 
```

`wget` comes pre-installed with most Unix and Linux distributions.
A free MS-windows version of `wget` is available for download [online](https://eternallybored.org/misc/wget/).

A periodic task for updating the tiles mirror can be created.
* MS-Windows: [Windows' Task Scheduler](https://technet.microsoft.com/en-us/library/cc748993(v=ws.11).aspx)
* Unix/Linux: the [cron](https://help.ubuntu.com/community/CronHowto) utility. 

## Building the map

Follow the process below if you want to create your own tiles or modify the map style.
[Maperitive](http://maperitive.net/) is used to create the map tiles and it runs on Windows, Linux and macOS.

### Minimal recommended configuration
* A 64-bit Windows PC
* 8 Gb RAM
* 20 Gb free disk space

_Notes:_
* This repository was not tested on Linux or macOS. Please submit your questions, comments and updates as [new issues](https://github.com/IsraelHikingMap/Map/issues/new).
* Linux and MacOS require the use of [Mono](http://www.mono-project.com/Main_Page) in order to run Maperitive.

### One-time setup

1. Download the [latest Maperitive version](http://maperitive.net/download/Maperitive-latest.zip) from the [Maperitive site](http://maperitive.net/)
2. Extract the contents of the zip file to a desired location. 
   * If you have Administrator permission for your Windows machine, you can unzip to the `Program Files` folder, but this is not a requirement.
   * If MOBAC will be used for creation of offline maps, the two installation directories need to have the same parent directory or the MOBAC directory needs to be added to the `PATH` environment variable.
3. Download the [Israel Hiking Map zip file](https://github.com/IsraelHikingMap/Map/archive/master.zip) from the [IsraelHikingMap/Map on GitHub](https://github.com/IsraelHikingMap/Map) site (this site if you read this file in GitHub).
4. Choose a location on a disk with no less than 10GB of free space. Our favorite locations are in the Maperitive Install folder, or within the Documents folders hierarchy.
5. Unzip the zip file to chosen location.
6. Rename the top `Map-master` folder to `IsraelHikingMap`.
7. Download the [wget zip file](https://eternallybored.org/misc/wget/releases/wget-1.18-win32.zip).
6. Create a `wget` directory in the same parent directory as the Maperitive installation directory. Alternatively, place the wget directory elsewhere and add it to the `PATH` environment variable.
7. Extract the contents of the zip file to the wget directory.

### Map tiles generation

1. Ensure you have Internet connection to enable downloading of the latest OpenStreetMap data.
2. Double-click on the `IsraelHikingMap\Scripts\Maperipy\CreateOruxMap.py` script file.
3. If asked how to open the file, please choose `maperitive.exe` from the Maperitive installation folder. 

This should generate 256x256 png tile files inside the `IsraelHikingMap\Site\Tiles` folder and would take several hours.
You may choose to do it overnight, but you need to make sure you don't get out of memory.

### Preparing offline use

To make the locally generated tiles available for offline use.

1. Follow the instructions to [prepare a map for offline use](#prepare-a-map-for-offline-use), and exit MOBAC. 
2. Download [`Israel Hiking.xml`](https://raw.githubusercontent.com/IsraelHikingMap/Map/master/Mobile%20Atlas%20Creator/mapsources/Israel%20Hiking.xml) to the `{MOBAC installtion folder}\mapsources` folder.
3. Edit the `IsraelHiking.xml` file and change the `\<sourceFolder\>` tag to the full path of the directory were the tiles were created, such as `...\{IsraelHikingMap Install folder}\Hebrew\Tiles`.
4. Run MOBAC
5. On the left side under _"Map Source"_ choose _"Isreal Hiking Local"_.
6. Re-create the atlas using your locally generated map.

-------------------------
Created by Harel Mazor and Zeev Stadler 31-Mar-13.

<!-- vim: set autoindent shiftwidth=2: -->
