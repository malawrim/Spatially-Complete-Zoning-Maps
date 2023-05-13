#!/usr/bin/env python3

import grass.script as gs
import os

grids = [
    "within_core",
    "within_sub",
    "between_sub_high",
    "between_sub_low",
    "between_core_low",
    "between_core_high",
]

# file_name = "_accuracy_grid_6km.shp"
# map_name = "NC_grid_6km@PERMANENT"

file_name = "_accuracy_county.shp"
map_name = "North_Carolina_State_and_County_Boundary_Polygons@PERMANENT"
file_path = "D:\\Zoning\\NC_analysis"


def main():
    #    for r in grids:
    for x in range(1, 16):
        # r = "between_core_r" + str(x)
        r = "between_sub_r" + str(x)
        zone_file = "NC_zones_no_protected_core@PERMANENT"
        rules = (
            "C:\\Users\\malawrim\\Documents\\GitHub\\Zoning\\accuracy_reclass_h0.txt"
        )
        if r.split("_")[1] == "sub":
            zone_file = "NC_zones_no_protected@PERMANENT"
            rules = "C:\\Users\\malawrim\\Documents\\GitHub\\Zoning\\accuracy_reclass_h2.txt"

        in_file = "pred_zones_redo.tif"
        out_file = "pred_" + r
        gs.run_command(
            "r.import",
            input=os.path.join(file_path, "results", r, in_file),
            output=out_file,
            overwrite=True,
        )

        in_file = out_file
        out_file = "acc_" + r
        expression = out_file + " = " + zone_file + " - " + in_file
        # gs.run_command("r.mapcalc", expression=expression, overwrite=True)
        gs.raster.mapcalc(exp=expression, overwrite=True)

        in_file = out_file
        out_file = in_file + "_reclass"
        gs.run_command(
            "r.reclass",
            input=in_file,
            output=out_file,
            rules=rules,
            overwrite=True,
        )

        out_file = r + file_name
        out_path = os.path.join(file_path, "results", r, out_file)
        in_file = "acc_" + r + "_reclass"
        gs.run_command(
            "v.rast.stats",
            map=map_name,
            flags="c",
            raster=in_file,
            column_prefix="a",
            method="number,sum",
        )
        gs.run_command(
            "v.db.addcolumn",
            map=map_name,
            columns="per_error double precision",
        )

        gs.run_command(
            "v.db.update",
            map=map_name,
            column="per_error",
            query_column="a_sum / (a_number + a_sum)",
        )

        gs.run_command(
            "v.out.ogr",
            overwrite=True,
            input=map_name,
            output=out_path,
            format="ESRI_Shapefile",
        )

        gs.run_command(
            "db.out.ogr",
            overwrite=True,
            input=map_name,
            output=os.path.join(file_path, "results", r, (r + "_acc_county.csv")),
            format="CSV",
        )

        gs.run_command(
            "v.db.dropcolumn",
            map=map_name,
            columns="a_number,a_sum,per_error",
        )


if __name__ == "__main__":
    main()
