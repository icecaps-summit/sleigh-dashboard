'''Author: Andrew Martin
Creation Date: 15/4/24

Script to demonstrate the new OOP implementation of the dashboard.
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
DL_gpr5 = dashboard.DataLoader.DataLoader('gpr5', '/data/gpr', 'summary_gpr_5_%Y%m%d.nc')
DL_gpr7 = dashboard.DataLoader.DataLoader('gpr7', '/data/gpr', 'summary_gpr_7_%Y%m%d.nc')
#DL_mvp
DL_simba = dashboard.DataLoader.DataLoader('simba', '/data/simba', 'summary_simba_%Y%m%d.nc')

dld = {
    'cl61': DL_cl61, 
    'mrr': DL_mrr,
    'gpr5':DL_gpr5,
    'gpr7':DL_gpr7,
    'simba':DL_simba
}


# we need to define the datetime picker that the Dashboard utilitses
start = dt.datetime(2024,3,10)
end = dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
dtr = (dt.datetime(2024,3,14), dt.datetime(2024,3,16)) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}

### LIDAR
#### PLOTTABLES
# starting simple, backscatter
class lidarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear', i=0, augment=False):
        pargs={
            'x':'time', 'y':'range', 'ylabel':'Height AGL (m)', 'xlabel':f'time{" "*i}', 'ylim':(0,5000)
        }
        if augment: pargs.update({'x':'time_', 'y':'range_'})
        super().__init__('cl61', variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title']=title

class radarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear', i=0, augment=False):
        pargs = {
            'x':'time', 'y':'range_bins','ylabel':'height AGL (m)','xlabel':f'time{" "*i}'
        }
        if augment: pargs.update({'x':'time_', 'y':'range_bins_'})
        super().__init__('mrr',variable,pargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title

'''
lidar_plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-2), cnorm='log')
lidar_plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,1))

lidar_tab = dashboard.Tab.Tab(
    name='lidar', 
    plottables=[lidar_plot_backscatter, lidar_plot_lindepol],
    dld = dld, # TODO:THIS NEEDS FIXING
    required_DL=['cl61'],
    longname='Vaisalla CL61 Ceilometer'
)

### RADAR
#### PLOTTABLES

radar_plot_Z = radarplot('Z_median', 'Z median (dBZ)', clim=(-10, 30))
radar_plot_VEL = radarplot('VEL_median', 'Doppler VEL median (m/s)', clim=(-10,10))
radar_plot_WIDTH = radarplot('WIDTH_median', 'Dopper WIDTH median (m/s)', clim=(5e-3, 5), cnorm='log')

radar_tab = dashboard.Tab.Tab(
    name='mRr',
    plottables=[radar_plot_Z, radar_plot_VEL, radar_plot_WIDTH],
    dld=dld, # TODO: fix this...
    required_DL=['mrr'],
    longname='Micro Rain Radar (MRR)'
)

# I should be able to serve the individual tabs as panel-servable objects

tabview = lambda: dashboard.TabView.TabView([lidar_tab, radar_tab])


db = dashboard.Dashboard.Dashboard(dtp_args, dld, tabview)



#pn.serve({'dashboard': db}, title='OOP dashboard', port=5006, websocket_origin='*', show=True)
#pn.serve({'lidar_tab': lidar_tab}, title='OOP dashboard', port=5006, websocket_origin='*', show=True)
'''


def test_lidar_tab():
    DL_cl61 = dashboard.DataLoader.DataLoader('cl61', '/data/cl61/daily', 'summary_cl61_%Y%m%d.nc')
    lidar_plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-2), cnorm='log')
    lidar_plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,1))
    lidar_tab = dashboard.Tab.Tab(
        name='lidar', 
        plottables=[lidar_plot_backscatter, lidar_plot_lindepol],
        dld = {'cl61':DL_cl61}, # TODO:THIS NEEDS FIXING
        required_DL=['cl61'],
        longname='Vaisalla CL61 Ceilometer'
    )
    pn.serve(lidar_tab, title='test lidar tab', port=5006, websocket_origin='*', show=True)

def test_radar_tab():
    DL_mrr = DL_mrr = dashboard.DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')
    radar_plot_Z = radarplot('Z_median', 'Z median (dBZ)', clim=(-10, 30))
    radar_plot_VEL = radarplot('VEL_median', 'Doppler VEL median (m/s)', clim=(-10,10))
    radar_plot_WIDTH = radarplot('WIDTH_median', 'Dopper WIDTH median (m/s)', clim=(5e-3, 5), cnorm='log')
    radar_tab = dashboard.Tab.Tab(
        name='mRr',
        plottables=[radar_plot_Z, radar_plot_VEL, radar_plot_WIDTH],
        dld={'mrr': DL_mrr}, # TODO: fix this...
        required_DL=['mrr'],
        longname='Micro Rain Radar (MRR)'
    )
    pn.serve(radar_tab, title='test radar tab', port=5006, websocket_origin='*', show=True)

def create_dld():
    DL_cl61 = dashboard.DataLoader.DataLoader('cl61', '/data/cl61/daily', 'summary_cl61_%Y%m%d.nc')
    DL_mrr = DL_mrr = dashboard.DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')
    dld = {'cl61': DL_cl61, 'mrr': DL_mrr}
    return dld

def create_new_TabView(dld, augment):
    lidar_plot_backscatter = lidarplot('beta_att_mean', 'mean attenuated backscatter', (1e-8,1e-2), cnorm='log', augment=augment)
    lidar_plot_lindepol = lidarplot('linear_depol_ratio_median', 'median linear depolarisation ratio', (0,1), augment=augment)
    lidar_tab = dashboard.Tab.Tab(
        name='lidar', 
        plottables=[lidar_plot_backscatter, lidar_plot_lindepol],
        dld = None, # TODO:THIS NEEDS FIXING
        required_DL=['cl61'],
        longname='Vaisalla CL61 Ceilometer',
        augment_dims=augment
    )
    radar_plot_Z = radarplot('Z_median', 'Z median (dBZ)', clim=(-10, 30), augment=augment)
    radar_plot_VEL = radarplot('VEL_median', 'Doppler VEL median (m/s)', clim=(-10,10), augment=augment)
    radar_plot_WIDTH = radarplot('WIDTH_median', 'Dopper WIDTH median (m/s)', clim=(5e-3, 5), cnorm='log', augment=augment)
    radar_tab = dashboard.Tab.Tab(
        name='mRr',
        plottables=[radar_plot_Z, radar_plot_VEL, radar_plot_WIDTH],
        dld=None, # TODO: fix this...
        required_DL=['mrr'],
        longname='Micro Rain Radar (MRR)',
        augment_dims=augment
    )

    tabview = dashboard.TabView.TabView([lidar_tab, radar_tab], dld, augment_dims=augment)
    return tabview

def test_TabView():
    dld = create_dld()
    tbv = create_new_TabView(dld)
    pn.serve(tbv, title='TabView test', port=5006, websocket_origin='*', show=True)


def test_Dashboard():
    start = dt.datetime(2024,3,10)
    end = dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
    dtr = (dt.datetime(2024,3,14), dt.datetime(2024,3,16)) # should start by displaying two days of data
    dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}

    dld = create_dld()

    db = dashboard.Dashboard.Dashboard(dtp_args=dtp_args, dict_DL=dld, tabview_func=create_new_TabView)

    pn. serve(db, title='Dashboard test', port=5006, websocket_origin='*', show=True)


#test_lidar_tab()
#test_radar_tab()
#test_TabView()
test_Dashboard()