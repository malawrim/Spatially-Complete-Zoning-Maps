## ---------------------------
##
## Script name: zone_tabular_cleaning.R
##
## Purpose of script: Cleaning tabular zoning data for merging with spatial data
## Called by zone_cleaning.R
## 
## zone_desc must be in this format: https://docs.google.com/spreadsheets/d/1VTPvUM-_gQwGZUdfe8UDHM0Eoy0BVdV47sQxAIHgVJk/edit?usp=sharing
##
## Author: Margaret A Lawrimore
## Email: malawrim@ncsu.edu
##
## ---------------------------

# Install Libraries
# install.packages("data.table")
# install.packages("sp")
# install.packages("tmap")
# library(devtools)
# devtools::install_github("mkuhn/dict")
# install.packages("googlesheets4")

library(data.table)
library(dict)

# function to find matching general class
which_zone <- function(zone_desc, zone_classes, zone_dict) {
  # original i in zone_dict$keys() but can't control the order they appear in the dictionary
  for (i in zone_classes) {
    for (j in zone_dict$get(i)) {
      if (grepl(j, zone_desc, ignore.case = T) == T) {
        return(i)
      }
    }
  }
  return("Other")
}

# Function to find matching residential class
which_res <- function(zone_desc, unit_size, res_dict) {
  mf <- list("Multifamily", "multi family", "multi-family")
  for (i in mf) {
    if (grepl(i, zone_desc, ignore.case = T) == T) {
      return("Residential Multifamily")
    }
  }
  for (i in res_dict$keys()) {
    if (!is.na(unit_size) && unit_size >= res_dict$get(i)[[1]] && unit_size <= res_dict$get(i)[[2]]) {
      return(i)
    }
  }
  return("Other")
}

zone_tabular_cleaning <- function(messy_data) {
  
  zone_classes <- list("Open Space",
                       "Planned Development",
                       "Downtown",
                       "Mixed-Use",
                       "Commercial",
                       "Industrial",
                       "Office-Institutional",
                       "Residential",
                       "Agriculture")
  
  zone_search <- list( list("Open Space", "Open-Space", "Conservancy", "Conservation", "natural resources", "water", "wetland", "flood", "Recreation"),
                       list("Planned"),
                       list("Downtown","central business district", "central business", "main street", "City Center"),
                       list("Mixed-Use", "Mixed Use", "mix", "employment center", "all uses", "Commerce Park", "Business Park", "corporate park"),
                       list("Commercial","Retail", "business", "shopping", "residential office", "residential-office"),
                       list("Industrial", "Manufacturing"),
                       list("Institutional", "office", "Medical", "University", "Universities", "Educational", "education"),
                       list("Residential", "multifamily", "multi-family", "manufactured home", "single family", "single-family"),
                       list("Agriculture", "Agricultural", "farm")
                       )
  
  res_classes <- list("Residential High",
                      "Residential Medium-High",
                      "Residential Medium",
                      "Residential Low",
                      "Residential Very-Low")
  
  res_search <- list(list(0, 6999),
                      list(7000, 14999),
                      list(15000, 29999),
                      list(30000, 40000),
                      list(40001, Inf))
  
  # Create dictionary with keys being new zone names and values being search terms
  zone_dict <- dict(init_keys = zone_classes, init_values = zone_search)
  res_dict <- dict(init_keys = res_classes, init_values = res_search)
  
  # make copy for assigning new zone ID
  clean_data <- messy_data

  # add new column
  clean_data$NewZn <- ""
  # Change format for Density of Land use column
  clean_data$`Density_of_Land_Use` <- gsub("Minimum Lot Size: ", "", clean_data$`Density_of_Land_Use`)
  clean_data$`Density_of_Land_Use` <- gsub(" Sq.Ft.", "", clean_data$`Density_of_Land_Use`)
  clean_data$`Density_of_Land_Use` <- gsub("No Minimum", "", clean_data$`Density_of_Land_Use`)
  clean_data$`Density_of_Land_Use` <- as.integer(clean_data$`Density_of_Land_Use`)
  # for each row in the original data assign new Zone ID
  foreach(x = 1:nrow(clean_data), .combine=list) %do% {
    clean_data[x, c("NewZn")] <- which_zone(clean_data[x, `Zone_Name`], zone_classes, zone_dict)
    # If not matched check the long description
    if(clean_data[x, c("NewZn")] == "Other") {
      clean_data[x, c("NewZn")] <- which_zone(clean_data[x, `Description_of_Uses`], zone_classes, zone_dict)
    }
    if (clean_data[x, c("NewZn")] == "Residential") {
      clean_data[x, c("NewZn")] <- which_res(clean_data[x, `Zone_Name`], clean_data[x, `Density_of_Land_Use`], res_dict)
    }
  }
  
  # Join Zone IDs to new Zone Names
  new_zn_id <- fread(paste(file_location, "Zone_Classification.csv", sep="\\"))
  clean_data <- merge(clean_data, new_zn_id, by.x="NewZn", by.y="Zone")
  
  # change jurisdiction to all lowercase
  clean_data$Jurisdiction <- tolower(clean_data$Jurisdiction)
  
  return(clean_data)
}
