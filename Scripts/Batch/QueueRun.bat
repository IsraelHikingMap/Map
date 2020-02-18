@REM Implement a queue of Maperitive and MOBAC jobs for
@REM Israel Hiking and Biking - IsraelHiking.osm.org.il
@REM
@REM Usage: QueueRun <script>
@REM
@REM where <script> is a .py, .mscript or a .bat script, without any 
@REM directory path.
@REM The scripts are taken from the Scripts\Maperipy, Scripts\Maperitive,
@REM and the MOBAC installation directory, respectively.
@REM
@REM General commands, optionally with arguments, can also be used.
@REM
@REM Scripts or commands will not be placed in the queue if the queue
@REM already has a job with the same name, ignoring path and extension.
@REM
@REM Copyright 2017 Zeev Stadler CC BY-NC-SA 3.0
@REM https://creativecommons.org/licenses/by-nc-sa/3.0/
@ECHO OFF

SETLOCAL ENABLEDELAYEDEXPANSION

@REM Add this script's dircetory to the path
PATH %~dp0;%PATH%
@REM Add Maperitive and Mobile Atlas Creator to the path
SET PROGDIRS=%programfiles%;%programfiles(x86)%;%~d0%programfiles:~2%;%~d0%programfiles(x86):~2%
FOR %%p in (Maperitive "Mobile Atlas Creator") DO IF NOT "%%~dpn$PROGDIRS:p"=="" PATH %%~dpn$PROGDIRS:p;!PATH!
SET PROGDIRS=

@REM Script is located at IsraelHiking\Scripts\Batch 
PUSHD %~dp0\..\..
SET ISRAELHIKING=%CD%

CALL .\Scripts\Batch\WaitInQueue "%ISRAELHIKING%\Cache\Queue" "%~n1"
IF ERRORLEVEL 1 EXIT /b %ERRORLEVEL%

IF "%~x1"==".py" (
  START "" /ABOVENORMAL /WAIT Maperitive -exitafter "%ISRAELHIKING%\Scripts\Maperipy\%~1"
) ELSE IF "%~x1"==".mscript" (
  START "" /ABOVENORMAL /WAIT Maperitive -exitafter "%ISRAELHIKING%\Scripts\Maperitive\%~1"
) ELSE (
  IF NOT "%~dp$PATH:1"=="" CD "%~dp$PATH:1"
  START "" /ABOVENORMAL /WAIT cmd.exe /C %*
)

IF EXIST "%QUEUEFILE%" DEL "%QUEUEFILE%"
@ECHO Job completed at %DATE% %TIME%. 1>&2
TIMEOUT 5
EXIT /b

@REM vim:sw=2:ai:ic:expandtab
