REM Prefetch minutely changefiles for
REM Israel Hiking and Biking - IsraelHiking.osm.org.il

SETLOCAL ENABLEDELAYEDEXPANSION

@REM Script is located at ...\Scripts\Batch 
PUSHD %~dp0..\..\Cache

SET BASIS=Hebrew\israel-and-palestine-updated.osm.pbf
IF NOT EXIST %BASIS% (
  SET BASIS=Hebrew\israel-and-palestine-latest.osm.pbf
  IF NOT EXIST !BASIS! (
    EXIT /B
  )
)

osmup.exe %BASIS% NUL.osc --base-url=http://download.openstreetmap.fr/replication/asia/israel_and_palestine --minute --tempfiles=openstreetmap_fr\asia\israel_and_palestine --keep-tempfiles --trust-tempfiles

POPD

TIMEOUT 5
EXIT /B
@REM vim:sw=2:ai:ic:expandtab
