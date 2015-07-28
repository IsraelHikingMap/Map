@REM TODO SETLOCAL
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%

SET ZIPPATH="%~f1"
IF %ZIPPATH%=="" SET ZIPPATH="%ISRAELHIKING%\Output\TileUpdate.zip"

@REM The FOR statement gets one full path and extracts its filename
FOR %%Z in (%ZIPPATH%) DO (
  SET ZIPFILE="%%~nxZ"
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

@REM TODO @ECHO off
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
FOR %%S in (%SITES%) DO (
  @ECHO %DATE% %TIME%
  REM Generate temporary script to upload %ZIPFILE%
   > %ZIPFILE%.scp ECHO option batch abort
  >> %ZIPFILE%.scp ECHO option confirm off
  >> %ZIPFILE%.scp ECHO option reconnect 45
  >> %ZIPFILE%.scp ECHO open %%S
  >> %ZIPFILE%.scp ECHO cd
  >> %ZIPFILE%.scp ECHO put -resume -preservetime -transfer=binary %ZIPPATH% temp/
  >> %ZIPFILE%.scp ECHO call unzip -q -d ~/public_html/IsraelHiking -o ~/temp/%ZIPFILE% ^&^& echo unzip Completed successfully ^|^| echo unzip Failed
  >> %ZIPFILE%.scp ECHO call ~/script/post_transfer.sh ~/temp/%ZIPFILE% ^&^& echo File transfered successfully ^|^| echo File transfered failed
  >> %ZIPFILE%.scp ECHO exit

  REM Execute script
  @ECHO on
  "%ISRAELHIKING%\..\..\WinSCP\WinSCP.com" /timeout=360 /script=%ZIPFILE%.scp

  @REM Save ERRORLEVEL in a variable
  IF ERRORLEVEL 1 SET ERRORLEVELWAS=%ERRORLEVEL%

  @REM Delete temporary script
  DEL %ZIPFILE%.scp
)

IF %ERRORLEVELWAS%==0 echo All Uploads were successful
@REM Delete Zip file if upload and extraction was successful
@REM TODO ERRORLEVEL from WinSCP is unreliable. Do not delete the zip file
@REM TODO IF %ERRORLEVELWAS%==0 echo. 2> %ZIPPATH%

POPD

@ECHO %DATE% %TIME%

@REM Set NOPAUSE to a command to execute instead of PAUSE
@REM For example, SET NOPAUSE=REM
IF DEFINED NOPAUSE (
  %NOPAUSE%
  @REM Check real ERRORLEVEL of the above command
  IF ERRORLEVEL 1 EXIT /B %ERRORLEVEL%
) ELSE (
  PAUSE
)

EXIT /B %ERRORLEVEL%

@REM vim:sw=2:ai:ic:expandtab
