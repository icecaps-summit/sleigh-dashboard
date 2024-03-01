import numpy as np
import pandas as pd
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn
pn.extension('echarts')
pn.extension(template='fast')

#####################################################################
# ....Determine today's and yesterday's dates
today = pd.Timestamp.now('UTC')
yesterday = pd.Timestamp.now('UTC')-pd.Timedelta('25h')

#####################################################################
# ....Read data from SLEIGH and MVP
power = xr.open_mfdataset(['/data/power/level2/power.mvp.level2.1min.' + yesterday.strftime('%Y%m%d') + '.000000.nc', '/data/power/level2/power.mvp.level2.1min.' + today.strftime('%Y%m%d') + '.000000.nc'])
power = power.sel(time=slice(yesterday.to_datetime64(), today.to_datetime64()))

#################### MINIMUM VIABLE POWERSUPPLY #####################
#####################################################################
# ....Row of battery and power numbers and gauges
p1 = pn.indicators.Number(name='Battery SOC', value=power.BatterySOC.resample(time='1h').mean().values[-1], format='{value:.0f}%', colors=[(25, 'red'), (50, 'gold'), (100, 'green')])

p2 = pn.indicators.Gauge(name="DC Power", value=np.round(power.DCWatts.resample(time='1h').mean().values[-1]), bounds=(0, 250), format='{value} W', colors=[(0.4, 'green'), (0.6, 'gold'), (1, 'red')],custom_opts={"pointer": {"itemStyle": {"color": 'black'}}})
#p2 = pn.indicators.Number(name='DC Power', value=power.DCWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(100, 'green'), (200, 'yellow'), (300, 'red')])

p3 = pn.indicators.Gauge(name="AC Power", value=np.round(power.ACOutputWatts.resample(time='1h').mean().values[-1]), bounds=(0, 1500), format='{value} W',colors=[(0.167, 'green'), (0.3, 'gold'), (1, 'red')],custom_opts={"pointer": {"itemStyle": {"color": 'black'}}})
#p3 = pn.indicators.Number(name='AC Power', value=power.ACOutputWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(250, 'green'), (350, 'yellow'), (500, 'red')])

p4 = pn.indicators.Number(name='Battery Voltage', value=power.BatteryVoltage.resample(time='1h').mean().values[-1], format='{value:.0f} V', colors=[(40, 'red'), (45, 'yellow'), (55, 'green'), (60, 'yellow'), (70, 'red') ])

row = pn.Row(p1, pn.Spacer(sizing_mode='stretch_width'), p2, pn.Spacer(sizing_mode='stretch_width'), p3, pn.Spacer(sizing_mode='stretch_width'), p4)

#####################################################################
# ....Column of time-series plots of battery and power variables
BatterySOC = xr.DataArray(power.BatterySOC.values, coords=[("time", power.time.values)], name='SOC [%]')
BatteryWatts = xr.DataArray(power.BatteryWatts.values, coords=[("time", power.time.values)], name='BattS [W]')

#overlay = hv.Curve([1, 2, 3], vdims=['A']) * hv.Curve([2, 3, 4], vdims=['A']) * hv.Curve([3, 2, 1], vdims=['B'])
#overlay.opts(multi_y=True)

p5 = BatterySOC.hvplot(grid=True, line_width=5, width=1400, height=400, title='BATTERIES', color='lightseagreen', vdims=['SOC [%]']).opts(active_tools=['box_zoom']) * BatteryWatts.hvplot(grid=True, line_width=5, width=1400, height=400, color='lightblue', vdims=['Batts [W]'])
p5.opts(multi_y=True)

SolarWatts_Tot = xr.DataArray(power.SolarWatts_East.values + power.SolarWatts_South.values + power.SolarWatts_West.values, coords=[("time", power.time.values)], name='Solar [W]')

WindWatts = xr.DataArray(power.WindWatts.values, coords=[("time", power.time.values)], name='Wind [W]')

p6 = SolarWatts_Tot.hvplot(grid=True, line_width=5, width=1400, height=400, title='RENEWABLES', color='sienna', vdim=['Solar [W]']).opts(active_tools=['box_zoom']) * WindWatts.hvplot(line_width=5, width=1400, height=400, color='darkkhaki', vdims=['Wind [W]'])
p6.opts(multi_y=True)

ACOutputWatts = xr.DataArray(power.ACOutputWatts.values, coords=[("time", power.time.values)], name='AC [W]')
DCInverterWatts = xr.DataArray(power.DCInverterWatts.values, coords=[("time", power.time.values)], name='DCInverterWatts')
DCWatts = SolarWatts_Tot + WindWatts - BatteryWatts - DCInverterWatts
DCWatts.name = 'DC [W]'

p7 = ACOutputWatts.hvplot(grid=True, line_width=5, width=1400, height=400, title='OUTPUT', color='firebrick', vdims=['AC [W]']).opts(active_tools=['box_zoom']) * DCWatts.hvplot(line_width=5, width=1400, height=400, color='blue', vdims=['DC [W]'])
p7.opts(multi_y=True)

col = pn.Column(p5, p6, p7)
#col.servable()

tabs = pn.Tabs(('Minimum Viable Powersupply', pn.Column(row, col)))

#################### INSTRUMENT UPTIME #####################
tabs.append(('Instrument Uptime', p5))

#################### NEAR-SURFACE METEOROLOGY #####################
tabs.append(('Near-surface Meteorology', p5))

#################### SURFACE ENERGY BUDGET #####################
tabs.append(('Surface Energy Budget', p5))

#################### CLOUD PROPERTIES #####################
tabs.append(('Cloud Properties', p5))

tabs.servable(title='SLEIGH-MVP Dashboard')
