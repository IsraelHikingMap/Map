from maperipy import App

MinLon=34
MaxLon=36

MinLat=29
MaxLat=34

App.run_command('set-dem-source ASTER')

for Lon in range (MinLon, MaxLon, 1) :
  for Lat in range (MinLat, MaxLat, 1) :
    App.run_command('generate-contours interval=10 bounds='+str(Lon)+','+str(Lat)+ ',' +str(Lon+1)+','+str(Lat+1))
    App.run_command('save-source ASTER-'+str(Lon)+'-'+str(Lat)+'.contours')

App.run_command('save-map-script file=Scripts\Contours.mscript')
