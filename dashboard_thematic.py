'''Author: Andrew Martin
Creation Date: 13/5/24

Script to implement the thematic dashboard for ICECAPS MELT.
'''
import warnings
warnings.filterwarnings('once')

import panel as pn
import datetime as dt
import hvplot.xarray
import holoviews as hv
import xarray as xr
import numpy as np

import traceback

import sleigh_dashboard as dashboard
import tabs.thematic
import tabs.instrument

DL_asfs = tabs.instrument.tab_asfs.DL_asfs_slow

dld = {
    'asfs':DL_asfs
}

def get_tabview(dld, augment) -> dashboard.TabView.TabView:
    tabview = dashboard.TabView.TabView(
        tablist=[
            #get_mvp_tab(augment),
            tabs.thematic.tab_met.get_met_tab(augment)
        ],
        dld=dld,
        augment_dims=augment
    )
    return tabview


def dashboard_thematic(dtp_args,dld):
    db = dashboard.Dashboard.Dashboard(
        dtp_args=dtp_args,
        dict_DL=dld,
        tabview_func=get_tabview
    )
    return db


def serve_dashboard_thematic(dld):
    # global datetime picker arguments
    start = dt.datetime(2024,5,9)
    end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...

    now = dt.datetime.now()
    dtr_end = dt.datetime(year=now.year, month=now.month, day=now.day)
    one_day = dt.timedelta(days=1)
    dtr = (dtr_end-one_day, dtr_end) # should start by displaying two days of data
    dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}
    
    serve = lambda: dashboard_thematic(dtp_args, dld)
    return serve


if __name__ == '__main__':
    db_func = serve_dashboard_thematic(dld)
    pn.serve(db_func,title='Thematic dashboard -- test', port=5006, websocket_origin='*', show=True)

