@TITLE Hebrew Tiles and offline files

SETLOCAL ENABLEDELAYEDEXPANSION

@TASKLIST /FI "IMAGENAME eq Maperitive.exe" | find "Maperitive.exe" && (
  @ECHO ==^> No parralel runs for Maperitive
  @GOTO :END
)

@REM Script is located at IsraelHiking\Scripts\Batch 
PATH %~dp0;%PATH%
PUSHD %~dp0\..\Maperipy
PATH %CD%;%PATH%
POPD

@REM Set Language
SET LANGUAGE=%~n0
@ECHO Creating %LANGUAGE% raster tiles

git pull
CALL IsraelHikingInstallOnce.py

@REM Maperitive
IF %LANGUAGE%==Hebrew (
  CALL CreateAllMaps.py
) ELSE (
  CALL CreateEnglishMaps.py
)
echo ERRORLEVEL: %ERRORLEVEL%

@REM PUSHD to the MOBAC directory
SET PROGDIRS=%programfiles%;%programfiles(x86)%;%~d0%programfiles:~2%;%~d0%programfiles(x86):~2%
FOR %%p in ("Mobile Atlas Creator") DO PUSHD %%~dpn$PROGDIRS:p

FOR %%S IN ("" " 16") DO (
  FOR %%M IN (Hiking MTB) DO (
    IF %LANGUAGE%==Hebrew (
      @ECHO CALLing "Create Israel %%~M%%~S.bat"
      CALL "Create Israel %%~M%%~S.bat"
    ) ELSE (
      @ECHO CALLing "Create Israel %%~M English%%~S.bat"
      CALL "Create Israel %%~M English%%~S.bat"
    )
  )
)

POPD

:END
