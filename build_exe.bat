@echo off
echo Building FGO Strategy Room Executable...

pyinstaller --noconfirm --onefile --windowed --name "FGO_Strategy_Room" ^
 --add-data "templates;templates" ^
 --add-data "static;static" ^
 --add-data "fgo_full_data_jp.db;." ^
 --hidden-import=engineio.async_drivers.threading ^
 app.py

echo Build complete! Executable is in the dist folder.
pause
