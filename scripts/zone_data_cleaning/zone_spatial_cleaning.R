library(data.table)
library(sp)
library(rgdal)

zone_spatial_cleaning <- function(spatial_county, tabular) {
  
  spatial_clean <- list()
  # For each municipality
  for ( k in 1:length(spatial_county$keys())) {

    spatial <- spatial_county$get(spatial_county$keys()[[k]])
    # jurisdiction <- unlist(strsplit(spatial_county$keys()[[k]], "_"))[[1]]
    
    # find column with zone ID
    zone_id_col <- 0
    prev_match_count <- 0
    juris_set <- F
    for(i in 1:ncol(spatial@data)) {
      match_count <- 0
      # if the column isn't all NAs, it is a character it may be jurisidiction or zones
      if (sum(is.na(spatial@data[,i])) != nrow(spatial@data) && class(spatial@data[,i]) == "character") {
        if (grepl("juris", colnames(spatial@data)[i], ignore.case = T) | grepl("munic", colnames(spatial@data)[i], ignore.case = T)| grepl("Jrsdctn", colnames(spatial@data)[i], ignore.case = T)) {
          if (!juris_set) {
            colnames(spatial@data)[i] <- "Jurisdiction"
          }
          juris_set <- T
        } else {
          # if column has an average of less than 5 characters this row may contain the zones
          if (mean(sapply(na.omit(spatial@data[,i]), nchar)) < 6) {
            # look for matches to determine which column has zone id's
            for (u in unique(tabular$Zone_ID)) {
              match_count <- match_count + sum(grepl(paste0('\\b', u, '\\b'), spatial@data[,i], ignore.case = T))
            }
            if ( match_count > prev_match_count) {
              prev_match_count <- match_count
              zone_id_col <- i
            }
          }
        }
      }
    }
    colnames(spatial@data)[zone_id_col] <- "Zone_ID"

    # remove NA's based on value in one column
    # subset(spatial@data, !is.na(spatial@data[,i]))
    
    # print original shapefile map
    tryCatch(
      expr = {
        tm <- tm_shape(spatial) +
          tm_fill("Zone_ID")
        tmap_save(tm, paste(wd,"\\data_cleaning", "\\maps\\", spatial_county$keys()[[k]], "_original.png", sep = ""))
      },
      error = function(e){
        cat("Printing original map for ", spatial_county$keys()[[k]], " using ggplot")
        to_sf <- st_as_sf(spatial)
        gg <- ggplot(data = to_sf) +
          geom_sf(aes(fill = Zone_ID)) +
          theme(panel.background = element_rect(fill = "#FFFFFF"),
                panel.border = element_blank(),
                panel.grid.major = element_blank(),
                axis.text.x = element_blank(),
                axis.text.y = element_blank(),
                axis.ticks.x = element_blank(),
                axis.ticks.y = element_blank())
        ggsave(filename = paste(wd,"\\data_cleaning", "\\maps\\", spatial_county$keys()[[k]], "_original.png", sep = ""), plot = gg)
      }
    )
    
    
    # If jurisdiction match wasn't found 
    if (!juris_set) {
      # add column for jurisdiction
      if ( grepl("county", spatial_county$keys()[[k]], ignore.case = T)) {
        spatial@data$Jurisdiction <- "county"
      } else {
        spatial@data$Jurisdiction <- unlist(strsplit(spatial_county$keys()[[k]], "_Zoning")[1])[[1]]
        # replace any underscores in jurisdiction column with spaces
        spatial@data$Jurisdiction <- gsub("_", " ", spatial@data$Jurisdiction)
      }
    # If jurisdiction is abbreviated
    } else if ( mean(sapply(na.omit(unique(spatial@data["Jurisdiction"])), nchar)) > 2 && mean(sapply(na.omit(unique(spatial@data["Jurisdiction"])), nchar)) < 3 ) {
      spatial@data$Jurisdiction <- tolower(spatial@data$Jurisdiction)
      
      # copy original jurisdiction to new data table
      jurisdiction <- data.table()
      jurisdiction$org <- unique(tabular$Jurisdiction)
      jurisdiction$new <- unique(tabular$Jurisdiction)
      for (i in jurisdiction$org) {
        split <- unlist(strsplit(i, " "))
        if (length(split) > 1) {
          jur <- paste(tolower(unlist(strsplit(split[1], ""))[1]), tolower(unlist(strsplit(split[2], ""))[1]), sep = "")
          jurisdiction$new <- gsub(i, jur, jurisdiction$new)
        } else {
          jur <- paste(tolower(unlist(strsplit(split[1], ""))[1]), tolower(unlist(strsplit(split[1], ""))[2]), sep = "")
          jurisdiction$new <- gsub(i, jur, jurisdiction$new)
        }
      }
      spatial <- merge(spatial, jurisdiction, by.x = "Jurisdiction", by.y = "new", all = F)
      names(spatial)[names(spatial) == "Jurisdiction"] <- "Jurisdict_abrev"
      names(spatial)[names(spatial) == "org"] <- "Jurisdiction"
      
    }
    
    if (grepl("_County", spatial_county$keys()[[k]]) == T & sum(grepl("county", spatial@data$Jurisdiction), ignore.case = T) < 2 ) {
      county <- strsplit(spatial_county$keys()[[k]], "_County_Zoning")[[1]]
      spatial@data$`Jurisdiction` <- gsub(paste0('\\b',county, '\\b'), "county", spatial@data$`Jurisdiction`, ignore.case = T)
    }
    
    # change jurisdiction to lowercase
    spatial@data$Jurisdiction <- tolower(spatial@data$Jurisdiction)
    # remove all spaces
    spatial@data$Zone_ID <- gsub(" ", "", spatial@data$Zone_ID)
    
    # for conditional districts remove conditional flag from zone id
    # -C
    # remove anything within parenthesis 
    spatial@data$Zone_ID <- gsub("\\s*\\([^\\)]+\\)","",spatial@data$Zone_ID)
    spatial@data$Zone_ID <- gsub("-CZD", "",gsub("/CD", "", gsub("CUP", "", spatial@data$Zone_ID)))
    spatial@data$Zone_ID <- gsub("CZ-", "", gsub("-CZ", "", gsub("/CZ", "", gsub("-CU", "", gsub("CU-", "", gsub("CUD-", "",  gsub("CUR-", "", gsub("-CUR", "", gsub("-CD", "", gsub("CD-", "", gsub("-SUP", "",  gsub("-SUD", "",  gsub("_CU", "", spatial@data$Zone_ID)))))))))))))
    spatial@data$Zone_ID <- gsub("CD", "", gsub("CZ", "", gsub("CU", "", spatial@data$Zone_ID)))
    spatial@data$Zone_ID <- gsub("CUR", "", gsub("SUP", "", gsub("CUD", "", spatial@data$Zone_ID)))
    
    # merge with tabular data
    current_county <- spatial_county$keys()[[k]]

    tryCatch(
      expr = {
        spatial_merge <- merge(spatial, tabular, by = c("Zone_ID", "Jurisdiction"), ignore.case = T, all.x = T)
        cat(current_county, ": sucessful merge\n", sep = "", file="spatial_merge_warnings.txt",append=TRUE)
        # count number of zones that weren't merged
        # percentage of polygons
        # perc_matched <- (nrow(spatial_merge@data) / nrow(spatial@data) ) * 100
        # percentage of area covered
        perc_matched <- (sum(as.data.table(area(spatial_merge))) / sum(as.data.table(area(spatial)))) * 100
        
        cat(current_county, ": ", "percentage matched = ", perc_matched, "%\n", file="spatial_merge_warnings.txt",append=TRUE)
        # zones in tabular but not in spatial
        tab_not_merged <- setdiff(unique(tabular[Jurisdiction %in% unique(spatial@data$Jurisdiction)]$Zone_ID), unique(as.data.table(spatial@data)[Jurisdiction %in% unique(tabular$Jurisdiction)]$Zone_ID))
        cat(current_county, ": ", length(tab_not_merged), " zone(s) in tabular but not in spatial: ", tab_not_merged, "\n", file="spatial_merge_warnings.txt",append=TRUE)
        # print(paste(length(tab_not_merged), " zone(s) in tabular but not in spatial: "))
        # print.table(tab_not_merged)
        # in spatial but no in tabular
        spat_not_merged <- setdiff(unique(as.data.table(spatial@data)[Jurisdiction %in% unique(tabular$Jurisdiction)]$Zone_ID), unique(tabular[Jurisdiction %in% unique(spatial@data$Jurisdiction)]$Zone_ID))
        cat(current_county, ": ", length(spat_not_merged), " zone(s) in spatial but not in tabular: ", spat_not_merged, "\n", file="spatial_merge_warnings.txt",append=TRUE)
        # if (length(tab_not_merged) > 0 | length(spat_not_merged) > 0) {
        #   cat("all tabular zones: ", sort(unique(tabular[Jurisdiction %in% unique(spatial@data$Jurisdiction)]$Zone_ID)), "\n", file="spatial_merge_warnings.txt",append=TRUE)
        #   cat("all spatial zones: ", sort(unique(as.data.table(spatial@data)[Jurisdiction %in% unique(tabular$Jurisdiction)]$Zone_ID)), "\n", file="spatial_merge_warnings.txt",append=TRUE)
        # }
      },
      error = function(e){
        print(paste(current_county, ": not merged", sep = ""))
      }
    )
    
    spatial_clean[[k]] <- spatial_merge
  }

  return(spatial_clean)
}