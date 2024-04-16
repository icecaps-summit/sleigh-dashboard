'''Author: Andrew Martin
Creation Date: 15/4/24

Script for the Dashboard class, which will ultimately be called in dashboard.py as a panel-viewable object.
'''

import panel as pn
from .DataLoader import DataLoader
from .TabView import TabView

class Dashboard:
    '''Dashboard is a class the provides all the functionality of the panel dashboard for use in dashboard.py. This involves:
    
    + handling data for the Dashboard instance via DataLoader object
    + Allowing viewing selection for all instruments via the global datetime picker
    + Displaying the initial TabsView object
    + Allowing for the creation of a second TabsView object for data comparisson if requested.

    ATTRIBUTES:


    METHODS:
    '''

    def __init__(self, 
        dtp_args: dict,
        dict_DL: dict[str: DataLoader],
        tabview_func: callable
    ):
        '''Initialisation function
        
        INPUTS:
            dtp_args: dict
                dictionary of all arguments provided to create the datetime range picker. These are the start, end, value and name parameters

            tabview_func : callable -> TabView
                a callable function that takes the input of a (dld = dict[str: DataLoader], augment:bool) and returns a TabView object, a collection of pre-determined tabs
        '''
        dtp_args['enable_seconds'] = False
        self.gdtp = pn.widgets.DatetimeRangePicker(**dtp_args)
        self.compare = pn.widgets.Switch(name='Compare', value=False)

        self.dld = dict_DL
        self.tabview_func = tabview_func
        self.tabview = tabview_func(self.dld, False)

        self.tabview.bind_gdtp(self.gdtp)

        self.top_row = pn.Row(
            pn.HSpacer(),
            '## global datetime picker:', self.gdtp,
            pn.HSpacer(), 
            '## Compare:',self.compare,
            pn.HSpacer(),
            sizing_mode='stretch_width', height=60
        )

    def __panel__(self):
        '''Function that retruns the panel-viewable implementation of the dashboard. This consists of a left spacer, and a column containing the top row, and relevant TabView objects beneath it.'''

        left_spacer = pn.Spacer(width=40)

        def main_content(compare):
            tabs_in_row = [left_spacer,self.tabview]
            if compare:
                new_tabview = self.tabview_func(self.dld, True)
                new_tabview.bind_gdtp(self.gdtp)
                tabs_in_row = [*tabs_in_row, 
                               pn.Spacer(width=40, styles={'background':'snow'}), 
                               new_tabview]
            tabs_in_row.append(pn.Spacer(width=20))
            return pn.Row(
                *tabs_in_row,
                sizing_mode='stretch_height'
            )


        return pn.Column(
            self.top_row,
            pn.bind(main_content, self.compare),
            sizing_mode = 'stretch_both'
        )

