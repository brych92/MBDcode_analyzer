@echo off
setlocal

rem Search for QGIS installation directory
for /d %%i in ("%ProgramFiles%\QGIS*") do (
    if exist "%%i\bin\qgis-bin.exe" (
        set QGIS_PATH=%%i
        goto :found
    )
)

:found

if not defined QGIS_PATH (
    echo QGIS installation not found.
    exit /b
)

rem Set paths to be added to PYTHONPATH
set PYTHONPATH=%QGIS_PATH%\apps\Python39;%QGIS_PATH%\apps\qgis\python;%PYTHONPATH%

rem Run your Python script or start Python interpreter
start /b pythonw MBDcode_analyzer.py

endlocal
