'''Author: Andrew Martin
Creation Date: 16/4/24

Script to demonstrate the new OOP implementation of the dashboard. This will contain multiple tabs for instruments with different plotting functions.
'''
import warnings
warnings.filterwarnings('once')


import panel as pn
import dashboard
import datetime as dt

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

dld = {
    'cl61': DL_cl61, 
    'mrr': DL_mrr,
    'gpr5':DL_gpr5,
    'gpr7':DL_gpr7,
    'simba':DL_simba
}

# global datetime picker arguments
start = dt.datetime(2024,3,10)
end = dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
dtr = (dt.datetime(2024,3,14), dt.datetime(2024,3,16)) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}


class lidarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear', augment=False):
        pargs={
            'x':'time', 'y':'range', 'ylabel':'Height AGL (m)', 'xlabel':'time', 'ylim':(0,5000)
        }
        if augment: pargs.update({'x':'time_', 'y':'range_'})
        super().__init__('cl61', variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title']=title


class radarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear',augment=False):
        pargs = {
            'x':'time', 'y':'range_bins','ylabel':'height AGL (m)','xlabel':'time'
        }
        if augment: pargs.update({'x':'time_', 'y':'range_bins_'})
        super().__init__('mrr',variable,pargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title


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


def get_lidar_tab(augment=False):
    plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-2), cnorm='log', augment=augment)
    plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,1), augment=augment)
    lidar_tab = dashboard.Tab.Tab(
        name='CL61', 
        plottables=[plot_backscatter, plot_lindepol],
        dld = None,
        required_DL=['cl61'],
        longname='Vaisalla CL61 Ceilometer',
        augment_dims=augment
    )
    return lidar_tab


def get_radar_tab(augment=False):
    plot_Z = radarplot('Z_median', 'Z median (dBZ)', clim=(-10, 30), augment=augment)
    plot_VEL = radarplot('VEL_median', 'Doppler VEL median (m/s)', clim=(-10,10), augment=augment)
    plot_WIDTH = radarplot('WIDTH_median', 'Dopper WIDTH median (m/s)', clim=(5e-3, 5), cnorm='log', augment=augment)
    radar_tab = dashboard.Tab.Tab(
        name='MRR',
        plottables=[plot_Z, plot_VEL, plot_WIDTH],
        dld=None,
        required_DL=['mrr'],
        longname='Micro Rain Radar (MRR)',
        augment_dims=augment
    )
    return radar_tab


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


def get_tabview(dld, augment) -> dashboard.TabView.TabView:
    tabview = dashboard.TabView.TabView(
        tablist=[
            get_lidar_tab(augment),
            get_radar_tab(augment),
            get_gpr_tab(augment)
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


pn.serve(oop_dashboard(dtp_args,dld),title='OOP Dashboard', port=5006, websocket_origin='*', show=True )

# Framework for testing a singular desired tab
#tab = get_radar_tab()
#tab.dld = dld
#pn.serve(tab, port=5006, websocket_origin='*', show=True)


