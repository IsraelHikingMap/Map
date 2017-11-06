@REM WaitInQueue - Wait in queue for mutual exclusion
@REM
@REM WaitInQueue - Wait in queue for mutual exclusion
@REM.
@REM Usage: CALL "%~n0" QueueDirectory [JobName]
@REM.
@REM Only one entry per JobName, if provided, is allowed.
@REM If JobName is already in the queue or was removed from the queue,
@REM exit with ERRORLEVEL 2
@REM.
@REM When the mutual exclusion is no longer needed, the caller may
@REM DEL %%QUEUEFILE%%
@REM
@REM Copyright 2017 Zeev Stadler CC BY-NC-SA 3.0
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
  IF EXIST "%QDIR%"\* GOTO Enqueue
  @ECHO Error: "%QDIR%" is not a direcctory. 1>&2
  @ECHO.
)
EXIT /B 1

:Enqueue
CALL :QueueHead
SET PID=
FOR /F "USEBACKQ SKIP=1 TOKENS=1*" %%p IN (
      `wmic process where "CommandLine like '%COMSPEC:\=\\%%%%RANDOM%%%'" get ParentProcessID`
      ) DO IF NOT "%%q"=="" (
  @REM Real output line
  IF "%%p"=="%HEADPID%" (
    @ECHO Process %%p already in queue. 1>&2
    EXIT /B 2
  )
  SET PID=%%p-%JOB%
)
IF NOT DEFINED PID (
  @ECHO Error: Could not determine the Process ID of the current script.  Exiting. 1>&2
  EXIT /B 1
)

IF NOT "%JOB%"=="" (
  DIR /B "%QDIR%"|FINDSTR /R /C:"^[0-9]*\-%JOB%$" >NUL
  IF NOT ERRORLEVEL 1 (
    @ECHO "%JOB%" job already in queue. 1>&2
    EXIT /B 2
  )
)

@REM Create a file in the queue directory
CALL >"%QDIR%\%PID%" && ICACLS "%QDIR%\%PID%" /GRANT BUILTIN\Users:F >NUL
IF ERRORLEVEL 1 (
  @ECHO Error: Cannot add job to queue. 1>&2
  EXIT /B %ERRORLEVEL%
)

@ECHO Entering queue at %DATE% %TIME%. 1>&2
TIMEOUT /T 1 >NUL
:CheckQueue
CALL :QueueHead
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEL%
IF "%ABORT%" == "TRUE" (
  @ECHO Job was removed from the queue. 1>&2
  ENDLOCAL
  EXIT /B 2
)
IF "%HEADPID%-%HEADJOB%"=="%PID%" (
  @ECHO Top of queue reached at %DATE% %TIME%. 1>&2
  ENDLOCAL
  SET QUEUEFILE="%QDIR%\%PID%"
  EXIT /B 0
)

@REM Wait in queue
TIMEOUT /T 360 >NUL
@REM Handle a break
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEL%
GOTO CheckQueue

:QueueHead
SET HEADPID=
SET ABORT=TRUE
FOR /F "USEBACKQ TOKENS=1* DELIMS=-" %%p IN (`DIR "%QDIR%" /O-D /B`) DO (
  @REM Head of queue is seen last
  SET HEADPID=%%p
  SET HEADJOB=%%q
  IF "!HEADPID!-!HEADJOB!"=="%PID%" (
    @REM This job is still in the queue
    SET ABORT=FALSE
  ) ELSE (
    TASKLIST /FO TABLE /NH /FI "PID eq !HEADPID!" | FINDSTR "!HEADPID!" >NUL
    IF ERRORLEVEL 1 (
      @REM Process !HEADPID! is no longer running, remove from queue
      DEL "%QDIR%\!HEADPID!-!HEADJOB!"
      IF EXIST "%QDIR%\!HEADPID!-!HEADJOB!" (
        @ECHO Cannot remove "!HEADPID!-!HEADJOB!" job from "%~1" queue. 1>&2
        EXIT /B 1
      )
    )
  )
)
GOTO :EOF

@REM vim:sw=2:ai:ic:expandtab
