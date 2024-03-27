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
    OPTS_2d = {'x':'time', 'y':'range','height':400, 'responsive':True, 'padding':0.1, 'xlim':dtrange, 'ylabel': 'Height AGL (m)', 'xlabel':'time'}
    # title to the tab
    p0 = pn.pane.Markdown('CL61 Vaisalla Ceilometer')
    title = pn.Row(p0)
    ######################## CLOUD HEIGHT INFORMATION ###########################
    #############################################################################

    p1 = ds.time_count.hvplot.scatter(x='time', ylim=[-1,16], label='time_count',
        height=400, grid=True, responsive=True,
        title='INSTRUMENT UPTIME', ylabel='records per 15 minutes'
    )
    #l=(p1_tgt + p1_src).cols(1)
    #l.opts(hv.opts.Layout(shared_axes=False, merge_tools=False))

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

    plot_cloud_bases = ds[['cloud_base_heights_mean']].hvplot.scatter(
        x='time', y='cloud_base_heights_mean', by='layer',
        s=5, color='white', label='CBH', xlim=dtrange,
        height=OPTS_2d['height'], responsive=True, legend=False
    )
    
    plot_backscatter = ds['beta_att_mean'].hvplot(
        title='mean Attenuated backscatter', **OPTS_2d, cnorm='log', clim=(1e-8, 1e-2), ylim=(0,5000),
        cmap='viridis'
    )
    def backscatter_base_heights(show_base_heights):
        plist = [plot_backscatter]
        if show_base_heights:
            plist = plist + [plot_cloud_bases]
        return hv.Overlay(plist).opts(ylim=(0,5000), xlim=dtrange)

    toggle = pn.widgets.Switch(name='Include cloud base heights', value=True)

    p_backscatter = pn.panel(pn.bind(backscatter_base_heights, show_base_heights=toggle), loading_indicator=True)

    p_lindepol = ds['linear_depol_ratio_median'].hvplot(
        title='median linear depolarisation ratio', **OPTS_2d, clim=(0,1)
    )

    # include all elements to be displayed in the returned pn.Column object
    display = pn.Column(title, 
        p1, toggle, p_backscatter, p_lindepol, plot_cloud_bases
    )

    left_spacer = pn.Column(width=10)
    return pn.Row(left_spacer, display, left_spacer) 
