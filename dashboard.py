#!/usr/bin/env -S python3 -u
import numpy as np
import pandas as pd
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn

import time, datetime, traceback, sys

#pn.extension(design='material', template='material')
 
from multiprocessing import Process

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0,'/home/sleigh/sleigh-dashboard/tabs')
from tab_cl61 import tab_cl61

alarm_color   = 'palevioletred'
warning_color = 'khaki'
happy_color   = 'mediumseagreen'

pn.extension('echarts', template='fast', nthreads=4, notifications=False)

def power_columns(refresh_button_state=None):

    print(refresh_button_state, type(refresh_button_state))

    #####################################################################
    # ....Determine today's and yesterday's dates
    today     = pd.Timestamp.now('UTC')
    yesterday = pd.Timestamp.now('UTC')-pd.Timedelta('24h')

    #####################################################################
    # ....Read data from SLEIGH and MVP
    power = get_power_data(start_date=yesterday, end_date=today, data_dir='/data/power/level2/')

    # get some info about how new the data is on the server
    tz            = datetime.timezone(datetime.timedelta(seconds=0))
    last_obs_time = pd.to_datetime(power.time.data[-1]).replace(tzinfo=tz)
    mins_ago      = str(int(np.abs((last_obs_time- pd.Timestamp.now('UTC')).total_seconds()/60)))
    curr_time     = today.strftime("%H:%M")
    tcoords       = [('time', power.time.values)]

    BatterySOC   = xr.DataArray(power.BatterySOC.values, coords=tcoords, name='SOC [%]')
    BatteryWatts = xr.DataArray(power.BatteryWatts.values, coords=tcoords, name='BattS [W]')

    SolarWatts_Tot = xr.DataArray(power.SolarWatts_East.values
                                  + power.SolarWatts_South.values
                                  + power.SolarWatts_West.values, coords=tcoords, name='Total')

    SolarWatts_E = xr.DataArray(power.SolarWatts_East.values  , coords=tcoords, name='East')
    SolarWatts_W = xr.DataArray(power.SolarWatts_West.values  , coords=tcoords, name='West')
    SolarWatts_S = xr.DataArray(power.SolarWatts_South.values , coords=tcoords, name='South')

    WindWatts       = xr.DataArray(power.WindWatts.values       , coords=tcoords, name='Wind [W]')
    ACOutputWatts   = xr.DataArray(power.ACOutputWatts.values   , coords=tcoords, name='AC [W]')
    DCInverterWatts = xr.DataArray(power.DCInverterWatts.values , coords=tcoords, name='DCInverterWatts')

    DCWatts = SolarWatts_Tot + WindWatts - BatteryWatts - DCInverterWatts
    DCWatts.name = 'DC [W]'

    SolarWatts = xr.merge([SolarWatts_Tot, SolarWatts_E, SolarWatts_W, SolarWatts_S])

    #################### MINIMUM VIABLE POWERSUPPLY #####################
    #####################################################################
    average_time = '10T'    # Currently 10 minutes
    last_time    = today

    # ....Row of battery and power numbers and gauges
    batt_soc = np.round(power.BatterySOC.resample(time=average_time).mean(skipna=True).values[-1],0) 
    p1 = pn.indicators.Gauge(name=f'\n\nSOC\n{batt_soc}%', 
                             value=batt_soc,
                             format=' ', 
                             bounds=(0, 100), 
                             colors=[(0.2, alarm_color), (0.5, warning_color), (1, happy_color)],
                             title_size=15,
                             height=220, 
		             num_splits=5, 
                             custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
                             )

    batt_v = np.round(power.BatteryVolts.resample(time=average_time).mean(skipna=True).values[-2],1) 
    p2 = pn.indicators.Gauge(name=f'\n\nBATT\n{batt_v}V', 
                             value=batt_v,
                             format=' ', 
                             bounds=(48, 58), 
                             colors=[(0.15, alarm_color), (0.3, warning_color), (0.7, happy_color),
                                     (0.85, warning_color), (1.0, alarm_color)],
                             title_size=15,
                             height=220, 
				             num_splits=5, 
                             custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
                             )


    ac_watts = np.round(power.ACOutputWatts.resample(time=average_time).mean(skipna=True).values[-2],1) 
    p3 = pn.indicators.Gauge(name=f'\n\nAC\n{batt_v}W', 
                             value=ac_watts,
                             format=' ', 
                             bounds=(0, 1500), 
                             colors=[(0.3, happy_color), (0.6, warning_color), (1.0, alarm_color)],
                             title_size=15,
                             height=220, 
				             num_splits=5, 
                             custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
                             )

    dc_watts = np.round(power.DCWatts.resample(time=average_time).mean(skipna=True).values[-1],0) 
    p4 = pn.indicators.Gauge(name=f'\n\nDC\n{batt_soc}W', 
                             value=dc_watts,
                             format=' ', 
                             bounds=(0, 300), 
                             colors=[(0.4, happy_color), (0.7, warning_color), (1, alarm_color)],
                             title_size=15,
                             height=220,
		             num_splits=5, 
                             custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
                             )


    row = pn.Row(p1, p2, p3, p4, 
		 pn.Spacer(width=100),
		 pn.Spacer(sizing_mode='stretch_width'))

    # %%
    #####################################################################
    # ....Column of time-series plots of battery and power variables
    #overlay = hv.Curve([1, 2, 3], vdims=['A']) * hv.Curve([2, 3, 4], vdims=['A']) * hv.Curve([3, 2, 1], vdims=['B'])
    #overlay.opts(multi_y=True)

    p5 = BatterySOC.hvplot(grid=True, 
                           height=400, 
                           title='BATTERIES (new data ' + mins_ago +'m ago; '+curr_time+')', 
                           label='SOC [%]',
                           color='mediumvioletred', responsive=True).opts(active_tools=['box_zoom']) * \
        BatteryWatts.hvplot(height=400, 
                            color='cornflowerblue', 
                            label='Batts [W]',
                            responsive=True)
    p5.opts(multi_y=True)

    splot = SolarWatts.hvplot.scatter(grid=True, 
                                      s = 2, 
                                      x = 'time', 
                                      y = ['Total', 'East', 'West', 'South'],
                                      color =  [warning_color, 'khaki', 'olive', 'darkgoldenrod' ],
                                  height=400, 
                                  title='RENEWABLES (new data ' + mins_ago +'m ago; '+curr_time+')',
                               label='Solar [W]',
                               responsive=True)

    #p6 = splot

    p6 = (splot* \
          WindWatts.hvplot.scatter(height=400, 
                                   x = 'time', 
                                   y = ['Wind [W]'], 
                                      s = 2, 
                              color='teal', 
                              label='Wind',
                              responsive=True))

    p6.opts(active_tools=['box_zoom'])

    splot = SolarWatts_Tot.hvplot(grid=True, 
                                  height=400, 
                                  title='RENEWABLES (new data ' + mins_ago +'m ago; '+curr_time+')',
                                  label='Solar [W]',
                                  color=warning_color, responsive=True)* \
          SolarWatts_W.hvplot(grid=True, 
                              label='West',
                               height=400, 
                               color='khaki', responsive=True)* \
          SolarWatts_S.hvplot(grid=True, 
                              label='South',
                               height=400, 
                               color='darkseagreen', responsive=True)* \
          SolarWatts_E.hvplot(grid=True, 
                              label='East',
                               height=400, 
                               color='tan', responsive=True)

    # p6 = hv.Overlay([SolarWatts_E.hvplot(title='RENEWABLES (most recent measurement from '+mins_ago+'m ago; '+curr_time+')',
    #                                      color='tan', label='Solar [W]',
    #                                      height=400, grid=True, responsive=True), 
    #                  SolarWatts_S.hvplot(color='darkkhaki', height=400, responsive=True),
    #                  SolarWatts_W.hvplot(color='darkgoldenrod', height=400, responsive=True),
    #                  SolarWatts_Tot.hvplot(color=warning_color,height=400, responsive=True)]) \
    #                 .opts(
    #                       responsive=True,
    #                       active_tools=['box_zoom']) * \
    # WindWatts.hvplot(height=400, 
    #                          color='lightblue', 
    #                          label='Wind [W]',
    #                          responsive=True).opts(multi_y=True)
    #p6.opts(multi_y=True)


    p7 = ACOutputWatts.hvplot(grid=True, 
                              height=400, 
                              title='OUTPUT (new data '+mins_ago+'m ago; '+curr_time+')', 
                              color='firebrick', 
                              label='AC [W]',
                              responsive=True).opts(active_tools=['box_zoom']) * \
                DCWatts.hvplot(height=400, 
                               color='darkgreen', 
                               label='DC [W]',
                               responsive=True)
    p7.opts(multi_y=True)

    col = pn.Column(p5, p6, p7)
    #col.servable()

    return pn.Column(pn.Column(row), col)

def create_tabs():

    update_button = pn.widgets.Button(name='ICECAPS MELT — MVP Dashboard, click to refresh data',
                                      button_type='primary', button_style='outline', 
                                      styles={'width':'96%'}, height=50,
                                      )
    pcs = pn.Column(pn.Spacer(height=10), 
                    pn.Row(pn.Spacer(sizing_mode='stretch_width'), update_button, pn.Spacer(sizing_mode='stretch_width')),
                    pn.Spacer(height=10), 
                    pn.panel(pn.bind(power_columns_wrapper, update_button), loading_indicator=True),
                    styles={'background': 'whitesmoke'})

    #power_title   = pn.pane.Markdown('# ICECAPS MELT — MVP Dashboard' ) 
    tabs          = pn.Tabs(('Minimum Viable Powersupply', pn.Column(pcs)))

    # %%
    #################### INSTRUMENT UPTIME #####################
    tabs.append(('Instrument Uptime', pn.pane.Markdown('# Coming soon...')))

    # %%
    #################### NEAR-SURFACE METEOROLOGY #####################
    tabs.append(('Near-surface Meteorology', pn.pane.Markdown('# Coming soon...')))

    # %%
    #################### SURFACE ENERGY BUDGET #####################
    tabs.append(('Surface Energy Budget', pn.pane.Markdown('# Coming soon...')))

    # %%
    #################### CLOUD PROPERTIES #####################
    tabs.append(('Cloud Properties', pn.pane.Markdown('# Coming soon...')))

    # %%
    tabs.append(('CL61', tab_cl61()))

    #tabs.servable(title='ICECAPS SLEIGH-MVP Dashboard')
    #tabs.servable(title='ICECAPS SLEIGH-MVP Dashboard')
    #tabs.show()

    return tabs

def get_power_data(start_date, end_date, data_dir='/data/power/level2/'):

    import glob

    data_list = []

    ds_list = []
    for curr_date in pd.date_range(start_date, end_date+datetime.timedelta(1)):
        data_list+=glob.glob(f'{data_dir}/power.mvp.level2.1min.'+curr_date.strftime('%Y%m%d')+ '.*.nc')
        ds = xr.open_dataset(glob.glob(f'{data_dir}/power.mvp.level2.1min.'+curr_date.strftime('%Y%m%d')+ '.*.nc')[0])
        ds_list.append(ds)
#    power = xr.open_mfdataset(data_list, drop_variables=['num_batts_installed, BattsOnline'])
    
    power = xr.concat(ds_list, dim='time')

    # ... select the requested range only... 
    power = power.sel(time=slice(start_date.to_datetime64(), end_date.to_datetime64()))

    return power.load()


def launch_server_process(panel_dict):

    server_thread = pn.serve(panel_dict, title='ICECAPS SLEIGH-MVP Dashboard',
                             port=6646, websocket_origin="*", show=False)

    return True # not necessary but explicit

def power_columns_wrapper(button_status):
    try:
        return power_columns(button_status)
    except:
        print_traceback(traceback.format_exc(), f"FAILURE")

def print_traceback(thetb, error_msg):

    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)
    print(f"!!! {error_msg} "                                                  , file=sys.stderr)
    print("\n\n"                                                               , file=sys.stderr)
    print(thetb                                                                   , file=sys.stderr)
    print(f"!!! ———————————————————————————————————————————————————————— !!! " , file=sys.stderr)

def main():

    while True:           

        try:
            tabs = create_tabs()
            
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
