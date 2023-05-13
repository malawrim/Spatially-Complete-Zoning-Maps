#!/usr/bin/env python3

'''
Script used to clean and stack predictors for zoning model 
Ran script in GRASS 
'''

import grass.script as gs

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
        rules="C:\RA\Zoning\nlcd_reclass.txt",
    )

    # combine all DEMs
    gs.run_command(
        "r.patch",
        overwrite=True,
        input="USGS_13_n34w078_20130911@PERMANENT,USGS_13_n34w079_20190913@PERMANENT,USGS_13_n35w077_20151130@PERMANENT,USGS_13_n35w078_20151130@PERMANENT,USGS_13_n35w079_20130911@PERMANENT,USGS_13_n35w080_20130911@PERMANENT,USGS_13_n37w077_20210610@PERMANENT,USGS_13_n37w077_20211220@PERMANENT,USGS_13_n37w078_20210305@PERMANENT,USGS_13_n37w078_20210610@PERMANENT,USGS_13_n37w079_20210305@PERMANENT,USGS_13_n37w080_20210305@PERMANENT,USGS_13_n37w081_20210305@PERMANENT,USGS_13_n37w082_20210305@PERMANENT,USGS_1_n34w078_20130911@PERMANENT,USGS_1_n34w079_20190913@PERMANENT,USGS_1_n35w077_20151130@PERMANENT,USGS_1_n35w078_20151130@PERMANENT,USGS_1_n35w079_20130911@PERMANENT,USGS_1_n35w080_20130911@PERMANENT,USGS_1_n35w081_20130911@PERMANENT,USGS_1_n35w083_20170309@PERMANENT,USGS_1_n35w084_20130911@PERMANENT,USGS_1_n35w085_20170824@PERMANENT,USGS_1_n36w076_20160315@PERMANENT,USGS_1_n36w077_20160315@PERMANENT,USGS_1_n36w078_20151125@PERMANENT,USGS_1_n36w079_20130911@PERMANENT,USGS_1_n36w080_20130911@PERMANENT,USGS_1_n36w081_20130911@PERMANENT,USGS_1_n36w082_20130911@PERMANENT,USGS_1_n36w083_20171114@PERMANENT,USGS_1_n36w084_20171109@PERMANENT,USGS_1_n36w085_20171101@PERMANENT,USGS_1_n37w076_20151106@PERMANENT,USGS_1_n37w077_20160315@PERMANENT,USGS_1_n37w077_20210610@PERMANENT,USGS_1_n37w077_20211220@PERMANENT,USGS_1_n37w078_20151109@PERMANENT,USGS_1_n37w078_20210305@PERMANENT,USGS_1_n37w078_20210610@PERMANENT,USGS_1_n37w079_20130911@PERMANENT,USGS_1_n37w079_20210305@PERMANENT,USGS_1_n37w080_20130911@PERMANENT,USGS_1_n37w080_20210305@PERMANENT,USGS_1_n37w081_20181203@PERMANENT,USGS_1_n37w081_20210305@PERMANENT,USGS_1_n37w082_20181127@PERMANENT,USGS_1_n37w082_20210305@PERMANENT,USGS_1_n37w083_20181127@PERMANENT",
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
        rules="C:\RA\Zoning\crop_reclass.txt",
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


def add_pred():
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
        input="D:\Raleigh_Prototype_Zoning\parcel\parcel_reclass.shp",
        layer="parcel_reclass",
        output="parcel_reclass",
    )
    
    gs.run_command(
        "v.import",
        overwrite=True,
        input="D:\Raleigh_Prototype_Zoning\parcel\NC_Parcels_all.gdb",
        layer="nc_parcels_pt",
        output="nc_parcels_pt",
    )

    ### maps from HAZUS ###
    # import all maps from geodatabase
    gs.run_command(
        "v.import",
        overwrite=True,
        input="D:\Raleigh_Prototype_Zoning\HAZUS\HAZUS.gdb",
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
        input="D:\Raleigh_Prototype_Zoning\HAZUS\hzBldgCountOccupB.xlsx",
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
        input="D:\Raleigh_Prototype_Zoning\parks",
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
    # v.import input=D:\Raleigh_Prototype_Zoning\parks layer=parks output=park_point
    gs.run_command(
        "v.import",
        overwrite=True,
        input="D:\Raleigh_Prototype_Zoning\parks",
        layer= "parks",
        output = "park_point",
    )

    # point to rast
    # v.to.rast input=park_point@PERMANENT type=point output=park_point use=val
    gs.run_command(
        "v.to.rast",
        overwrite=True,
        input="park_point@PERMANENT",
        type="point",
        output="park_point",
        use="val",
    )

    # calculate distance from point
    # r.grow.distance input=park_point@PERMANENT distance=park_dist
    gs.run_command(
        "r.grow.distance",
        overwrite=True,
        input="park_point",
        distance="dist_park",
    )

    ## SVI ##
    # import
    #v.import input=C:\RA\Zoning\SVI\ layer=SVI2018_NORTHCAROLINA_tract output=SVI2018_NORTHCAROLINA_tract
    gs.run_command(
        "v.import",
        overwrite=True,
        input="C:\RA\Zoning\SVI",
        layer="SVI2018_NORTHCAROLINA_tract",
        output="SVI2018_NORTHCAROLINA_tract",
    )
    # to rast
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=housing_units use=attr attribute_column=E_HU label_column=E_HU
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
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=hu_10_plus use=attr attribute_column=EP_MUNIT label_column=EP_MUNIT
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
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=mobile_homes use=attr attribute_column=EP_MOBILE label_column=EP_MOBILE
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
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=income use=attr attribute_column=EP_PCI label_column=EP_PCI
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
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=housing_transport use=attr attribute_column=RPL_THEME4 label_column=RPL_THEME4
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
    # bjobs -r -X -o "jobid queue cpu_used run_time avg_mem max_mem slots delimiter=','"

    # ranking for household composition
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=house_comp use=attr attribute_column=RPL_THEME2 label_column=RPL_THEME2
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
    # v.to.rast input=SVI2018_NORTHCAROLINA_tract@PERMANENT type=area output=SVI use=attr attribute_column=RPL_THEMES label_column=RPL_THEMES
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

# Export data as stack
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
    #r.out.gdal -c -m input=stack output=D:\Raleigh_Prototype_Zoning\NC_analysis\pred_stack.tif format=GTiff
    gs.run_command( 
        "r.out.gdal",
        overwrite=True,
        input="stack",
        output="SVI",
        flags = "cm"
    )

# Exort data from GRASS format as .tif
def export():

    output = ["SVI", "house_comp", "housing_transport", "income", "mobile_homes", "hu_10_plus", "housing_units", "dist_park", "park_binary", "dist_hzAirportFlty", "dist_hzCareFlty", "dist_hzFireStation", "dist_hzPoliceStation", "dist_hzSchool", "dist_hzRailwaySegment", "vote_dem","vote_rep","vote_unaffiliated"]
    
    for index, item in enumerate(output):
        gs.run_command( 
            "r.out.gdal",
            input=item,
            output="D:\Raleigh_Prototype_Zoning\NC_analysis\\" + item + ".tif",
            format="GTiff",
            flags="c",
        )

    # name of output rasters
    output = ["nlcd_reclass.tif",
            "dist_ag.tif",
            "dist_lake.tif",
            "slope.tif",
            "road_density.tif",
            "blg_density.tif",
            "building_ht_rast.tif",
            "dist_census_place.tif",
            "pop_rast.tif",
            "pop_dens.tif",
            "dist_interstate.tif",
            "SVI.tif",
            "house_comp.tif",
            "income.tif",
            "hu_10_plus.tif",
            "housing_units.tif",
            "dist_park.tif",
            "dist_hzAirportFlty.tif",
            "dist_hzCareFlty.tif",
            "dist_hzFireStation.tif",
            "dist_hzPoliceStation.tif",
            "dist_hzSchool.tif",
            "dist_hzRailwaySegment.tif",
            "vote_dem.tif",
            "vote_rep.tif"]

if __name__ == "__main__":
    main()
    add_pred()
    export()

def zone_pro():
    gs.run_command( 
        "r.zonal.classes",
        zone_map="collected_counties@PERMANENT",
        raster="NC_patch_hierarchy@PERMANENT",
        csvfile="D:\\Raleigh_Prototype_Zoning\\NC_analysis\\proportion\\zone_county.csv",
        separator="comma",
        flags="p",
        overwrite = True,
    )

    gs.run_command( 
        "r.zonal.classes",
        zone_map="collected_counties@PERMANENT",
        raster="NC_patch_hierarchy@PERMANENT",
        vectormap="zone_county",
        flags="p",
        overwrite = True,
    )

    col = [
        "prop_100",
        "prop_101",
        "prop_102",
        "prop_110",
        "prop_120",
        "prop_130",
        "prop_131",
        "prop_200",
        "prop_201",
        "prop_202",
        "prop_203",
        "prop_204",
        "prop_300",
        "prop_301",
        "prop_302",
        "prop_400",
    ]
    for index, item in enumerate(col):
        gs.run_command( 
            "v.to.rast",
            input="zone_county@PERMANENT",
            output="zone_"+item,
            use="attr",
            attribute_column=item,
        )
        gs.run_command( 
            "r.out.gdal",
            input="zone_"+item,
            output="D:\\Raleigh_Prototype_Zoning\\NC_analysis\\proportion\\" + "zone_"+ item + ".tif",
            format="GTiff",
            flags="c",
        )
        #v.to.rast input=zone_county@PERMANENT output=zone_prop_100 use=attr attribute_column=prop_100

def zone_pro_core():
    gs.run_command( 
        "r.zonal.classes",
        zone_map="collected_counties@PERMANENT",
        raster="NC_og_h0_zones@PERMANENT",
        csvfile="D:\\Raleigh_Prototype_Zoning\\NC_analysis\\proportion\\zone_county_core.csv",
        separator="comma",
        flags="p",
        overwrite = True,
    )
        
    gs.run_command( 
        "r.zonal.classes",
        zone_map="collected_counties@PERMANENT",
        raster="NC_og_h0_zones@PERMANENT",
        vectormap="zone_county_core",
        flags="p",
        overwrite = True,
    )

    col = [
        "prop_1",
        "prop_2",
        "prop_3",
        "prop_4",
    ]
    for index, item in enumerate(col):
        gs.run_command( 
            "v.to.rast",
            input="zone_county_core@PERMANENT",
            output="zone_"+item,
            use="attr",
            attribute_column=item,
        )
        gs.run_command( 
            "r.out.gdal",
            input="zone_"+item,
            output="D:\\Raleigh_Prototype_Zoning\\NC_analysis\\proportion\\" + "zone_"+ item + ".tif",
            format="GTiff",
            flags="c",
        )
        #v.to.rast input=zone_county@PERMANENT output=zone_prop_100 use=attr attribute_column=prop_100
