#!/bin/bash

echo "Fetching files..."

for file in ../Data/*map.nc
do
    echo "Found file: $file"
    echo "Interpolating $file"
    python concate_maps.py "$file"
    echo "Done"
done