import warnings
warnings.filterwarnings("once")

import xarray as xr
import numpy as np
import datetime as dt

from sleigh_dashboard import DataLoader, Plottables, Tab



def preproc_GFS(gfs):
    gfs = gfs.expand_dims({'init_time':[gfs.time.values[0]]})
    gfs = gfs.rename_dims({'time': 'time_index'})
    gfs['time'] = xr.DataArray(
        data = [gfs.time.values], dims=['init_time','time_index']
    )
    gfs['recency'] = (gfs.time - gfs.init_time)
    
    #f_alpha = lambda x,n: 0.1+ 0.9* ( 1 - np.power(x,n))
    f_alpha = lambda x,n: (1 - x) * np.exp(-4*np.power(x,2))
    
    #gfs['recency_alpha'] = 1 - 0.9 * gfs['recency'] / np.max(gfs['recency'])
    
    gfs['recency_alpha']=f_alpha( gfs['recency']/np.max(gfs['recency']), 0.25)

    return gfs



class DataLoader_GFS(DataLoader.DataLoader):
    def _get_files_from_dtr(self, dtr: tuple[dt.datetime, dt.datetime]) -> list[str]:
        flist = super()._get_files_from_dtr(dtr)

        flist_list = [ [f.replace('*',tstr) for f in flist] for tstr in ['00','06','12','18']]
        return [v for fl in flist_list for v in fl]


def DL_gfs():
    return DataLoader_GFS('gfs', '/data/weather/GFS', 'Raven_GFS_Global_0p5deg_%Y%m%d_*00.nc', sortby_dim='init_time', concat_dim = 'init_time', file_preproc=preproc_GFS)

class gfs_recency_alpha_plot(Plottables.Plot_scatter):
    def __init__(self, variable, title, plotargs={}, augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        super().__init__('gfs', variable, plotargs)
        self.plotargs['title'] = title
        self.plotargs['s'] = 20
        self.plotfuncs=[self.plot]
        self.by = 'init_time'
        if augment: self.by += '_'

    def plot(self, dd):
        try:
            dd = self.postproc(dd)
            return dd['gfs'].hvplot.scatter(y=self.variable, alpha='recency_alpha', **self.plotargs, by=self.by)
        except Exception as e:
            return e
        

def get_gfs_tab(augment=False):
    #p_Ts = dashboard.Plottables.Plot_scatter(
    #   'gfs', 'Ts', 
    #    {'x':'time', 'by':'init_time', #'alpha':'recency_alpha'}
    #)
    p_Ts = gfs_recency_alpha_plot('Ts', 'Surface Temperature', {}, augment=augment)
    p_Ps = gfs_recency_alpha_plot('Ps', 'Surface Pressure', {}, augment=augment)
    p_ws = gfs_recency_alpha_plot('ws', 'Wind Speed', {}, augment=augment)
    p_wd = gfs_recency_alpha_plot('wd', 'Wind direction', {}, augment=augment)
    p_pr = gfs_recency_alpha_plot('pr', 'Precipitation', {}, augment=augment)

    gfs_tab = Tab.Tab(
        'GFS', [p_Ts, p_Ps, p_ws, p_wd, p_pr], None, ['gfs'], 'GFS weather', augment_dims=augment
    )
    return gfs_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_gfs_tab()
    tab.dld = {'gfs':DL_gfs()}
    serve(tab, port=5006, websocket_origin='*', show=True)