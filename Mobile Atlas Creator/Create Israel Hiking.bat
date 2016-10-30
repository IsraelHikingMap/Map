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

%~d0
CD "%~dp0"

REM Wait for tilestore unlock
REM
REM http://stackoverflow.com/questions/10518151/how-to-check-in-command-line-if-a-given-file-or-directory-is-locked-used-by-any/10520609#10520609
REM

:CheckLock
2>NUL (2>>"tilestore\lock" (CALL )) || ( (ECHO Another MOBAC is running... ) && TIMEOUT /T 300 /NOBREAK  && GOTO CheckLock)

REM Add 7-Zip directories to path
SETLOCAL
PATH %PATH%;%~d0\Program Files\7-Zip;%~d0\Program Files\7-ZipPortable\App\7-Zip

REM Set the AtlasName
REM

SET ATLASNAME=%~n0
SET ATLASNAME=%ATLASNAME:~7%
TITLE Creating Atlas: %ATLASNAME%

SET ATLASDIR=%~d0\Users\%USERNAME%\Documents\Maps\OruxMaps\%ATLASNAME%
IF EXIST "%ATLASDIR%\" (
    RMDIR /S /Q "%ATLASDIR%"
    TIMEOUT /T 3 /NOBREAK
)

@ECHO %DATE% %TIME%: Creating Atlas: %ATLASNAME%
"java" -Xms64m -jar Mobile_Atlas_Creator.jar create "%ATLASNAME%" "%ATLASDIR%"

@ECHO %DATE% %TIME%

@ECHO OFF
IF NOT ERRORLEVEL 1 (
    @REM Copy the new map
    PUSHD "%ATLASDIR%"
    @REM Atlas internal name is unknown
    FOR /D %%A IN ( * ) DO (
	SET ATLASSUBDIR=%%A
    )
    @REM Create a zip fille of the map
    @ECHO Creatting %ATLASNAME: =%.zip
    "7z.exe" a -tzip -mx9 "%ATLASNAME: =%.zip" *
    FOR  %%D IN ( %HOMEDRIVE%%HOMEPATH% D:%HOMEPATH% ) DO (
        FOR %%P IN ( "%%~D\Google Drive\oruxmaps\oruxmaps mapfiles" "%%~D\Dropbox\Folder Sharing\dropsync\oruxmaps\mapfiles" "%%~D\Dropbox\Folder Sharing\GF\mapfiles" "%%~D\Dropbox\Public\Israel Hiking\oruxmaps mapfiles" "%%~D\Documents\GitHub\IsraelHiking\Map\Site\Oruxmaps\mapfiles" ) DO (
            IF EXIST "%%~P\%ATLASNAME%\" (
                @ECHO Updating %%~P\%ATLASNAME%
		XCOPY /D /Y /S %ATLASSUBDIR% "%%~P\%ATLASNAME%"
            )
	    IF EXIST "%%~dpP"\%ATLASNAME: =%.zip (
		@ECHO Updating %%~dpP%ATLASNAME: =%.zip
		@ECHO COPY /Y "%ATLASNAME: =%.zip" %%~dpP
		COPY /Y "%ATLASNAME: =%.zip" "%%~dpP"
	    )
        )
    )
    POPD
)

@ECHO %DATE% %TIME%: Completed Creating Atlas: %ATLASNAME%

ENDLOCAL

@REM Set NOPAUSE to a command to execute instead of PAUSE
@REM For example, SET NOPAUSE=REM
IF DEFINED NOPAUSE (
    @REM To ensure non-empty parenthesis
    %NOPAUSE%
) ELSE (
    PAUSE
)
@ECHO ON

@REM	vim: autoindent shiftwidth=4
