# set working directory
wd <- "D:\\Raleigh_Prototype_Zoning"
setwd(wd)

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
file_location <- "Q:\\Shared drives\\CNR - Land & Climate Change\\Zoning_Project\\Processed Zoning Data"
counties <- list.files(file_location, pattern = "*_County")
counties
# test_counties <- counties[1:20]
# counties <- test_counties
# Dictionary to hold processed tabular data for all counties
tabular_dict <- dict()
source("C:\\Users\\malawrim\\Documents\\GitHub\\Zoning\\zone_tabular_cleaning.R")
# Set file to print all output to
sink("D:\\Raleigh_Prototype_Zoning\\data_cleaning\\tabular_cleaning.txt")
# consider passing in functions as params
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
        # print(paste(county, ": error encountered when calling zone_tabular_cleaning", sep = ""))
        tabular_dict$set(county, "Not cleaned")
      }
    )
    cat(county, " cleaned\n")
  }
}

# cores <- detectCores() - 1
# cl <- parallel::makeCluster(cores)
# registerDoParallel(cl)
tabular_cleaning(counties, tabular_dict, file_location)
# end file sending output to
sink()
# stopCluster(cl)
# read_sheet("https://docs.google.com/spreadsheets/d/1YMyebwujEnV23cL3ieRT6XBcXxteLk3ogQzy7JSebtw/edit?usp=sharing")

file_location <- "Q:\\Shared drives\\CNR - Land & Climate Change\\Zoning_Project\\Raw Zoning Data"
setwd(paste(wd, "data_cleaning", sep = "\\"))

# Dictionary to hold processed spatial data for all counties
spatial_dict <- dict()
source("C:\\Users\\malawrim\\Documents\\GitHub\\Zoning\\zone_spatial_cleaning.R")
# cores <- detectCores() - 1
# cl <- parallel::makeCluster(cores)
# registerDoParallel(cl)
foreach(val = counties) %do% {
  # municipal <- list.files(paste(file_location, val, sep="\\"), pattern = "*_Zoning")
  # If i don't have tabular entries for all of the shapefiles
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
        # print(paste(val, ": error encountered when calling zone_spatial_cleaning", sep = ""))
        spatial_dict$set(val,"not merged")
      }
    )
  }
}
# stopCluster(cl)
# # check that merge was successful
# # check correct number of columns
# ncol(spatial_merge) == ncol(spatial) + ncol(tabular) - 2
# # check that no new NA's were introduced
# sum(is.na(spatial_merge$ZnID))
# sum(is.na(spatial_merge$Color))
# sum(is.na(tabular))
# sum(is.na(spatial@data))
# # also do a couple of random checks in the actual data table to see if anything weird happened
# View(spatial_merge)
# 

setwd(paste(wd, "data_cleaning", "maps", sep = "\\"))

print_zone_map <- function(municpality, location, zones, zone_col) {
  # calculating the percent of each zone
  # zone_count <- as.data.table(municpality@data)[, .N, by=.(NewZn)]
  # total <- sum(zone_count$N)
  # res_rows <- grep("Residential", zone_count$NewZn)
  # res_sum <- 0
  # for( i in res_rows ) {
  #   res_sum <- res_sum + zone_count$N[i]
  # }
  # zone_count <- rbind(zone_count[], data.table("Residential", res_sum), use.names=F)
  # zone_count$percent <- format(round(zone_count$N / total, 4) * 100, nsmall = 2) 
  # zoneandcolor <- data.table(zones, zone_col)
  # zone_merge <- merge(zoneandcolor, zone_count, by.x = "zones", by.y = "NewZn")
  # 
  zones = unique(municpality$NewZn)
  colors = unique(municpality$Color)
  colors[is.na(colors)] = "#cccccc"
  # general zones 
  tm <- tm_shape(municpality) +
    tm_fill("Color") +
    tmap_options(check.and.fix = T) +
    tm_borders("black", lwd = 0.5) +
    tm_add_legend("symbol", title = location,
                 labels = zones,
                 col = colors, size = 1)
    
  tmap_save(tm, paste(location, ".png", sep = ""))
  
  # to_sf <- st_as_sf(municpality)
  # gg <- ggplot(data = to_sf) +
  #   geom_sf(aes(fill = Color)) +
  #   theme(panel.background = element_rect(fill = "#FFFFFF"),
  #         panel.border = element_blank(),
  #         panel.grid.major = element_blank(),
  #         axis.text.x = element_blank(),
  #         axis.text.y = element_blank(),
  #         axis.ticks.x = element_blank(),
  #         axis.ticks.y = element_blank())
  # ggsave(filename = paste(location, ".png", sep = ""), plot = gg)
}


print_res_map <- function(municpality, location, res_zones, res_zone_col) {
  # residential zones
  tm <- tm_shape(municpality) +
    tm_fill("ResColor") +
    tmap_options(check.and.fix = T) +
    tm_borders("black", lwd = 0.5) +
    tm_add_legend("symbol", title = location, labels = res_zones, col = res_zone_col, size = 1)
  tmap_save(tm, paste(location, "_res.png", sep = ""))
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
    # find percentage of polygons by zone 
    ## TODO not great because the polygons aren't equal sizes 
    ## I need to do this with the raster version
    tryCatch(
      expr = {
        print_zone_map(municpality, location, zones, zone_col)
        # print_res_map(municpality, location, res_zones, res_zone_col)
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
