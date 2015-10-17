@echo off
REM maketiles.bat

python makeTiles.py 8 res/tiles.rc res/tiles
python makeTiles.py 16 res/tiles.rc res/tiles
python makeTiles.py 32 res/tiles.rc res/tiles
REM python makeTiles.py 64 res/tiles.rc res/tiles