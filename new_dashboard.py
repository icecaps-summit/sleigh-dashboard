'''Author: Andrew Martin
Creation Date: 15/4/24

Script to demonstrate the new OOP implementation of the dashboard.
'''


import panel as pn
import dashboard
import datetime as dt

import dashboard.Dashboard
import dashboard.Plottables
import dashboard.DataLoader
import dashboard.Tab
import dashboard.TabView

# DataLoader objects need to be defined to control the dataflow in the program
DL_lidar = dashboard.DataLoader.DataLoader('cl61', '/data/cl61/daily', 'summary_cl61_%Y%m%d.nc')
DL_radar = dashboard.DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')

dld = {'cl61': DL_lidar, 'mrr': DL_radar}


# we need to define the datetime picker that the Dashboard utilitses
start = dt.datetime(2024,3,10)
end = dt.datetime(2024,3,25) # deliberately including days at the end where data doesn't exist, DataLoader should be impervious to these problems...
dtr = (dt.datetime(2024,3,14), dt.datetime(2024,3,16)) # should start by displaying two days of data
dtp_args = {'value':dtr, 'start':start, 'end':end, 'name':'global dtp picker'}

### LIDAR
#### PLOTTABLES
# starting simple, backscatter
lidar_plot_backscatter = dashboard.Plottables.Plot_2D(
    datasource='cl61', variable='beta_att_mean',
    plotargs={
        'x':'time', 'y':'range', 'ylabel': 'Height AGL (m)', 'xlabel':'time', 'ylim':(0,5000), 'title': 'mean attenuated backscatter'
    }, 
    cnorm='log', 
    clim=(1e-8, 1e-2)
)
lidar_plot_lindepol = dashboard.Plottables.Plot_2D(
    datasource='cl61', variable='linear_depol_ratio_median',
    plotargs={
        'x':'time', 'y':'range', 'ylabel':'Height AGL (m)', 'xlabel':'time', 'ylim':(0,5000), 'title':'Linear depolarisation ratio'
    },
    clim=(0,1)
)

lidar_tab = dashboard.Tab.Tab(
    name='lidar', 
    plottables=[lidar_plot_backscatter, lidar_plot_lindepol],
    dld = dld, # TODO:THIS NEEDS FIXING
    required_DL=['cl61'],
    longname='Vaisalla CL61 Ceilometer'
)

### RADAR
#### PLOTTABLES
class radarplot(dashboard.Plottables.Plot_2D):
    def __init__(self, variable, title, clim, cmap='viridis', cnorm='linear'):
        pargs = {
            'x':'time', 'y':'range_bins','ylabel':'height AGL (m)','xlabel':'time'
        }
        super().__init__('mrr',variable,pargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title

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

tabview = dashboard.TabView.TabView([lidar_tab, radar_tab])


db = dashboard.Dashboard.Dashboard(dtp_args, dld, tabview)



pn.serve({'dashboard': db}, title='OOP dashboard', port=5006, websocket_origin='*', show=True)