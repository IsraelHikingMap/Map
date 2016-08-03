@TITLE Pull updates from remote Git repository

@REM @ECHO OFF
@SETLOCAL ENABLEDELAYEDEXPANSION

@ECHO Check if Maperitive is running
@TASKLIST /FI "IMAGENAME eq Maperitive.exe" | find "Maperitive.exe" && (
  @ECHO ==^> No Git pull
  @GOTO :END
)

@REM Script is located at IsraelHiking\Scripts\Batch 
@PUSHD %~dp0\..\..
@SET ISRAELHIKING=%CD%
@CD %ISRAELHIKING%

@FOR /D %%P IN ( %LOCALAPPDATA%\GitHub\PortableGit_* ) DO @SET PATH=!PATH!;%%P

git-cmd.exe git pull --verbose ^& EXIT

:END
EXIT
