# Spatially-Continuous-Zoning-Maps
 Repository for scripts necessary to process, run, and analyze machine learning model used to predict zoning at scale.

|Script Name |	Language |	General Purpose |	Detailed Purpose |
|------------|----------|-----------------|------------------|
|zone_postprocess	| Python Notebook |	Visualization	| Visualize results for within-county implementation - precision, recall, F1, R2, feature importance|
|generic_zoning_script	| Python	| Random Forest	| Run random forest on HPC for zoning project. Generic script copied to run many iterations of the model including between-county and within-county models|
|copy_scripts	| Python |	Miscellaneous	| Copy generic_zoning_script.py to run multiple iterations of model on HPC |
|copy_scripts	| Batch (.csh)	| Miscellaneous	| Batch script used to run copy scripts |
|make_batch	| Python |	Miscellaneous	| Create batch scripts for all versions of generic_zoning_script |
|make_batch	| Batch (.csh) |	Miscellaneous |	Batch script used to run make_batch |
|zone_cleaning	| R	| Preprocessing |	Merge spatial and tabular zoning data |
|zone_spatial_cleaning	| R	| Preprocessing |	Clean jurisdictions spatial zoning data to prepare for merging with tabular data |
|zone_tabular_cleaning	| R	| Preprocessing |	Clean jurisdictions tabular zoning data to prepare for merging with spatial data |
|zoning_inputs	| Python	| Preprocessing |	Clean and set extent for all predictors for zoning model |
|zone_python	| YAML |	Environment |	Environment for zoning project (on HPC) |
