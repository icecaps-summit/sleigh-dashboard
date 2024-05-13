import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

DL_simba = DataLoader.DataLoader('simba', '/data/simba', 'summary_simba_%Y%m%d.nc')


class simbaplot_2d(Plottables.Plot_2D):
    def __init__(self, variable, title, clim=(None, None), cmap='viridis', cnorm='linear', augment=False):
        pargs = {
            'x':'time', 'y':'height', 'xlabel':'time', 'ylabel':'Height AGL (cm)'
        }
        if augment: pargs.update({'x':'time_', 'y':'height_'})
        super().__init__('simba',variable, pargs, cmap=cmap, cnorm=cnorm, clim=clim)
        self.plotargs['title'] = title


class simbaplot_scatter(Plottables.Plot_line_scatter):
    def __init__(self, variable, title, plotargs={}, augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        super().__init__('simba',variable, plotargs)
        self.plotargs['title'] = title

def get_simba_tab(augment=False):
    p_T = simbaplot_2d('temperature', 'Temperature (°C)', augment=augment, clim=(-35,5))
    p_samplespan = simbaplot_scatter('sample_span', 'Sample span', {},augment=augment)
    p_batt = simbaplot_scatter('battery_voltage', 'Battery Voltage (V)', {}, augment=augment)
    p_startstop = simbaplot_scatter('sample_start', 'Sample time', {'label':'start'}, augment=augment) * simbaplot_scatter('sample_end', 'Sample time', {'label':'end'}, augment=augment)
    p_numsamp = simbaplot_scatter('sample_number', 'Sample number', {},  augment=augment)
    p_num_seq = simbaplot_scatter('sequence_number', 'Sequence number', {},  augment=augment)

    simba_tab = Tab.Tab(
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


if __name__ == '__main__':
    from panel import serve
    tab = get_simba_tab()
    tab.dld = {'simba':DL_simba}
    serve(tab, port=5006, websocket_origin='*', show=True)