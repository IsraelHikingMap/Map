@ECHO off
SETLOCAL
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%

SET ZIPPATH="%~f1"
IF %ZIPPATH%=="" SET ZIPPATH="%ISRAELHIKING%\Output\TileUpdate.zip"

PATH %PATH%;%~d0\Program Files\WinSCP;%ProgramFiles%\WinSCP;%ProgramFiles(x86)%\WinSCP

@REM The FOR statement gets one full path and extracts its filename
FOR %%Z in (%ZIPPATH%) DO (
  SET ZIPFILE="%%~nxZ"
  SET ZIPDIR="%%~dpZ"
)

IF "%2"=="" (
  IF "%SITES%"=="" (
    SET SITES=Upload-osm.org.il
    @REM zip files of the Tiles directory are uploaded to trailze
    IF %ZIPFILE:~1,4%==Tile SET SITES=Upload-osm.org.il trailze
  )
) ELSE (
  SET SITES= %2 %3 %4 %5 %6 %7 %8 %9
)

REM If needed, start Pageant: an SSH authentication agent for WinSCP and Plink
IF EXIST .\PuTTYOSM.ppk (
  TASKLIST | FIND /i "pageant.exe" > NUL
  IF ERRORLEVEL 1 (
    start .\PuTTYOSM.ppk
    ECHO.
    ECHO =================================
    ECHO Please enter the upload passowrd, 
    ECHO and then...
    PAUSE
    ECHO.
  )
)

SET ERRORLEVELWAS=0
@ECHO SITES=%SITES%
FOR %%S in (%SITES%) DO (

  @ECHO %DATE% %TIME%: Uploading to %%S
  @ECHO Current Directory: %CD%
  @ECHO Uploading: %ZIPPATH%
  REM Generate temporary script to upload %ZIPFILE%
   > %ZIPFILE%.scp ECHO option batch abort
  >> %ZIPFILE%.scp ECHO option confirm off
  >> %ZIPFILE%.scp ECHO option reconnect 45
  >> %ZIPFILE%.scp ECHO open %%S
  >> %ZIPFILE%.scp ECHO cd
  >> %ZIPFILE%.scp ECHO put -resume -preservetime -transfer=binary %ZIPPATH% temp/
  @REM exit 2 is required to abort a WinSCP script in case of call failure
  >> %ZIPFILE%.scp ECHO call unzip -q -d ~/public_html/IsraelHiking -o ~/temp/%ZIPFILE% ^|^| exit 2
  >> %ZIPFILE%.scp ECHO call ~/script/post_transfer.sh ~/temp/%ZIPFILE% ^|^| exit 2
  >> %ZIPFILE%.scp ECHO exit
  ECHO. 2> %ZIPFILE%.log

  REM Execute script
  WinSCP.com /timeout=360 /script=%ZIPFILE%.scp /log=%ZIPFILE%.log
  IF ERRORLEVEL 1 (
    @ECHO WinSCP returned an error
    SET ERRORLEVELWAS=1
  ) else (
    DEL %ZIPFILE%.scp %ZIPFILE%.log
  )
  @ECHO %DATE% %TIME%: Completed uploading to %%S
)

IF %ERRORLEVELWAS%==0 (
  ECHO All Uploads were successful
  @REM If upload was successful move Zip to Archive
  @REM and replace with an empty file 
  IF NOT EXIST %ZIPDIR%\Archive (
    MKDIR %ZIPDIR%\Archive
  )
  MOVE %ZIPPATH% %ZIPDIR%\Archive
  ECHO. 2> %ZIPPATH%
)

POPD

@ECHO %DATE% %TIME%

@REM Set NOPAUSE to a command to execute instead of PAUSE
@REM For example, SET NOPAUSE=REM
IF DEFINED NOPAUSE (
  @REM To ensure non-empty parenthesis
  %NOPAUSE%
) ELSE (
  PAUSE
)

EXIT /B %ERRORLEVELWAS%

@REM vim:sw=2:ai:ic:expandtab
