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
dtr = (dt.datetime(2024,3,14), dt.datetime(2024,3,16)) # should start by displaying two days of data
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
    plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-2), cnorm='log', augment=augment)
    plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,1), cmap='greys', augment=augment)
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


################################################### MVP

class mvpplot_scatter(dashboard.Plottables.Plot_scatter):
    def __init__(self,variable, title, augment=False, postproc = None):
        pargs = {
            'x': 'time', 'xlabel': 'time'
        }
        if augment: pargs.update({'x':'time_'})
        super().__init__('mvp',variable, pargs)
        self.plotargs['title'] = title
        del self.plotargs['label']
        if postproc is not None:
            self.postproc = postproc

class mvpplot_scatter_batts(mvpplot_scatter):
    def plot(self, dd):
        try:
            try:
                tcoords = [('time', dd['mvp'].time.values)]
            except:
                tcoords = [('time', dd['mvp'].time_.values)]
            BatterySOC = xr.DataArray(dd['mvp'].BatterySOC.values, coords=tcoords, name='SOC [%]')
            BatteryWatts = xr.DataArray(dd['mvp'].BatteryWatts.values, coords=tcoords, name='BattS [W]')

            p = BatterySOC.hvplot(
                grid=True, 
                height=400, 
                title='BATTERIES', 
                label='SOC [%]',
                color='mediumvioletred', responsive=True
            ).opts(active_tools=['box_zoom']) * \
            BatteryWatts.hvplot(
                height=400, 
                color='cornflowerblue', 
                label='Batts [W]',
                responsive=True
            )
            p.opts(multi_y=True)
            return p
        except Exception as e:
            print(traceback.format_exc())
            return e


class mvpplot_scatter_renewables(mvpplot_scatter):
    def plot(self, dd):
        try:
            try:
                tcoords = [('time', dd['mvp'].time.values)]
            except:
                tcoords = [('time', dd['mvp'].time_.values)]
            SolarWatts_E = xr.DataArray(dd['mvp'].SolarWatts_East.values  , coords=tcoords, name='East')
            SolarWatts_W = xr.DataArray(dd['mvp'].SolarWatts_West.values  , coords=tcoords, name='West')
            SolarWatts_S = xr.DataArray(dd['mvp'].SolarWatts_South.values , coords=tcoords, name='South')
            SolarWatts_Tot = xr.DataArray(
                SolarWatts_E.values + SolarWatts_S.values + SolarWatts_W.values, coords=tcoords, name='Total')
            WindWatts = xr.DataArray(dd['mvp'].WindWatts.values, coords=tcoords, name='Wind [W]')
            SolarWatts = xr.merge([SolarWatts_Tot, SolarWatts_E, SolarWatts_W, SolarWatts_S])

            warning_color = 'khaki'

            splot = SolarWatts.hvplot.scatter(
                grid=True, 
                s = 2, 
                x = 'time', 
                y = ['Total', 'East', 'West','South'],
                color =  ['palevioletred', 'khaki', 'olive', 'darkgoldenrod'],
                height=400, 
                title='RENEWABLES',
                label='Solar [W]',
                responsive=True
            )
            p = splot*WindWatts.hvplot.scatter(
                height=400, 
                x = 'time', 
                y = ['Wind [W]'], 
                s = 2, 
                color='teal', 
                label='Wind',
                responsive=True
            )
            p.opts(active_tools=['box_zoom'])
            return p
        except Exception as e:
            print(traceback.format_exc())
            return e

def postproc_mvp_batts(dd):
    tdim = [k for k in dd['mvp'].sizes.keys() if 'time' in k][0]
    print('lnmepnfepmfepomfspomfmfespomf', tdim)
    tcoords = [('time', dd['mvp'][tdim].values)]
    
    BatterySOC = xr.DataArray(dd['mvp'].BatterySOC.values, coords=tcoords, name='SOC [%]')
    
    BatteryWatts = xr.DataArray(dd['mvp'].BatteryWatts.values, coords=tcoords, name='Power [W]')

    dd['batts'] = xr.merge([BatterySOC,BatteryWatts])
    return dd


def postproc_mvp_renewables(dd):
    #dd = { 'mvp': xr.Dataset(mvp data) }
    tdim = [k for k in dd['mvp'].sizes.keys() if 'time' in k][0]
    print('lnmepnfepmfepomfspomfmfespomf', tdim)
    tcoords = [('time', dd['mvp'][tdim].values)]

    SolarWatts_E = xr.DataArray(dd['mvp'].SolarWatts_East.values  , coords=tcoords, name='East')
    SolarWatts_W = xr.DataArray(dd['mvp'].SolarWatts_West.values  , coords=tcoords, name='West')
    SolarWatts_S = xr.DataArray(dd['mvp'].SolarWatts_South.values , coords=tcoords, name='South')
    SolarWatts_Tot = xr.DataArray(
        SolarWatts_E.values + SolarWatts_S.values + SolarWatts_W.values, coords=tcoords, name='Total')
    
    WindWatts = xr.DataArray(dd['mvp'].WindWatts.values, coords=tcoords, name='Wind')
    RenewableWatts = xr.merge([SolarWatts_Tot, SolarWatts_E, SolarWatts_W, SolarWatts_S, WindWatts])

    dd['renewable'] = RenewableWatts
    return dd


def get_mvp_tab(augment=False):
    #p_batts = mvpplot_scatter_batts('battery', 'BATTERIES', augment=augment)
    p_batts_soc = dashboard.Plottables.Plot_scatter(
        'batts', 'SOC [%]',
        plotargs={
            'ylim':(-5,105), 'title':'BATTERIES',
            'color': 'mediumvioletred','responsive':True, 'multi_y':True
        },
        postproc=postproc_mvp_batts
    )
    p_batts_soc.datasource = 'batts'
    p_batts_soc.postproc = postproc_mvp_batts
    p_batts_power = dashboard.Plottables.Plot_scatter(
        'batts', 'Power [W]',
        plotargs={
            'color':'cornflowerblue', 'ylim':(None,None), 'multi_y':True
        }
    )
    p_batts_power.datasource = 'batts'
    p_batts_power.postproc = postproc_mvp_batts


    p_renenwables_1 = mvpplot_scatter(
        ['Total', 'East', 'West', 'South', 'Wind'],
        'RENEWABLES', augment=augment,
        postproc=postproc_mvp_renewables
    )
    p_renenwables_1.plotargs.update(
        {
            'color': ['palevioletred','khaki', 'olive', 'darkgoldenrod', 'teal'],
            #'label': ['Total', 'East', 'West', 'South', 'Wind']
        }
    )
    p_renenwables_1.datasource = 'renewable'
    p_renenwables_1.postproc = postproc_mvp_renewables

    p_renenwables = mvpplot_scatter_renewables('renewables', 'RENEWABLES', augment=augment)

    #tab
    mvp_tab = dashboard.Tab.Tab(
        'MVP', 
        #[p_renenwables_1, p_renenwables],
        [p_batts_soc*p_batts_power, p_renenwables_1, p_renenwables],
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
    gfs['recency_alpha'] = 1 - 0.9 * gfs['recency'] / np.max(gfs['recency'])
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
            get_gpr_tab(augment),
            get_simba_tab(augment),
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
#tab = get_gfs_tab()
#tab.dld = dld
#pn.serve(tab, port=5006, websocket_origin='*', show=True)


