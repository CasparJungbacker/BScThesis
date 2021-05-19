'''

This script merges interpolated files and adds coordinates + timestamps

'''

import xarray as xr
import numpy as np
import fnmatch
import os

def get_files():

    files = []

    for file in os.listdir("../Data"):
        if fnmatch.fnmatch(file, "uxg*.nc"):
            files.append("../Data/" + str(file))

    return files

if __name__ == "__main__":

    # List of files
    files = get_files()
    
    # Load from list
    ds = xr.open_mfdataset(files, combine="nested", concat_dim='dim_2', chunks={'dim_2': 10}, parallel=True)

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

    # Depth
    depths = np.arange(19, -1, -1) # meters below surface

    da = ds.assign_coords({"dim_0": b, "dim_1": a, "dim_2": time, "dim_3": depths}).transpose('dim_2', 'dim_0', 'dim_1', 'dim_3')
    da.rename({"dim_0": "lat", "dim_1": "lon", "dim_2": "time", "dim_3": "depth"})
    da.to_netcdf("../Data/uxg_with_coords.nc")

