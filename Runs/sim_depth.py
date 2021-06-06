import cartopy.feature as cf
import cartopy.crs as ccrs
from numpy.core.fromnumeric import repeat
import sys
sys.path.append("..")
import format_data
import xarray as xr
import numpy as np
from datetime import timedelta
import os

from parcels import FieldSet
from parcels import ParticleSet
from parcels import AdvectionRK4_3D
from parcels import JITParticle
from parcels import ErrorCode
from parcels import Variable


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

def write_fieldset():
    ds, fset = fieldset()
    fset.write("depth_field_with_salinity_density")

def out_of_bounds(particle, fieldset, time):
    if particle.lat < 51.75:
        particle.lat = 51.75
    if particle.lat > 53:
        particle.lat = 53
    if particle.lon < 3:
        particle.lon = 3
    if particle.lon > 4.75:
        particle.lon = 4.75

class SampleParticleInitZero(JITParticle):
    density = Variable("density", initial=0)

def sample_density(particle, fieldset, time):
    particle.density = fieldset.R[time, particle.depth, particle.lat, particle.lon]

def delete_particle(particle, fieldset, time):
    particle.delete()

def push_from_surface(particle, fieldset, time):
    if particle.depth < 0.1:
        particle.depth = 0.1
    if particle.depth > 18.9:
        particle.depth = 18.9


def main(timestamp, runtime, repeat=False):

    # write_fieldset()
    day = timestamp[0]
    hour = timestamp[1]
    minute = timestamp[2]
    runtime = runtime

    print(50*"-") 
    print(f"Simulation on {timestamp}, for {runtime} days")
    print(50*"-") 

    output_name = f"output_with_depth_{day}_{hour}_{minute}.nc"

    fset = FieldSet.from_parcels("../../Data/depth_field_with_density_salinity", extra_fields={"W": "W", "R": "R"},
                                 chunksize=False)

    npart = 20
    lon = 4.1 * np.ones(npart)
    lat = 52.125 * np.ones(npart)
    repeatdt = timedelta(minutes=10) if repeat else None
    depth = np.arange(0, 20, 1)
    output_dt = timedelta(minutes=10)

    fset.add_constant('halo_north', fset.U.lat[-1])
    fset.add_constant('halo_south', fset.U.lat[0])
    fset.add_constant('halo_west', fset.U.lon[0])

    fset.add_periodic_halo(zonal=True, meridional=True)

    pset = ParticleSet(fieldset=fset,
                       pclass=SampleParticleInitZero,
                       lon=lon, lat=lat, depth=depth,
                       time=timedelta(days=day-17, hours=hour, minutes=minute).total_seconds(),
                       repeatdt=repeatdt)

    density_kernel = pset.Kernel(sample_density)
    out_of_bounds_kernel = pset.Kernel(out_of_bounds)
    push_from_surface_kernel = pset.Kernel(push_from_surface)

    pset.execute(density_kernel, dt=0)

    output_file = pset.ParticleFile(name=output_name, outputdt=output_dt)

    pset.execute(AdvectionRK4_3D + density_kernel, runtime=timedelta(hours=3, minutes=30),
                 dt=output_dt, output_file=output_file, verbose_progress=True, recovery={ErrorCode.ErrorOutOfBounds: delete_particle})

    pset.repeatdt = None

    pset.execute(AdvectionRK4_3D + density_kernel + push_from_surface_kernel, runtime=timedelta(days = runtime),
                 dt=output_dt, output_file=output_file, verbose_progress=True, recovery={ErrorCode.ErrorOutOfBounds: delete_particle})

    output_file.export()
    output_file.close()

    return 0

if __name__ == "__main__":
    timestamps = [(17,7,40)]#, (17,1,10), (18,9,0)] # (day, hour, minute)
    runtime = [5]#, 13, 12] # Days
    repeat = True
    for timestamp, runtime in zip(timestamps, runtime):
        main(timestamp, runtime, repeat)
