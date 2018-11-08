@REM WaitInQueue - Wait in queue for mutual exclusion
@REM.
@REM Usage: CALL "%~n0" QueueDirectory [JobName]
@REM.
@REM Only one entry per JobName, if provided, is allowed.
@REM If JobName is already in the queue or is removed while waiting 
@REM in the queue, exit with ERRORLEVEL 2
@REM.
@REM When the mutual exclusion is no longer needed, the caller may
@REM DEL "%QUEUEFILE%"
@REM Otherwise, other processes in the queue wait for the caller 
@REM process to terminate.
@REM
@REM Copyright 2017-2018 Zeev Stadler CC BY-NC-SA 3.0
@REM https://creativecommons.org/licenses/by-nc-sa/3.0/
@ECHO OFF

SETLOCAL ENABLEDELAYEDEXPANSION

SET QDIR=%~f1
SET JOB=%~2
IF NOT "%QDIR%"=="" (
  IF NOT EXIST "%QDIR%" (
    MKDIR "%QDIR%" && ICACLS "%QDIR%" /GRANT "BUILTIN\Users:(OI)(CI)(F)"
    IF ERRORLEVEL 1 (
      @ECHO Error: Cannot create queue directory "%QDIR%". 1>&2
      EXIT /B %ERRORLEVEL%
    )
  )
)
IF NOT EXIST "%QDIR%"\* (
  @ECHO Error: "%QDIR%" is not a direcctory. 1>&2
  @ECHO.
  EXIT /B 1
)

SET JOBID=
FOR /F "USEBACKQ SKIP=1 TOKENS=1*" %%p IN (
      `wmic process where "CommandLine like '%COMSPEC:\=\\%%%%RANDOM%%%'" get ParentProcessID`
      ) DO IF NOT "%%q"=="" (
  @REM Real output line
  IF EXIST "%QDIR%\%%p-*." (
    @ECHO Process %%p already in queue. 1>&2
    EXIT /B 2
  )
  SET JOBID=%%p-%JOB%
)
IF NOT DEFINED JOBID (
  @ECHO Error: Could not determine the Process ID of the current script.  Exiting. 1>&2
  EXIT /B 1
)

CALL :CleanQueue
IF NOT "%JOB%"=="" (
  DIR /B "%QDIR%"|FINDSTR /R /C:"^[0-9]*\-%JOB%$" >NUL
  IF NOT ERRORLEVEL 1 (
    @ECHO Job "%JOB%" is already in queue. 1>&2
    EXIT /B 2
  )
)

@REM Create a file in the queue directory
SET QUEUEFILE=%QDIR%\%JOBID%
CALL >"%QUEUEFILE%" && ICACLS "%QUEUEFILE%" /GRANT BUILTIN\Users:F >NUL
IF ERRORLEVEL 1 (
  @ECHO Error: Cannot add job to queue. 1>&2
  EXIT /B %ERRORLEVEL%
)

@ECHO Entering queue at %DATE% %TIME%. 1>&2
TIMEOUT /T 1 >NUL

:CheckQueue
@REM Find the head of the queue
FOR /F "USEBACKQ TOKENS=* DELIMS=*" %%h IN (`DIR "%QDIR%" /O-D /B`) DO (
  @REM Head of queue is seen last
  SET HEAD=%%h
)
IF "%HEAD%"=="%JOBID%" (
  @ECHO Top of queue reached at %DATE% %TIME%. 1>&2
  ENDLOCAL
  @REM Keep QUEUEFILE after ENDLOCAL
  SET QUEUEFILE=%QUEUEFILE%
  EXIT /B 0
)

@REM Wait in queue
TIMEOUT /T 300 >NUL
@REM Handle a break
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEL%
IF NOT EXIST "%QUEUEFILE%." (
  @ECHO Job was removed from the queue. 1>&2
  EXIT /B 2
)
CALL :CleanQueue
GOTO CheckQueue

:CleanQueue
@REM Remove inactive jobs from the queue
FOR /F "USEBACKQ TOKENS=1* DELIMS=-" %%p IN (`DIR "%QDIR%" /O-D /B`) DO (
  SET PID=%%p
  SET NAME=%%q
  TASKLIST /FO TABLE /NH /FI "PID eq !PID!" | FINDSTR "!PID!" >NUL
  IF ERRORLEVEL 1 (
    @REM Process !PID! is no longer running, remove from queue
    DEL "%QDIR%\!PID!-!NAME!"
    IF EXIST "%QDIR%\!PID!-!NAME!" (
      @ECHO Cannot remove "!PID!-!NAME!" job from "%~1" queue. 1>&2
      EXIT /B 1
    )
  )
)
GOTO :EOF

@REM vim:sw=2:ai:ic:expandtab
