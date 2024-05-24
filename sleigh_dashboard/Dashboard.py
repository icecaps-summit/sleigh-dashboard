'''
Author: Andrew Martin
Creation Date: 15/4/24

Script for the Dashboard class, which will ultimately be called in dashboard.py as a
panel-viewable object.

'''

import panel as pn

from panel import HSpacer, Spacer

from .DataLoader import DataLoader
from .TabView import TabView

class Dashboard:
    '''
    Dashboard is a class the provides all the functionality of the panel dashboard
    for use in dashboard.py. This involves:
    
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
        self.gdtp         = pn.widgets.DatetimeRangePicker(**dtp_args,
                                                           align='center',
                                                           styles={"margin-left": "-5px",})

        self.compare      = pn.widgets.Switch(name='Compare', value=False,
                                              align='center', styles={"margin-left": "-10px",})

        self.dld          = dict_DL
        self.tabview_func = tabview_func
        self.tabview      = tabview_func(self.dld, False)

        self.tabview.bind_gdtp(self.gdtp)

        hh = 100
        self.__header_height__=hh

        # these are served as part of the blog... kinda sketchy but I like it
        self.logo = "https://icecapsmelt.org/" + \
            "_image?href=%2F%40fs%2Fapp%2Fsrc%2Fassets%2Fimages%2Fgreenland_small.png"
        self.banner = "https://icecapsmelt.org/" + \
            "_image?href=%2F%40fs%2Fapp%2Fsrc%2Fassets%2Fimages%2Fmsf_pano_small.jpg"

        home_button = pn.widgets.Button(
            name="Home", button_type="primary",
            width=100, margin=5, align="center"
        ) 

        home_click= """
                    window.open("https://icecapsmelt.org", "_self")
                    """
        home_button.js_on_click(code=home_click)

        instruments_button = pn.widgets.Button(
            name="Instruments", button_type="primary",
            width=130, margin=5, align="center"
        ) 
        instruments_click = """
                            window.open("https://icecapsmelt.org/data/instrument", "_self")
                            """
        instruments_button.js_on_click(code=instruments_click)

        science_button = pn.widgets.Button(
            name="Science", button_type="primary",
            width=100, margin=5, align="center"
        ) 
        science_click = """
                        window.open("https://icecapsmelt.org/data/science", "_self")
                        """
        science_button.js_on_click(code=science_click)


        button_row = pn.Row(home_button, instruments_button, science_button,
                            styles={"margin-top": "-10px",})
        button_col = pn.Column(
            '## ICECAPS-MELT Data  Dashboard',
            button_row,
            sizing_mode = 'stretch_both',
            styles={"margin-top": "3px",
                    },
        )

        logo_png = pn.pane.PNG(self.logo, height=hh-20, width=hh-20,
                               margin=10, sizing_mode="fixed", align="start")

        banner_str = f'url("{self.banner}"),' + \
            'linear-gradient(0deg,#c5d8f8 20%, #d7e7ff 40%, #d7e7ff)'

        self.header = pn.Row(
            logo_png,
            button_col,
            HSpacer(),
            margin=0,
            height=hh,
            sizing_mode="stretch_width",
            styles={"background-image": banner_str,
                    "background-position": "right",
                    "background-size": f"contain",
                    "background-repeat": "no-repeat",
                    },
        )


        select_labels  = pn.Row('### Time range', pn.HSpacer(),'###  Compare', width=400,
                                styles={"margin": '0px', 'margin-bottom': '-15px'})
        select_objects = pn.Row(self.gdtp, pn.HSpacer(), self.compare, width=390)
        select_column  = pn.Column(select_labels, select_objects)


        self.top_row = pn.Row(
            pn.HSpacer(),
            select_column, 
            pn.HSpacer(max_width=50),
            sizing_mode='stretch_width',
            align='center',
            height=90,
            styles={"margin-bottom": '-40px'},
        )

    def __panel__(self):
        '''
        Function that retruns the panel-viewable implementation of the
        dashboard. This consists of a left spacer, and a column containing the top row,
        and relevant TabView objects beneath it.

        '''

        left_spacer = pn.Spacer(width=40)

        def main_content(compare):
            tabs_in_row = [left_spacer,self.tabview]
            if compare: #TODO: this often shits the bed, needs rigorous testing
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
            self.header, 
            self.top_row,
            pn.bind(main_content, self.compare),
            sizing_mode = 'stretch_both'
        )

