#!/usr/bin/env python3
"""
This script imports all predicted zoning maps from random forest model.
Accuracy maps are computed and can be aggregated to county or 3-km grid. 

Usage: Run using built-in GRASS GIS python editor other accepted IDE. 
See https://grasswiki.osgeo.org/wiki/GRASS_and_Python and https://grasswiki.osgeo.org/wiki/Tools_for_Python_programming

Written using Python 3 and GRASS 8
"""

import grass.script as gs
import os

# set this flag for county or grid results
# scale = "county"
scale = "grid"

# list of results to read and maps to make
model = [
    "within_core",
    "within_sub",
    "between_core_r1",
    "between_core_r2",
    "between_core_r3",
    "between_core_r4",
    "between_core_r5",
    "between_core_r6",
    "between_core_r7",
    "between_core_r8",
    "between_core_r9",
    "between_core_r10",
    "between_core_r11",
    "between_core_r12",
    "between_core_r13",
    "between_core_r14",
    "between_core_r15",
    "between_sub_r1",
    "between_sub_r2",
    "between_sub_r3",
    "between_sub_r4",
    "between_sub_r5",
    "between_sub_r6",
    "between_sub_r7",
    "between_sub_r8",
    "between_sub_r9",
    "between_sub_r10",
    "between_sub_r11",
    "between_sub_r12",
    "between_sub_r13",
    "between_sub_r14",
    "between_sub_r15",
]

file_name = "_accuracy_county.shp"
map_name = "North_Carolina_State_and_County_Boundary_Polygons@PERMANENT"

if scale == "grid":
    file_name = "_accuracy_grid_3km.shp"
    map_name = "NC_grid_3km@PERMANENT"

zone_file_sub = "sub_district_observed_zones@PERMANENT"
zone_file_core = "core_district_observed_zones@PERMANENT"

file_path = os.getcwd()


def main():
    # Assumes file system with folder for each model (see model list above) and a predicted layer inside named "pred_zones.tif"
    for m in model:
        zone_file = zone_file_core
        rules = os.path.join(file_path, "reclass", "accuracy_reclass.txt")
        if m.split("_")[1] == "sub":
            zone_file = zone_file_sub

        in_file = "pred_zones.tif"
        out_file = "pred_" + m
        # import layer
        gs.run_command(
            "r.import",
            input=os.path.join(file_path, m, in_file),
            output=out_file,
            overwrite=True,
        )

        # find difference between predicted and observed
        in_file = out_file
        out_file = "acc_" + m
        expression = out_file + " = " + zone_file + " - " + in_file
        gs.raster.mapcalc(exp=expression, overwrite=True)

        # reclassify to have 0 where predicted and observe match and 1 where they do not
        in_file = out_file
        out_file = in_file + "_reclass"
        gs.run_command(
            "r.reclass",
            input=in_file,
            output=out_file,
            rules=rules,
            overwrite=True,
        )
        # count the number of misclassifcations within area of interest (grid or county; set using scale parameter)
        out_file = m + file_name
        out_path = os.path.join(file_path, m, out_file)
        in_file = "acc_" + m + "_reclass"
        gs.run_command(
            "v.rast.stats",
            map=map_name,
            flags="c",
            raster=in_file,
            column_prefix="a",
            method="number,sum",
        )
        # Create emtpy column used to store percent error
        gs.run_command(
            "v.db.addcolumn",
            map=map_name,
            columns="per_error double precision",
        )
        # Calculate percent error
        gs.run_command(
            "v.db.update",
            map=map_name,
            column="per_error",
            query_column="a_sum / (a_number + a_sum)",
        )
        # Export result
        gs.run_command(
            "v.out.ogr",
            overwrite=True,
            input=map_name,
            output=out_path,
            format="ESRI_Shapefile",
        )
        # Export result as table
        gs.run_command(
            "db.out.ogr",
            overwrite=True,
            input=map_name,
            output=os.path.join(file_path, m, (m + "_acc_county.csv")),
            format="CSV",
        )
        # Clean up "scale" vector (grid or county) for next loop
        gs.run_command(
            "v.db.dropcolumn",
            map=map_name,
            columns="a_number,a_sum,per_error",
        )


if __name__ == "__main__":
    main()
