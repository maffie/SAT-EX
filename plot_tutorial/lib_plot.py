#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 08:51:54 2017
Plotting functions
@author: stijndc
"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import colors as colors
from mpl_toolkits.basemap import Basemap


def convert_data(DF, key='R', cutoff=False):
    """
    Convert pandas dataframa to numpy array suitable for plotting with basemap.
    Dataframe should have columns 'lat', 'lon' and some key value to be plotted. 
    
    Parameters
    ----------
    DF: pandas dataframe
    key: column name of value to be plotted
    cutoff: if True, set all negative key values equal to zero 
    
    Returns
    -------
    matplotlib ax object
    """
    
    # Lat, lon mappings
    mappingLon = dict(zip(np.arange(-179.5,180.5,1), np.arange(0,360,1)))
    mappingLat = dict(zip(np.arange(-89.5,90.5,1), np.arange(179,-1,-1)))
    
    # Initialize globalMap array
    globalMapKey = np.empty((1,180,360))
    globalMapKey[:] = np.NAN
     
    # Loop over rows of DF and fill globalMap array with key
    for i in range(len(DF)):
        a  = DF.loc[i, 'lat']
        b =  DF.loc[i, 'lon']
        globalMapKey[0, mappingLat[float(a)],mappingLon[float(b)]] = DF.loc[i, key]
    
    GM_transpose = np.transpose(globalMapKey[0,:,:])
    GM_rot = np.rot90(GM_transpose)
    
    if cutoff:
        GM_rot[GM_rot < 0] = 0         

    converted_array = GM_rot[22:164,:] #crop the poles                        
                                 
    return(converted_array)
    
def convert_data_USA(DF, key='R', cutoff=False):
    """
    Convert pandas dataframa to numpy array suitable for plotting with basemap.
    Dataframe should have columns 'lat', 'lon' and some key value to be plotted. 
    
    Parameters
    ----------
    DF: pandas dataframe
    key: column name of value to be plotted
    cutoff: if True, set all negative key values equal to zero 
    
    Returns
    -------
    matplotlib ax object
    """
    # filter df first. only retain pixels in USA
    lat_filter = DF['lat'].isin(np.arange(15.5,47.5, 1))
    lon_filter = DF['lon'].isin(np.arange(-123.5,-59.5,1))
        
    DF = DF.loc[lat_filter & lon_filter,:]
    DF = DF.reset_index(drop=True)
    
    # Lat, lon mappings
    lat = np.arange(15.5,47.5, 1)
    lon = np.arange(-123.5,-59.5,1)
    mappingLat = dict(zip(lat, np.arange(0, len(lat), 1)))
    mappingLon = dict(zip(lon, np.arange(len(lon)-1, -1, -1)))
    
    # Initialize globalMap array
    globalMapKey = np.empty((1,len(lat),len(lon)))
    globalMapKey[:] = np.NAN
     
    # Loop over rows of DF and fill globalMap array with key
    for i in range(len(DF)):
        a  = DF.loc[i, 'lat']
        b =  DF.loc[i, 'lon']
        globalMapKey[0, mappingLat[float(a)],mappingLon[float(b)]] = DF.loc[i, key]
    
    GM_transpose = np.transpose(globalMapKey[0,:,:])
    GM_rot = np.rot90(GM_transpose)
       
    # Now flip it and for some reason it works
    GM_flip = np.flipud(GM_rot) 
    GM_flip=np.fliplr(GM_flip)
    return(GM_flip)



def basemap_plot(fig, ax, globalmaparray, boundaries=np.arange(0, 1, 0.1),
                 colscheme='Blues', customcol=False, colorbar=True, USA=False):
    """
    Plots data from converted dataframe on world map
    
    Parameters
    ----------
    fig, ax: matplotlib objects
    globalmaparray: np array (see convert_data function)
    boundaries: list of boundaries for color bar
    USA: if true, plot only USA
    colscheme: name of colorbrewr scheme to be used. You can also pass a custom
    listedcolormap to this argument, if it is of lenght (len(boundaries) - 1).
    For more info check http://seaborn.pydata.org/tutorial/color_palettes.html  
    For the  names of colorbrewer color schemes check https://www.nceas.ucsb.edu/~frazier/RSpatialGuides/colorPaletteCheatsheet.pdf
    """
    
    if (customcol==False): 
        cmap = colors.ListedColormap(sns.color_palette(colscheme, len(boundaries)-1))
    else:
        cmap = customcol
        
    cmap.set_bad('white') # Set NaNs to #bababa
    
    m = Basemap(projection='cyl', ax=ax,
                llcrnrlon=-179.5,llcrnrlat=-67.5, urcrnrlon=179.5,
                urcrnrlat=73.5, lat_0 = 0, lon_0 = 0)
    
    if USA:
        m = Basemap(projection='cyl', ax=ax,
                    llcrnrlon=-124.5,llcrnrlat=14.5, urcrnrlon=-60.5,
                    urcrnrlat=47.5)
    
    m.drawcoastlines()
    
    norm = colors.BoundaryNorm(boundaries, cmap.N, clip=False)
    
    # Put everything on the map
    csR = m.imshow(globalmaparray, cmap = cmap, interpolation='none', norm=norm)
    
    # Add colorbar
    if colorbar:
        if USA:
            cax = fig.add_axes([0.80, 0.25, 0.05, 0.50], frame_on=True)
        else:
            cax = fig.add_axes([0.05, 0.2, 0.05, 0.50], frame_on=True, )
        
        cbarTv = plt.colorbar(csR, ticks=boundaries, orientation="vertical",
                              cmap = cmap,
                              cax = cax,
                              boundaries = boundaries,
                              norm=norm, drawedges=True)

    
        cbarTv.ax.tick_params(labelsize=30) # Font size of labels

    #fig.tight_layout(fig, rect=[0, 0, 1, 1])    

        
        
        
        
        
        

    
