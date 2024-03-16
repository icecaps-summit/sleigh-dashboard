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

def load_mrr():
    dir_mrr = '/data/mrr/'
    files_mrr = [os.path.join( dir_mrr,f ) for f in os.listdir(dir_mrr) if 'summary_mrr' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    ds = xr.open_mfdataset(files_mrr).load()
    return ds

def tab_mrr(dtrange=(None, None)):
    ds = load_mrr()

    OPTS_scatter = {'x':'time', 's':2, 'height':250, 'responsive':True, 'grid':True, 'padding':0.1, 'xlim':dtrange}
    OPTS_2d = {'x':'time', 'y':'range_bins','height':400, 'responsive':True, 'padding':0.1, 'xlim':dtrange}
    OPTS_taller = {k:v for k,v in OPTS_scatter.items()}
    OPTS_taller['height'] = 400

    def set_border_fill_color(plot, elememt):
        b = plot.state
        b.border_fill_color = 'whitesmoke'

    var_plots = []
    IGNORE_VARS = ('time', 'range_bins')
    #for v in [a for a in ds.variables if a not in IGNORE_VARS]:
    #    print(v)
    #    try:
    #        if ds[v].ndim == 2:
    #            p = ds[v].hvplot.QuadMesh(title=v, **OPTS_2d)
    #        elif ds[v].ndim == 1:
    #            p = ds[v].hvplot.scatter(title=v, **OPTS_scatter)
    #        var_plots.append(p)
    #    except Exception as e:
    #        print(traceback.format_exc(e))
    #        continue
    #        var_plots.append( pn.pane.Markdown(f'## {v}: failed\n{traceback.format_exc(e)}') )

    # ['time', 'range_bins', 'time_count', 'Z_median', 'VEL_median', 'WIDTH_median', 'Z_std', 'VEL_std', 'WIDTH_std', 'RR_mean', 'LWC_meansum', 'Z_nullrate', 'VEL_nullrate', 'WIDTH_nullrate', 'RR_nullrate', 'LWC_nullrate']
    var_plots.append(
        ds.Z_median.hvplot(title='Z median',**OPTS_2d, cmap='viridis')
    )
    var_plots.append(
        ds.VEL_median.hvplot(title='VEL median', **OPTS_2d, cmap='magma')
    )
    var_plots.append(
        ds.WIDTH_median.hvplot(title='WIDTH median', **OPTS_2d, cmap='magma')
    )
    #var_plots.append(
    #    ds.RR_mean.hvplot.scatter(title='Rainfall Rate mean', **OPTS_scatter, ylabel='Rainfall Rate')
    #)
    var_plots.append(
        ds.LWC_meansum.hvplot.scatter(title='LWC mean', **OPTS_scatter)
    )

    left_spacer = pn.Column(width=20)
    TAB = pn.Column(pn.pane.Markdown('# Coming soon?'), *var_plots)

    return pn.Row(left_spacer, TAB, left_spacer)