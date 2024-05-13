import warnings
warnings.filterwarnings("once")

import xarray as xr
import panel as pn
import holoviews as hv
import numpy as np

from sleigh_dashboard import DataLoader, Plottables, Tab


def mvp_load_preproc(mvp):
    tcoords = [('time', mvp.time.values)]
    mvp['BatterySOC'] = xr.DataArray(mvp.BatterySOC.values, coords=tcoords, name='SOC [%]')
    mvp['BatteryWatts'] = xr.DataArray(mvp.BatteryWatts.values, coords=tcoords, name='BattS [W]')

    mvp['SolarWatts_Tot'] = xr.DataArray(
        mvp.SolarWatts_East.values
        + mvp.SolarWatts_South.values
        + mvp.SolarWatts_West.values,
        coords=tcoords, name='Total'
    )

    mvp['SolarWatts_E'] = xr.DataArray(mvp.SolarWatts_East.values  , coords=tcoords, name='East')
    mvp['SolarWatts_W'] = xr.DataArray(mvp.SolarWatts_West.values  , coords=tcoords, name='West')
    mvp['SolarWatts_S'] = xr.DataArray(mvp.SolarWatts_South.values , coords=tcoords, name='South')

    mvp['WindWatts'] = xr.DataArray(mvp.WindWatts.values, coords=tcoords, name='Wind [W]')
    mvp['ACOutputWatts'] = xr.DataArray(mvp.ACOutputWatts.values, coords=tcoords, name='AC [W]')
    mvp['DCInverterWatts'] = xr.DataArray(mvp.DCInverterWatts.values, coords=tcoords, name='DCInverterWatts')

    mvp['DCWatts'] = mvp.SolarWatts_Tot + mvp.WindWatts - mvp.BatteryWatts - mvp.DCInverterWatts
    mvp.DCWatts.name = 'DC [W]'
    return mvp

DL_mvp = DataLoader.DataLoader('mvp', '/data/power/level2', 'power.mvp.level2.1min.%Y%m%d.000000.nc', file_preproc=mvp_load_preproc)

class mvp_dials_plot(Plottables.BasePlottable):
    def __init__(self):
        super().__init__('mvp', 'BatterySOC', {})
        self.plotfuncs = [self.plot]

    def plot(self, dd):
        try:
            alarm_color   = 'palevioletred'
            warning_color = 'khaki'
            happy_color   = 'mediumseagreen'

            t_avg = '20Min'
            batt_soc = np.round(dd['mvp'].BatterySOC.resample(time=t_avg).mean(skipna=True).values[-1],0)
            batt_v = np.round(dd['mvp'].BatteryVolts.resample(time=t_avg).mean(skipna=True).values[-1], 0)
            ac_watts = np.round(dd['mvp'].ACOutputWatts.resample(time=t_avg).mean(skipna=True).values[-2], 1)
            dc_watts = np.round(dd['mvp'].DCWatts.resample(time=t_avg).mean(skipna=True).values[-1],0)

            G1 = pn.indicators.Gauge(
                name=f'SOC\n\n{batt_soc}%',
                value=batt_soc, bounds=(0,100), 
                colors=[(0.2,alarm_color), (0.5, warning_color), (1, happy_color)],
                title_size=15,height=220, num_splits=5,
                custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
            )
            G2 = pn.indicators.Gauge(
                name=f'BATT\n\n{batt_v}V',
                value=batt_v, bounds=(48, 58), 
                colors=[(0.15, alarm_color), (0.3, warning_color), (0.7, happy_color),(0.85, warning_color), (1.0, alarm_color)],
                title_size=15, height=220, num_splits=5, 
                custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
            )
            G3 = pn.indicators.Gauge(
                name=f'AC\n\n{ac_watts}W',
                value=ac_watts, bounds=(0, 1500), 
                colors=[(0.3, happy_color), (0.6, warning_color), (1.0, alarm_color)],
                title_size=15, height=220, num_splits=5, 
                custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}
            )
            G4 = pn.indicators.Gauge(
                name=f'DC\n\n{dc_watts}W',
                value=dc_watts, bounds=(0, 300), 
                colors=[(0.4, happy_color), (0.7, warning_color), (1, alarm_color)],
                title_size=15, height=220, num_splits=5, 
                custom_opts={"detail": {"fontSize": "5"}, "axislabel": {"fontSize": "5"}}     
            )
            R = pn.Row(G1, G2, G3, G4, sizing_mode='stretch_width')
            return R
        except Exception as e:
            return e


class Plot_MultiY_scatter(Plottables.Plot_scatter):
    def __init__(self, datasource, variable, plotargs, ylims, vdims, labels, height=300, s=5):
        super().__init__(datasource, variable, plotargs, height, s)
        self.ylims = ylims
        self.vdims = vdims # TODO: fix multi_y issues
        self.labels=labels
        self.plotargs['responsive'] = True
        del self.plotargs['label']

    def plot(self, dd):
        try:
            dd = self.postproc(dd)
            plots = []
            for v, vd, lab in zip(self.variable, self.vdims, self.labels):
                plots.append(
                    dd[self.datasource][v].hvplot.scatter(**self.plotargs, ylim=self.ylims[vd],
                    #vdims=[vd],
                    yaxis=vd,
                    label=lab).opts(multi_y=True, legend_position='bottom_right')
                )
            p = hv.Overlay(plots).opts(multi_y=True, legend_position='top_left')
            print('legend moved?')
            #p.opts(multi_y=True)
            return p
        except Exception as e:
            return e

class mvpplot_scatter(Plottables.Plot_line_scatter):
    def __init__(self,variable, title, plotargs, augment=False, postproc = None):
        plotargs.update({'x': 'time', 'xlabel':'time'})
        if augment: plotargs.update({'x':'time_'})
        plotargs['title'] = title
        super().__init__('mvp',variable, plotargs)
        if postproc is not None:
            self.postproc = postproc


def get_mvp_tab(augment=False):
    p_zero = Plottables.Plot_hline('mvp', 'BatterySOC',{'color':'black'},0)

    p_dials = mvp_dials_plot()

    p_renewables= Plot_MultiY_scatter(
        'mvp', 
        ['SolarWatts_Tot', 'SolarWatts_E', 'SolarWatts_S', 'SolarWatts_W', 'WindWatts'], 
        {'x':'time', 'xlabel':'time', 'title':'RENEWABLES'}, 
        ylims={'left':(0,5000),'right':(0,2000)},
        vdims=['left','left','left','left','right'],
        labels=['Solar total', 'East', 'South', 'West', 'Wind']
    )
    p_SOC = mvpplot_scatter(
        'BatterySOC', 'Battery State of Charge',
        {'ylim':(-5,105), 'ylabel':'SOC %'},
        augment=augment
    )
    p_batteryWatts = mvpplot_scatter(
        'BatteryWatts', 'Battery Power', 
        {'ylabel':'Power (W)'},
        augment=augment
    )*p_zero

    p_ACDC = mvpplot_scatter(
        ['ACOutputWatts', 'DCWatts'], 'OUTPUT',
        {'label':['AC', 'DC'], 'ylim':(-100, None)},
        augment=augment
    )
    p_ACDC= Plot_MultiY_scatter(
        'mvp', 
        ['ACOutputWatts', 'DCWatts'], 
        {'x':'time', 'xlabel':'time', 'title':'OUTPUT'}, 
        ylims={'left':(-100,None)},
        vdims=['left','left'],
        labels=['AC', 'DC']
    )

    #tab
    mvp_tab = Tab.Tab(
        'MVP', 
        #[p_renenwables_1, p_renenwables],
        #[p_batts_soc*p_batts_power, p_renenwables_1, p_renenwables,p_renewables_new],
        #[p_dials],
        [p_SOC, p_batteryWatts, p_renewables, p_ACDC * p_zero],
        None, ['mvp'], 
        'Minimum Viable Powersystem',augment_dims=augment
    )
    
    return mvp_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_mvp_tab()
    tab.dld = {'mvp':DL_mvp}
    serve(tab, port=5006, websocket_origin='*', show=True)