#!/usr/bin/env python3

'''
This script imports all predictors to be used in zoning random forest model.
Predicts are cleaned, stacked, and exported for use in model. 

Usage: Run using built-in GRASS GIS python editor other accepted IDE. 
See https://grasswiki.osgeo.org/wiki/GRASS_and_Python and https://grasswiki.osgeo.org/wiki/Tools_for_Python_programming

Written using Python 3 and GRASS 8
'''

import grass.script as gs
import os
import glob

# names for vectors after converting to raster
final = [
    "building_ht_rast@PERMANENT",
    "dist_ag@PERMANENT",
    "dist_census_place@PERMANENT",
    "dist_interstate@PERMANENT",
    "dist_metro_area@PERMANENT",
    "dist_protected@PERMANENT",
    "dist_road@PERMANENT",
    "nlcd_reclass@PERMANENT",
    "pop_dens@PERMANENT",
    "pop_rast@PERMANENT",
    "protected_rast@PERMANENT",
    "road_density@PERMANENT",
    "blg_density@PERMANENT",
    "dist_building@PERMANENT",
    "blg_area_rast@PERMANENT",
    "impervious@PERMANENT",
    "slope@PERMANENT",
    "dist_river@PERMANENT",
    "dist_lake@PERMANENT",
    "dist_interchange@PERMANENT",
]

# names for vector data to be imported
output_vect = [
    "building_ht",
    "census_places",
    "metro_area",
    "roads",
    "census_bloc",
    "protected",
    "blg_area",
    "blg_footprint",
    "streams_rivers",
    "lakes",
    "interchange",
    "pop",
    "parcel"
]

# names for rasters after importing
output_rast = ["agriculture", "crop_mask", "nlcd", "road_density", "blg_density", "impervious"]

# names for vector input data
files_vect = [
    "building_height_national\srtm_derived_building_heights_by_block_group_conterminous_US\srtm_bg_building_heights.gdb",
    "cities\\tl_2021_37_place.shp",
    "cities\\2019_us_metropolitan_statistical_area.shp",
    "Tigers_Road_State_2016\\37\\tl_2016_37_roads.shp",
    "census_block\census_block.shp",
    "protected_areas\protected_nc.shp",
    "building_density\\blg_den_join.shp",
    "building_density\\Building_footprint.shp",
    "water\streams_rivers.shp",
    "water\lakes.shp",
    "interchanges\\tl_2016_cont_us_psroads_intsct_all.shp",
    "pop_block\pop_block.shp",
    "parcel\NC_Parcels_all.gdb"
]

# names for rasters input data
files_rast = [
    "crop\crop.tif",
    "crop\CMASK_2021_37.tif"
    "nlcd2019\\nlcd_nc.tif",
    "Road_Density\\NC_roadDen.tif",
    "building_density\\blg_density.tif",
    "impervious\impervious_nc.tif",
]

# set file_path to location of all input parameters
file_path = os.getcwd()

# load all files
def main():
    for index, item in enumerate(output_vect):
        input = "D:\Zoning\Raleigh_Prototype_Zoning\\" + files_vect[index]
        gs.run_command(
            "v.import", overwrite=True, input=input, output=item, extent="region"
        )
        # v.import input=D:\Raleigh_Prototype_Zoning\parcel\NC_Parcels_all.gdb layer=nc_parcels_poly output=nc_parcels_poly

    for index, item in enumerate(output_rast):
        input = "D:\Zoning\Raleigh_Prototype_Zoning\\" + files_rast[index]
        gs.run_command(
            "r.import", overwrite=True, input=input, output=item, extent="region"
        )
    # import elevation data
    # USGS_13
    # patch
    v_to_rast_input = [
        "blg_area@PERMANENT",
        "metro_area@PERMANENT",
        "census_places@PERMANENT",
        "roads@PERMANENT",
        "interchange@PERMANENT",
        "streams_rivers@PERMANENT",
        "lakes@PERMANENT",
        "interstate@PERMANENT",
        "protected@PERMANENT",
    ]
    # inputs to calculate distance on
    grow_distance_input = [
        "blg_area_rast@PERMANENT",
        "metro_areas_rast@PERMANENT",
        "census_places_rast@PERMANENT",
        "road_rast@PERMANENT",
        "interchange_rast@PERMANENT",
        "stream_river_rast@PERMANENT",
        "lake_rast@PERMANENT",
        "interstate_rast@PERMANENT",
        "protected_rast@PERMANENT",
    ]
    # data type for above array
    type = [
        "area",
        "area",
        "area",
        "line",
        "point",
        "line",
        "area",
        "line",
        "area",
    ]
    # what data to get out of above array
    use = ["attr", "val", "val", "val", "attr", "val", "val", "val", "val"]
    attr = ["Area_new", "Code"]
    count = 0
    # output names of distance features
    grow_distance_output = [
        "dist_building@PERMANENT",
        "dist_metro_area@PERMANENT",
        "dist_census_place@PERMANENT",
        "dist_road@PERMANENT",
        "dist_interchange@PERMANENT",
        "dist_river@PERMANENT",
        "dist_lake@PERMANENT",
        "dist_interstate@PERMANENT",
        "dist_protected@PERMANENT",
    ]

    # get interstate out of road file
    gs.run_command(
        "v.extract",
        input="roads@PERMANENT",
        output="interstate@PERMANENT",
        where="RTTYP = 'I' OR RTTYP = 'U'",
    )

    # iterate over vectors that need to be converted to rasters
    for index, item in enumerate(v_to_rast_input):
        if use[index] == "attr":
            gs.run_command(
                "v.to.rast",
                overwrite=True,
                input=item,
                type=type[index],
                output=grow_distance_input[index],
                use=use[index],
                attribute_column=attr[count],
            )
            count += 1
        else:
            gs.run_command(
                "v.to.rast",
                overwrite=True,
                input=item,
                type=type[index],
                output=grow_distance_input[index],
                use=use[index],
            )
        gs.run_command(
            "r.grow.distance",
            overwrite=True,
            input=grow_distance_input[index],
            distance=grow_distance_output[index],
        )

    # reclassify NLCD data 
    gs.run_command(
        "r.reclass",
        overwrite=True,
        input="nlcd@PERMANENT",
        output="nlcd_reclass@PERMANENT",
        rules=os.path.join(file_path, "reclass", "nlcd_reclass.txt"),
    )

    # to store name of imported DEMS
    dems = []
    # import all DEMS in folder
    for f in glob.glob(os.path.join(file_path, "DEM", "*.tif")):
        # import DEM
        gs.run_command(
            "r.import",
            input = f,
            overwrite = True,
        )
        # keep list of DEMs imported
        dems.append(os.path.basename(f).split(".tif")[0] + "@PERMANENT")
    # turn list into comma delimited string for input into next function (r.patch)
    dem_input = ','.join(dems)

    
    # combine all DEMs into one raster layer
    gs.run_command(
        "r.patch",
        overwrite=True,
        input=dem_input,
        output="DEM@PERMANENT",
    )

    # Calculate slope
    gs.run_command(
        "r.slope.aspect", overwrite=True, elevation="DEM@PERMANENT", slope="slope"
    )

    # convert population to raster
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="pop@PERMANENT",
        type="area",
        output="pop_rast@PERMANENT",
        use="attr",
        attribute_column="Totl_Pp",
    )

    # convert parcel poly data to rast 
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="parcel@PERMANENT",
        type="area",
        output="parcel_rast@PERMANENT",
        use="attr",
        attribute_column="Totl_Pp",
    )

    # convert parcel point data to rast 
    # v.to.rast input=nc_parcels_pt@PERMANENT type=point output=parcel_pt_rast use=val
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="nc_parcels_pt@PERMANENT",
        type="point",
        output="parcel_pt_rast@PERMANENT",
        use="val",
    )

# r.grow.distance -m --overwrite input=parcel_pt_rast@PERMANENT distance=dist_parcel
    # get datatable from pop
    gs.run_command(
        "v.to.db",
        overwrite=True,
        map="pop@PERMANENT",
        option="area",
        columns="area",
        units="meters",
        query_column="Totl_Pp",
    )

    # create column names pop_dens
    gs.run_command(
        "v.db.addcolumn",
        map="pop@PERMANENT",
        columns="pop_dens double",
    )

    # calculate population density
    gs.run_command(
        "v.db.update",
        map="pop@PERMANENT",
        layer="1",
        column="pop_dens",
        query_column="Totl_Pp/(area/100)",
    )

    # convert population density to raster
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="pop@PERMANENT",
        type="area",
        output="pop_dens@PERMANENT",
        use="attr",
        attribute_column="pop_dens",
    )

    # reclassify crop data
    gs.run_command(
        "r.reclass",
        overwrite=True,
        input="agriculture@PERMANENT",
        output="ag_reclass@PERMANENT",
        rules=os.path.join(file_path, "reclass", "crop_reclass.txt"),
    )

    # calculate distance to agricultural land
    gs.run_command(
        "r.grow.distance",
        overwrite=True,
        input="ag_reclass@PERMANENT",
        distance="dist_ag@PERMANENT",
    )

    # convert building height layer to raster
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="building_ht@PERMANENT",
        type="area",
        output="building_ht_rast@PERMANENT",
        use="attr",
        attribute_column="SEPH",
        label_column="Height_cat",
    )

    ## parcel data ##
    # add column for area
    #v.db.addcolumn map=nc_parcels_poly@PERMANENT columns="parcel_area DOUBLE"
    gs.run_command(
        "v.db.addcolumn",
        overwrite=True,
        map="nc_parcels_poly@PERMANENT",
        columns="parcel_area DOUBLE",
    )
    # calculate area
    #v.to.db map=nc_parcels_poly@PERMANENT type=boundary option=area columns=parcel_area
    gs.run_command(
        "v.to.db",
        overwrite=True,
        map="nc_parcels_poly@PERMANENT",
        type="boundary",
        option="area",
        columns="parcel_area",
    )
    
    # to rast
    # v.to.rast input=nc_parcels_poly@PERMANENT type=area output=parcel_area use=attr attribute_column=parcel_area
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="nc_parcels_poly@PERMANENT",
        type="area",
        output="parcel_area",
        use="attr",
        attribute_column="parcel_area",
    )

    # v.import input=D:\Raleigh_Prototype_Zoning\parcel\parcel_reclass.dbf layer=parcel_reclass output=parcel_reclass
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "parcel", "parcel_reclass.shp"),
        layer="parcel_reclass",
        output="parcel_reclass",
    )
    
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "parcel", "NC_Parcels_all.gdb"),
        layer="nc_parcels_pt",
        output="nc_parcels_pt",
    )

    ### maps from HAZUS ###
    # import all maps from geodatabase
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "HAZUS", "HAZUS.gdb"),
    )

    gs.run_command(
        "v.db.addcolumn",
        overwrite=True,
        map="hzCensusBlock@PERMANENT",
        columns="block_double DOUBLE",
    )

    gs.run_command(
        "v.db.update",
        overwrite=True,
        map="hzCensusBlock@PERMANENT",
        column="block_double DOUBLE",
        where="UPDATE hzCensusBlock SET block_double = CensusBlock"
    )
    # UPDATE hzCensusBlock SET block_double = CensusBlock 

    # import table with building info
    # db.in.ogr --overwrite input=D:\Raleigh_Prototype_Zoning\HAZUS\hzBldgCountOccupB.xlsx output=hz_bldg_tab
    gs.run_command(
        "db.in.ogr",
        overwrite=True,
        input=os.path.join(file_path, "HAZUS", "hzBldgCountOccupB.xlsx"),
        output="hz_bldg_tab",
    )

    # join table with census block
    # v.db.join map=hzCensusBlock@PERMANENT column=CensusBlock other_table=hz_bldg_tab other_column=CensusBlock
    gs.run_command(
        "v.db.join",
        map="hzCensusBlock@PERMANENT",
        column="CensusBlock",
        other_table="hz_bldg_tab",
        other_column="CensusBlock",
    )

    # import voter data
    # db.in.ogr input=D:\Raleigh_Prototype_Zoning\NC_analysis\vote\registered_voters.csv output=voter_tab
    gs.run_command(
        "db.in.ogr",
        input="D:\\Raleigh_Prototype_Zoning\\vote\\registered_voters.csv",
        output="voter_tab",
    )
    gs.run_command(
        "v.db.join",
        map="North_Carolina_State_and_County_Boundary_Polygons@PERMANENT",
        column="County",
        other_table="voter_tab",
        other_column="County",
    )
    # v.db.join map=county_boundary@PERMANENT column=County other_table=voter_tab other_column=County
    # v.to.rast input=county_boundary@PERMANENT type=area output=vote_rep use=attr attribute_column=rep_num label_column=rep_num
    gs.run_command(
        "v.to.rast",
        input="North_Carolina_State_and_County_Boundary_Polygons",
        type="area",
        output="vote_rep",
        use="attr",
        attribute_column="rep_num"
    )

    gs.run_command(
        "v.to.rast",
        input="North_Carolina_State_and_County_Boundary_Polygons",
        type="area",
        output="vote_dem",
        use="attr",
        attribute_column="dem_num"
    )

    gs.run_command(
        "v.to.rast",
        input="North_Carolina_State_and_County_Boundary_Polygons",
        type="area",
        output="vote_unaffiliated",
        use="attr",
        attribute_column="independent_num"
    )
    # railroad to rast
    #v.to.rast input=hzRailwaySegment@PERMANENT type=line output=hzRailwaySegment_rast use=val
    gs.run_command(
            "v.to.rast",
            input="hzRailwaySegment",
            type="line",
            output="hzRailwaySegment_rast",
            use="val",
        )

    # tracts to rast
    gs.run_command(
        "v.to.rast",
        input="hzCensusBlock",
        type="area",
        output="hzCensusBlock_rast",
        use="attr",

    )
    # point to rast
    v_to_rast_hazus = ["hzAirportFlty", "hzCareFlty", "hzFireStation", "hzPoliceStation", "hzSchool"]
    
    for index, item in enumerate(v_to_rast_hazus):
        # convert to rast
        gs.run_command(
            "v.to.rast",
            input=item,
            type="point",
            output=item + "_rast",
            use="val",
        )

        # calculate distance
        gs.run_command(
            "r.grow.distance",
            overwrite=True,
            input=item + "_rast",
            distance="dist_" + item,
        )

    ### Parks ###
    # import polygons
    # v.import input=D:\Raleigh_Prototype_Zoning\parks layer=park_poly output=park_poly
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "parks"),
        layer= "park_poly",
        output = "park_poly",
    )

    # park or not park - binary raster
    # v.to.rast --overwrite input=park_poly@PERMANENT type=area output=park_binary@PERMANENT use=val
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="park_poly@PERMANENT",
        type="area",
        output="park_binary",
        use="val",
    )

    # import park points
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "parks"),
        layer= "parks",
        output = "park_point",
    )

    # point to rast
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="park_point@PERMANENT",
        type="point",
        output="park_point",
        use="val",
    )

    # calculate distance from point
    gs.run_command(
        "r.grow.distance",
        overwrite=True,
        input="park_point",
        distance="dist_park",
    )

    ## SVI ##
    # import
    gs.run_command(
        "v.import",
        overwrite=True,
        input=os.path.join(file_path, "SVI"),
        layer="SVI2018_NORTHCAROLINA_tract",
        output="SVI2018_NORTHCAROLINA_tract",
    )
    # to rast
    # Housing units count
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="housing_units",
        use="attr",
        attribute_column="E_HU",
        label_column="E_HU",
    )

    # count of housing stuctures with 10 or more units
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="hu_10_plus",
        use="attr",
        attribute_column="EP_MUNIT",
        label_column="EP_MUNIT",
    )

    # number of mobile homes
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="mobile_homes",
        use="attr",
        attribute_column="EP_MOBILE",
        label_column="EP_MOBILE",
    )

    # per capita income
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="income",
        use="attr",
        attribute_column="EP_PCI",
        label_column="EP_PCI",
    )

    # ranking for housing/transportation
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="housing_transport",
        use="attr",
        attribute_column="RPL_THEME4",
        label_column="RPL_THEME4",
    )

    # ranking for household composition
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="house_comp",
        use="attr",
        attribute_column="RPL_THEME2",
        label_column="RPL_THEME2",
    )

    # SVI
    gs.run_command( 
        "v.to.rast",
        overwrite=True,
        input="SVI2018_NORTHCAROLINA_tract@PERMANENT",
        type="area",
        output="SVI",
        use="attr",
        attribute_column="RPL_THEMES",
        label_column="RPL_THEMES",
    )

# Exort data from GRASS format as .tif
def export():

    output = ["dist_ag@PERMANENT",
        "dist_building@PERMANENT",
        "dist_census_place@PERMANENT",
        "dist_hzAirportFlty@PERMANENT",
        "dist_hzCareFlty@PERMANENT",
        "dist_hzFireStation@PERMANENT",
        "dist_hzPoliceStation@PERMANENT",
        "dist_hzRailwaySegment@PERMANENT",
        "dist_hzSchool@PERMANENT",  
        "dist_interchange@PERMANENT",
        "dist_interstate@PERMANENT",
        "dist_lake@PERMANENT",
        "dist_metro_area@PERMANENT",
        "dist_park@PERMANENT",
        "dist_protected@PERMANENT", 
        "dist_river@PERMANENT",
        "dist_road@PERMANENT",      
        "park_dist@PERMANENT",
        "slope@PERMANENT",        
        "impervious@PERMANENT",
        "protected_rast@PERMANENT", 
        "blg_area_rast@PERMANENT",
        "blg_density@PERMANENT",    
        "road_density@PERMANENT",
        "nlcd_reclass@PERMANENT",   
        "ag_reclass@PERMANENT",
        "SVI@PERMANENT",            
        "house_comp@PERMANENT",
        "housing_transport@PERMANENT",
        "housing_units@PERMANENT",
        "income@PERMANENT",         
        "hu_10_plus@PERMANENT",
        "park_binary@PERMANENT",    
        "vote_dem@PERMANENT",
        "vote_rep@PERMANENT",       
        "vote_unaffiliated@PERMANENT",
        "building_ht_rast@PERMANENT",
        "pop_dens@PERMANENT",
        "pop_rast@PERMANENT",       
        "NC_patch_hierarchy@PERMANENT",
        "NC_county@PERMANENT",]  
    
    # export all files to pred folder
    for item in output:
        gs.run_command( 
            "r.out.gdal",
            input=item,
            output=os.path.join(file_path, "pred", (item.split("@PERMANENT")[0] + ".tif")),
            format="GTiff",
            flags="c",
        )

if __name__ == "__main__":
    main()
    export()

# Could alternatively export all predictors in one raster stack
def export_stack():
    # make group called stack
    group_list = ["dist_ag@PERMANENT",
        "dist_building@PERMANENT",
        "dist_census_place@PERMANENT",
        "dist_hzAirportFlty@PERMANENT",
        "dist_hzCareFlty@PERMANENT",
        "dist_hzFireStation@PERMANENT",
        "dist_hzPoliceStation@PERMANENT",
        "dist_hzRailwaySegment@PERMANENT",
        "dist_hzSchool@PERMANENT",  
        "dist_interchange@PERMANENT",
        "dist_interstate@PERMANENT",
        "dist_lake@PERMANENT",
        "dist_metro_area@PERMANENT",
        "dist_park@PERMANENT",
        "dist_protected@PERMANENT", 
        "dist_river@PERMANENT",
        "dist_road@PERMANENT",      
        "park_dist@PERMANENT",
        "slope@PERMANENT",        
        "impervious@PERMANENT",
        "protected_rast@PERMANENT", 
        "blg_area_rast@PERMANENT",
        "blg_density@PERMANENT",    
        "road_density@PERMANENT",
        "nlcd_reclass@PERMANENT",   
        "ag_reclass@PERMANENT",
        "SVI@PERMANENT",            
        "house_comp@PERMANENT",
        "housing_transport@PERMANENT",
        "housing_units@PERMANENT",
        "income@PERMANENT",         
        "hu_10_plus@PERMANENT",
        "park_binary@PERMANENT",    
        "vote_dem@PERMANENT",
        "vote_rep@PERMANENT",       
        "vote_unaffiliated@PERMANENT",
        "building_ht_rast@PERMANENT",
        "pop_dens@PERMANENT",
        "pop_rast@PERMANENT",       
        "NC_patch_hierarchy@PERMANENT",
        "NC_county@PERMANENT",]  
    gs.run_command( 
        "i.group",
        group="stack",
        input=group_list,
    )
    gs.run_command( 
        "r.out.gdal",
        overwrite=True,
        input="stack",
        output="predictor_stack",
        flags = "cm"
    )