import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

DL_mrr = DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')

class radarplot(Plottables.Plot_2D):
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
    radar_tab = Tab.Tab(
        name='MRR',
        plottables=[plot_Z, plot_VEL, plot_WIDTH],
        dld=None,
        required_DL=['mrr'],
        longname='Micro Rain Radar (MRR)',
        augment_dims=augment
    )
    return radar_tab

