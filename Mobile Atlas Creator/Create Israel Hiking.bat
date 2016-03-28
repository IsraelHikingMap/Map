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
cd "%~dp0"

REM Wait for tilestore unlock
REM
REM http://stackoverflow.com/questions/10518151/how-to-check-in-command-line-if-a-given-file-or-directory-is-locked-used-by-any/10520609#10520609
REM

:CheckLock
2>nul (2>>"tilestore\lock" (call )) || ( (ECHO Another MOBAC is running... ) && timeout /t 300 /NOBREAK  && GOTO CheckLock)

REM Add porobable Java bin directories to path
SETLOCAL
path %PATH%;%ProgramFiles%\Java\jre7\bin
path %PATH%;%ProgramFiles%\Java\jre6\bin
path %PATH%;%ProgramFiles% (x86)\Java\jre7\bin
path %PATH%;%ProgramFiles% (x86)\Java\jre6\bin

REM Set the AtlasName
REM

SET ATLASNAME=%~n0
SET ATLASNAME=%ATLASNAME:~7%
TITLE Creating Atlas: %ATLASNAME%

SET ATLASDIR=atlases\%ATLASNAME%
IF exist "%ATLASDIR%"\. rmdir /s /q "%ATLASDIR%"

@echo %DATE% %TIME%
"java" -Xms64m -jar Mobile_Atlas_Creator.jar create "%ATLASNAME%" "%ATLASDIR%"

@echo %DATE% %TIME%
IF NOT ERRORLEVEL 1 (
    FOR  %%D in ( %HOMEDRIVE%%HOMEPATH% %~d0%HOMEPATH% D:%HOMEPATH% ) do (
        FOR %%P in ( "%%D\Google Drive\oruxmaps\oruxmaps mapfiles" "%%D\Dropbox\Folder Sharing\dropsync\oruxmaps\mapfiles" "%%D\Dropbox\Folder Sharing\GF\mapfiles" "%%D\Dropbox\Public\Israel Hiking\oruxmaps mapfiles" ) do (
            IF exist %%P\"%ATLASNAME%" (
                @ECHO Updating atlas "%ATLASNAME%" at %%P
                XCOPY /D /Y /S "%ATLASDIR%\%ATLASNAME%" %%P\"%ATLASNAME%"
            )
        )
    )
)

@echo %DATE% %TIME%: Completed Creating Atlas: %ATLASNAME%

ENDLOCAL

if "%NOPAUSE%"=="TRUE" (
    @REM
) ELSE (
    PAUSE
)

@REM	vim: autoindent shiftwidth=4
