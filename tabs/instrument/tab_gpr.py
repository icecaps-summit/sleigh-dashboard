import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

def DL_gpr5():
    return DataLoader.DataLoader('gpr5', '/data/gpr', 'summary_gpr_5G_%Y%m%d.nc')
def DL_gpr7():
    return DataLoader.DataLoader('gpr7', '/data/gpr', 'summary_gpr_7G_%Y%m%d.nc')

class gprplot_2d(Plottables.Plot_2D):
    def __init__(self, gpr, variable, title, clim=(None, None), cmap='viridis', cnorm='linear', augment=False):
        pargs = {
            'x': 'time', 'y':'step', 'xlabel':'time', 'ylabel':'step', 'flip_yaxis':True
        }
        if augment: pargs.update({'x':'time_', 'y':'step_'})
        super().__init__(f'gpr{gpr}', variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title'] = title


class gprplot_scatter(Plottables.Plot_line_scatter):
    def __init__(self, gpr, variable, plotargs, title, augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        super().__init__(f'gpr{gpr}', variable, plotargs)
        self.plotargs['title'] = title


def get_gpr_tab(augment=False):
    plot_DM5 = gprplot_2d(5, 'DM_mean', 'Combined DM mean', augment=augment)
    plot_DM7 = gprplot_2d(7, 'DM_mean', 'Combined DM mean', augment=augment)
    
    plot_DM5_std = gprplot_2d(5, 'DM_std', 'Combined DM std', augment=augment)
    plot_DM7_std = gprplot_2d(7, 'DM_std', 'Combined DM std', augment=augment)

    plot_f5 = gprplot_scatter(5,'f', {'ylabel':'f (?)', 'label':'5'}, 'Combined f', augment)
    plot_f7 = gprplot_scatter(7,'f', {'label': '7'}, 'Combined f', augment)

    gpr_tab = Tab.Tab(
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


if __name__ == '__main__':
    from panel import serve
    tab = get_gpr_tab()
    tab.dld = {'gpr5':DL_gpr5(), 'gpr7':DL_gpr7()}
    serve(tab, port=5006, websocket_origin='*', show=True)
