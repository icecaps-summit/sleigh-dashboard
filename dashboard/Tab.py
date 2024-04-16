'''Author: Andrew Martin
Creation Date: 15/4/24

Script containing the Tab class, which will display the individual plots required for each individual class.
The class will also hold references to the relevant DataLoader objects required to display the data.
Each tab also has its own instrument-specific datetime range picker that can be linked to a global datetime picker if desired. 
'''

import panel as pn
from .DataLoader import DataLoader
from .Plottables import BasePlottable
import xarray as xr

import datetime as dt

_default_dtr = (dt.datetime.now()-dt.timedelta(days=1), dt.datetime.now())

class Tab:
    '''The Tab class provides all of the functionality of an individual viewable tab in the Dashboard.
    Each tab will have references only to the DataLoader objects it requires access to in order to plot the required data. It will also contain an instrument-specific datetime picker that can be linked to a global datetime picker for the Dashboard.
    The DataLoader objects will be bound to the specific datetime picker, so changes to the selected range will attempt to load new data. 
    '''

    def __init__(self,
        name: str,
        plottables: list[BasePlottable],
        dld: dict[str: DataLoader] | None,
        required_DL: list[str],
        longname: str | None = None,
    ):
        self.name = name
        
        # upon initialisation, the DatetimeRangePicker assumes default values (allows standalone use). When used within a Dashboard, self.bind_gdtp can be used to bind a global datetime range picker.
        self.dtp = pn.widgets.DatetimeRangePicker(name=f'{name} datetime picker', value=_default_dtr)
        self.dld = dld
        self.required_DL = required_DL
        self.plottables = plottables

        self.data = pn.bind(self._bind_data, self.dtp)

        if longname is None: longname = name
        self.top_row = pn.Row(
            pn.pane.Markdown(f'# {longname}'),
            pn.HSpacer(),
            f'{name} datetime picker', self.dtp,
            pn.HSpacer(),
            sizing_mode='stretch_width', height=60
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
    

    def bind_gdtp(self, gdtp: pn.widgets.DatetimeRangePicker):
        self.dtp.start = gdtp.start
        self.dtp.end = gdtp.end
        self.dtp.value = gdtp.value
        '''
        self.dtp = pn.widgets.DatetimeRangePicker(
            name=f'{self.name} datetime picker', value=gdtp.value,
            start=gdtp.start, end=gdtp.end, 
            enable_seconds=False
        )
        '''
        # binds the Tab objects datetime picker to the global one. Changes in the global dtp reflect in the local one.
        #self.dtp.value = self.gdtp.value
        return
    

    def _bind_data(self, dtr) -> dict[str:xr.Dataset]:
        print(f'Tab. {self.name}_bind_data()')
        # data needs rebinding each time that the dtp is updated
        if self.dld is not None:
            data = {
                inst: self.dld[inst](dtr)
                for inst in self.required_DL
            }
            return data
        else: return None



