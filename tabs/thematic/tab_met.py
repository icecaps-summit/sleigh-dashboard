'''Author: Andrew Martin
Creation date: 13/5/24

Script containing the functionality for the meteorological thematic tab for ICECAPS MELT
'''

import warnings
warnings.filterwarnings("once")

import xarray as xr
import panel as pn
import holoviews as hv
import numpy as np

from sleigh_dashboard import DataLoader, Plottables, Tab

def get_met_tab(augment=False):
    basic_pargs = {'x':'time', 'xlabel': 'time'}

    plot_T = Plottables.Plot_line_scatter('asfs', 'vaisala_T_mean', {**basic_pargs, 'ylabel':'Temperature (C)'})
    if augment: plot_T.plotargs['x'] += '_'

    plot_P = Plottables.Plot_line_scatter('asfs', 'vaisala_P_mean', {**basic_pargs, 'ylabel': 'Pressure (hPa)'})
    if augment: plot_P.plotargs['x'] += '_'

    plot_RH = Plottables.Plot_line_scatter('asfs', 'vaisala_RH_mean', {**basic_pargs, 'ylabel': 'Relative humidity (%)'})
    if augment: plot_RH.plotargs['x'] += '_'

    tab_met = Tab.Tab(
        'MET',
        [plot_T, plot_P, plot_RH],
        dld=None,
        required_DL=['asfs'],
        longname='METEOROLOGICAL',
        augment_dims=augment
    )
    return tab_met