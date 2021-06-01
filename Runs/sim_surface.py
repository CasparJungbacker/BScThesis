from attr import fields
import cartopy.feature as cf
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy.core.numeric import indices
from parcels.field import Field
from parcels.kernels.advection import AdvectionRK4
import sys
sys.path.append("..")
import format_data
import xarray as xr
import numpy as np
from datetime import timedelta
from parcels import FieldSet, ParticleSet, AdvectionRK4_3D, JITParticle, plotTrajectoriesFile, ErrorCode
import os

def fieldset():

    data_dir = os.path.join("..", "..", "Data_local")

    nc_data = format_data.NCdata(data_dir)

    uxg = nc_data.clip(nc_data.preprocess("uxg"))
    uyg = nc_data.clip(nc_data.preprocess("uyg"))

    ds = xr.Dataset({"U": uxg.__xarray_dataarray_variable__,
                     "V": uyg.__xarray_dataarray_variable__})

    variables = {"U": "U", "V": "V"}

    dimensions = {"U": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"},
                  "V": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}}

    return ds, FieldSet.from_xarray_dataset(ds=ds, variables=variables, dimensions=dimensions)

def out_of_bounds(particle, fieldset, time):
    if particle.lat < 51.75:
        particle.lat = 51.75
    if particle.lat > 53:
        particle.lat = 53
    if particle.lon < 3:
        particle.lon = 3
    if particle.lon > 4.75:
        particle.lon = 4.75

def main():

    fset = FieldSet.from_parcels("../../Data/surface_field", indices={"depth": [19]})

    nsteps = 144*14  # Particle every 10 minutes
    lon = 4.075 * np.ones(nsteps)
    lat = 51.995 * np.ones(nsteps)
    depth = np.zeros(nsteps)
    time = np.arange(0, nsteps) * timedelta(minutes=10).total_seconds()
    output_dt = timedelta(minutes=10)

    fset.add_constant('halo_north', fset.U.lat[-1])
    fset.add_constant('halo_south', fset.U.lat[0])
    fset.add_constant('halo_west', fset.U.lon[0])

    fset.add_periodic_halo(zonal=True, meridional=True)

    pset = ParticleSet(fieldset=fset, pclass=JITParticle,
                       lon=lon, lat=lat, depth=depth, time=time)

    output_file = pset.ParticleFile(name="surface.nc", outputdt=output_dt)

    out_of_bounds_kernel = pset.Kernel(out_of_bounds)

    pset.execute(AdvectionRK4 + out_of_bounds_kernel, runtime=timedelta(days=14),
                 dt=output_dt, output_file=output_file, verbose_progress=True)

    output_file.export()
    output_file.close()

    return 0


if __name__ == "__main__":
    main()
