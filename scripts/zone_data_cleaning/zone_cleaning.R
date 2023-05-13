## ---------------------------
##
## Script name: zone_cleaning.R
##
## Purpose of script: Merging spatial and tabular zoning data
## 
##
## Author: Margaret A Lawrimore
## Email: malawrim@ncsu.edu
##
## ---------------------------

# set working directory
wd <- getwd()
setwd(wd)

# Load libraries
library(data.table)
library(dict)
library(sp)
library(iterators)
library(doParallel)
library(tmap)
library(raster)
library(rgdal)
library(ggplot2)

# For parsing the description and filling in short_desc column from descriptor data
file_location <- "Processed_Zoning_Data"
counties <- list.files(file_location, pattern = "*_County")
counties
# Dictionary to hold processed tabular data for all counties
tabular_dict <- dict()
source("scripts\\zone_data_cleaning\\zone_tabular_cleaning.R")
# Set file to print all output to
sink("tabular_cleaning.txt")
tabular_cleaning <- function(counties, tabular_dict, file_location) {
  foreach(county = counties, .combine = list) %do% {
    county_sheet <- gsub("_County", "_Zoning_Original - Sheet1.csv", county)
    file_path <- paste(file_location, county, county_sheet, sep="\\")
    messy_data <- data.table::data.table()
    if (file.exists(file_path)) {
      messy_data <- data.table::fread(file_path)
      # remove spaces in column names
      colnames(messy_data) <- gsub(" ", "_", colnames(messy_data))
    } else {
      cat(county, "file not found: ", file_path, "\n")
    }
    tryCatch(
      expr = {
        tabular_dict$set(county, zone_tabular_cleaning(messy_data))
      },
      error = function(e){
        cat(county, ": error encountered when calling zone_tabular_cleaning", "\n")
        tabular_dict$set(county, "Not cleaned")
      }
    )
    cat(county, " cleaned\n")
  }
}

tabular_cleaning(counties, tabular_dict, file_location)
# end file sending output to
sink()

# pass file location of raw spatial zoning data
file_location <- "Raw_Zoning_Data"
setwd(paste(wd, "data_cleaning", sep = "\\"))

# Dictionary to hold processed spatial data for all counties
spatial_dict <- dict()
source("scripts\\zone_data_cleaning\\zone_spatial_cleaning.R")

foreach(val = counties) %do% {
  municipal <- unique(tabular_dict$get(val)$Jurisdiction)
  municipal <- lapply(municipal, tools::toTitleCase)
  municipal <- gsub(" ", "_", municipal)
  municipal <- paste(municipal,"_Zoning", sep = "")
  municipal <- gsub("County_Zoning", paste(val, "_Zoning", sep = ""), municipal)
  # Dictionary for that counties shapefiles - municipalities and counties
  county_shape <- dict()
  for ( j in municipal ) {
    file_path <- paste(file_location, val, j, paste(j, ".zip", sep = ""), sep="\\") 
    if (file.exists(file_path)) {
      # check if it has been previously unzipped
      if(!dir.exists(paste(wd, "data_cleaning", j, sep="\\"))) {
        unzip(file_path, overwrite = T)
        # if files were unzipped outside of a county unique folder
        # move to new folder
        if (!file.exists(paste(wd, "data_cleaning", j, sep="\\"))) {
          shape_name <- list.files(paste(wd, "data_cleaning", sep="\\"), pattern ="\\.(dbf|shp|shx|cpg|prj|sbn|sbx|xml)$")
          # create new folder
          dir.create(paste(wd, "data_cleaning", j, sep="\\"))
          # move file to new folder
          for (s in shape_name) {
            file.rename(from = paste(wd, "data_cleaning", s, sep = "\\"), to = paste(wd, "data_cleaning", j, s, sep="\\"))
          }
        }
      }
      # Find shapefile name
      shape_name <- list.files(paste(wd, "data_cleaning", j, sep="\\"), pattern ="\\.shp$")
      shape_name <- unlist(strsplit(shape_name[1], "\\.shp"))[[1]]
      
      county_shape$set(j, readOGR(paste(wd, "data_cleaning", j, sep="\\" ), shape_name, verbose = FALSE))
    }
  }
  # returns a list containing all spatial dataframes for the municipalities in the county
  if (tabular_dict$get(val) == "Not cleaned") {
    print(paste(val, " tabular data not found when called for spatial cleaning"))
  } else {
    tryCatch(
      expr = {
        spatial_dict$set(val,zone_spatial_cleaning(county_shape, tabular_dict$get(val)))
      },
      error = function(e){
        cat(val, ": error encountered when calling zone_spatial_cleaning", "%\n", file="spatial_merge_errors.txt",append=TRUE)
        spatial_dict$set(val,"not merged")
      }
    )
  }
}


setwd(paste(wd, "data_cleaning", "maps", sep = "\\"))

print_zone_map <- function(municpality, location, zones, zone_col) {
  zones = unique(municpality$NewZn)
  colors = unique(municpality$Color)
  colors[is.na(colors)] = "#cccccc"
  tm <- tm_shape(municpality) +
    tm_fill("Color") +
    tmap_options(check.and.fix = T) +
    tm_borders("black", lwd = 0.5) +
    tm_add_legend("symbol", title = location,
                 labels = zones,
                 col = colors, size = 1)
    
  tmap_save(tm, paste(location, ".png", sep = ""))
}

# view map
foreach(val = counties) %do% {
  foreach(municpality = spatial_dict$get(val)) %do% {
    # What county/municipality
    if ( length(unique(municpality@data$Jurisdiction)) > 1 ) {
      location <- val
    } else if ( unique(municpality@data$Jurisdiction) == "county" ) {
      location <- val
    } else {
      location <- unique(municpality@data$Jurisdiction)
    }
    location <- gsub(" ", "_", location)
    tryCatch(
      expr = {
        print_zone_map(municpality, location, zones, zone_col)
      },
      error = function(e){
        print(paste("Could not print map for ", location))
      }
    )
  }
}

# Save all shapefiles
setwd(paste(wd, "data_cleaning", "shapefiles", sep = "\\"))
foreach(val = counties) %do% {
  foreach(municpality = spatial_dict$get(val)) %do% {
    # What county/municipality
    if ( length(unique(municpality@data$Jurisdiction)) > 1 ) {
      location <- val
    } else if ( unique(municpality@data$Jurisdiction) == "county" ) {
      location <- val
    } else {
      location <- unique(municpality@data$Jurisdiction)
    }
    location <- gsub(" ", "_", location)
    tryCatch(
      expr = {
        # shapefile(municpality, file=paste0(location,".shp"), overwrite = T)
        writeOGR(municpality, dsn = paste0("./",location), layer = location, driver = "ESRI Shapefile", overwrite_layer = T)
      },
      error = function(e){
        print(paste("Could not save shapefile for ", location))
      }
    )
  }
}

# shapefile is faster
# system.time(shapefile(municpality, file=paste0(location,".shp")))
# system.time(writeOGR(municpality, dsn = paste0("./",location), layer = location, driver = "ESRI Shapefile"))
