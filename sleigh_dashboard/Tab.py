'''
Author: Andrew Martin
Creation Date: 15/4/24

Script containing the Tab class, which will display the individual plots required for
each individual class.  The class will also hold references to the relevant DataLoader
objects required to display the data.  Each tab also has its own instrument-specific
datetime range picker that can be linked to a global datetime picker if desired.

'''

import panel as pn
from .DataLoader import DataLoader
from .Plottables import BasePlottable
import xarray as xr

import datetime as dt

_dt_now = dt.datetime.now()
_today = dt.date(year=_dt_now.year, month=_dt_now.month, day=_dt_now.day)
_default_dtr = (_today-dt.timedelta(days=1), _today)

class Tab:
    '''
    The Tab class provides all of the functionality of an individual viewable tab in
    the Dashboard.  Each tab will have references only to the DataLoader objects it
    requires access to in order to plot the required data. It will also contain an
    instrument-specific datetime picker that can be linked to a global datetime picker
    for the Dashboard.  The DataLoader objects will be bound to the specific datetime
    picker, so changes to the selected range will attempt to load new data.
    '''

    def __init__(self,
        name: str,
        plottables: list[BasePlottable],
        dld: dict[str: DataLoader] | None,
        required_DL: list[str],
        longname: str | None = None,
        augment_dims: bool = False # used to rename data dims in event that Tab is a comparison tab...
    ):
        self.name = name
        
        # upon initialisation, the DateRangePicker assumes default values (allows
        # standalone use). When used within a Dashboard, self.bind_gdtp can be used to
        # bind a global datetime range picker.

        #self.dtp = pn.widgets.DatetimeRangePicker(name=f'{name} datetime picker', value=_default_dtr)
        self.dtp = pn.widgets.DateRangePicker(name=f'', value=_default_dtr, width=175, align="center")
        self.dld = dld
        self.required_DL = required_DL
        self.plottables = plottables
        self.augment_dims = augment_dims

        self.data = pn.bind(self._bind_data, self.dtp)

        if longname is None: longname = name
        self.top_row = pn.Row(
            pn.pane.Markdown(f'# {longname}'),
            pn.HSpacer(),
            f'{name} time range', self.dtp,
            pn.HSpacer(),
            align="center",
            sizing_mode='stretch_width', 
        )

        self.scroll_bkg = 'snow'

        # calling the plottable objects ensures that the tab-bound data is now also bound to the plottable object
        [pn.bind(p,self.data) for p in self.plottables]
        print(f'Tab {self.name}.__init__(): {self.plottables=}')

    
    def _data_column(self, dtr):
        print(f'Tab {self.name}._data_column running')
        data_column_objs = []
        for p in self.plottables:
            p(self.data)
            data_column_objs.append(p)
            data_column_objs.append(pn.VSpacer(height=20, styles={'background':self.scroll_bkg}))
        data_column = pn.Row(
            pn.Spacer(width=40, styles={'background':self.scroll_bkg}),
            pn.Column(*data_column_objs, sizing_mode='stretch_width'),
            pn.Spacer(width=40, styles={'background':self.scroll_bkg}),
            #scroll=True
        )
        return data_column


    def __panel__(self):
        '''Function that returns the panel-viewable object that is the tab content. This will be the top row containing the tab title, the datetime picker for the tab; and the scrollable column containing the actual plots. This will have a spacer on the left and right to allow for scrolling of the plots easily.'''
        dc = pn.bind(self._data_column, self.dtp)
        return pn.Column(self.top_row, dc)
    
    def _bind_gdtp_val(self, gdtr):
        print(f'#### Tab {self.name}._bind_gdtp_val: {gdtr=}')
        self.dtp.value = gdtr

    def bind_gdtp(self, gdtp: pn.widgets.DateRangePicker):
        self.gdtp = gdtp
        self.dtp.value = self.gdtp
        self.dtp.start = self.gdtp.start
        self.dtp.end = self.gdtp.end
        #pn.bind(self._bind_gdtp_val, self.gdtp)
        print(f'#### Tab {self.name}.bind_gdtp complete')
        '''
        self.dtp = pn.widgets.DateRangePicker(
            name=f'{self.name} time range', value=gdtp.value,
            start=gdtp.start, end=gdtp.end, 
        )
        '''
        # binds the Tab objects datetime picker to the global one. Changes in the global dtp reflect in the local one.
        #self.dtp.value = self.gdtp.value
        return
    

    def _bind_data(self, dtr) -> dict[str:xr.Dataset]:
        print(f'Tab. {self.name}_bind_data({self.augment_dims=})')
        # data needs rebinding each time that the dtp is updated
        if self.dld is not None:
            data = {
                inst: self.dld[inst](dtr, self.augment_dims)
                for inst in self.required_DL
            }
            return data
        else: return None



