# Spatially-Continuous-Zoning-Maps
 Repository for scripts necessary to process, run, and analyze machine learning model used to predict zoning at scale.

|Script Name |	Folder Location | Language |	General Purpose |	Detailed Purpose |
|------------|-----------------|----------|-----------------|------------------|
|zone_cleaning	| zone_data_cleaning | R	| Preprocessing |	Merge spatial and tabular zoning data |
|zone_spatial_cleaning	| zone_data_cleaning | R	| Preprocessing |	Clean jurisdictions spatial zoning data to prepare for merging with tabular data |
|zone_tabular_cleaning	| zone_data_cleaning | R	| Preprocessing |	Clean jurisdictions tabular zoning data to prepare for merging with spatial data |
|zoning_shape_to_rast	| zone_data_cleaning | Python	| Preprocessing |	Load reclassified zoning shapefiles in GRASS GIS Environment |
|zoning_inputs	| predictor_cleaning | Python	| Preprocessing |	Clean and set extent for all predictors for zoning model |
|generic_zoning_script	| machine_learning_model | Python	| Random Forest	| Run random forest on HPC for zoning project. Generic script copied to run many iterations of the model including between-county and within-county models|
|zone_python	| base folder | YAML |	Environment | Conda environment for project |
|copy_scripts	| machine_learning_model | Python |	Miscellaneous	| Copy generic_zoning_script.py to run multiple iterations of model on HPC |
|make_batch	| machine_learning_model | Python |	Miscellaneous	| Create batch scripts for all versions of generic_zoning_script |
|zone_postprocess_between	| post_process | Python Notebook |	post-processing results	| Compute average performance of between-county model runs - precision, recall, F1, R2, feature importance|
|zone_postprocess	| post_process | Python |	post-processing results	| Generates accuracy maps in GRASS GIS|
