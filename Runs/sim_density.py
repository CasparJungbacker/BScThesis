import xarray as xr
import numpy as np
from datetime import timedelta
from parcels import FieldSet, ParticleSet, AdvectionRK4_3D, JITParticle, plotTrajectoriesFile
import os
import sys
sys.path.append("..")
import format_data
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cf

if __name__=="__main__":
    data_dir = format_data.data_dir(os.path.join("..", "..", "Data_local"))

    uxg = data_dir.preprocess("uxg")
    uyg = data_dir.preprocess("uyg")
    uzg = data_dir.preprocess("uzg")

    uxg_clipped = data_dir.clip(uxg)
    uyg_clipped = data_dir.clip(uyg)
    uzg_clipped = data_dir.clip(uzg)

    ds = xr.Dataset({"U": uxg_clipped.__xarray_dataarray_variable__,
                     "V": uyg_clipped.__xarray_dataarray_variable__,
                     "W": uzg_clipped.__xarray_dataarray_variable__})

    variables = {"U": "U", "V": "V", "W":"W"}#, "R": "rho"}
    dimensions = {"U": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}, 
                  "V": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}, 
                  "W": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}}

    nsteps = 7 # 7 timesteps of a particle at every meter depth
    npart = 20
    lon = 4.075 * np.ones(nsteps*npart) 
    lat = 51.995 * np.ones(nsteps*npart)
    depth = np.tile(np.arange(0, 20, 1), nsteps)
    time = (np.arange(0, nsteps) * timedelta(minutes=30).total_seconds()) + timedelta(days=4).total_seconds() 
    time = np.repeat(time, npart)# Drop particles at 20 minute interval after 11:30 at 20-09
    output_dt = timedelta(minutes=20)

    pset = ParticleSet(fieldset=fieldset,
                       pclass=JITParticle,
                       lon=lon,
                       lat=lat,
                       depth=depth,
                       time=time)

    output_file = pset.ParticleFile(name="depth_test.nc", outputdt=output_dt)

    pset.execute(AdvectionRK4_3D,
             runtime=timedelta(days=2),
             dt=output_dt,
             output_file=output_file,
             verbose_progress=True)

    output_file.export()
    output_file.close()