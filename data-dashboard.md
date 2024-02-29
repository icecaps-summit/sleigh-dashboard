---
title: "ICECAPS-MELT - RAVEN CAMP 2024"
author: 
    Von P. Walden
    Michael Gallagher
date: 28 February 2024
---

# SLEIGH Dashboard for ICECAPS-MELT

```python
import xarray as xr
import hvplot.xarray # noqa
import holoviews as hv
import panel as pn

pn.extension(template='fast')

power = xr.open_dataset('data/power/level2/power.mvp.level2.1min.20240229.000000.nc')
```

## Power Summary

```python
p1 = pn.indicators.Number(name='Battery SOC', value=power.BatterySOC.resample(time='1h').mean().values[-1], format='{value:.0f}%', colors=[(25, 'red'), (50, 'yellow'), (100, 'green')]
)

p2 = pn.indicators.Number(name='Power Usage (DC)', value=power.DCWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(100, 'green'), (200, 'yellow'), (300, 'red')]
)

p3 = pn.indicators.Number(name='Power Usage (AC)', value=power.ACOutputWatts.resample(time='1h').mean().values[-1], format='{value:.0f}W', colors=[(250, 'green'), (350, 'yellow'), (500, 'red')]
)

p4 = pn.indicators.Number(name='Battery Voltage', value=power.BatteryVoltage.resample(time='1h').mean().values[-1], format='{value:.0f}V', colors=[(40, 'red'), (45, 'yellow'), (55, 'green'), (60, 'yellow'), (70, 'red') ]
)

row1 = pn.Row(p1, pn.Spacer(sizing_mode='stretch_width'), p2, pn.Spacer(sizing_mode='stretch_width'), p3, pn.Spacer(sizing_mode='stretch_width'), p4)

row1.servable()

batterySOC = xr.DataArray(power.BatterySOC.values, coords=[("time", power.time.values)], name='BatterySOC')

p5 = batterySOC.hvplot(line_width=5, width=1200, height=600, title='Battery State Of Charge')

row2 = pn.Row(p5)
row2.servable()
```
