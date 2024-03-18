import numpy as np
import xarray as xr
import hvplot.xarray # noqa
import hvplot.pandas
import hvplot
import holoviews as hv
import panel as pn

import datetime as dt
import os

import warnings
warnings.filterwarnings("ignore")

def load_cl61():
    dir_cl61 = '/data/cl61/daily'
    files_cl61 = [os.path.join( dir_cl61,f ) for f in os.listdir(dir_cl61) if 'summary_cl61' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    print('attempting load:')
    ds = xr.open_mfdataset(files_cl61)
    print('success')

    return ds

def tab_cl61(ds, dtrange=(None, None)):
    #ds = load_cl61()

    # title to the tab
    p0 = pn.pane.Markdown('CL61 Vaisalla Ceilometer')
    title = pn.Row(p0)
    ######################## CLOUD HEIGHT INFORMATION ###########################
    #############################################################################

    p1 = ds.time_count.hvplot.scatter(x='time', ylim=[-1,16], label='time_count',
        height=400, grid=True, responsive=True,
        title='INSTRUMENT UPTIME', ylabel='records per 15 minutes'
    )
    p1_tgt = p1.relabel('INSTRUMENT UPTIME').opts(height=400)
    p1_src = p1.opts(height=50, yaxis=None, default_tools=[], shared_axes=False, ylim=(-1,16))
    hv.plotting.links.RangeToolLink(
        p1_src, p1_tgt, axes=['x', 'y'], boundsx=dtrange, boundsy=(None, None)
    )
    #l=(p1_tgt + p1_src).cols(1)
    #l.opts(hv.opts.Layout(shared_axes=False, merge_tools=False))

    ds['zero'] = 1e-10*ds.cloud_thickness_mean
    p2 = ds.hvplot.scatter(x='time', y='cloud_base_heights_mean', by='layer',
        s=2, color='blue', label='CBH', xlim=dtrange,
        height=400, grid=True, responsive=True,
        title='CLOUD LOCATION'
    ) * ds.hvplot.errorbars(x='time', y='cloud_base_heights_mean', yerr1='zero', yerr2='cloud_thickness_mean', by='layer', label='CBH', xlim=dtrange,
        color='orange',
        height=400, grid=True, responsive=True
    )
    #p1 = pn.bind(pf1, dtrange=dt_range_picker)

    #p3 = ds.cloud_thickness_mean.hvplot.scatter(x='time', by='layer')


    #################### DATA STREAM NULLRATE ###############################

    def unstack_xarray_dataset_by_dim(ds: xr.Dataset, dim):
        '''Function to unstack dataset variables along a finite, discrete dimension
        
        e.g. ds.<var>(..., dim) -> <var>_dim0, <var>_dim1, ..., <var>_dimN
        '''
        new_ds = ds[[]]
        for v in ds.variables:
            if dim in ds[v].dims:
                for di in ds[dim].values:
                    new_ds[f'{v}_{dim}{di}'] = ds[v].sel({dim:di}).squeeze()
            else:
                new_ds[v] = ds[v]
        return new_ds


    '''
    VARS_nullrate = (v for v in ds.variables if '_nullrate' in v)
    ds_nullrate = unstack_xarray_dataset_by_dim(ds[[*VARS_nullrate]], 'layer')
    df_heatmap = ds_nullrate.to_dataframe(dim_order=('time',))#.astype({'time':np.datetime64})
    df_heatmap = df_heatmap[[v for v in df_heatmap.keys() if '_nullrate' in v]]
    #p_nullrate = df_heatmap.hvplot.heatmap(x='index',height=400, responsive=True)
    #p_nullrate = df_heatmap.hvplot.scatter(x='time', height=400).opts(ylim=(-0.1,1.1), xlim=dtrange)
    p_nullrate = df_heatmap.hvplot.heatmap(height=500, ylim=dtrange, rot=70, xaxis='top')
    '''
    p_nullrate = pn.pane.Markdown('## nullrate coming soon')

    # include all elements to be displayed in the returned pn.Column object
    display = pn.Column(title,p1_tgt, p1_src, p_nullrate, p2)#, p3)#dt_range_picker, p1)

    left_spacer = pn.Column(width=10)
    return pn.Row(left_spacer, display, left_spacer) 
