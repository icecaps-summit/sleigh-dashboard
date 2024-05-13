'''Author: Andrew Martin
Creation Date: 16/4/24

Script to demonstrate the new OOP implementation of the dashboard. This will contain multiple tabs for instruments with different plotting functions.
'''
import warnings
warnings.filterwarnings('once')


import panel as pn
import dashboard
import datetime as dt
import hvplot.xarray
import holoviews as hv
import xarray as xr
import numpy as np

import traceback

import dashboard.Dashboard
import dashboard.Plottables
import dashboard.DataLoader
import dashboard.Tab
import dashboard.TabView

# DataLoader objects need to be defined to control the dataflow in the program
DL_cl61 = dashboard.DataLoader.DataLoader('cl61', '/data/cl61/daily', 'summary_cl61_%Y%m%d.nc')
DL_mrr = dashboard.DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')
#DL_asfs
DL_gpr5 = dashboard.DataLoader.DataLoader('gpr5', '/data/gpr', 'summary_gpr_5G_%Y%m%d.nc')
DL_gpr7 = dashboard.DataLoader.DataLoader('gpr7', '/data/gpr', 'summary_gpr_7G_%Y%m%d.nc')
#DL_mvp
DL_simba = dashboard.DataLoader.DataLoader('simba', '/data/simba', 'summary_simba_%Y%m%d.nc')
DL_mvp = dashboard.DataLoader.DataLoader('mvp', '/data/power/level2', 'power.mvp.level2.1min.%Y%m%d.000000.nc')

dld = {
    'cl61': DL_cl61, 
    'mrr': DL_mrr,
    'gpr5':DL_gpr5,
    'gpr7':DL_gpr7,
    'simba':DL_simba,
    'mvp':DL_mvp
}

# global datetime picker arguments
start = dt.datetime(2024,3,10)
end = None#dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...

now = dt.datetime.now()
dtr_end = dt.datetime(year=now.year, month=now.month, day=now.day)
one_day = dt.timedelta(days=1)
dtr = (dtr_end-one_day, dtr_end) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}


########################### LIDAR


class lidarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear', augment=False):
        pargs={
            'x':'time', 'y':'range', 'ylabel':'Height AGL (m)', 'xlabel':'time', 'ylim':(0,5000)
        }
        if augment: pargs.update({'x':'time_', 'y':'range_'})
        super().__init__('cl61', variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title']=title


def get_lidar_tab(augment=False):
    plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-4), cnorm='log', augment=augment)

    plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,0.5), cmap='cividis', augment=augment)

    lidar_tab = dashboard.Tab.Tab(
        name='CL61', 
        plottables=[plot_backscatter, plot_lindepol],
        dld = None,
        required_DL=['cl61'],
        longname='Vaisalla CL61 Ceilometer',
        augment_dims=augment
    )
    return lidar_tab


############################################# RADAR

class radarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear',augment=False):
        pargs = {
            'x':'time', 'y':'range_bins','ylabel':'height AGL (m)','xlabel':'time'
        }
        if augment: pargs.update({'x':'time_', 'y':'range_bins_'})
        super().__init__('mrr',variable,pargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title


def get_radar_tab(augment=False):
    plot_Z = radarplot('Z_median', 'Z median (dBZ)', clim=(-10, 30), augment=augment)
    plot_VEL = radarplot('VEL_median', 'Doppler VEL median (m/s)', clim=(-10,10), augment=augment, cmap='RdBu')
    plot_WIDTH = radarplot('WIDTH_median', 'Dopper WIDTH median (m/s)', clim=(5e-3, 5), cnorm='log', augment=augment, cmap='magma')
    radar_tab = dashboard.Tab.Tab(
        name='MRR',
        plottables=[plot_Z, plot_VEL, plot_WIDTH],
        dld=None,
        required_DL=['mrr'],
        longname='Micro Rain Radar (MRR)',
        augment_dims=augment
    )
    return radar_tab


##################################################### GPR


class gprplot_2d(dashboard.Plottables.Plot_2D):
    def __init__(self, gpr, variable, title, clim=(None, None), cmap='viridis', cnorm='linear', augment=False):
        pargs = {
            'x': 'time', 'y':'step', 'xlabel':'time', 'ylabel':'step', 'flip_yaxis':True
        }
        if augment: pargs.update({'x':'time_', 'y':'step_'})
        super().__init__(f'gpr{gpr}', variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title'] = title


class gprplot_scatter(dashboard.Plottables.Plot_scatter):
    def __init__(self, gpr, variable, title, augment=False):
        pargs = {
            'x': 'time', 'xlabel':'time'
        }
        if augment: pargs.update({'x': 'time_'})
        super().__init__(f'gpr{gpr}', variable, pargs)
        self.plotargs['title'] = title


def get_gpr_tab(augment=False):
    plot_DM5 = gprplot_2d(5, 'DM_mean', 'Combined DM mean', augment=augment)
    plot_DM7 = gprplot_2d(7, 'DM_mean', 'Combined DM mean', augment=augment)
    
    plot_DM5_std = gprplot_2d(5, 'DM_std', 'Combined DM std', augment=augment)
    plot_DM7_std = gprplot_2d(7, 'DM_std', 'Combined DM std', augment=augment)

    plot_f5 = gprplot_scatter(5,'f', 'Combined f', augment)
    plot_f7 = gprplot_scatter(7,'f', 'Combined f', augment)

    gpr_tab = dashboard.Tab.Tab(
       name='GPR',
       plottables=[
           plot_DM7*plot_DM5,
           plot_DM5_std*plot_DM7_std,
           plot_f5*plot_f7
        ],
       dld=None,
       required_DL=['gpr5', 'gpr7'],
       longname='Ground Penetrating Radar',
       augment_dims=augment 
    )
    return gpr_tab


#################################################### SIMBA


class simbaplot_2d(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim=(None, None), cmap='viridis', cnorm='linear', augment=False):
        pargs = {
            'x':'time', 'y':'height', 'xlabel':'time', 'ylabel':'Height AGL (cm)'
        }
        if augment: pargs.update({'x':'time_', 'y':'height_'})
        super().__init__('simba',variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title'] = title


class simbaplot_scatter(dashboard.Plottables.Plot_scatter):
    def __init__(self, variable, title, augment=False):
        pargs = {
            'x': 'time', 'xlabel': 'time'
        }
        if augment: pargs.update({'x':'time_'})
        super().__init__('simba',variable, pargs)
        self.plotargs['title'] = title


def get_simba_tab(augment=False):
    p_T = simbaplot_2d('temperature', 'Temperature (°C)', augment=augment, clim=(-35,5))
    p_samplespan = simbaplot_scatter('sample_span', 'Sample span', augment=augment)
    p_batt = simbaplot_scatter('battery_voltage', 'Battery Voltage (V)', augment=augment)
    p_startstop = simbaplot_scatter(['sample_start','sample_end'], 'Sample time', augment=augment)
    p_numsamp = simbaplot_scatter('sample_number', 'Sample number', augment=augment)
    p_num_seq = simbaplot_scatter('sequence_number', 'Sequence number', augment=augment)

    simba_tab = dashboard.Tab.Tab(
        name='Simba',
        plottables=[
            p_T, p_samplespan, p_batt, 
            p_startstop,
            p_numsamp, p_num_seq
        ],
        dld=None,
        required_DL=['simba'],
        longname='Simba thermistor string',
        augment_dims=augment
    )
    return simba_tab

################################################### MWR

DL_mwr = dashboard.DataLoader.DataLoader('mwr', '/data/mwr', 'summary_mwr_%Y%m%d.nc')

dld['mwr']=DL_mwr

class mwr_plot(dashboard.Plottables.Plot_scatter):
    def __init__(self, variable, title, augment=False):
        pargs = {
            'x': 'time', 'xlabel': 'time'
        }
        if augment: pargs.update({'x':'time_'})
        super().__init__('mwr',variable, pargs)
        self.plotargs['title'] = title


def get_mwr_tab(augment=False):
    p_TB_mean = mwr_plot('BRT_TBs_mean', 'Mean brightness temperature', augment)
    p_TB_mean.plotargs['by']='number_frequencies'

    p_alarm = mwr_plot('HKD_AlFl_sum', 'Alarm Flag (summed)', augment)

    p_recT = mwr_plot('HKD_Rec1_T_mean','Receiver temperature', augment) * mwr_plot('HKD_Rec2_T_mean', 'Receiver temperature', augment)

    mwr_tab = dashboard.Tab.Tab(
        name='MWR',
        plottables=[p_TB_mean, p_alarm,p_recT],
        dld=None,
        required_DL=['mwr'],
        longname='HATPRO Microwave Radiometer',
        augment_dims=augment
    )
    return mwr_tab


################################################### ASFS


DL_asfs_slow = dashboard.DataLoader.DataLoader('asfs', '/data/asfs','summary_asfs_slow_%Y%m%d.nc')

dld['asfs'] = DL_asfs_slow

class asfsplot(dashboard.Plottables.Plot_line_scatter):
    def __init__(self, variable: str | list[str], plotargs: dict, title ,augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        plotargs['title'] = title
        super().__init__('asfs', variable, plotargs)


def get_asfs_tab(augment=False):
    p_rad = \
        asfsplot('sr30_swu_IrrC_mean',{'label':'SWU', 'ylabel':'Power (W/m2)'},'RADIATION', augment=augment) * \
        asfsplot('sr30_swd_IrrC_mean',{'label':'SWD'},'RADIATION', augment=augment) * \
        asfsplot('ir20_lwu_Wm2_mean',{'label':'LWU'},'RADIATION', augment=augment) * \
        asfsplot('ir20_lwd_Wm2_mean',{'label':'LWD'},'RADIATION', augment=augment)
    
    p_fp = \
        asfsplot('fp_A_Wm2_mean', {'label':'A', 'ylabel':'Power (W/m2)'}, 'FLUX PLATES', augment=augment) * \
        asfsplot('fp_B_Wm2_mean', {'label':'B'}, 'FLUX PLATES', augment=augment)
    
    p_fantach = \
        asfsplot('sr30_swu_fantach_mean', {'label':'SWU', 'ylabel': 'tachometer (?)'},'FANTACH', augment=augment) * \
        asfsplot('sr30_swd_fantach_mean', {'label':'SWD'},'FANTACH', augment=augment) * \
        asfsplot('ir20_lwu_fan_mean', {'label':'LWU'}, 'FANTACH', augment=augment) * \
        asfsplot('ir20_lwd_fan_mean', {'label':'LWD'}, 'FANTACH', augment=augment)
    
    p_rad_heat = \
        asfsplot('sr30_swu_heatA_mean', {'label':'SWU', 'ylabel': 'Heater (?)'}, 'RAD HEATERS', augment=augment) * \
        asfsplot('sr30_swd_heatA_mean', {'label':'SWD'}, 'RAD HEATERS', augment=augment)
    
    p_sr50 = asfsplot('sr50_dist_mean', {'ylabel': 'Height (?)'}, 'SR50 SNOW HEIGHT', augment=augment)

    p_wind = \
        asfsplot('wspd_u_mean', {'label':'u', 'ylabel':'speed (m/s)'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_v_mean', {'label':'v'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_w_mean', {'label':'w'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_vec_mean', {'label':'total'}, 'SONIC ANEMOMETER', augment=augment)
    
    p_wind_dir = asfsplot('wdir_vec_mean', {'ylabel':'wind direction (###deg from REF###)'}, 'WIND DIRECTION', augment=augment)

    p_vaisala_T = asfsplot('vaisala_T_mean', {'ylabel': 'Temperature (C)'}, 'VAISALA TEMPERATURE', augment=augment)
    p_vaisala_P = asfsplot('vaisala_P_mean', {'ylabel': 'Pressure (?)'}, 'VAISALA PRESSURE', augment=augment)
    p_vaisala_RH = asfsplot('vaisala_RH_mean', {'ylabel': 'Relative humidity (%)'}, 'VAISALA RH', augment=augment)
    
    asfs_tab = dashboard.Tab.Tab(
        'ASFS',
        [p_rad, p_fp, p_sr50, p_wind, p_wind_dir, p_vaisala_T, p_vaisala_P, p_vaisala_RH, p_fantach, p_rad_heat],
        dld=None,
        required_DL=['asfs'],
        longname='Atmospheric Surface Flux Station',
        augment_dims=augment
    )
    return asfs_tab


################################################### MVP

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

DL_mvp = dashboard.DataLoader.DataLoader('mvp', '/data/power/level2', 'power.mvp.level2.1min.%Y%m%d.000000.nc', file_preproc=mvp_load_preproc)
dld['mvp'] = DL_mvp

class mvp_dials_plot(dashboard.Plottables.BasePlottable):
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


class Plot_MultiY_scatter(dashboard.Plottables.Plot_scatter):
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

class mvpplot_scatter(dashboard.Plottables.Plot_scatter):
    def __init__(self,variable, title, plotargs, augment=False, postproc = None):
        plotargs.update({'x': 'time', 'xlabel':'time'})
        pargs = plotargs
        if augment: pargs.update({'x':'time_'})
        super().__init__('mvp',variable, pargs)
        self.plotargs['title'] = title
        del self.plotargs['label']
        if postproc is not None:
            self.postproc = postproc


def get_mvp_tab(augment=False):
    p_zero = dashboard.Plottables.Plot_hline('mvp', 'BatterySOC',{'color':'black'},0)

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
    mvp_tab = dashboard.Tab.Tab(
        'MVP', 
        #[p_renenwables_1, p_renenwables],
        #[p_batts_soc*p_batts_power, p_renenwables_1, p_renenwables,p_renewables_new],
        [p_dials],
        #[p_dials, p_SOC, p_batteryWatts, p_renewables, p_ACDC * p_zero],
        dld, ['mvp'], 
        'Minimum Viable Powersystem',augment_dims=augment
    )
    
    return mvp_tab




##################################################
#GFS weather

def preproc_GFS(gfs):
    gfs = gfs.expand_dims({'init_time':[gfs.time.values[0]]})
    gfs = gfs.rename_dims({'time': 'time_index'})
    gfs['time'] = xr.DataArray(
        data = [gfs.time.values], dims=['init_time','time_index']
    )
    gfs['recency'] = (gfs.time - gfs.init_time)
    
    #f_alpha = lambda x,n: 0.1+ 0.9* ( 1 - np.power(x,n))
    f_alpha = lambda x,n: (1 - x) * np.exp(-4*np.power(x,2))
    
    #gfs['recency_alpha'] = 1 - 0.9 * gfs['recency'] / np.max(gfs['recency'])
    
    gfs['recency_alpha']=f_alpha( gfs['recency']/np.max(gfs['recency']), 0.25)

    return gfs



class DataLoader_GFS(dashboard.DataLoader.DataLoader):
    def _get_files_from_dtr(self, dtr: tuple[dt.datetime, dt.datetime]) -> list[str]:
        flist = super()._get_files_from_dtr(dtr)
        flist_00 = [f.replace('*', '00') for f in flist]
        flist_06 = [f.replace('*', '06') for f in flist]

        flist_list = [ [f.replace('*',tstr) for f in flist] for tstr in ['00','06','12','18']]
        return [v for fl in flist_list for v in fl]


DL_gfs = DataLoader_GFS('gfs', '/data/weather/GFS', 'Raven_GFS_Global_0p5deg_%Y%m%d_*00.nc', sortby_dim='init_time', concat_dim = 'init_time', file_preproc=preproc_GFS)

dld['gfs'] = DL_gfs

class gfs_recency_alpha_plot(dashboard.Plottables.Plot_scatter):
    def __init__(self, variable, title, augment=False):
        pargs = {
            'x': 'time', 'xlabel': 'time'
        }
        if augment: pargs.update({'x': 'time_'})
        super().__init__('gfs', variable, pargs)
        self.plotargs['title']=title
        self.plotargs['s'] = 20
        self.plotfuncs=[self.plot]
        self.by = 'init_time'
        if augment: self.by += '_'

    def plot(self, dd):
        try:
            dd = self.postproc(dd)
            return dd['gfs'].hvplot.scatter(y=self.variable, alpha='recency_alpha', **self.plotargs, by=self.by)
        except Exception as e:
            return e

def get_gfs_tab(augment=False):
    #p_Ts = dashboard.Plottables.Plot_scatter(
    #   'gfs', 'Ts', 
    #    {'x':'time', 'by':'init_time', #'alpha':'recency_alpha'}
    #)
    p_Ts = gfs_recency_alpha_plot('Ts', 'Surface Temperature', augment=augment)
    p_Ps = gfs_recency_alpha_plot('Ps', 'Surface Pressure', augment=augment)
    p_ws = gfs_recency_alpha_plot('ws', 'Wind Speed', augment=augment)
    p_wd = gfs_recency_alpha_plot('wd', 'Wind direction', augment=augment)
    p_pr = gfs_recency_alpha_plot('pr', 'Precipitation', augment=augment)

    gfs_tab = dashboard.Tab.Tab(
        'GFS', [p_Ts, p_Ps, p_ws, p_wd, p_pr], dld, ['gfs'], 'GFS weather', augment_dims=augment
    )
    return gfs_tab




####################################################
# Dashboard



def get_tabview(dld, augment) -> dashboard.TabView.TabView:
    tabview = dashboard.TabView.TabView(
        tablist=[
            #get_mvp_tab(augment),
            get_lidar_tab(augment),
            get_radar_tab(augment),
            get_mwr_tab(augment),
            get_asfs_tab(augment),
            get_gpr_tab(augment),
            get_simba_tab(augment),
            get_mvp_tab(augment),
            get_gfs_tab(augment),
        ],
        dld=dld,
        augment_dims=augment
    )
    return tabview


def oop_dashboard(dtp_args,dld):
    db = dashboard.Dashboard.Dashboard(
        dtp_args=dtp_args,
        dict_DL=dld,
        tabview_func=get_tabview
    )
    return db

serve_dashboard = lambda: oop_dashboard(dtp_args, dld)


pn.serve(serve_dashboard,title='OOP Dashboard', port=5006, websocket_origin='*', show=True )

# Framework for testing a singular desired tab
#tab = get_asfs_tab()
#tab.dld = dld
#pn.serve(tab, port=5006, websocket_origin='*', show=True)


