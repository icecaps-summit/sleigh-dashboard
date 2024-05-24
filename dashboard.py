#!/usr/bin/env -S python3 -u
import time, traceback, sys

from multiprocessing import Process

import datetime  as dt
import numpy     as np
import pandas    as pd
import xarray    as xr
import holoviews as hv
import panel     as pn
 
from panel import HSpacer, Spacer

import dashboard_instrument, dashboard_science

pn.extension(design='material', template='material',
             global_css=[':root { --design-primary-color: steelblue; }',
                         ':root { --panel-primary-color: mediumturquoise; }',
                         ])

import warnings
warnings.filterwarnings("ignore")

pn.extension('echarts', template='fast', nthreads=4, notifications=False)

# Create the standard global datetime picker choices.
# Specific datetime-limited dashboards (i.e. melt events) should have
# their datetime ranges specified in their files
start = dt.date(2024,5,15)
end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
now = dt.datetime.now()
dtr_end = dt.date(year=now.year, month=now.month, day=now.day)
one_day = dt.timedelta(days=1)
dtr = (dtr_end-one_day, dtr_end) # should start by first day of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':''}

# lambda functions to create panel entries
db_instrument = \
    lambda: dashboard_instrument.dashboard_instruments(dtp_args,
                                                       dashboard_instrument.create_dld()
                                                       )
db_science = \
    lambda: dashboard_science.dashboard_science(dtp_args,
                                                dashboard_instrument.create_dld())
def launch_server_process(panel_dict, port):

    server_thread = pn.serve(panel_dict,
                             title='ICECAPS SLEIGH-MVP Dashboard',
                             port=port,
                             logo =logo_image,
                             index='science/',
                             location='science',
                             websocket_origin='*',
                             show=False)

    return True # not necessary but explicit


def print_traceback(tb, error_msg):

    print(f"!!! ———————————————————————————————————————————————————————— !!! " ,
          file=sys.stderr)
    print(f"!!! {error_msg} "                                                  ,
          file=sys.stderr)
    print("\n\n"                                                               ,
          file=sys.stderr)
    print(tb                                                                   ,
          file=sys.stderr)
    print(f"!!! ———————————————————————————————————————————————————————— !!! " ,
          file=sys.stderr)

def main(port=6646):
    # delete / entry to get the index back 
    panel_dict = {
        '/' : db_instrument,
        'science': db_science,
        'instrument': db_instrument,
    } # if you make other pages, add them here... 

    logo_image = "https://icecapsmelt.org/_image?href=%2F%40fs%2Fapp%2Fsrc%2Fassets%2Fimages%2Fgreenland_small.png"

    server_thread = pn.serve(panel_dict,
                             title='ICECAPS SLEIGH-MVP Dashboard',
                             port=port,
                             logo=logo_image,
                             websocket_origin='*',
                             show=False)

# this runs the function main as the main program... functions
# to come after the main code so it presents in a more logical, C-like, way
# https://stackoverflow.com/questions/11241523/why-does-python-code-run-faster-in-a-function
if __name__ == '__main__':

    PORT = 6646

    import argparse
    parser = argparse.ArgumentParser(description='Run the dashboard to display the summarised data from the ICECAPS MELT Raven 2024 deployment.')
    parser.add_argument('-pd', action='store_true', help="Include this flag to chnage the port from 6646 (deployment) to 5006 (pre-deployment).")
    #parser.add_argument('')
    args = parser.parse_args()
    pd = args.pd
    if pd:
        PORT = 5006
    
    main(port=PORT)
