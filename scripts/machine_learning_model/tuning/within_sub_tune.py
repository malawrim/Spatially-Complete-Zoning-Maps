import sys

# for distributed mem
from mpi4py import MPI
import psutil

# comm = MPI.COMM_WORLD

# rank = comm.Get_rank()
# cpuNumber = psutil.Process().cpu_num()
# nodeName = MPI.Get_processor_name()

# let dask and MPI work together
from dask_mpi import initialize

initialize()

from dask.distributed import Client

import dask.dataframe as dd
import dask.array as da
import dask.bag as db
from dask.array.image import imread
from dask_ml.model_selection import train_test_split

import joblib
from sklearn.utils import parallel_backend

import glob
import os

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import rasterio
from rasterio.plot import show

from sklearn.ensemble import RandomForestClassifier

# get file name from which you will determine other variables
test_name = os.path.basename(__file__).split(".")[0]
test_name_split = test_name.split("_")

# within or between tests?
split_type = test_name_split[0]

# core or sub districts?
hierarchy = test_name_split[1]

# set folder path for output metrics
output_file_path = os.path.join(os.getcwd(), test_name)

# output filename
out_file = "out_" + test_name + ".txt"

# percentage of dataset set aside for testing
split_per = 0.2

# if there are more than three entries in test name then it is asserting the train/test split
if len(test_name_split) == 4:
    split_per = float(test_name_split[3]) / 100

# original zones
og_zone_file = "NC_zones_no_protected.tif"

# number of tasks
tasks = 16

# set folder path
file_path = os.path.join(os.getcwd(), "pred")

# Helper function for testing - print statements to output file
def send_update(statement):
    f = open(out_file, "a")
    f.write(statement + "\n")
    f.close()


# Helper function for pulling in zoning mask
def read_mask(extent):
    if extent == "NC":
        mask = rasterio.open(os.path.join(file_path, "NC_county.tif")).read_masks()
    else:
        mask = rasterio.open(os.path.join(file_path, og_zone_file)).read_masks()
    mask[mask == 0] = 1
    mask[mask == 255] = 0
    return mask


# Preprocessing function for stacking images using imread
def clean_rast(rast):
    extent = "zones"
    # change all nan to 0 in features
    rast = np.nan_to_num(rast, nan=0)
    # open zone mask
    mask = read_mask(extent)
    # mask array
    rast_ma = ma.masked_array(rast, mask=mask, fill_value=-999)
    # compress to remove NA
    comp = ma.compressed(rast_ma)
    return comp


# Function to reshape the compressed arrays (add back NAs) and visualize
def visualize(rast, extent):
    class_prediction_reshape = read_mask(extent)[0]
    class_prediction_reshape[class_prediction_reshape == False] = rast
    # plt.imshow(class_prediction_reshape)
    return class_prediction_reshape


# Helper function to load .tif and stack
def da_load(rast_list, filename):
    f = open(out_file, "a")
    f.write(filename)
    f.write("\n")
    f.close()
    im = imread(filename, preprocess=clean_rast)
    rast_list.append(im)
    return rast_list


# load files
rasters = glob.glob(os.path.join(file_path, "*.tif"))
rasters = sorted(rasters, key=str.casefold)
rast_list = []

for i in rasters:
    if (i != (os.path.join(file_path, og_zone_file))) & (
        i != (os.path.join(file_path, "pred_stack.tif"))
    ):
        rast_list = da_load(rast_list, i)

zones = imread(os.path.join(file_path, og_zone_file), preprocess=clean_rast)

# stack rasters along correct axis
t_stack = da.stack(rast_list, axis=2)
# t_stack = t_stack[0].rechunk({0: "auto", 1: t_stack[0].shape[1]})

# function for reclassifying zones based on chosen hierarchy level
def reclass_hierarchy(hierarchy, reclass):
    # Hierarchy reclassification
    if hierarchy == "core":
        reclass[(reclass >= 100) & (reclass < 200)] = 1
        reclass[(reclass >= 200) & (reclass < 300)] = 2
        reclass[(reclass >= 300) & (reclass < 400)] = 3
    return reclass


zones = reclass_hierarchy(hierarchy, zones)

# double check zones are right
df = pd.DataFrame(zones.compute())
df.to_csv("zones.csv", header=False, index=False)
# remove zones from comp_t
# t_stack = np.delete(t_stack, 40, 1)
# t_stack = t_stack.rechunk({0: "auto", 1: t_stack.shape[1]})

f = open(out_file, "a")
f.write("size of t_stack: ")
f.write(str(t_stack.shape[0]))
f.write(" , ")
f.write(str(t_stack.shape[1]))
f.write("\nsize of zones: ")
f.write(str(zones.shape[0]))
f.write(" , ")
f.write(str(zones.shape[1]))
f.close()

t_stack = t_stack[0].rechunk({0: "auto", 1: t_stack[0].shape[1]})
zones = zones.rechunk({1: t_stack.chunks[0][0]})[0]
train_features, test_features, train_labels, test_labels = train_test_split(
    t_stack, zones, test_size=0.2, train_size=0.8, random_state=42
)
f = open(out_file, "a")
f.write("\nsize of train_features: ")
f.write(str(train_features.shape[0]))
f.write(" , ")
f.write(str(train_features.shape[1]))
f.write("\nsize of train_labels: ")
f.write(str(train_labels.shape[0]))
f.close()

# start Dask client
client = Client()
f = open(out_file, "a")
f.write("created client about to initiate RF\n")
f.close()
with parallel_backend("dask"):
    # Model with undersampling used
    from sklearn.ensemble import RandomForestClassifier

    # Instantiate model with 100 decision trees
    rf = RandomForestClassifier()

df = pd.DataFrame(test_labels.compute())
df.to_csv("test_labels.csv", header=False, index=False)

f = open(out_file, "a")
f.write("about to fit RF\n")
f.close()

# persist training_features in memory
train_features = train_features.persist()
train_labels = train_labels.persist()

# Tuning
from sklearn.model_selection import GridSearchCV

# Create the parameter grid based on the results of random search
# testing really short version to see how long it takes and if it works
param_grid = {
    "random_state": [42],
    "max_depth": [10, 25],
    "max_features": [5, 6],
    "n_estimators": [50],
}
# param_grid = {
#     "random_state": [42],
#     "max_depth": [10, 25, 50],
#     "max_features": [4, 5, 6, 7],
#     "n_estimators": [50, 100, 250],
# }
# Instantiate the grid search model
grid_search = GridSearchCV(
    estimator=rf, param_grid=param_grid, cv=3, n_jobs=16, verbose=2
)

send_update("grid search called")

# Fit the grid search to the data
grid_search.fit(train_features, train_labels)
grid_search.best_params_
send_update("grid search fit")

df = pd.DataFrame.from_dict(grid_search.cv_results_)
df.to_csv("tuning_results.csv", header=False, index=False)

send_update("grid search results written to csv")

best_grid = grid_search.best_estimator_


def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    print("Model Performance")
    print("Average Error: {:0.4f} degrees.".format(np.mean(errors)))
    print("Accuracy = {:0.2f}%.".format(accuracy))

    return accuracy


send_update("About to eval grid search")

grid_accuracy = evaluate(best_grid, test_features, test_labels)
grid_accuracy
