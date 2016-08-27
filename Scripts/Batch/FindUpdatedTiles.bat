@ECHO OFF
REM Usage:
REM FindUpdatedTiles [Tiles sub/directory ...]
REM
REM Find and upload Tiles created after the Israel-and-Palestine.pdb file
REM This script is used when the tile genaration process was interrupted
REM and some generated tiles were not uploaded.
REM
REM - Relative paths are taken from IsraelHiking\Site
REM - The default directories are chosen according to the Zip files found in
REM   the output directory
REM 
REM Examples:
REM FindUpdatedTiles 
REM FindUpdatedTiles mtbTiles
REM FindUpdatedTiles Tiles\15 Tiles\16
REM

SETLOCAL EnableDelayedExpansion
PUSHD %~dp0\..\..
SET ERRORLEVELWAS=0
SET UPLOADTILES="%CD%\Scripts\Batch\UploadTiles.bat"
PATH %PATH%;%~d0\Program Files\7-Zip;%CD%\Scripts\Batch\UploadTiles

ECHO Searching and uploading recently created tiles
SET TILES=
IF NOT [%1]==[] (
  SET TILES=%*
) ELSE (
  REM Choose the directories to scan according to the Zip files found in
  REM the output directory
  ECHO Looking for Zip files in the "output" directory
  IF NOT EXIST output\LastModified.zip (
    ECHO LastModified.zip not found
  ) ELSE IF NOT EXIST output\TileUpdate.zip (
    ECHO TileUpdate.zip not found
    SET TILES=Tiles\7 Tiles\8 Tiles\9 Tiles\10 Tiles\11 Tiles\12 Tiles\13 ^
	Tiles\14 Tiles\15
  ) ELSE IF NOT EXIST output\OverlayTiles.zip (
    ECHO OverlayTiles.zip not found
    SET TILES=OverlayTiles
  ) ELSE IF NOT EXIST output\TileUpdate16.zip (
    ECHO TileUpdate16.zip not found
    SET TILES=Tiles\16
  ) ELSE IF NOT EXIST output\mtbTileUpdate.zip (
    ECHO mtbTileUpdate.zip not found
    SET TILES=mtbTiles
  ) ELSE (
    ECHO All zip files were found
  )
  SET NUMZIPFILES=0
  FOR %%Z in (output\TileUpdate.zip ^
	      output\OverlayTiles.zip ^
	      output\TileUpdate16.zip ^
	      output\mtbTileUpdate.zip ) DO (
    IF EXIST %%Z (
      SET /A NUMZIPFILES=!NUMZIPFILES! + 1
      IF %%~zZ NEQ 0 (
	ECHO Restarting upload of %%Z
	CALL %UPLOADTILES% %%Z
      )
    )
  )
  IF !NUMZIPFILES!==4 (
    @REM All zip files were found and uploaded
    @REM Can also upload LastModified.zip
    FOR %%Z in ( output\LastModified.zip ) DO (
      IF %%~zZ NEQ 0 (
	ECHO Restarting upload of %%Z
	CALL %UPLOADTILES% %%Z
      )
    )
  )
)
IF "%TILES%"=="" (
  EXIT /B
)

CD Site
ECHO Finding updated Tiles in:
ECHO %TILES%
@REM
@REM Use a unique ID for partiel Zip file in order to enable the map creation
@REM to restart at the correct stage
@REM Use first 4 characters of the directory to enable automatic selection of
@REM upload destinations
@REM
SET UNIQUEID=%TILES:~0,4%-%DATE:~-10%-%RANDOM%
SET UNIQUEID=%UNIQUEID:/=-%

@REM The upload script should not pause
SET NOPAUSE=REM

ECHO Finding recently changed Tiles...
"%~d0\Program Files\UnxUtils\usr\local\wbin\find.exe" %TILES% -name "*.png" ^
    -newer "..\Cache\israel-and-palestine-latest.osm.pbf" -print ^
    > "%TEMP%\%UNIQUEID%.lst"

ECHO Adding them to a zip file...
IF EXIST ..\output\%UNIQUEID%.zip (
  DEL ..\output\%UNIQUEID%.zip
)
"7z.exe" a -tzip ..\output\%UNIQUEID%.zip @%TEMP%\%UNIQUEID%.lst 

ECHO Uploading the tiles...
CALL %UPLOADTILES% output\%UNIQUEID%.zip

IF ERRORLEVEL 1 (
  @ECHO UploadTiles returned an error
  SET ERRORLEVELWAS=1
)
@ECHO %DATE% %TIME%: Completed uploading to %%S

REM Restore original Directory
POPD

EXIT /B %ERRORLEVELWAS%

@REM vim:sw=2:ai
