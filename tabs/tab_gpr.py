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

def load_gpr():
    dir_gpr = '/data/gpr/'
    files_gpr7 = [os.path.join( dir_gpr,f ) for f in os.listdir(dir_gpr) if 'summary_gpr_7' in f]
    files_gpr5 = [os.path.join( dir_gpr,f ) for f in os.listdir(dir_gpr) if 'summary_gpr_5' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    RNVARS=('DM_mean', 'DM_std', 'f')
    ds5 = xr.open_mfdataset(files_gpr5).load()
    ds5 = ds5.rename({i: i+'_5' for i in RNVARS})
    ds7 = xr.open_mfdataset(files_gpr7).load()
    ds7 = ds7.rename({i: i+'_7' for i in RNVARS})

    ds = xr.merge([ds5,ds7])

    return ds

def tab_gpr(ds, dtrange=(None, None)):
    #ds = load_mrr()

    OPTS_scatter = {'x':'time', 's':2, 'height':250, 'responsive':True, 'grid':True, 'padding':0.1, 'xlim':dtrange, 'xlabel':'time'}
    OPTS_2d = {'x':'time', 'y':'step', 'height':400, 'responsive':True, 'padding':0.1, 'xlim':dtrange, 'ylabel': 'step', 'xlabel':'time', 'flip_yaxis':True}
    OPTS_taller = {k:v for k,v in OPTS_scatter.items()}
    OPTS_taller['height'] = 400

    def set_border_fill_color(plot, elememt):
        b = plot.state
        b.border_fill_color = 'whitesmoke'

    var_plots = []
    IGNORE_VARS = ('time', 'step')
    for v in [a for a in ds.variables if a not in IGNORE_VARS]:
        print(v)
        try:
            if ds[v].ndim == 2:
                p = ds[v].hvplot(title=v, **OPTS_2d)
            elif ds[v].ndim == 1:
                p = ds[v].hvplot.scatter(title=v, **OPTS_scatter)
            var_plots.append(p)
        except Exception as e:
            print(traceback.format_exc(e))
            continue
            var_plots.append( pn.pane.Markdown(f'## {v}: failed\n{traceback.format_exc(e)}') )

    p_combDM = ds['DM_mean_5'].hvplot(
        title='Combined DM mean', **OPTS_2d
    ) * ds['DM_mean_7'].hvplot(
        **OPTS_2d
    )

    p_comb_DM_std = ds['DM_std_5'].hvplot(
        title='Combined DM std', **OPTS_2d
    ) * ds['DM_std_7'].hvplot(
        **OPTS_2d
    )

    left_spacer = pn.Column(width=20)
    TAB = pn.Column(pn.pane.Markdown('# GPR'), p_combDM, p_comb_DM_std, *var_plots)
    return pn.Row(left_spacer, TAB, left_spacer)