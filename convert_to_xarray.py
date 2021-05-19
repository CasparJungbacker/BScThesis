'''

This script provides functions that convert the interpolated files
to the correct xarray dataset for use with oceanparcels, that is,
the array is transposed and coordinates + timesteps are added.

'''

import xarray as xr
import numpy as np
import fnmatch
import os

# List of files
files = []
for file in os.listdir("../Data"):
    if fnmatch.fnmatch(file, "uxg*.nc"):
        files.append("../Data/" + str(file))
        
ds = xr.open_mfdataset(files, chunks=16, concat_dim="dim_2", parallel=True)
del ds