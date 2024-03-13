import numpy as np
import xarray as xr
import hvplot.xarray # noqa
import hvplot
import holoviews as hv
import panel as pn

import datetime as dt
import os

def load_asfs():
    dir_asfs = '/data/asfs/'
    files_asfs = [os.path.join( dir_asfs,f ) for f in os.listdir(dir_asfs) if 'summary_asfs_sci' in f]

    # Does a preprocess function need including?
    # Do we need to specify the dimension along which to concatenate (hopefully not)
    ds = xr.open_mfdataset(files_asfs)
    return ds

def tab_asfs():
    ds = load_asfs()

    # title to the tab
    p0 = pn.pane.Markdown('# Automated Surface Flux Station')
    title = pn.Row(p0)

    ######################## DATETIME RANGE SELECTION ###########################
    #############################################################################

    '''
    # the following dtrange goes from the start of yesterday to the end of yesterday. This should be the latest day of available data...
    dtrange = ( dt.datetime.today().date() - dt.timedelta(days=2), dt.datetime.today().date() )
    dt_range_picker = pn.widgets.DatetimeRangePicker(name='Datetime range:', value=dtrange, enable_seconds=False)
    '''
    dttd = dt.datetime.today()
    start_of_today = dt.datetime(dttd.year, dttd.month, dttd.day)
    dtrange = ( start_of_today - dt.timedelta(days=2), start_of_today )
    ######################## ALL VARIABLES PLOT #################################
    #############################################################################
    OPTS_SCATTER = {'x':'time', 's':2, 'height':250, 'responsive':True, 'grid':True, 'padding':0.1}
    
    OPTS_TALLER = {k:v for k,v in OPTS_SCATTER.items()}
    OPTS_TALLER['height'] = 400

    def set_border_fill_color(plot, elememt):
        b = plot.state
        b.border_fill_color = 'whitesmoke'

    ### scantime
    p_scantime = ds['scantime'].hvplot.scatter(
        title='scantime', label='mean', **OPTS_SCATTER, color='green', ylim=(0,None)
    ) * ds['scantime_min'].hvplot.scatter(
        label='min', **OPTS_SCATTER, color='blue'
    ) * ds['scantime_max'].hvplot.scatter(
        label='max', **OPTS_SCATTER, color='red'
    ).opts(hooks=[set_border_fill_color])

    p_boxtemp = ds['PTemp_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='Logger Electronics Panel T [degC]'
    ).opts(hooks=[set_border_fill_color])

    p_sw_cal = ds['sr30_swu_IrrC_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='SW T-corrected Irradiance [W/m2]', label='SWU', color='blue'
    ) * ds['sr30_swd_IrrC_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='SWD', color='red'
    ).opts(hooks=[set_border_fill_color])

    p_lw_cal = ds['ir20_lwu_Wm2_Avg'].hvplot.scatter(
        title='LW Calibrated Flux [W/m2]', label='LWU', **OPTS_SCATTER, color='blue'
    ) * ds['ir20_lwd_Wm2_Avg'].hvplot.scatter(
        label='LWD', **OPTS_SCATTER, color='red'
    ).opts(hooks=[set_border_fill_color])


    ds['lw_net'] = ds['ir20_lwd_Wm2_Avg'] - ds['ir20_lwu_Wm2_Avg']
    ds['sw_net'] = ds['sr30_swd_IrrC_Avg'] - ds['sr30_swu_IrrC_Avg']
    ds['rad_net'] = ds['lw_net'] + ds['sw_net']
    p_rad = ds['rad_net'].hvplot.scatter(
        **OPTS_TALLER, title='RADIATION [W/m2]', label='NET', color='olivedrab'
    ) * ds['sw_net'].hvplot.scatter(
        **OPTS_TALLER, label='SW NET', color='darkcyan'
    ) * ds['sr30_swu_IrrC_Avg'].hvplot.scatter(
        **OPTS_TALLER, label='SWU', color='darkblue'
    ) * ds['sr30_swd_IrrC_Avg'].hvplot.scatter(
        **OPTS_TALLER, label='SWD', color='aqua'
    ) * ds['lw_net'].hvplot.scatter(
        **OPTS_TALLER, label='LW NET', color='goldenrod'
    ) * ds['ir20_lwu_Wm2_Avg'].hvplot.scatter(
        **OPTS_TALLER, label='LWU', color='firebrick'
    ) * ds['ir20_lwd_Wm2_Avg'].hvplot.scatter(
        **OPTS_TALLER, label='LWD', color='lightcoral'
    ).opts(hooks=[set_border_fill_color])

    p_plate_flux = ds['fp_A_Wm2_Avg'].hvplot.scatter(
        title='Flux plate calibrated flux [W/m2]', label='A', **OPTS_SCATTER, color='orange'
    ) * ds['fp_B_Wm2_Avg'].hvplot.scatter(
        label='B', **OPTS_SCATTER, color='purple'
    ).opts(hooks=[set_border_fill_color])

    p_gas_density = ds['licor_co2_out_Avg'].hvplot.scatter(
        title='Gas densities', label='co2 [mg/m3]', **OPTS_SCATTER, color='blue'
    ) * ds['licor_h2o_out_Avg'].hvplot.scatter(
        label='h2o [g/m3]', **OPTS_SCATTER, color='red'
    ).opts(multi_y=True).opts(hooks=[set_border_fill_color])

    p_licor_sig = ds['licor_co2_str_out_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='Licor signal strength [%]', color='red'
    ).opts(hooks=[set_border_fill_color])

    p_snow_acoustic = ds['sr50_dist_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='Snow acoustic sensor', label='(uncorrected) distance', color='red'
    ) * ds['sr50_qc_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='signal quality value', color='green'
    ).opts(multi_y=True).opts(hooks=[set_border_fill_color])

   
    p_metek_wind = ds['metek_x_Avg(1)'].hvplot.scatter(
        **OPTS_SCATTER, title='Metek winds [m/s]', label='x', color='red'
    ) * ds['metek_y_Avg(1)'].hvplot.scatter(
        **OPTS_SCATTER, label='y', color='green'
    ) * ds['metek_z_Avg(1)'].hvplot.scatter(
        **OPTS_SCATTER, label='z', color='blue'
    ).opts(hooks=[set_border_fill_color])


    # metek Incl[X,Y] and sr30_swd_tilt
    p_metek_incl = ds['metek_InclX_Avg(1)'].hvplot.scatter(
        **OPTS_SCATTER, title='Inclinations [deg]', label='metek X', color='blue'
    ) * ds['metek_InclY_Avg(1)'].hvplot.scatter(
        **OPTS_SCATTER, label='metek Y', color='red'
    ) * ds['sr30_swd_tilt_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='SWD', color='green'
    ).opts(hooks=[set_border_fill_color])

    p_sw_tach = ds['sr30_swu_fantach_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='SW Fan Tachometers [Hz]', label='SWU', color='blue'
    ) * ds['sr30_swd_fantach_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='SWD', color='red'
    ).opts(hooks=[set_border_fill_color])

    p_sw_heatcurr = ds['sr30_swu_heatA_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='SW Heater Current [mA]', label='SWU', color='blue'
    ) * ds['sr30_swd_heatA_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='SWD', color='red'
    ).opts(hooks=[set_border_fill_color])

    p_lw_heatv = ds['ir20_lwu_fan_Avg'].hvplot.scatter(
        **OPTS_SCATTER, title='LW Fan Voltage [mV]', label='LWU', color='blue'
    ) * ds['ir20_lwd_fan_Avg'].hvplot.scatter(
        **OPTS_SCATTER, label='LWD', color='red'
    ).opts(hooks=[set_border_fill_color])



    #print([v for v in ds.variables])
    #print(ds)
    #var_plots = []
    #for v in [a for a in ds.variables if a!='time']:
    #    var_plots.append( 
    #        ds[v].hvplot.scatter(
    #            title=v, **OPTS_SCATTER
    #        ) 
    #    )

    # include all elements to be displayed in the returned pn.Column object
    display = pn.Column(title,pn.Column(p_scantime, p_boxtemp, p_sw_cal, p_lw_cal, p_rad, p_plate_flux, p_gas_density, p_licor_sig, p_snow_acoustic, p_metek_wind, p_metek_incl, p_sw_tach, p_sw_heatcurr, p_lw_heatv))#, *var_plots)
    return display 