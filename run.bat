@echo off
setlocal

rem Search for QGIS installation directory
for /d %%i in ("%ProgramFiles%\QGIS*") do (
    echo Checking directory: %%i
    if exist "%%i\bin\qgis-bin.exe" (
        set QGIS_PATH=%%i
        echo Found "%%i\bin\qgis-bin.exe"
	goto :found
    )
    if exist "%%i\bin\qgis-ltr-bin.exe" (
        set QGIS_PATH=%%i
        echo Found "%%i\bin\qgis-ltr-bin.exe"
	goto :found
    )
)


:found

if not defined QGIS_PATH (
    echo QGIS installation not found.
    pause
exit /b
)

set PYTHONPATH=%QGIS_PATH%\apps\Python39;%QGIS_PATH%\apps\qgis\python;%QGIS_PATH%\apps\qgis-ltr\python;%QGIS_PATH%\apps\Python39\Lib\site-packages;
echo PYTHONPATH set to "%PYTHONPATH%"

set Path=%QGIS_PATH%\apps\Python39
echo Path set to "%Path%"

start /b pythonw MBDcode_analyzer.py

rem python MBDcode_analyzer.py

rem pause