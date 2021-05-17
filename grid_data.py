# -*- coding: utf-8 -*-
"""
Created on Fri May  7 12:19:59 2021

Goal: attempting dask parallelized approach for large concatenated map files

@author: 920507
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
#from metpy.units import units

path = r'O:\DCSM output sept14'

df5 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0005_map.nc')
df6 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0006_map.nc')
df7 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0007_map.nc')
df8 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0008_map.nc')
df9 = xr.open_mfdataset(path+'\DCSM-FM_RW1_sept14_0009_map.nc')

df5 = df5.drop_dims(['nBndLink','nNetNode','wdim','nFlowElemContourPts','nFlowLink','nNetLink','nNetElem','nmesh2d_EnclosurePoints','nmesh2d_EnclosureInstance', 'nmesh2d_EnclosureParts'])
df6 = df6.drop_dims(['nBndLink','nNetNode','wdim','nFlowElemContourPts','nFlowLink','nNetLink','nNetElem','nmesh2d_EnclosurePoints','nmesh2d_EnclosureInstance', 'nmesh2d_EnclosureParts'])
df7 = df7.drop_dims(['nBndLink','nNetNode','wdim','nFlowElemContourPts','nFlowLink','nNetLink','nNetElem','nmesh2d_EnclosurePoints','nmesh2d_EnclosureInstance', 'nmesh2d_EnclosureParts'])
df8 = df8.drop_dims(['nBndLink','nNetNode','wdim','nFlowElemContourPts','nFlowLink','nNetLink','nNetElem','nmesh2d_EnclosurePoints','nmesh2d_EnclosureInstance', 'nmesh2d_EnclosureParts'])
df9 = df9.drop_dims(['nBndLink','nNetNode','wdim','nFlowElemContourPts','nFlowLink','nNetLink','nNetElem','nmesh2d_EnclosurePoints','nmesh2d_EnclosureInstance', 'nmesh2d_EnclosureParts'])

df = xr.combine_nested([df5,df6,df7,df8,df9],concat_dim='nFlowElem')
df = df.drop(labels=['mesh2d_enclosure_container','Mesh2D','FlowElemDomain','FlowElemGlobalNr','FlowElem_bac','FlowElem_xzw','FlowElem_yzw','ucxa','ucya','timestep'])

df = df.isel(time=slice(100)).transpose('nFlowElem','time','laydim')

df = df.chunk({'nFlowElem': -1,'time':1})

#df =    xr.concat(objs = [df5.ucx,df6.ucx,df7.ucx,df8.ucx,df9.ucx],
#                          dim = 'nFlowElem',
#                          coords = 'minimal')
#df = df.chunk({'time':1})
# df_merged_y =    xr.concat(objs = [df5.ucy,df6.ucy,df7.ucy,df8.ucy,df9.ucy],
#                           dim = 'nFlowElem',
#                           # data_vars = ['ucy'],
#                           coords = 'minimal')

#ux = df_merged.transpose('nFlowElem','time','laydim') #.loc[dict(laydim=19)]
# uy = df_merged_y.transpose('nFlowElem','time','laydim') #.loc[dict(laydim=19)]

#xc = df_merged.FlowElem_xcc
#yc = df_merged.FlowElem_ycc
#x = xc.values
#y = yc.values

########################################################################
#Define what structured grid - which we're gonna fill - should look like
latlow = 51.75
latup = 53
lonlow = 3
lonup = 4.75

df1 = df.where(df.FlowElem_xcc > lonlow, drop = True)
df2 = df1.where(df1.FlowElem_xcc < lonup, drop = True)
df3 = df2.where(df2.FlowElem_ycc < latup, drop = True)
df4 = df3.where(df3.FlowElem_ycc > lonup, drop = True)

res = (1/(60/0.125));
a = np.arange(lonlow+(res*1.5)/2,lonup,res*1.5) #longitude 560 values
b = np.arange(latlow+(res)/2,latup,res) #latitude 600 values

xint,yint = np.meshgrid(a,b) #560 lon x 600 lat

xint = xr.DataArray(xint)
yint = xr.DataArray(yint)

#times_pd = df_merged.time

##########################################################
#Function to fill grid with velocity data 

def interp_to_grid(u,xc,yc,xint,yint):
    print(u.shape,xc.shape,xint.shape) 
    print(type(u),type(xc),type(xint))
    # u = np.moveaxis(u, [0,1,2], [1,2,0] )
    ug = griddata((xc,yc),u,(xint,yint), method='nearest', fill_value=np.nan)
    # print(ug.shape)
    return ug 
#
#uxg = xr.apply_ufunc(interp_to_grid,
#                     df4.ucx, x, y, xint, yint,
#                     dask = 'allowed',
#                     input_core_dims=[['nFlowElem','time','laydim'],['nFlowElem'],['nFlowElem'],['dim_0','dim_1'],['dim_0','dim_1']],  
#                     output_core_dims=[['dim_0','dim_1','time','laydim']],
#                     )
#uxg1 = xr.apply_ufunc(interp_to_grid,
#                     df4.ucx, df4.FlowElem_xcc, df4.FlowElem_xcc, xint, yint,
#                     dask = 'allowed',
#                     input_core_dims=[['nFlowElem'],['nFlowElem'],['nFlowElem'],['dim_0','dim_1'],['dim_0','dim_1']],
#                     output_core_dims=[['dim_0','dim_1']],
#                     output_dtypes = [xr.DataArray]
#                     )
    
x = df4.FlowElem_xcc.values
y = df4.FlowElem_xcc.values

uxg = interp_to_grid(df4.ucx.values, x, y, xint, yint)
uxg = xr.DataArray(uxg)

uxg.to_netcdf(path+'\\uxg.nc')

del uxg

uyg = interp_to_grid(df4.ucy.values, x, y, xint, yint)
uyg = xr.DataArray(uyg)

uyg.to_netcdf(path+'\\uyg.nc')

del uyg

uzg = interp_to_grid(df4.ucz.values, x, y, xint, yint)
uzg = xr.DataArray(uzg)

uzg.to_netcdf(path+'\\uzg.nc')

del uzg

rho = interp_to_grid(df4.rho.values, x, y, xint, yint)
rho = xr.DataArray(rho)

rho.to_netcdf(path+'\\rho.nc')

del rho

sa1 = interp_to_grid(df4.sa1.values, x, y, xint, yint)
sa1 = xr.DataArray(sa1)

sa1.to_netcdf(path+'\\sal.nc')

del sa1