@REM Create and upload a given Tiles levels
@REM Usage
@REM 	ZipLevel ["new"] [<Level> ...]
@REM 		examples:
@REM 		ZipLevel Tiles\16 
@REM - The default directories are
@REM   Tiles\7 Tiles\8 Tiles\9 Tiles\10 Tiles\11 Tiles\12 Tiles\13 Tiles\14 Tiles\15
@REM
@REM 	ZipLevel ["new"] <Level> "start" <dirnum>
@REM		Start at a given directory number of a single level
@REM

@REM TODO @ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

@REM Script is located at IsraelHiking\Scripts\Batch 
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%
CD %ISRAELHIKING%\Site

ECHO Positional Parameters 0-9: %0 %1 %2 %3 %4 %5 %6 %7 %8 %9
ECHO Positional Parameters *  : %*

SET DIRMIN=0
SET DIRMAX=99999999
IF [%1]==[] (
  SET LEVEL=Tiles\7 Tiles\8 Tiles\9 Tiles\10 Tiles\11 Tiles\12 Tiles\13 Tiles\14 Tiles\15
) ELSE (
  IF /I [%1]==[new] (
    @REM TODO SHIFT /1 does not work well with %*
    SET NEWER=YES
    IF /I [%3]==[start] (
      SET LEVEL=%2
      SET DIRMIN=%4
      IF /I [%5]==[end] (
	IF [%6]==[] (
	  SET DIRMAX=%4
	) ELSE (
	  SET DIRMAX=%6
	)
      )
    ) ELSE (
      SET LEVEL=%*
    )
  ) ELSE (
    IF /I [%2]==[start] (
      SET LEVEL=%1
      SET DIRMIN=%3
      IF /I [%4]==[end] (
	IF [%5]==[] (
	  SET DIRMAX=%3
	) ELSE (
	  SET DIRMAX=%5
	)
      )
    ) ELSE (
      SET LEVEL=%*
    )
  )
)

@REM Upload script should not pause
SET NOPAUSE=REM

REM Change to Script's directory
REM TODO Allow uploading of different tile sets

FOR /D %%L in ( %LEVEL% ) DO (
  IF /I NOT [%%L]==[new] (
    SET ZIPNAME=%%L
    @REM ECHO ZIPNAME #1: !ZIPNAME!
    SET ZIPNAME=!ZIPNAME:\=-!
    @REM ECHO ZIPNAME #2: !ZIPNAME!
    FOR /D  %%D in (%%L\*) DO (
      IF %%~nD GEQ %DIRMIN% (
	IF %%~nD LEQ %DIRMAX% (
	  SET ZIPPATH="%ISRAELHIKING%\Output\!ZIPNAME!-%%~nD.zip"
	  SET ZIPLST="%ISRAELHIKING%\Output\!ZIPNAME!-%%~nD.lst"
	  REM Delete zip file if it already exists
	  IF EXIST !ZIPPATH! (
	    DEL !ZIPPATH!
	  )
	  @ECHO ON
	  IF [%NEWER%]==[] (
            @ECHO Creating !ZIPPATH!...
	    "%~d0\Program Files\7-ZipPortable\App\7-Zip\7z" a -tzip !ZIPPATH! -r %%D\*.png > NUL
	    CALL ..\Scripts\Batch\UploadTiles.bat !ZIPPATH!
	  ) ELSE (
	    "%~d0\Program Files\UnxUtils\usr\local\wbin\find.exe" %%D -name "*.png" -newer "%ISRAELHIKING%\Cache\israel-and-palestine-latest.osm.pbf" -print > !ZIPLST!
	    echo %ERRORLEVEL%
	    @REM TODO "%~d0\Program Files\UnxUtils\usr\local\wbin\find.exe" %%D -name "*.png" -print > !ZIPLST!

	    @REM The FOR statement gets one list file
	    @REM echo CD: %CD%
	    @REM echo %D: %%D
	    @REM ECHO ZIPPATH.lst is: !ZIPLST!
	    @REM DIR !ZIPLST!
	    @REM TODO
	    @REM POPD
	    @REM EXIT /B
	    FOR %%Z in (!ZIPLST!) DO (
	      echo Size of %%Z is %%~zZ
	      dir %%Z
	      if %%~zZ GTR 0 (
		@REM Creates non-empty zip file and Upload it
		"%~d0\Program Files\7-ZipPortable\App\7-Zip\7z" a -tzip !ZIPPATH! @!ZIPLST! > NUL
		CALL ..\Scripts\Batch\UploadTiles.bat !ZIPPATH!
	      )
	    )
	    DEL !ZIPLST!
	  )
	  @REM TODO @ECHO OFF
	  IF NOT ERRORLEVEL 1 (
	    @REM Remove Zip file
	    @REM TODO DEL !ZIPPATH!
	  )
	)
      )
    )
  )
)

REM Restore original Directory
POPD

@REM vim:sw=2:ai:ic:expandtab
