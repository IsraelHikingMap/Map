" A Vim (http://www.vim.org) script to adapt the Norwegian MTB map legend in Israel
" 
" The script performs a horizontal flip of the legend_mtb.osm and saves to the disk
" It also corrects cliff direction
" 
" NOTE: The editor is returned to the original contents in order to
" enable further changes in the source and re-invocation
" 
" Other transformations are currently commented out
"
" To run the script 
" * Open in in Vim
" * File -> Split Open -> legend_mtb.osm
" * Return to the the script's window
" * Execite the script by typing ":so %" and then Enter
" * To exit type ":qall!" and then Enter
"

" Switch to the legend.osm buffer
let mywindow = winnr()
exe bufwinnr("legend.osm") . "wincmd w"

if 1
   " Calculate legend center from minimal and maximal lat and lon 
   let minlat=90.0
   let maxlat=-90.0
   " silent
   g/\(lat='\)\@<=\d\+/.normal n"dyt':let lat=str2float(@d)|if lat < minlat|let minlat = lat|endif|if lat > maxlat|let maxlat=lat|endif
   echo "Legend height: " maxlat "-" minlat "=" maxlat - minlat
   let minlon=180.0
   let maxlon=-180.0
   silent g/\(lon='\)\@<=\d\+/.normal n"dyt':let lon=str2float(@d)|if lon < minlon|let minlon = lon|endif|if lon > maxlon|let maxlon=lon|endif
   echo "Legend width: " maxlon "-" minlon "=" maxlon - minlon
   let centerlat = (minlat+maxlat)/2
   echo "Center Lat: (" minlat "+" maxlat ")/2 =" centerlat
   let centerlon = (minlon+maxlon)/2
   echo "Center Lon: (" minlon "+" maxlon ")/2 =" centerlon
endif

" Min lon
"   <node id='-528' action='modify' visible='true' lat='63.44548579408874' lon='10.348122343061222' />
" Max lon
"   <node id='-522' action='modify' visible='true' lat='63.44008636763261' lon='10.43745349740511'>
" Lon center
"   (63.43113570731234+63.44756702121195)/2 = 63.439351
"   Re-calculate the expression on the line above by executing
"   s#\("\(.*\)= \).*#\=submatch(1).string(eval(submatch(2)))#
 
"   
"   <node id='-56' action='modify' visible='true' lat='63.44666055704215'  lon='10.356068932605455' />
"   <node id='-54' action='modify' visible='true' lat='63.44668037481367'  lon='10.373284535329544' />
"   <node id='-52' action='modify' visible='true' lat='63.43488214155656'  lon='10.373352484748287' />
"   <node id='-50' action='modify' visible='true' lat='63.434862315619604' lon='10.356136882024199' />

" Lat center
" ((63.44666055704215+63.44668037481367+63.43488214155656+63.434862315619604))/4 = 63.44077134725799
" Height
" ((63.44666055704215+63.44668037481367)-(63.43488214155656+63.434862315619604))/2 = 0.01179823733983

" Center lon:
" (10.373284535329544+10.373352484748287+10.356068932605455+10.356136882024199)/4 = 10.36471070867687
" Width
" ((10.373284535329544+10.373352484748287)-(10.356068932605455+10.356136882024199))/2 = 0.01721560272409


" IsraelHiking

" Lat
" 32.7902
" 32.8442
" Center lat:
" (32.7902+32.8442)/2 = 32.8172
" Height:
" 32.8442-32.7902 = 0.054

" Lon
" 35.5630
" 35.5830
" Lon center
" (35.5630+35.5830)/2 = 35.573
" Width
" 35.5830-35.5630 = 0.02

" Lat factor:
" newheight/oldheight
let latfactor = 0.054/0.01179823733983
let latfactor = 2
echo "Lat Factor:" latfactor

" Lon Factor: 
" newwidth/oldwidth
let lonfactor = 0.02/0.01721560272409
let lonfactor = 2
echo "Lon Factor:" lonfactor

let newcenterlat=centerlat
let newcenterlon=centerlon
if 1
  " newposition = (oldposition - oldcenter)*factor + newcenter
  %s#lat=\'\([0-9.]\+\)#\=printf("lat='%.11f",((str2float(submatch(1))-centerlat)*latfactor)+newcenterlat)#
  %s#lon=\'\([0-9.]\+\)#\=printf("lon='%.12f",((str2float(submatch(1))-centerlon)*lonfactor)+newcenterlon)#
endif

if 0
  " horizontal flip
  %s#lon=\'\([0-9.]\+\)#\=printf("lon='%.12f",centerlon*2-(str2float(submatch(1))))#
  " Correct cliff dircetion
  1;/v='cliff'/-1;.m-2
endif

if 0
  " Save and undo
  w
  undo
endif

" Switch back to the script buffer
exe mywindow . "wincmd w"

" vim: set autoindent noexpandtab shiftwidth=2:

