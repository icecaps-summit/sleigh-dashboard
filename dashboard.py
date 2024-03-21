#!/usr/bin/env -S python3 -u
import numpy as np
import pandas as pd
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn

import time, datetime, traceback, sys

from tabs import tab_cl61
from tabs import tab_asfs
from tabs import tab_mrr
from tabs import tab_mvp
from tabs import tab_simba
from tabs import tab_gpr

pn.extension(design='material', template='material')

#pn.extension(design='material', template='material')
 
from multiprocessing import Process

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0,'/home/website_admin/sleigh-dashboard/tabs')

alarm_color   = 'palevioletred'
warning_color = 'khaki'
happy_color   = 'mediumseagreen'

pn.extension('echarts', template='fast', nthreads=4, notifications=False)

def create_tabs():
    # create the datetimerange picker and update button that appear on all tabs
    now = datetime.datetime.now()
    t_day_start = datetime.time(0,0,0)
    t_yyday = datetime.date.today() - datetime.timedelta(days=2)
    start_yyday = datetime.datetime.combine(t_yyday, t_day_start)
    epoch=datetime.date(2024,3,1)
    datetimerange_select = pn.widgets.DatetimeRangePicker(
        name='Default time range:',
        value = (start_yyday, now), enable_seconds=False, start=epoch
    )

    #power_title   = pn.pane.Markdown('# ICECAPS MELT — MVP Dashboard' ) 
    t_mvp = pn.bind(tab_mvp.tab_mvp, dtrange=datetimerange_select)
    tabs = pn.Tabs(('Minimum Viable Powersupply', t_mvp))

    #################### INSTRUMENT UPTIME #####################
    tabs.append(('Instrument Uptime', pn.pane.Markdown('# Coming soon...')))

    ds_cl61 = tab_cl61.load_cl61()
    ds_asfs = tab_asfs.load_asfs()
    ds_mrr = tab_mrr.load_mrr()
    ds_simba = tab_simba.load_simba()
    ds_gpr = tab_gpr.load_gpr()

    t_cl61 = pn.bind(tab_cl61.tab_cl61, dtrange=datetimerange_select, ds=ds_cl61)
    tabs.append(('CL61', t_cl61))
    
    t_asfs = pn.bind(tab_asfs.tab_asfs, dtrange=datetimerange_select, ds=ds_asfs)
    tabs.append(('ASFS', t_asfs))
    
    t_mrr = pn.bind(tab_mrr.tab_mrr, dtrange=datetimerange_select, ds=ds_mrr)
    tabs.append(('MRR', t_mrr))

    t_simba = pn.bind(tab_simba.tab_simba, dtrange=datetimerange_select, ds=ds_simba)
    tabs.append(('SIMBA', t_simba))

    t_gpr = pn.bind(tab_gpr.tab_gpr, dtrange=datetimerange_select, ds=ds_gpr)
    tabs.append(('GPR', t_gpr))
    
    tabs.append(('MWR', pn.pane.Markdown('# Coming soon...')))
    tabs.append(('BLE', pn.pane.Markdown('# Coming soon...')))

    display = pn.Column(
        datetimerange_select,
        tabs
    )

    return display


def launch_server_process(panel_dict):

    server_thread = pn.serve(panel_dict, title='ICECAPS SLEIGH-MVP Dashboard',
                             port=6646, websocket_origin="*", show=False) # deployment
                             #port=5006, websocket_origin='*', show=False) # testing
    return True # not necessary but explicit


def print_traceback(thetb, error_msg):

    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)
    print(f"!!! {error_msg} "                                                  , file=sys.stderr)
    print("\n\n"                                                               , file=sys.stderr)
    print(thetb                                                                   , file=sys.stderr)
    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)


def main():
    while True:           
        try:
            tabs = create_tabs
            print(f'{type(tabs)=}')
            panel_dict = {'dashboard': tabs} # if you make other pages, add them here... 

            p = Process(target=launch_server_process, args=(panel_dict,))
            p.start()
            for s in range(0,6000):
                if s % 600 ==0 : print("... we could do work here... but we're still alive")
                time.sleep(1)

            print("Restarting websocket...")

            p.join(timeout=1); p.terminate()
            
        except KeyboardInterrupt:   
            print("Exiting...")
            exit()

        except Exception as e:
            print(e)


# this runs the function main as the main program... functions
# to come after the main code so it presents in a more logical, C-like, way
# https://stackoverflow.com/questions/11241523/why-does-python-code-run-faster-in-a-function
if __name__ == '__main__':
    main()
