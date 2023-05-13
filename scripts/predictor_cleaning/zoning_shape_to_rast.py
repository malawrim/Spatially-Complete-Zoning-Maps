#!/usr/bin/env python3

"""
This script imports all zoning maps (created using scripts in zone_data_cleaning folder) into GRASS mapset
and converts them to 30-m rasters with the same name as the shapefile.

Usage: Run using built-in GRASS GIS python editor other accepted IDE. 
See https://grasswiki.osgeo.org/wiki/GRASS_and_Python and https://grasswiki.osgeo.org/wiki/Tools_for_Python_programming

Written using Python 3 and GRASS 8
"""

import os
import glob

import grass.script as gs

# See zoning_inputs.py for loading predictors into GRASS
# file location of all input zoning maps
file_path = os.path.join(os.getcwd(), "data_cleaning", "shapefiles")
# empty array to be filled with names of zoning maps added to GRASS mapset
layers = []


# load all files in from R
def main():
    files = glob.glob(file_path + "\\*.shp")
    for f in files:
        try:
            gs.run_command("v.import", overwrite=True, input=f)
            layers.append(f.split(file_path + "\\")[1].split(".shp")[0] + "@PERMANENT")
        except:
            with open(os.path.join(file_path, "output.txt"), "a") as out:
                print(f, file=out)


# convert vector to raster
def v_to_rast():
    for map in layers:
        out = map.split("@")[0] + "_rast"

        gs.run_command(
            "v.to.rast",
            overwrite=True,
            input=map,
            type="area",
            output=out,
            use="attr",
            attribute_column="ZnID",
            label_column="ZnCl",
            rgb_column="Color",
        )


if __name__ == "__main__":
    main()
