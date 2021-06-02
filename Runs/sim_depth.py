import cartopy.feature as cf
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import repeat
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

    data_dir = os.path.join("..", "..", "Data")

    nc_data = format_data.NCdata(data_dir)

    print("Clipping Data...")
    uxg = nc_data.clip(nc_data.preprocess("uxg"))
    uyg = nc_data.clip(nc_data.preprocess("uyg"))
    uzg = nc_data.clip(nc_data.preprocess("uzg"))
    rho = nc_data.clip(nc_data.preprocess("rho"))
    sal = nc_data.clip(nc_data.preprocess("sal"))

    ds = xr.Dataset({"U": uxg.__xarray_dataarray_variable__,
                     "V": uyg.__xarray_dataarray_variable__,
                     "W": uzg.__xarray_dataarray_variable__,
                     "R": rho.__xarray_dataarray_variable__,
                     "S": sal.__xarray_dataarray_variable__})

    variables = {"U": "U", "V": "V", "W": "W"}#, "R": "R", "S": "S"}

    dimensions = {"U": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"},
                  "V": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"},
                  "W": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}}#,
                  #"R": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"},
                  #"S": {"lat": "lat", "lon": "lon", "time": "time", "depth": "depth"}}

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

def sample_density(particle, fieldset, time):
    pass

def delete_particle(particle, fieldset, time):
    particle.delete()


def main():

    #ds, fset = fieldset()
    fset = FieldSet.from_parcels("../../Data_local/depth_field_with_density_salinity", extra_fields={"W": "W", "R": "R"},
                                chunksize="auto")

    npart = 20
    lon = 4.075 * np.ones(npart)
    lat = 51.995 * np.ones(npart)
    repeatdt = timedelta(minutes=10)
    depth = np.arange(0,20,1)
    output_dt = timedelta(minutes=10)

    fset.add_constant('halo_north', fset.U.lat[-1])
    fset.add_constant('halo_south', fset.U.lat[0])
    fset.add_constant('halo_west', fset.U.lon[0])

    fset.add_periodic_halo(zonal=True, meridional=True)

    pset = ParticleSet(fieldset=fset, pclass=JITParticle,
                       lon=lon.tolist(), lat=lat.tolist(), depth=depth.tolist(), repeatdt=repeatdt)

    output_file = pset.ParticleFile(name="depth.nc", outputdt=output_dt)

    out_of_bounds_kernel = pset.Kernel(out_of_bounds)

    pset.execute(AdvectionRK4_3D + out_of_bounds_kernel, runtime=timedelta(days=14),
                 dt=output_dt, output_file=output_file, verbose_progress=True, recovery={ErrorCode.ErrorOutOfBounds: delete_particle})

    output_file.export()
    output_file.close()

    return 0


if __name__ == "__main__":
    main()
