# BScThesis
BSc Thesis concerning particle tracking in the Rhine ROFI

Runs/ contains the files used to perform particle simulations, as well as the notebooks used to postprocess these simulations

grid_data.py is used to interpolate the Delft3D data on a structured grid. Keep in mind that time is sliced, the slice can be changed in line #33

format_data.py is used to parse the interpolated files, and return a single xarray dataset containing all the timesteps. The file also contains a method to mask land data

plot_domain_data.ipynb and plot_his_data are used to plot some quantities of the Delft3D output
