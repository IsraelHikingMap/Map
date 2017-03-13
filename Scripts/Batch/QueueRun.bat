
REM Implement a queue of Maperitive and MOBAC jobs for
REM Israel Hiking and Biking - IsraelHuking.osm.org.il
REM
REM Usage: [Start] QueueRun <script>
REM
REM where <script> is a .py, .mscript or a Create*.bat script, without any 
REM absolute or relative directory path. 
REM The scripts are taken from the Scripts\Maperipy, Scripts\Maperitive,
REM and the MOBAC installation directory, respectively.

SETLOCAL ENABLEDELAYEDEXPANSION

@REM Add this script's dircetory to the path
PATH %PATH%;%~dp0
@REM Add Maperitive and Mobile Atlas Creator to the path
SET PROGDIRS=%programfiles%;%programfiles(x86)%;%~d0%programfiles:~2%;%~d0%programfiles(x86):~2%
FOR %%p in (Maperitive "Mobile Atlas Creator") DO IF NOT "%%~dpn$PROGDIRS:p"=="" PATH !PATH!;%%~dpn$PROGDIRS:p
SET PROGDIRS=

@REM Script is located at IsraelHiking\Scripts\Batch 
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%

CALL .\Scripts\Batch\WaitInQueue "%ISRAELHIKING%\Cache\Queue" "%~n1"
IF ERRORLEVEL 1 EXIT

IF "%~x1"==".py" (
  Maperitive -exitafter "%ISRAELHIKING%\Scripts\Maperipy\%~1"
) ELSE IF "%~x1"==".mscript" (
  Maperitive -exitafter "%ISRAELHIKING%\Scripts\Maperitive\%~1"
) ELSE (
  IF NOT "%~dp$PATH:1"=="" CD "%~dp$PATH:1"
  IF "%~x1"==".bat" (
    CALL %*
  ) ELSE (
    %*
  )
)

DEL %QUEUEFILE%
TIMEOUT 5
EXIT
@REM vim:sw=2:ai:ic:expandtab
