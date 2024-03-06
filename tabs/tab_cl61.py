import numpy as np
import xarray as xr
import hvplot.xarray # noqa
import hvplot
import holoviews as hv
import panel as pn

import datetime as dt
import os

def testfn():
    print('relative import worked!')

def load_cl61():
    dir_cl61 = '/data/cl61/daily'
    files_cl61 = [os.path.join( dir_cl61,f ) for f in os.listdir(dir_cl61) if 'summary_cl61' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    ds = xr.open_mfdataset(files_cl61)

    return ds

def tab_cl61():
    ds = load_cl61()

    # title to the tab
    p0 = pn.pane.Markdown('CL61 Vaisalla Ceilometer')
    title = pn.Row(p0)

    ######################## DATETIME RANGE SELECTION ###########################
    #############################################################################

    '''
    # the following dtrange goes from the start of yesterday to the end of yesterday. This should be the latest day of available data...
    dtrange = ( dt.datetime.today().date() - dt.timedelta(days=2), dt.datetime.today().date() )
    dt_range_picker = pn.widgets.DatetimeRangePicker(name='Datetime range:', value=dtrange, enable_seconds=False)
    '''
    dttd = dt.datetime.today()
    start_of_today = dt.datetime(dttd.year, dttd.month, dttd.day)
    dtrange = ( start_of_today - dt.timedelta(days=2), start_of_today )
    ######################## CLOUD HEIGHT INFORMATION ###########################
    #############################################################################

    p1 = ds.time_count.hvplot.scatter(x='time', ylim=[-1,16], label='time_count',
        height=400, grid=True, responsive=True,
        title='INSTRUMENT UPTIME', ylabel='records per 15 minutes'
    )
    p1_tgt = p1.relabel('INSTRUMENT UPTIME').opts(height=400, toolbar='disable')
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

    # include all elements to be displayed in the returned pn.Column object
    display = pn.Column(title,p1_tgt, p1_src, p2)#, p3)#dt_range_picker, p1)
    return display 
