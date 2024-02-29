---
title: "ICECAPS-MELT - RAVEN CAMP 2024"
author: 
    Von P. Walden
    Michael Gallagher
date: 28 February 2024
---

# SLEIGH Dashboard for ICECAPS-MELT

```python
import numpy as np
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn
pn.extension('echarts')
pn.extension(template='fast')

power = xr.open_dataset('data/power/level2/power.mvp.level2.1min.20240229.000000.nc')

p1 = pn.indicators.Number(name='Battery SOC', value=power.BatterySOC.resample(time='1h').mean().values[-1], format='{value:.0f}%', colors=[(25, 'red'), (50, 'gold'), (100, 'green')]
)

p2 = pn.indicators.Gauge(name="DC Power", value=np.round(power.DCWatts.resample(time='1h').mean().values[-1]), bounds=(0, 250), format='{value} W', colors=[(0.4, 'green'), (0.6, 'gold'), (1, 'red')])
#p2 = pn.indicators.Number(name='DC Power', value=power.DCWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(100, 'green'), (200, 'yellow'), (300, 'red')])

p3 = pn.indicators.Gauge(name="AC Power", value=np.round(power.ACOutputWatts.resample(time='1h').mean().values[-1]), bounds=(0, 1500), format='{value} W',colors=[(0.167, 'green'), (0.3, 'gold'), (1, 'red')],)
#p3 = pn.indicators.Number(name='AC Power', value=power.ACOutputWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(250, 'green'), (350, 'yellow'), (500, 'red')])

p4 = pn.indicators.Number(name='Battery Voltage', value=power.BatteryVoltage.resample(time='1h').mean().values[-1], format='{value:.0f} V', colors=[(40, 'red'), (45, 'yellow'), (55, 'green'), (60, 'yellow'), (70, 'red') ]
)

row = pn.Row(p1, pn.Spacer(sizing_mode='stretch_width'), p2, pn.Spacer(sizing_mode='stretch_width'), p3, pn.Spacer(sizing_mode='stretch_width'), p4)
row.servable()


batterySOC = xr.DataArray(power.BatterySOC.values, coords=[("time", power.time.values)], name='BatterySOC')

p5 = batterySOC.hvplot(line_width=7, width=1300, height=400, title='Batteries', color='darkcyan')
# Battery Watts = lightblue

solarWatts = xr.DataArray(power.SolarWatts_East.values + power.SolarWatts_South.values + power.SolarWatts_West.values, coords=[("time", power.time.values)], name='SolarWatts')

windWatts = xr.DataArray(power.WindWatts.values, coords=[("time", power.time.values)], name='windWatts')

p6 = solarWatts.hvplot(line_width=7, width=1300, height=400, title='Renewables', color='wheat') * windWatts.hvplot(line_width=7, width=1300, height=400, title='Renewables', color='purple')

ACOutputWatts = xr.DataArray(power.ACOutputWatts.values, coords=[("time", power.time.values)], name='ACOutputWatts')

DCWatts = xr.DataArray(power.DCWatts.values, coords=[("time", power.time.values)], name='DCWatts')

p7 = ACOutputWatts.hvplot(line_width=7, width=1300, height=400, title='Output', color='darkred') * DCWatts.hvplot(line_width=7, width=1300, height=400, title='Output', color='slategrey')

col = pn.Column(p5, p6, p7)
col.servable()
```
