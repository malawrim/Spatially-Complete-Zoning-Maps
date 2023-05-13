#!/usr/bin/env python3

import grass.script as gs
import glob

# run bash script rural_counties_GRASS.sh
# or run gs.run_command('v.import', input='C:\RA\Zoning\Raleigh_Prototype_Zoning\Tigers_Road_State_2016\37\tl_2016_37_roads.shp' output='roads') for all files
layers = [
    "Brunswick_County@PERMANENT",
    "Buncombe_County@PERMANENT",
    "Carteret_County@PERMANENT",
    "Chatham_County@PERMANENT",
    "Chowan_County@PERMANENT",
    "Cleveland_County@PERMANENT",
    "Cleveland_County_Res@PERMANENT",
    "Cumberland_County@PERMANENT",
    "Currituck_County@PERMANENT",
    "Dare_County@PERMANENT",
    "Davidson_County@PERMANENT",
    "Davie_County@PERMANENT",
    "Durham_County@PERMANENT",
    "Forsyth_County@PERMANENT",
    "Gaston_County@PERMANENT",
    "Guilford_County@PERMANENT",
    "Guilford_County_subdivide@PERMANENT",
    "Harnett_County@PERMANENT",
    "Haywood_County@PERMANENT",
    "Henderson_County@PERMANENT",
    "Iredell_County@PERMANENT",
    "Johnston_County@PERMANENT",
    "Lee_County@PERMANENT",
    "Lincoln_County@PERMANENT",
    "Mecklenburg_County@PERMANENT",
    "New_Hanover_County@PERMANENT",
    "Onslow_County@PERMANENT",
    "Orange_County@PERMANENT",
    "Pitt_County@PERMANENT",
    "Randolph_County@PERMANENT",
    "Rockingham_County@PERMANENT",
    "Rowan_County@PERMANENT",
    "Union_County@PERMANENT",
    "Wake_County@PERMANENT",
    "Wayne_County@PERMANENT",
    "Wilkes_County@PERMANENT",
    "Wilson_County@PERMANENT",
    "Yadkin_County@PERMANENT",
    "andrews@PERMANENT",
    "angier@PERMANENT",
    "apex@PERMANENT",
    "asheville@PERMANENT",
    "belmont@PERMANENT",
    "boone@PERMANENT",
    "boonville@PERMANENT",
    "carrboro@PERMANENT",
    "cary@PERMANENT",
    "chapel_hill@PERMANENT",
    "charlotte@PERMANENT",
    "cherryville@PERMANENT",
    "concord@PERMANENT",
    "east_bend@PERMANENT",
    "edenton@PERMANENT",
    "fayetteville@PERMANENT",
    "fletcher@PERMANENT",
    "garner@PERMANENT",
    "gastonia@PERMANENT",
    "goldsboro@PERMANENT",
    "greenville@PERMANENT",
    "harrisburg@PERMANENT",
    "hendersonville@PERMANENT",
    "high_point@PERMANENT",
    "hillsborough@PERMANENT",
    "holly_springs@PERMANENT",
    "knightdale@PERMANENT",
    "mooresville@PERMANENT",
    "morehead@PERMANENT",
    "morrisville@PERMANENT",
    "mt__pleasant@PERMANENT",
    "murphy@PERMANENT",
    "nags_head@PERMANENT",
    "newport@PERMANENT",
    "north_wilkesboro@PERMANENT",
    "pittsboro@PERMANENT",
    "raleigh@PERMANENT",
    "siler_city@PERMANENT",
    "statesville@PERMANENT",
    "troutman@PERMANENT",
    "wake_forest@PERMANENT",
    "wendell@PERMANENT",
    "wilkesboro@PERMANENT",
    "wilmington@PERMANENT",
    "wilson@PERMANENT",
    "yadkinville@PERMANENT",
    "zebulon@PERMANENT",
]

# load all files in from R
def main():
    # all_files = glob.glob("D:\Raleigh_Prototype_Zoning\data_cleaning\shapefiles\*.shp")
    files = [
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wadesboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Anson_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Brunswick_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\asheville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Buncombe_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\harrisburg.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\concord.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\mt._pleasant.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\morehead.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Carteret_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\newport.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\siler_city.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\pittsboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Chatham_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\andrews.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\murphy.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\edenton.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Chowan_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Cleveland_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\fayetteville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Cumberland_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Currituck_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\nags_head.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Dare_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Davidson_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Davie_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Durham_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Forsyth_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Gaston_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\belmont.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\gastonia.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\high_point.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Guilford_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Harnett_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Haywood_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\hendersonville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Henderson_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\fletcher.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\troutman.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\statesville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Iredell_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\mooresville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Johnston_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Lee_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Lincoln_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Mecklenburg_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\charlotte.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wilmington.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\New_Hanover_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Onslow_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\carrboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Orange_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\chapel_hill.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\hillsborough.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\greenville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Pitt_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Randolph_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Rockingham_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Rowan_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Union_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Wake_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\zebulon.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\morrisville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wendell.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wake_forest.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\raleigh.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\cary.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\knightdale.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\angier.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\holly_springs.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\apex.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\garner.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\boone.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Wayne_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\goldsboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wilkesboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Wilkes_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\north_wilkesboro.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Wilson_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\wilson.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\east_bend.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\boonville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\jonesville.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\Yadkin_County.shp",
        "D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\yadkinville.shp",
    ]
    for f in files:
        try:
            gs.run_command("v.import", overwrite=True, input=f)
        except:
            with open(
                "D:\Raleigh_Prototype_Zoning\data_cleaning\shapefiles\output.txt", "a"
            ) as out:
                print(f, file=out)

## Guilford county needs to snap so all polygons are included
# v.import input=D:\Raleigh_Prototype_Zoning\data_cleaning\shapefiles\Guilford_County.shp output=Guilford_County snap=0.0001 --overwrite
# convert vector to raster
def v_to_rast():
    for map in layers:
        out = map.split("@")
        out = out[0] + "_rast"

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


files = []
# If I have already converted to rast once but found an issue in a single county can use this fuction
def v_to_rast_redo():
    for map in files:
        input = map.split("D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\")[
            1
        ].split(".shp")[0]
        out = input + "_rast"
        input = input + "@PERMANENT"
        gs.run_command(
            "v.to.rast",
            overwrite=True,
            input=input,
            type="area",
            output=out,
            use="attr",
            attribute_column="ZnID",
            label_column="ZnCl",
            rgb_column="Color",
        )


# Set color table of vector data
def set_color_table():
    # gs.run_command("g.list", flags="m", type="vector")
    for map in layers:
        gs.run_command(
            "v.colors",
            map=map,
            use="attr",
            column="ZnID",
            rules="C:/RA/Zoning/Raleigh_Prototype_Zoning/scripts/zone_color_rules_NC.txt",
        )


# Set raster color table of vector data
def set_rast_color_table():
    # gs.run_command("g.list", flags="m", type="vector")
    for map in layers:
        map = map.split("@")[0] + "_rast@PERMANENT"

        gs.run_command(
            "r.colors",
            map=map,
            rules="C:\\RA\\Zoning\\Raleigh_Prototype_Zoning\\scripts\\zone_color_rules_NC.txt",
        )


def set_color_redo():
    for map in files:
        input = (
            map.split("D:\\Raleigh_Prototype_Zoning\\data_cleaning\\shapefiles\\")[
                1
            ].split(".shp")[0]
            + "@PERMANENT"
        )
        gs.run_command(
            "v.colors",
            map=input,
            use="attr",
            column="ZnID",
            rules="C:\\RA\\Zoning\\Raleigh_Prototype_Zoning\\scripts\\zone_color_rules_NC.txt",
        )
v.colors map=NC_patch_new@PERMANENT use="attr" column="ZnID" rules="C:\\RA\\Zoning\\Raleigh_Prototype_Zoning\\scripts\\zone_color_rules_NC.txt"


if __name__ == "__main__":
    main()
