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

# commenting out for testing stratified train/test split
# from dask_ml.model_selection import train_test_split

import joblib
from sklearn.model_selection import train_test_split
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

# if the filepath doesn't exist - create directory
if not os.path.exists(output_file_path):
    os.mkdir(output_file_path)

# output filename
out_file = "out_" + test_name + ".txt"

# percentage of dataset set aside for testing
split_per = 0.2

# if there are more than three entries in test name then it is asserting the train/test split
if len(test_name_split) == 4:
    split_per = float(test_name_split[3]) / 100

# flag - True if running the model for NC extent
NC_extent = True

# if there are three entries in test_name then it is one of the random between county tests
if len(test_name_split) == 3:
    # flag - True if running the model for NC extent
    NC_extent = False

# original zones
og_zone_file = "NC_zones_no_protected.tif"

# number of tasks
tasks = 16

# set folder path
input_file_path = os.path.join(os.getcwd(), "pred")


# Helper function for testing - print statements to output file
def send_update(statement):
    f = open(out_file, "a")
    f.write(statement + "\n")
    f.close()


# Helper function for pulling in zoning mask
def read_mask(extent):
    if extent == "NC":
        mask = rasterio.open(
            os.path.join(input_file_path, "NC_county.tif")
        ).read_masks()
    else:
        mask = rasterio.open(os.path.join(input_file_path, og_zone_file)).read_masks()
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
    class_prediction_reshape = read_mask(extent)[0].astype(np.float32)
    class_prediction_reshape[class_prediction_reshape == 1] = np.nan
    class_prediction_reshape[class_prediction_reshape == 0] = rast
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
rasters = glob.glob(os.path.join(input_file_path, "*.tif"))
rasters = sorted(rasters, key=str.casefold)

zone_index = rasters.index(os.path.join(input_file_path, og_zone_file))
county_index = rasters.index(os.path.join(input_file_path, "NC_county.tif"))
rast_list = []

if split_type == "within":
    for i in rasters:
        if (i != os.path.join(input_file_path, "NC_county.tif")) & (
            i != (os.path.join(input_file_path, og_zone_file))
        ):
            rast_list = da_load(rast_list, i)

elif split_type == "between":
    for i in rasters:
        rast_list = da_load(rast_list, i)


# function for reclassifying zones based on chosen hierarchy level
def reclass_hierarchy(hierarchy, reclass):
    # Hierarchy reclassification
    if hierarchy == "core":
        reclass[(reclass >= 100) & (reclass < 200)] = 1
        reclass[(reclass >= 200) & (reclass < 300)] = 2
        reclass[(reclass >= 300) & (reclass < 400)] = 3
    return reclass


# stack rasters along correct axis
t_stack = da.stack(rast_list, axis=2)

# split based on percentage of whole dataset
if split_type == "within":
    zones = imread(os.path.join(input_file_path, og_zone_file), preprocess=clean_rast)
    zones = reclass_hierarchy(hierarchy, zones)
    # double check zones are right
    df = pd.DataFrame(zones.compute())
    # t_stack = t_stack[0].rechunk({0: "auto", 1: t_stack[0].shape[1]})
    t_stack = t_stack[0].rechunk({0: -1, 1: t_stack[0].shape[1]})
    zones = zones.rechunk({1: t_stack.chunks[0][0]})[0]
    # simple random sampling
    # train_features, test_features, train_labels, test_labels = train_test_split(
    #     t_stack, zones, test_size=0.2, train_size=0.8, random_state=42
    # )
    # stratified sampling
    train_features, test_features, train_labels, test_labels = train_test_split(
        # check stratify might need to just be classes (100, 101, etc.))
        t_stack,
        zones,
        test_size=0.2,
        train_size=0.8,
        random_state=42,
    )
    train_features = train_features.persist()
    train_labels = train_labels.persist()
    test_features = test_features.persist()
    test_labels = test_labels.persist()


# split by percentage of counties
elif split_type == "between":
    t_stack = t_stack[0].rechunk({0: "auto", 1: t_stack[0].shape[1]})
    t_stack[:, zone_index] = reclass_hierarchy(hierarchy, t_stack[:, zone_index])
    # avail_county = np.unique(t_stack[:, county_index])

    avail_county = [
        97,
        193,
        179,
        183,
        129,
        63,
        135,
        37,
        85,
        147,
        195,
        191,
        101,
        19,
        133,
        31,
        51,
        119,
        71,
        45,
        105,
        109,
        21,
        159,
        57,
        151,
        59,
        81,
        67,
        41,
        197,
        53,
        89,
        157,
        39,
        87,
        189,
        25,
        55,
    ]

    county_test = np.random.choice(
        avail_county, size=round(len(avail_county) * split_per), replace=False
    )
    county_train = np.array(list(set(avail_county) - set(county_test)))
    send_update("county_test: " + str(county_test))
    send_update("county_train: " + str(county_train))

    # features and zones separated by county
    train_features = t_stack[np.isin(t_stack[:, county_index], county_train)]
    train_features = train_features.persist()
    train_features.compute_chunk_sizes()
    test_features = t_stack[np.isin(t_stack[:, county_index], county_test)]
    test_features = test_features.persist()
    test_features.compute_chunk_sizes()

    # separate zone labels and predictors
    # train_labels = reclass_hierarchy(hierarchy, train_features[:, zone_index])
    # test_labels = reclass_hierarchy(hierarchy, test_features[:, zone_index])

    # separate zone labels and predictors
    train_labels = train_features[:, zone_index]
    test_labels = test_features[:, zone_index]

    train_labels = train_labels.persist()
    train_labels.compute_chunk_sizes()
    test_labels = test_labels.persist()
    test_labels.compute_chunk_sizes()

    # delete county and zone layers from array
    train_features = np.delete(train_features.compute(), zone_index, 1)
    test_features = np.delete(test_features.compute(), zone_index, 1)
    # keeping in county to see
    train_features = np.delete(train_features, county_index, 1)
    test_features = np.delete(test_features, county_index, 1)

    t_stack = np.delete(t_stack, zone_index, 1)
    t_stack = np.delete(t_stack, county_index, 1)

# print sizes of objects as check
send_update("size of t_stack: " + str(t_stack.shape[0]) + " , " + str(t_stack.shape[1]))
send_update(
    "size of train_features: "
    + str(train_features.shape[0])
    + " , "
    + str(train_features.shape[1])
)
send_update("size of train_labels: " + str(train_labels.shape[0]))

# start Dask client
client = Client()
send_update("created client about to initiate RF\n")
with parallel_backend("dask"):
    # Model with undersampling used
    from sklearn.ensemble import RandomForestClassifier

    # Instantiate model with 100 decision trees
    rf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=25,
        max_features=6,
        n_jobs=16,
    )

    # if running balanced
    # rf = RandomForestClassifier(
    #     n_estimators=100,
    #     random_state=42,
    #     max_depth=25,
    #     max_features=6,
    #     n_jobs=16,
    #     class_weight="balanced",
    # )

df = pd.DataFrame(test_labels.compute())
df.to_csv("test_labels.csv", header=False, index=False)

send_update("about to fit RF\n")

# Fit the model on training data
rf.fit(train_features, train_labels)
send_update("RF fit\n")

# remove training data from RAM
del train_features
del train_labels

class_prediction = rf.predict(test_features)
send_update("prediction complete\n")
with open(os.path.join(output_file_path, "class_pred.npy"), "wb") as f:
    np.save(f, class_prediction)

from sklearn.metrics import r2_score

r2 = r2_score(test_labels, class_prediction)
sys.stdout.write("R2 = " + str(r2) + "\n")

# Classificaton Report
from sklearn.metrics import classification_report

sys.stdout.write(classification_report(test_labels, class_prediction, digits=4))
report = classification_report(
    test_labels, class_prediction, digits=4, output_dict=True
)
df = pd.DataFrame(report).transpose()

# add R2 to dataframe
df.loc[len(df.index)] = [r2, r2, r2, r2]
df.to_pickle(os.path.join(output_file_path, "class_report.pkl"))
df.to_csv(os.path.join(output_file_path, "class_report.csv"))
send_update("classification report written\n")

# Confusion Matrix
from sklearn.metrics import confusion_matrix

conf_mat = confusion_matrix(test_labels, class_prediction)
with open(os.path.join(output_file_path, "conf_mat.npy"), "wb") as f:
    np.save(f, conf_mat)
df = pd.DataFrame(conf_mat)
df.to_csv(os.path.join(output_file_path, "conf_mat.csv"))

# predict for whole study area
whole_class_prediction = rf.predict(t_stack)
with open(os.path.join(output_file_path, "whole_class_pred.npy"), "wb") as f:
    np.save(f, whole_class_prediction)

# Get numerical feature importances
importances = rf.feature_importances_

# band names
with open(os.path.join(output_file_path, "feature_import.npy"), "wb") as f:
    np.save(f, importances)

df = pd.DataFrame(importances)
df.to_csv(os.path.join(output_file_path, "feature_import.csv"))

# get predicted layer with NAs put back in
class_prediction_reshape = visualize(whole_class_prediction, "county")

# write output to tif
kwargs = rasterio.open(os.path.join(input_file_path, og_zone_file)).meta
kwargs.update(dtype=rasterio.float32, count=1, compress="lzw")

with rasterio.open(
    os.path.join(output_file_path, "pred_zones.tif"), "w", **kwargs
) as dst:
    dst.write_band(1, class_prediction_reshape.astype(rasterio.float32))

# get NC scale data
if NC_extent == True:
    # clean up
    del t_stack
    del test_features
    del test_labels
    del whole_class_prediction
    del class_prediction_reshape

    # Preprocessing function for stacking images using imread
    # write over clean_rast function with new extent
    def clean_rast(rast):
        extent = "NC"
        # change all nan to 0 in features
        rast = np.nan_to_num(rast, nan=0)
        # open zone mask
        mask = read_mask(extent)
        # mask array
        rast_ma = ma.masked_array(rast, mask=mask, fill_value=-999)
        # compress to remove NA
        comp = ma.compressed(rast_ma)
        return comp

    rast_list = []

    for i in rasters:
        if (
            (i != os.path.join(input_file_path, og_zone_file))
            & (i != os.path.join(input_file_path, "pred_stack.tif"))
        ) & (i != os.path.join(input_file_path, "NC_county.tif")):
            rast_list = da_load(rast_list, i)

    # stack rasters along correct axis
    NC_stack = da.stack(rast_list, axis=2)
    send_update("NC_stack created")

    NC_stack = NC_stack[0].rechunk({0: "auto", 1: NC_stack[0].shape[1]})
    send_update("NC_stack rechunked")

    NC_prediction = rf.predict(NC_stack)
    send_update("NC_stack predicted")

    with open(os.path.join(output_file_path, "NC_pred.npy"), "wb") as f:
        np.save(f, NC_prediction)

    # get layer for all of NC with NAs put back in
    NC_prediction_reshape = visualize(NC_prediction, "NC")

    send_update("reshaped, about to output as .tif")

    # write output to tif
    kwargs = rasterio.open(os.path.join(input_file_path, "NC_county.tif")).meta
    kwargs.update(dtype=rasterio.float32, count=1, compress="lzw")

    with rasterio.open(
        os.path.join(output_file_path, "pred_NC.tif"), "w", **kwargs
    ) as dst:
        dst.write_band(1, NC_prediction_reshape.astype(rasterio.float32))
