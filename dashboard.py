#!/usr/bin/env -S python3 -u
import numpy as np
import pandas as pd
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn
import datetime as dt

import time, traceback, sys

import dashboard_instrument, dashboard_thematic

pn.extension(design='material', template='material')

#pn.extension(design='material', template='material')
 
from multiprocessing import Process

import warnings
warnings.filterwarnings("ignore")

pn.extension('echarts', template='fast', nthreads=4, notifications=False)

# Create the standard global datetime picker choices. Specific datetime-limitted dashboards (i.e. melt events) should have their datetime ranges specified in their files
start = dt.datetime(2024,5,9)
end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
now = dt.datetime.now()
dtr_end = dt.datetime(year=now.year, month=now.month, day=now.day)
one_day = dt.timedelta(days=1)
dtr = (dtr_end-one_day, dtr_end) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}

db_instrument = lambda: dashboard_instrument.dashboard_instruments(dtp_args, dashboard_instrument.create_dld())
db_thematic = lambda: dashboard_thematic.dashboard_thematic(dtp_args, dashboard_instrument.create_dld())



def launch_server_process(panel_dict, port):
    server_thread = pn.serve(panel_dict, title='ICECAPS SLEIGH-MVP Dashboard',
                             port=port, websocket_origin='*', show=False)
    return True # not necessary but explicit


def print_traceback(thetb, error_msg):

    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)
    print(f"!!! {error_msg} "                                                  , file=sys.stderr)
    print("\n\n"                                                               , file=sys.stderr)
    print(thetb                                                                   , file=sys.stderr)
    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)


def main(port=6646):
    while True:           
        try:
            panel_dict = {
                'instrument': db_instrument,
                'thematic': db_thematic
            } # if you make other pages, add them here... 

            p = Process(target=launch_server_process, args=(panel_dict,port))
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

        finally:
            p.terminate()


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
