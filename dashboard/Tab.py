'''Author: Andrew Martin
Creation Date: 15/4/24

Script containing the Tab class, which will display the individual plots required for each individual class.
The class will also hold references to the relevant DataLoader objects required to display the data.
Each tab also has its own instrument-specific datetime range picker that can be linked to a global datetime picker if desired. 
'''

import panel as pn
from .DataLoader import DataLoader
from .Plottables import BasePlottable

class Tab:
    '''The Tab class provides all of the functionality of an individual viewable tab in the Dashboard.
    Each tab will have references only to the DataLoader objects it requires access to in order to plot the required data. It will also contain an instrument-specific datetime picker that can be linked to a global datetime picker for the Dashboard.
    The DataLoader objects will be bound to the specific datetime picker, so changes to the selected range will attempt to load new data. 
    '''

    def __init__(self,
        name: str,
        plottables: list[BasePlottable],
        dld: dict[str: DataLoader],
        required_DL: list[str],
        longname: str | None = None,
    ):
        self.name = name
        
        # upon initialisation, the DatetimeRangePicker assumes default values (allows standalone use). When used within a Dashboard, self.bind_gdtp can be used to bind a global datetime range picker.
        self.dtp = pn.widgets.DatetimeRangePicker(name=f'{name} datetime picker')
        self.dld = dld
        self.required_DL = required_DL
        self._bind_data()

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
        self.plottables = plottables
        [p(self.data) for p in self.plottables]

        pn.bind(self.print_boo, self.dtp)


    def __panel__(self):
        '''Function that returns the panel-viewable object that is the tab content. This will be the top row containing the tab title, the datetime picker for the tab; and the scrollable column containing the actual plots. This will have a spacer on the left and right to allow for scrolling of the plots easily.'''
        print(f'Tab {self.name}.__panel__(): {self.plottables=}')
        data_column_objs = [obj for tup in [(p ,pn.VSpacer(height=20, styles={'background':self.scroll_bkg})) for p in self.plottables]
                            for obj in tup]
        plot_row = pn.Row(
            pn.Spacer(width=40, styles={'background':self.scroll_bkg}),
            pn.Column(*data_column_objs, sizing_mode='stretch_width'),
            pn.Spacer(width=40, styles={'background':self.scroll_bkg}),
            scroll=True
        )

        return pn.Column(self.top_row, plot_row)
    

    def bind_gdtp(self, gdtp: pn.widgets.DatetimeRangePicker):
        self.gdtp = gdtp
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
        self._bind_data()
        return
    

    def _bind_data(self):
        print(f'Tab. {self.name}_bind_data()')
        # data needs rebinding each time that the dtp is updated
        self.data = {
            inst: pn.bind(self.dld[inst], self.dtp)
            for inst in self.required_DL
        }

    def print_boo(self, dtr):
        print(dtr)



