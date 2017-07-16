REM Prefetch minutely changefiles for
REM Israel Hiking and Biking - IsraelHuking.osm.org.il

SETLOCAL

@REM Script is located at ...\Scripts\Batch 
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%

IF EXIST "%ISRAELHIKING%\Cache\Hebrew\israel-and-palestine-updated.osm.pbf" (
  SET BASIS="%ISRAELHIKING%\Cache\Hebrew\israel-and-palestine-updated.osm.pbf"
) ELSE IF EXIST "%ISRAELHIKING%\Cache\Hebrew\israel-and-palestine-latest.osm.pbf" (
  SET BASIS="%ISRAELHIKING%\Cache\Hebrew\israel-and-palestine-latest.osm.pbf"
) ELSE (
  EXIT /B
)

osmup.exe %BASIS% NUL.osc --base-url=http://download.openstreetmap.fr/replication/asia/israel_and_palestine --minute --tempfiles="%ISRAELHIKING%\Cache\openstreetmap_fr\asia\israel_and_palestine" --keep-tempfiles --trust-tempfiles

TIMEOUT 5
EXIT /B
@REM vim:sw=2:ai:ic:expandtab
