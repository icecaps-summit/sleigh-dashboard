'''Author: Andrew Martin
Creation Date: 16/4/24

Script to demonstrate the new OOP implementation of the dashboard. This will contain multiple tabs for instruments with different plotting functions.
'''
import warnings

import tabs.instrument

warnings.filterwarnings('once')


import panel as pn
import datetime as dt
import hvplot.xarray
import holoviews as hv
import xarray as xr
import numpy as np

import traceback

import sleigh_dashboard as dashboard

import tabs

# DataLoader objects need to be defined to control the dataflow in the program
DL_asfs = tabs.instrument.tab_asfs.DL_asfs_slow
DL_cl61 = tabs.instrument.tab_cl61.DL_cl61
DL_gfs = tabs.instrument.tab_gfs.DL_gfs
DL_gpr5 = tabs.instrument.tab_gpr.DL_gpr5
DL_gpr7 = tabs.instrument.tab_gpr.DL_gpr7
DL_mrr = tabs.instrument.tab_mrr.DL_mrr
DL_mwr = tabs.instrument.tab_mwr.DL_mwr
DL_mvp = tabs.instrument.tab_mvp.DL_mvp
DL_simba = tabs.instrument.tab_simba.DL_simba

dld = {
    'asfs': DL_asfs,
    'cl61': DL_cl61,
    'gfs': DL_gfs,
    'gpr5':DL_gpr5,
    'gpr7':DL_gpr7, 
    'mrr': DL_mrr,
    'mwr': DL_mwr,
    'mvp':DL_mvp,
    'simba':DL_simba,
}

# global datetime picker arguments
start = dt.datetime(2024,5,9)
end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...

now = dt.datetime.now()
dtr_end = dt.datetime(year=now.year, month=now.month, day=now.day)
one_day = dt.timedelta(days=1)
dtr = (dtr_end-one_day, dtr_end) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}


def get_tabview(dld, augment) -> dashboard.TabView.TabView:
    tabview = dashboard.TabView.TabView(
        tablist=[
            #get_mvp_tab(augment),
            tabs.instrument.tab_cl61.get_lidar_tab(augment),
            tabs.instrument.tab_mrr.get_radar_tab(augment),
            tabs.instrument.tab_mwr.get_mwr_tab(augment),
            tabs.instrument.tab_asfs.get_asfs_tab(augment),
            tabs.instrument.tab_gpr.get_gpr_tab(augment),
            tabs.instrument.tab_simba.get_simba_tab(augment),
            tabs.instrument.tab_mvp.get_mvp_tab(augment),
            tabs.instrument.tab_gfs.get_gfs_tab(augment),
        ],
        dld=dld,
        augment_dims=augment
    )
    return tabview

def oop_dashboard(dtp_args,dld):
    db = dashboard.Dashboard.Dashboard(
        dtp_args=dtp_args,
        dict_DL=dld,
        tabview_func=get_tabview
    )
    return db

serve_dashboard = lambda: oop_dashboard(dtp_args, dld)


pn.serve(serve_dashboard,title='OOP Dashboard', port=5006, websocket_origin='*', show=True )

# Framework for testing a singular desired tab
#tab = get_simba_tab()
#tab.dld = dld
#pn.serve(tab, port=5006, websocket_origin='*', show=True)

