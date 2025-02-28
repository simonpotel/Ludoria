#!/bin/bash

set -e

mkdir -p builds/configs

pip install pyinstaller

echo "Building client..."
pyinstaller --onefile --name client \
    --distpath builds \
    --workpath builds/temp \
    --specpath builds/temp \
    client.py

echo "Building server..."
pyinstaller --onefile --name server \
    --distpath builds \
    --workpath builds/temp \
    --specpath builds/temp \
    start_server.py

echo "Copying configuration files..."
cp configs/quadrants.json builds/configs/
cp configs/server.json builds/configs/

rm -rf builds/temp
rm -rf *.spec

echo "Build completed successfully!"
echo "Executables and configs are available in the builds directory:"
echo "- builds/client.exe (or client on Linux)"
echo "- builds/server.exe (or server on Linux)"
echo "- builds/configs/quadrants.json"
echo "- builds/configs/server.json" 