# Spatially-Continuous-Zoning-Maps
 Repository for scripts neccessary to process, run, and analyze machine learning model used to predict zoning at scale.

|Script Name |	Language |	General Purpose |	Detailed Purpose |
|------------|----------|-----------------|------------------|
|zone_postprocess	|Python Notebook|	Visualization	|visualize results for within-county implementation - Precision, recall, F1, R2, Feature importance|
|generic_zoning_script	|Python	Random Forest	script to run random forest on HPC for zoning project. Generic script copied to run many iterations of model including between and within-county implementations.|
|copy_scripts	|Python|	Miscellaneous	|Used to copy generic_zoning_script.py to run multiple iterations of model on HPC|
|copy_scripts	|Batch (.csh)	|Miscellaneous	|Batch script used to run copy scripts|
|make_batch	|Python|	Miscellaneous	|Create batch scripts for all versions of generic_zoning_script |
|make_batch	|Batch (.csh)|	Miscellaneous|	Batch script used to run make_batch|
|zone_cleaning	|R	|Preprocessing|	merge spatial and tabular zoning data|
|zone_spatial_cleaning	|R	Preprocessing|	clean jurisidictions spatial zoning data to prepare for merging with tabular data |
|zone_tabular_cleaning	|R	Preprocessing|	clean jurisidictions tabular zoning data to prepare for merging with spatial data |
|zoning_inputs	|Python	|Preprocessing|	clean and set extent for all predictors for zoning model|
|zone_python	|YAML|	Environment|	Environment for Zoning project (on HPC)|
