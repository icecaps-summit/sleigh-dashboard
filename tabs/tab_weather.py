import numpy as np
import xarray as xr
import hvplot.xarray # noqa
import hvplot
import holoviews as hv
import panel as pn

import datetime as dt
import os
import traceback

import warnings
warnings.filterwarnings("ignore")

def load_gfs_weather():
    dir_weather = '/data/weather/GFS'
    
    # ....Obtain all the weather filenames (and sort 'em)
    fns = sorted(glob(dir_weather+'*.nc'))
    
    # ....Loads the most recent weather file
    ds = xr.open_dataset(fns[-1])
    
    return

def tab_weather(ds):
    # ....Create weather plots
    p_Ts = ds['Ts'].hvplot()
    p_Ps = ds['Ps'].hvplot()
    p_ws = ds['ws'].hvplot()
    p_wd = ds['wd'].hvplot()
    p_pr = ds['pr'].hvplot()
    
    # ....Set up panels and tab
    left_spacer = pn.Column(width=20)
    TAB = pn.Column(pn.pane.Markdown('# GFS Weather'), p_Ts, p_Ps, p_ws, p_wd, p_pr)
    
    return pn.Row(left_spacer, TAB, left_spacer)