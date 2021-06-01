@TITLE Make link duplicates for MOBAC scripts

@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

PUSHD %~dp0

IF .%1==. (
  SET SOURCE=Create Israel Hiking.bat
) ELSE (
  SET SOURCE=%1
)

FOR %%L IN ("" " English") DO (
  FOR %%M IN (Hiking MTB) DO (
    FOR %%S IN ("" " 16") DO (
      SET TARGET=Create Israel %%~M%%~L%%~S.bat
      IF NOT "%SOURCE%"=="!TARGET!" (
	IF EXIST "!TARGET!". DEL "!TARGET!"
	MKLINK /H "!TARGET!" "%SOURCE%"
      )
    )
  )
)

POPD
