'''Author: Andrew Martin
Creation date: 13/5/24

Script containing the functionality for the clouds thematic tab for the ICECAPS MELT project.
The dld is expected to be provided from the create_dld() function in dashboard_instruments
'''

import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

DL_cl61 = DataLoader.DataLoader('lidar', '/data/cl61', 'summary_cl61_%Y%m%d.nc')
DL_mrr = DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')
DL_mwr = DataLoader.DataLoader('mwr', '/data/mwr', 'summary_mwr_%Y%m%d.nc')
dld = {
    'cl61':DL_cl61,
    'mrr':DL_mrr,
    'mwr':DL_mwr
}

class augplot2d(Plottables.Plot_2D):
    def __init__(self, datasource, variable, plotargs, title, clim, cmap='viridis', cnorm='linear',augment=False):
        if augment:
            plotargs['x'] += '_'
            plotargs['y'] += '_'
        super().__init__(datasource,variable,plotargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title

class augplot1d(Plottables.Plot_line_scatter):
    def __init__(self, datasource, variable, plotargs, title, height=300, lw=2, s=50, marker='+', augment=False):
        if augment: plotargs['x'] += '_'
        if augment and 'by' in plotargs: plotargs['by'] += '_'
        super().__init__(datasource, variable, plotargs, height, lw, s, marker)
        self.plotargs['title'] = title

def get_clouds_tab(augment=False):
    pargs_cl61 = {'x':'time', 'y':'range', 'ylabel':'Height AGL (m)', 'xlabel':'time', 'ylim':(0,5000)}
    plot_backscatter = augplot2d('cl61', 'beta_att_mean', pargs_cl61, 'Mean attenuated backscatter - lidar', clim=(1e-8,1e-4), cnorm='log', augment=augment)
    plot_depol = augplot2d('cl61', 'linear_depol_ratio_median', pargs_cl61, 'Median linear depolarisation ratio - lidar', clim=(0,0.5), cmap='cividis', augment=augment)

    pargs_mrr = {'x':'time', 'y':'range_bins','ylabel':'height AGL (m)','xlabel':'time', 'ylim':(0,5000)}
    plot_Z = augplot2d('mrr','Z_median', pargs_mrr, 'Z median (dBZ) - radar', clim=(-10, 30), augment=augment)
    plot_VEL = augplot2d('mrr','VEL_median', pargs_mrr, 'Doppler VEL median (m/s) - radar', clim=(-2,6), augment=augment, cmap='RdBu')

    pargs_mwr = {'x':'time', 'by':'number_frequencies'}
    plot_TB = augplot1d('mwr', 'BRT_TBs_mean', pargs_mwr, 'Mean brightness temperature', augment=augment)

    clouds_tab = Tab.Tab(
        name='Clouds',
        plottables=[plot_backscatter, plot_depol, plot_Z, plot_VEL, plot_TB],
        dld=None,
        required_DL=['cl61','mrr','mwr'],
        longname='Clouds',
        augment_dims=augment
    )
    return clouds_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_clouds_tab()
    tab.dld = dld
    serve(tab, port=5006, websocket_origin='*', show=True)
