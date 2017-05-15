
# coding: utf-8

# Python script to convert raw data in a .netcdf file into residuals
# via a linear decomposition approach: first the trend is calculated and subtracted, then a cyclical component. 
# Usage in command line:
# python Time_series_decomposition.py resolution infile.nc outfile.nc
# 
# resolution should be one of monthly - weekly - daily

# Import libraries
import os
import glob
import sys
import pandas as pd
import xarray as xr
import numpy as np
import scipy.stats # for calculation of trend

from tqdm import tqdm # progressbar

#-----COMMAND LINE ARGUMENTS----#
resolution = sys.argv[1]
infile = sys.argv[2]
outfile = sys.argv[3]
#-------------------------------#

assert resolution in ['monthly', 'weekly', 'daily'],	 "Resolution should be one of ('monthly', 'weekly', 'daily'"

# Define function to calculate the trend
def calc_trend(ndarray, t):
    """Calculate linear trend
    Inputs
    ------
    x: numpy array with original data
    t: np array with timestamps
    
    Returns
    --------
    T: estimate of the linear trend    
    """
    slope = scipy.stats.linregress(t, ndarray).slope
    intercept = scipy.stats.linregress(t, ndarray).intercept
    T = t*slope + intercept
    return(T)


# Read in data
LAI = xr.open_dataset(infile)

# Extract to numpy
print('Extracting data to numpy...')
LAI_npdata = LAI['LAI'].values
npshape = LAI_npdata.shape
print('Done!')

# Numpy array to store trend component
LAI_trend_np = np.ndarray(shape=npshape)

print('Starting loop...')
# Loop over pixels, store the trend component 
for lat in tqdm(range(0,len(LAI.lat))):
    for lon in range(0,len(LAI.lon)):
        if not np.all(np.isnan(LAI_npdata[:,lat,lon])): # skip if all data is NaN for this pixel
            LAI_trend_np[:,lat,lon] = calc_trend(LAI_npdata[:,lat,lon], np.arange(0,npshape[0]))
        else:
            LAI_trend_np[:,lat,lon]=np.nan
            
print('Detrending done...')

# Store trend component in xarray dataArray
LAI_trend = xr.DataArray(LAI_trend_np, dims=['time', 'lat', 'lon'],
                               coords=LAI.coords)
# Calculate detrended data
LAI_detrended = LAI - LAI_trend

# Estimate cycle component
# Conform the cycle component onto the same index as the detrended data, and extract to numpy array so we
# can extract it element-wise

if resolution == 'monthly':
    y_w_mean = LAI_detrended.groupby('time.month').mean(dim='time') # monthly resolution
    y_w_mean_expanded = y_w_mean.reindex({'month': LAI_detrended.time.to_series().index.month})['LAI'].values 
elif resolution == 'weekly':
    y_w_mean = LAI_detrended.groupby('time.weekofyear').mean(dim='time') # weekly resolution
    y_w_mean_expanded = y_w_mean.reindex({'weekofyear': LAI_detrended.time.to_series().index.weekofyear})['LAI'].values 
elif resolution == 'daily':
    y_w_mean = LAI_detrended.groupby('time.dayofyear').mean(dim='time') # daily resolution
    y_w_mean_expanded = y_w_mean.reindex({'dayofyear': LAI_detrended.time.to_series().index.dayofyear})['LAI'].values 

else:
    print('Provide adequate resolution')

# Finally, obtain residuals
LAI_resid = LAI_detrended-y_w_mean_expanded

print('Done!')

# dump
LAI_resid.to_netcdf(outfile)



