'''

Author: Andrew Martin
Creation date: 15/5/24

Script containing the functionality for the surface energy budget science tab for the
ICECAPS MELT project.  The dld is expected to be provided from the create_dld() function
in dashboard_instruments 

'''

import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

DL_asfs = DataLoader.DataLoader('lidar', '/data/cl61', 'summary_cl61_%Y%m%d.nc')
DL_turb = DataLoader.DataLoader('mrr','/data/mrr', 'summary_mrr_%Y%m%d.nc')
dld = {
    'asfs':DL_asfs,
    'turb':DL_turb
}

class augplot2d(Plottables.Plot_2D):
    def __init__(self, datasource, variable, plotargs, title, clim, cmap='viridis', cnorm='linear',augment=False):
        if augment:
            plotargs['x'] += '_'
            plotargs['y'] += '_'
        super().__init__(datasource,variable,plotargs, cmap=cmap, clim=clim, cnorm=cnorm)
        self.plotargs['title'] = title

class augplot1d(Plottables.Plot_line_scatter):
    def __init__(self, datasource, variable, plotargs, title, height=300, lw=2, s=50, marker='+', posptroc=(lambda x:x), augment=False):
        if augment: plotargs['x'] += '_'
        if augment and 'by' in plotargs: plotargs['by'] += '_'
        super().__init__(datasource, variable, plotargs, height, lw, s, marker, postproc=posptroc)
        self.plotargs['title'] = title

def get_seb_tab(augment=False):
    pargs_asfs = {'x':'time', 'xlabel':'time', 'ylabel':'Power (W/m2)'}
    
    def pproc_rad(dd):
        dd['asfs']['SW'] = dd['asfs']['sr30_swd_IrrC_mean'] - dd['asfs']['sr30_swu_IrrC_mean']
        dd['asfs']['LW'] = dd['asfs']['ir20_lwd_Wm2_mean'] - dd['asfs']['ir20_lwu_Wm2_mean']
        dd['asfs']['RAD'] = dd['asfs']['SW'] + dd['asfs']['LW']
        return dd

    p_sw = \
        augplot1d('asfs', 'sr30_swu_IrrC_mean', {**pargs_asfs, 'label':'SWU'},'SW RADIATION', augment=augment) * \
        augplot1d('asfs', 'sr30_swd_IrrC_mean', {'label':'SWD'},'SW RADIATION', augment=augment) * \
        augplot1d('asfs', 'SW', {'label':'SW total'},'SW RADIATION', posptroc=pproc_rad, augment=augment)

    def pproc_LW_total(dd):
        dd['asfs']['LW'] = dd['asfs']['ir20_lwd_Wm2_mean'] - dd['asfs']['ir20_lwu_Wm2_mean']
        return dd
    p_lw = \
        augplot1d('asfs', 'ir20_lwu_Wm2_mean', {**pargs_asfs, 'label':'LWU'}, 'LW RADIATION', augment=augment) * \
        augplot1d('asfs', 'ir20_lwd_Wm2_mean', {'label':'LWD'}, 'LW RADIATION', augment=augment) * \
        augplot1d('asfs', 'LW', {'label':'LW total'}, 'LW RADIATION', posptroc=pproc_rad, augment=augment)

    p_rad = \
        augplot1d('asfs', 'SW', {**pargs_asfs, 'label':'SW'}, 'NET RADIATION', posptroc=pproc_rad, augment=augment) *\
        augplot1d('asfs', 'LW', {**pargs_asfs, 'label':'LW'}, 'NET RADIATION', posptroc=pproc_rad, augment=augment) *\
        augplot1d('asfs', 'RAD', {**pargs_asfs, 'label':'NET'}, 'NET RADIATION', posptroc=pproc_rad, augment=augment)

    def pproc_turbulent(dd):
        dd['asfs']['TURB'] = dd['turb']['Hs_mean'] + dd['turb']['Hl_mean']
        return dd
    p_turb = \
        augplot1d('turb', 'Hs_mean', {**pargs_asfs, 'label':'Sensible'}, 'TURBULENT HEAT', augment=augment) *\
        augplot1d('turb', 'Hl_mean', {'label':'Latent'}, 'TURBULENT HEAT FLUXES', augment=augment) *\
        augplot1d('asfs', 'TURB', {'label': 'Net'}, 'TURBULENT HEAT FLUXES', posptroc=pproc_turbulent,augment=augment)
    
    p_subsurf = \
        augplot1d('asfs', 'fp_A_Wm2_mean', {**pargs_asfs, 'label':'A'}, 'SUBSURFACE FLUX', augment=augment) *\
        augplot1d('asfs', 'fp_B_Wm2_mean', {'label':'B'}, 'SUBSURFACE FLUX', augment=augment) *\
        augplot1d('asfs', 'fp_C_Wm2_mean', {'label':'C'}, 'SUBSURFACE FLUX', augment=augment)

    seb_tab = Tab.Tab(
        name='SEB',
        plottables=[p_sw, p_lw, p_rad, p_turb, p_subsurf],
        dld=None,
        required_DL=['asfs','turb'],
        longname='Surface Energy Budget',
        augment_dims=augment
    )
    return seb_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_seb_tab()
    tab.dld = dld
    serve(tab, port=5006, websocket_origin='*', show=True)
