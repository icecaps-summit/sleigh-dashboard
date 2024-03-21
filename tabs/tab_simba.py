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

def load_simba():
    dir_simba = '/data/simba/'
    files_simba = [os.path.join( dir_simba,f ) for f in os.listdir(dir_simba) if 'summary_simba' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    ds = xr.open_mfdataset(files_simba).load()
    return ds

def tab_simba(ds, dtrange=(None, None)):
    #ds = load_mrr()

    OPTS_scatter = {'x':'time', 's':2, 'height':250, 'responsive':True, 'grid':True, 'padding':0.1, 'xlim':dtrange, 'xlabel':'time'}
    OPTS_2d = {'x':'time', 'y':'height','height':400, 'responsive':True, 'padding':0.1, 'xlim':dtrange, 'ylabel': 'Height AGL (cm)', 'xlabel':'time'}
    OPTS_taller = {k:v for k,v in OPTS_scatter.items()}
    OPTS_taller['height'] = 400

    def set_border_fill_color(plot, elememt):
        b = plot.state
        b.border_fill_color = 'whitesmoke'

    p_temperature = ds['temperature'].hvplot(
        title='Temperature (°C)', **OPTS_2d, cmap='viridis', clim=(-35,None)
    )

    p_sample_span = ds['sample_span'].hvplot.scatter(
        title='Sample span', **OPTS_scatter
    )

    p_batt = ds['battery_voltage'].hvplot.scatter(
        title='Battery voltage (V)', **OPTS_scatter
    )

    p_start_stop = ds['sample_start'].hvplot.scatter(
        title='Sample time', **OPTS_scatter, label='start', color='green'
    ) * ds['sample_end'].hvplot.scatter(
        **OPTS_scatter, label='end', color='red'
    )

    p_num_samp = ds['sample_number'].hvplot.scatter(
        title='Sample number', **OPTS_scatter, color='orange'
    ) 
    p_num_seq = ds['sequence_number'].hvplot.scatter(
        title='Sequence number', **OPTS_scatter, color='purple'
    )
    #p_nums.opts(multi_y=True)

    left_spacer = pn.Column(width=20)
    TAB = pn.Column(
        pn.pane.Markdown('# SIMBA'), p_temperature, p_start_stop, p_sample_span, p_batt, p_num_samp, p_num_seq,
        styles={'background': 'whitesmoke'}
    )
    return pn.Row(left_spacer, TAB, left_spacer)