#!/usr/bin/env -S python3 -u
import numpy as np
import pandas as pd
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn

import time, datetime

#pn.extension(design='material', template='material')

from multiprocessing import Process

import warnings
warnings.filterwarnings("ignore")


def process_data():

    pn.extension('echarts', template='fast', nthreads=4, notifications=False)


    #####################################################################
    # ....Determine today's and yesterday's dates
    today     = pd.Timestamp.now('UTC')
    yesterday = pd.Timestamp.now('UTC')-pd.Timedelta('24h')

    #####################################################################
    # ....Read data from SLEIGH and MVP
    power = get_power_data(start_date=yesterday, end_date=today, data_dir='/data/power/level2/')

    tz = datetime.timezone(datetime.timedelta(seconds=0))
    last_obs_time = pd.to_datetime(power.time.data[-1]).replace(tzinfo=tz)
    secs_ago =str(int(np.abs((last_obs_time- pd.Timestamp.now('UTC')).total_seconds()/60)))

    BatterySOC = xr.DataArray(power.BatterySOC.values,
                              coords=[("time", power.time.values)], name='SOC [%]')

    BatteryWatts = xr.DataArray(power.BatteryWatts.values,
                                coords=[("time", power.time.values)], name='BattS [W]')

    SolarWatts_Tot = xr.DataArray(power.SolarWatts_East.values
                                  + power.SolarWatts_South.values
                                  + power.SolarWatts_West.values,
                                  coords=[("time", power.time.values)], name='Total')

    SolarWatts_E = xr.DataArray(power.SolarWatts_East.values,
                                  coords=[("time", power.time.values)], name='East')
    SolarWatts_W = xr.DataArray(power.SolarWatts_West.values,
                                  coords=[("time", power.time.values)], name='West')
    SolarWatts_S = xr.DataArray(power.SolarWatts_South.values,
                                  coords=[("time", power.time.values)], name='South')


    WindWatts = xr.DataArray(power.WindWatts.values,
                             coords=[("time", power.time.values)], name='Wind [W]')

    ACOutputWatts = xr.DataArray(power.ACOutputWatts.values,
                                 coords=[("time", power.time.values)], name='AC [W]')

    DCInverterWatts = xr.DataArray(power.DCInverterWatts.values,
                                   coords=[("time", power.time.values)], name='DCInverterWatts')

    DCWatts = SolarWatts_Tot + WindWatts - BatteryWatts - DCInverterWatts

    DCWatts.name = 'DC [W]'

    SolarWatts = xr.merge([SolarWatts_Tot, SolarWatts_E, SolarWatts_W, SolarWatts_S])

    # %%
    p0 = pn.pane.Markdown('# ICECAPS SLEIGH-MVP Dashboard')
    title = row = pn.Row(p0)


    # %%
    #################### MINIMUM VIABLE POWERSUPPLY #####################
    #####################################################################
    averagingTime = '10T'    # Currently 10 minutes
    
    last_time = today

    # ....Row of battery and power numbers and gauges
    p1 = pn.indicators.Number(name='Battery SOC', 
                              value=power.BatterySOC.resample(time=averagingTime).mean().values[-1], 
                              format='{value:.0f}%',
                              colors=[(25, 'red'), (50, 'gold'), (100, 'green')]
    )

    p2 = pn.indicators.Gauge(name='DC Power', 
                             value=np.round(power.DCWatts.resample(time=averagingTime).mean().values[-1]), 
                             bounds=(0, 250), 
                             format='{value} W', 
                             colors=[(0.4, 'green'), (0.6, 'gold'), (1, 'red')],
                             tooltip_format='{b} : {c} W',
    )
    #                         custom_opts={"pointer": {"itemStyle": {"color": 'black'}}}
    #)

    p3 = pn.indicators.Gauge(name="AC Power", 
                             value=np.round(power.ACOutputWatts.resample(time=averagingTime).mean().values[-1]), 
                             bounds=(0, 1500), 
                             format='{value} W',
                             colors=[(0.167, 'green'), (0.3, 'gold'), (1, 'red')],
                             tooltip_format='{b} : {c} W',
    )
    #                         custom_opts={"pointer": {"itemStyle": {"color": 'black'}}}
    #)

    p4 = pn.indicators.Number(name='Battery Voltage', 
                              value=power.BatteryVoltage.resample(time=averagingTime).mean().values[-1], 
                              format='{value:.1f} V', 
                              colors=[(40, 'red'), (45, 'yellow'), (55, 'green'), (60, 'yellow'), (70, 'red')]
    )

    row = pn.Row(p1, pn.Spacer(sizing_mode='stretch_width'), 
                 p2, pn.Spacer(sizing_mode='stretch_width'), 
                 p3, pn.Spacer(sizing_mode='stretch_width'), 
                 p4
    )

    # %%
    #####################################################################
    # ....Column of time-series plots of battery and power variables
    #overlay = hv.Curve([1, 2, 3], vdims=['A']) * hv.Curve([2, 3, 4], vdims=['A']) * hv.Curve([3, 2, 1], vdims=['B'])
    #overlay.opts(multi_y=True)

    p5 = BatterySOC.hvplot(grid=True, 
                           height=400, 
                           title='BATTERIES (last data from ' + secs_ago +' mins ago)', 
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
                                      color =  ['gold', 'khaki', 'olive', 'darkgoldenrod' ],
                                  height=400, 
                                  title='RENEWABLES (last data from ' + secs_ago +' mins ago)',
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
                                  title='RENEWABLES (last data from ' + secs_ago +' mins ago)',
                               label='Solar [W]',
                               color='gold', responsive=True)* \
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


    # p6 = hv.Overlay([SolarWatts_E.hvplot(title='RENEWABLES (most recent measurement from '+secs_ago+' mins ago)',
    #                                      color='tan', label='Solar [W]',
    #                                      height=400, grid=True, responsive=True), 
    #                  SolarWatts_S.hvplot(color='darkkhaki', height=400, responsive=True),
    #                  SolarWatts_W.hvplot(color='darkgoldenrod', height=400, responsive=True),
    #                  SolarWatts_Tot.hvplot(color='gold',height=400, responsive=True)]) \
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
                              title='OUTPUT (last data from '+secs_ago+' mins ago)', 
                              color='firebrick', 
                              label='AC [W]',
                              responsive=True).opts(active_tools=['box_zoom']) * \
                DCWatts.hvplot(height=400, 
                               color='darkgreen', 
                               label='DC [W]',
                               responsive=True)
    p7.opts(multi_y=True)

    # %%
    col = pn.Column(p5, p6, p7)
    #col.servable()

    tabs = pn.Tabs(('Minimum Viable Powersupply', pn.Column(title, row, col)))

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
    #tabs.servable(title='ICECAPS SLEIGH-MVP Dashboard')
    #tabs.servable(title='ICECAPS SLEIGH-MVP Dashboard')
    #tabs.show()

    return tabs

def get_power_data(start_date, end_date, data_dir='/data/power/level2/'):

    import glob

    data_list = []
    for curr_date in pd.date_range(start_date, end_date+datetime.timedelta(1)):
        data_list+=glob.glob(f'{data_dir}/power.mvp.level2.1min.'+curr_date.strftime('%Y%m%d')+ '.*.nc')


    power = xr.open_mfdataset(data_list)

    #power = xr.concat([power_yesterday, power_today], dim='time')

    # ... select the requested range only... 
    power = power.sel(time=slice(start_date.to_datetime64(), end_date.to_datetime64()))

    return power.load()


def launch_server_process(panel_dict):

    server_thread = pn.serve(panel_dict, title='ICECAPS SLEIGH-MVP Dashboard',
                             port=6646, websocket_origin="*", show=False)

    return True # not necessary but explicit

def main():

    while True:           

        try:
            tabs = process_data()
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
