import warnings
warnings.filterwarnings("once")

from sleigh_dashboard import DataLoader, Plottables, Tab

def DL_asfs_slow():
    return DataLoader.DataLoader('asfs', '/data/asfs','summary_asfs_slow_%Y%m%d.nc')

class asfsplot(Plottables.Plot_line_scatter):
    def __init__(self, variable: str | list[str], plotargs: dict, title ,augment=False):
        plotargs['x'] = 'time'
        plotargs['xlabel'] = 'time'
        if augment: plotargs['x'] = 'time_'
        super().__init__('asfs', variable, plotargs)
        self.plotargs['title'] = title


def get_asfs_tab(augment=False):
    p_rad = \
        asfsplot('sr30_swu_IrrC_mean',{'label':'SWU', 'ylabel':'Power (W/m2)'},'RADIATION', augment=augment) * \
        asfsplot('sr30_swd_IrrC_mean',{'label':'SWD'},'RADIATION', augment=augment) * \
        asfsplot('ir20_lwu_Wm2_mean',{'label':'LWU'},'RADIATION', augment=augment) * \
        asfsplot('ir20_lwd_Wm2_mean',{'label':'LWD'},'RADIATION', augment=augment)
    
    p_fp = \
        asfsplot('fp_A_Wm2_mean', {'label':'A', 'ylabel':'Power (W/m2)'}, 'FLUX PLATES', augment=augment) * \
        asfsplot('fp_B_Wm2_mean', {'label':'B'}, 'FLUX PLATES', augment=augment)
    
    p_fantach = \
        asfsplot('sr30_swu_fantach_mean', {'label':'SWU', 'ylabel': 'tachometer (Hz)'},'SW FANS', augment=augment) * \
        asfsplot('sr30_swd_fantach_mean', {'label':'SWD'},'SW FANS', augment=augment)
    p_lw_fans = \
        asfsplot('ir20_lwu_fan_mean', {'label':'LWU', 'ylabel':'Voltage (mV)'}, 'LW FANS', augment=augment) * \
        asfsplot('ir20_lwd_fan_mean', {'label':'LWD'}, 'LW FANS', augment=augment)
    
    p_rad_heat = \
        asfsplot('sr30_swu_heatA_mean', {'label':'SWU', 'ylabel': 'Heater (mA)'}, 'RAD HEATERS', augment=augment) * \
        asfsplot('sr30_swd_heatA_mean', {'label':'SWD'}, 'RAD HEATERS', augment=augment)
    
    p_sr50 = asfsplot('sr50_dist_mean', {'ylabel': 'Height (?)'}, 'SR50 SNOW HEIGHT', augment=augment)

    p_wind = \
        asfsplot('wspd_u_mean', {'label':'u', 'ylabel':'speed (m/s)'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_v_mean', {'label':'v'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_w_mean', {'label':'w'}, 'SONIC ANEMOMETER', augment=augment) * \
        asfsplot('wspd_vec_mean', {'label':'total'}, 'SONIC ANEMOMETER', augment=augment)
    
    p_wind_dir = asfsplot('wdir_vec_mean', {'ylabel':'wind direction (###deg from REF###)'}, 'WIND DIRECTION', augment=augment)

    p_vaisala_T = asfsplot('vaisala_T_mean', {'ylabel': 'Temperature (C)'}, 'VAISALA TEMPERATURE', augment=augment)
    p_vaisala_P = asfsplot('vaisala_P_mean', {'ylabel': 'Pressure (?)'}, 'VAISALA PRESSURE', augment=augment)
    p_vaisala_RH = asfsplot('vaisala_RH_mean', {'ylabel': 'Relative humidity (%)'}, 'VAISALA RH', augment=augment)
    
    asfs_tab = Tab.Tab(
        'ASFS',
        [p_rad, p_fp, p_sr50, p_wind, p_wind_dir, p_vaisala_T, p_vaisala_P, p_vaisala_RH, p_fantach, p_lw_fans, p_rad_heat],
        dld=None,
        required_DL=['asfs'],
        longname='Atmospheric Surface Flux Station',
        augment_dims=augment
    )
    return asfs_tab


if __name__ == '__main__':
    from panel import serve
    tab = get_asfs_tab()
    tab.dld = {'asfs':DL_asfs_slow()}
    serve(tab, port=5006, websocket_origin='*', show=True)