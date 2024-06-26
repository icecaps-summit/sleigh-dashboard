'''
Author: Andrew Martin
Creation Date: 13/5/24

Script to implement the science dashboard for ICECAPS MELT.
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
import tabs.science
import tabs.instrument
from dashboard_instrument import create_dld

DL_asfs = tabs.instrument.tab_asfs.DL_asfs_slow

dld = create_dld()

def get_tabview(dld, augment) -> dashboard.TabView.TabView:
    tabview = dashboard.TabView.TabView(
        tablist=[
            #get_mvp_tab(augment),
            tabs.science.tab_met.get_met_tab(augment),
            tabs.science.tab_clouds.get_clouds_tab(augment),
            tabs.science.tab_seb.get_seb_tab(augment),
            tabs.instrument.tab_mvp.get_mvp_tab(augment)
        ],
        dld=dld,
        augment_dims=augment
    )
    return tabview


def dashboard_science(dtp_args,dld):
    db = dashboard.Dashboard.Dashboard(
        dtp_args=dtp_args,
        dict_DL=dld,
        tabview_func=get_tabview
    )
    return db


def serve_dashboard_science(dld):
    # global datetime picker arguments
    start = dt.datetime(2024,5,9)
    end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...

    now = dt.datetime.now()
    dtr_end = dt.datetime(year=now.year, month=now.month, day=now.day)
    one_day = dt.timedelta(days=1)
    dtr = (dtr_end-one_day, dtr_end) # should start by displaying two days of data
    dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':''}
    
    serve = lambda: dashboard_science(dtp_args, dld)
    return serve

if __name__ == '__main__':
    db_func = serve_dashboard_science(dld)
 
    logo_image = "https://icecapsmelt.org/_image?href=%2F%40fs%2Fapp%2Fsrc%2Fassets%2Fimages%2Fgreenland_small.png"

    file_menu = pn.widgets.MenuButton(
        name="Blog", button_type="primary",
        items=["Save"], width=60, margin=0, align="start"
)
    action_bar = pn.Row(
        pn.pane.PNG(logo_image, height=500, width=500, margin=0, sizing_mode="fixed", align="start"),
        file_menu,
        HSpacer(),
        sizing_mode="stretch_width",
        styles={"background": "WhiteSmoke"},
    )

    print(f" !!! there should be a header here... !!!")

    pn.serve(db_func,
             header=[action_bar],
             head='ICECAPS-MELT science dashboard',
             title='ICECAPS-MELT science dashboard',
             port=5006,
             websocket_origin='*',
             show=True)

