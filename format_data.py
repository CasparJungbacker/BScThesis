import xarray as xr
import numpy as np
import fnmatch
import os
import geopandas
import rioxarray
from shapely.geometry import mapping

data_dir = os.path.join("..", "Data")

def file_num(x):
    return x[-5:]

def preprocess(dim):
    
    global data_dir

    if dim not in ["uxg", "uyg", "uzg", "rho", "sal"]:
        raise OSError(f"File {dim} not found") 

    file_list = os.listdir(data_dir)
    nc_files = []
    
    for file in sorted(file_list, key=file_num):
        if fnmatch.fnmatch(file, f"{dim}_part*.nc"):
            nc_files.append(os.path.join(data_dir, str(file)))
            
    ds = xr.open_mfdataset(nc_files, combine="nested", concat_dim="dim_2")
    
    # Spatial coordinates
    latlow = 51.75
    latup = 53
    lonlow = 3
    lonup = 4.75

    res = (1/(60/0.125));
    a = np.arange(lonlow+(res*1.5)/2,lonup,res*1.5) # Longitude 560 values
    b = np.arange(latlow+(res)/2,latup,res) # Latitude 600 values
    
    # Timestamps
    time = np.load("simulation_timestamps.npy")

    # Depths
    depths = np.arange(19, -1, -1) # meters below surface
    
    da = ds.assign_coords({"dim_0": b, "dim_1": a, "dim_2": time, "dim_3": depths}).transpose('dim_2', 'dim_0', 'dim_1', 'dim_3')
    
    da = da.rename({"dim_0": "lat", "dim_1": "lon", "dim_2": "time", "dim_3": "depth"})
    
    return da

def clip(dataarray):

    global data_dir

    da = dataarray.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)

    da.rio.write_crs("epsg:4668", inplace=True)

    shape = geopandas.read_file(data_dir + "/Shapefiles/ne_10m_land.shp")

    clipped = da.rio.clip(shape.geometry.apply(mapping), shape.crs, drop=False, invert=True)

    return clipped
