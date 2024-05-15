import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

def DL_cl61():
    return DataLoader.DataLoader('cl61', '/data/cl61/daily', 'summary_cl61_%Y%m%d.nc')

class lidarplot(Plottables.Plot_2D):
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

    lidar_tab = Tab.Tab(
        name='CL61', 
        plottables=[plot_backscatter, plot_lindepol],
        dld = None,
        required_DL=['cl61'],
        longname='Vaisalla CL61 Ceilometer',
        augment_dims=augment
    )
    return lidar_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_lidar_tab()
    tab.dld = {'cl61':DL_cl61()}
    serve(tab, port=5006, websocket_origin='*', show=True)