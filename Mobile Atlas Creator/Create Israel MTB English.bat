@ECHO OFF
REM Create an atlas with MOBAC and copy to Google Drive and/or Dropbox (if installed)
REM
REM File name MUST be of the form "Create <Full Atlas Name>.bat", such as "Create Israel Hiking.bat"
REM where the Atlas name and the Profile name must also be the same!
REM
REM As such, a hard link to this file, with a different name will create a different atlas.
REM Moreover, updates to one file will be reflected in all files, and a deletion
REM of any one file will not impact the others.
REM For more information:
REM http://devtidbits.com/2009/09/07/windows-file-junctions-symbolic-links-and-hard-links/
REM
REM To create a hard link from a command prompt, use:
REM 	mklink /h "Create <new Atlas Name>.bat" "Create <existing Atlas Name>.bat"
REM

PUSHD "%~dp0"

REM Set the AtlasName
REM

SETLOCAL
SET ATLASNAME=%~n0
SET ATLASNAME=%ATLASNAME:~7%

IF NOT EXIST "logs\*" (
    MKDIR logs
)

@REM Redirect outrout to log file

@REM FOR DEBUG CALL :MAIN > "logs\%ATLASNAME%-%DATE:~-4%-%DATE:~4,2%-%DATE:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log" 2>&1
CALL :MAIN > logs\"%ATLASNAME%.log" 2>&1

POPD

EXIT /B

@REM ===================
:MAIN
@REM ===================

TITLE Creating Atlas: %ATLASNAME%

REM Wait for tilestore unlock
@REM
@REM http://stackoverflow.com/questions/10518151/how-to-check-in-command-line-if-a-given-file-or-directory-is-locked-used-by-any/10520609#10520609
@REM

IF NOT EXIST "tilestore\" MKDIR tilestore
:CheckLock
2>NUL (2>>"tilestore\lock" (CALL )) || ( (ECHO Another MOBAC is running... ) && TIMEOUT > NUL: /T 300 /NOBREAK  && GOTO CheckLock)

@REM Add 7-Zip directories to path
PATH %PATH%;%~d0\Program Files\7-Zip;%~d0\Program Files\7-ZipPortable\App\7-Zip

SET ATLASDIR=%~d0\Users\%USERNAME%\Documents\Maps\OruxMaps.tmp\%ATLASNAME%
IF EXIST "%ATLASDIR%\" (
    RMDIR /S /Q "%ATLASDIR%"
    TIMEOUT > NUL: /T 3 /NOBREAK
)

@ECHO %DATE% %TIME%: Creating Atlas: %ATLASNAME%
"java" -Xms512m -Xmx512m -jar Mobile_Atlas_Creator.jar create "%ATLASNAME%" "%ATLASDIR%"

@ECHO %DATE% %TIME%

SET DESTDIR=%ATLASNAME: English=%
IF "%DESTDIR%"=="%ATLASNAME%" (
    SET LANG=Hebrew
) ELSE (
    SET LANG=English
)
SET ZIPNAME=%DESTDIR: =%.zip
IF ERRORLEVEL 1 GOTO :EOF

@REM Copy the new map
PUSHD "%ATLASDIR%"
@REM Atlas internal name is unknown
FOR /D %%A IN ( * ) DO (
    SET ATLASSUBDIR="%%~A"
)
@REM Create a zip file of the map
@ECHO Creatting %ZIPNAME%
"7z.exe" a -tzip -mx9 "%ZIPNAME%" *
FOR  %%D IN ( %HOMEDRIVE%%HOMEPATH% ) DO (
    FOR %%P IN ( "M:\%LANG%\Oruxmaps" "%%~D\Google Drive\oruxmaps\oruxmaps mapfiles" "%%~D\Dropbox\Folder Sharing\dropsync\oruxmaps\mapfiles" "%%~D\Dropbox\Folder Sharing\GF\mapfiles" "%%~D\Dropbox\Public\Israel Hiking\oruxmaps mapfiles" ) DO (
	IF EXIST "%%~P\%DESTDIR%\" (
	    @ECHO Updating "%%~P\%DESTDIR%"
	    XCOPY /Y /S %ATLASSUBDIR% "%%~P\%DESTDIR%"
	)
	IF EXIST "%%~P\%ZIPNAME%" (
	    @ECHO Updating %%~P\%ZIPNAME%
	    @ECHO COPY /Y "%ZIPNAME%" "%%~P"
	    COPY /Y "%ZIPNAME%" "%%~P"
	)
    )
)
POPD

RMDIR /Q/S "%ATLASDIR%"

@ECHO %DATE% %TIME%: Completed Creating Atlas: %ATLASNAME%

ENDLOCAL

@REM	vim: autoindent shiftwidth=4
