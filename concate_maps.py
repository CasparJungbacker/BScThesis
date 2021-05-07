# -*- coding: utf-8 -*-
"""
Created on Thu May  6 17:55:37 2021

Goal: (1) concatenate map files, (2) interpolate merged map file to regular grid

@author: 920507
"""
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

path = r'O:\DCSM output sept14'

df5 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0005_map.nc')
df6 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0006_map.nc')
df7 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0007_map.nc')
df8 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0008_map.nc')
df9 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0009_map.nc')
    

#df_merged =    xr.concat(objs = [df5.ucx,df6.ucx,df7.ucx,df8.ucx,df9.ucx],
#                          dim = 'nFlowElem',
#                          # data_vars = ['ucx'],
#                          coords = 'minimal')

ucx =    xr.concat(objs = [df5.ucx,df6.ucx,df7.ucx,df8.ucx,df9.ucx],
                          dim = 'nFlowElem',
                          # data_vars = ['ucx'],
                          coords = 'minimal')

## variables
# ucx - horizontal velocity west->east
# ucy - horizontal velocity south->north
# rho - density 
# ucz - vertical velocity (not sure if you need this already since you only consider the surface layer now)
# optional: sa1 - salinity


#ucy =    xr.concat(objs = [df5.ucy,df6.ucy,df7.ucy,df8.ucy,df9.ucy],
#                          dim = 'nFlowElem',
#                          # data_vars = ['ucy'],
#                          coords = 'minimal')
#
#ucz =    xr.concat(objs = [df5.ucz,df6.ucz,df7.ucz,df8.ucz,df9.ucz],
#                          dim = 'nFlowElem',
#                          # data_vars = ['ucy'],
#                          coords = 'minimal')
# ds_merged = xr.concat(objs = [df5,df6,df7,df8,df9],
#                           dim = 'nFlowElem',
#                           # data_vars = ['ucx'],
#                           coords = 'minimal',
#                           compat='equals')

##Check if it worked
#plt.figure
#plt.scatter(df_merged.FlowElem_xcc,df_merged.FlowElem_ycc)

ux = ucx.transpose('nFlowElem','time','laydim').loc[dict(laydim=19)]

xc = ucx.FlowElem_xcc
yc = ucx.FlowElem_ycc
x = xc.values
y = yc.values

########################################################################
#Define what structured grid - which we're gonna fill - should look like
latlow = 51.75
latup = 53
lonlow = 3
lonup = 4.75

res = (1/(60/0.125));
a = np.arange(lonlow+(res*1.5)/2,lonup,res*1.5) #longitude 560 values
b = np.arange(latlow+(res)/2,latup,res) #latitude 600 values

xint,yint = np.meshgrid(a,b) #560 lon x 600 lat

xint = xr.DataArray(xint)
yint = xr.DataArray(yint)

times_pd = ucx.time

##########################################################
#Function to fill grid with velocity data 

def interp_to_grid(u,xc,yc,xint,yint):
    print(u.shape,xc.shape,xint.shape)
    ug = griddata((xc,yc),u,(xint,yint), method='nearest', fill_value=np.nan)
    return ug 

##########################################################
#Fill grid with velocity data 
uxg = xr.apply_ufunc(interp_to_grid,
                     ux, xc, yc, xint, yint,
                     dask = 'allowed',
                     input_core_dims=[['nFlowElem','time'],['nFlowElem'],['nFlowElem'],['dim_0','dim_1'],['dim_0','dim_1']],
                     output_core_dims=[['dim_0','dim_1','time']],
                     output_dtypes = [xr.DataArray]
                     )

#uxg.to_netcdf(path where to save)
#
#uyg = xr.apply_ufunc(interp_to_grid,
#                     uy, xc, yc, xint, yint,
#                     dask = 'allowed',
#                     input_core_dims=[['nFlowElem','time'],['nFlowElem'],['nFlowElem'],['dim_0','dim_1'],['dim_0','dim_1']],
#                     output_core_dims=[['dim_0','dim_1','time']],
#                     output_dtypes = [xr.DataArray]
#                     )

#uyg.to_netcdf(path where to save)

#ds_layer = xr.Dataset({
#    'uxg_xarray': (('latitude','longitude','time'),uxg),
#    'uyg_xarray': (('latitude','longitude','time'),uyg),
#    'latitude': ('latitude', b, {'units': 'degree_north'}), 
#    'longitude': ('longitude', a, {'units': 'degree_east'}),
#    'time': ('time', times_pd)
#    })
#
#ds_layer.to_netcdf(path where to save)
