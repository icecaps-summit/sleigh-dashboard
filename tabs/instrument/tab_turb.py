import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

def DL_asfs_turb():
    return DataLoader.DataLoader('turb', '/data/asfs','summary_asfs_turb_%Y%m%d.nc')

class asfsplot(Plottables.Plot_line_scatter):
    def __init__(self, variable: str | list[str], plotargs: dict, title ,augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        super().__init__('turb', variable, plotargs)
        self.plotargs['title'] = title


def get_turb_tab(augment=False):
    
    p_flux = \
        asfsplot('Hs_mean', {'label': 'Hs', 'ylabel':'Flux (Wm2)'}, 'HEAT FLUXES', augment=augment) *\
        asfsplot('Hl_mean', {'label': 'Hl'}, 'HEAT FLUXES', augment=augment) *\
        asfsplot('bulk_Hs_mean', {'label': 'turb_Hs'}, 'HEAT FLUXES', augment=augment) *\
        asfsplot('bulk_Hl_mean', {'label': 'turb_Hl'}, 'HEAT FLUXES', augment=augment)
    
    p_drag = \
        asfsplot('Cd_mean', {'label':'Cd', 'ylabel':'Drag coefficient (units?)'}, 'DRAG COEFICIENT', augment=augment)*\
        asfsplot('bulk_Cd_mean', {'label':'turb_Cd'}, 'DRAG COEFFICIENT', augment=augment)
    
    p_ustar = \
        asfsplot('ustar_mean', {'label':'ustar', 'ylabel':'ustar (units?)'}, 'USTAR', augment=augment) * \
        asfsplot('bulk_ustar_mean', {'label':'turb_ustar'}, 'USTAR', augment=augment)

    turb_tab = Tab.Tab(
        'turb',
        [p_flux, p_drag, p_ustar],
        dld=None,
        required_DL=['turb'],
        longname='Atmospheric Surface Flux Station - Turbulence',
        augment_dims=augment
    )
    return turb_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_turb_tab()
    tab.dld = {'turb':DL_asfs_turb()}
    serve(tab, port=5006, websocket_origin='*', show=True)