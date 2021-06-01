@TITLE Hebrew Tiles and offline files

@ECHO OFF
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

git pull
CALL IsraelHikingInstallOnce.py

@REM Maperitive
IF %LANGUAGE%==Hebrew (
  CALL CreateAllMaps.py
) ELSE (
  CALL CreateEnglishMaps.py
)

@REM PUSHD to the MOBAC directory
SET PROGDIRS=%programfiles%;%programfiles(x86)%;%~d0%programfiles:~2%;%~d0%programfiles(x86):~2%
FOR %%p in ("Mobile Atlas Creator") DO PUSHD %%~dpn$PROGDIRS:p

FOR %%S IN ("" " 16") DO (
  FOR %%M IN (Hiking MTB) DO (
    IF %LANGUAGE%==Hebrew (
      CALL "Create Israel %%~M%%~S.bat"
    ) ELSE (
      CALL "Create Israel %%~M% English%~S.bat"
    )
  )
)

POPD

:END
