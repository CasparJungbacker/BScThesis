import xarray as xr
import numpy as np
import fnmatch
import os

data_dir = os.path.join("..", "Data")

def preprocess(dim):
    
    global data_dir
    
    files = []

    if dim not in ["uxg", "uyg", "uzg", "rho", "sal"]:
        raise OSError(f"File {dim} not found") 
    
    for file in os.listdir(data_dir):
        if fnmatch.fnmatch(file, f"{dim}_part*.nc"):
            files.append(os.path.join(data_dir, str(file)))
            
    ds = xr.open_mfdataset(files, combine="nested", concat_dim="dim_2")
    
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