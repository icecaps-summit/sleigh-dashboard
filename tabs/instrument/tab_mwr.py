import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

def DL_mwr():
    return DataLoader.DataLoader('mwr', '/data/mwr', 'summary_mwr_%Y%m%d.nc')

class mwr_plot(Plottables.Plot_line_scatter):
    def __init__(self, variable, title, plotargs={}, augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        plotargs['title'] = title
        if augment: plotargs['x'] = 'time_'
        super().__init__('mwr',variable, plotargs)
        self.plotargs['title'] = title


def get_mwr_tab(augment=False):
    by='number_frequencies'
    if augment: by += '_'
    p_TB_mean = mwr_plot('BRT_TBs_mean', 'Mean brightness temperature', {'by':by}, augment=augment)

    p_alarm = mwr_plot('HKD_AlFl_sum', 'Alarm Flag (summed)',{}, augment=augment)

    p_recT = mwr_plot('HKD_Rec1_T_mean','Receiver temperature', {}, augment=augment) * mwr_plot('HKD_Rec2_T_mean', 'Receiver temperature', {}, augment=augment)

    mwr_tab = Tab.Tab(
        name='MWR',
        plottables=[p_TB_mean, p_alarm,p_recT],
        dld=None,
        required_DL=['mwr'],
        longname='HATPRO Microwave Radiometer',
        augment_dims=augment
    )
    return mwr_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_mwr_tab()
    tab.dld = {'mwr':DL_mwr()}
    serve(tab, port=5006, websocket_origin='*', show=True)