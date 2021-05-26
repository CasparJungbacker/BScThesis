from parcels import FieldSet, ParticleSet, AdvectionRK4, fieldset
from parcels.particle import JITParticle
import xarray as xr
import numpy as np
import sys
from datetime import timedelta

def main(arg):

    if arg == None:
        print("No file provided")
        sys.exit(2)

    output_fname = arg
    
    fset = FieldSet.from_parcels(basename=arg)

    pset = ParticleSet(fieldset=fset,
                       pclass=JITParticle,
                       lon=np.linspace(4.07301, 4.082842, 10),
                       lat=np.linspace(51.976749, 51.986356, 10),
                       time=timedelta(hours=9).total_seconds())

    output_file = pset.ParticleFile(name=output_fname+"_output.nc",
                                    outputdt=timedelta(minutes=20)) # Always use 20 minutes

    pset.execute(AdvectionRK4,
                 runtime=timedelta(days=1),
                 dt=timedelta(minutes=20),
                 output_file=output_file)

    output_file.export()
    output_file.close()

    return 0

if __name__ == "__main__":
    arg = "../Data/fieldset_surface" # Enter fieldset file here
    main(arg)