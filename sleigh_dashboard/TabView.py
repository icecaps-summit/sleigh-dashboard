'''Author: Andrew Martin
Creation Date: 15/4/24

Script containing the TabView class, that will define the object conatining the individual tabs to be viewed in the Dashboard. This acts primarily as a holder of the Tab class, and passes DataLoader objects from the Dashboard to the indiividual tabs.
'''

from .Tab import Tab
from .DataLoader import DataLoader
import panel as pn

class TabView:
    '''TabView is the class containing the individual tabs to be displayed, and acts as an interface between the global DataLoader classes of the Dashboard and the individual data requirements of the instrument-specific Tab objects.
    
    ATTRIBUTES:
    
    
    METHODS:
    
    '''

    def __init__(self, 
        tablist: list[Tab],
        dld: dict[str: DataLoader],
        augment_dims = False
    ):
        self.tablist = tablist
        self.dld = dld
        self.augment_dims = augment_dims
        for tab in tablist:
            tab.dld = self.dld
            tab.augment_dims = augment_dims
            

    def __call__(self) -> pn.Tabs:
        return pn.Tabs(
            *[(t.name, t) for t in self.tablist],
            sizing_mode='stretch_both', dynamic=True
        )

    def __panel__(self):
        return self.__call__()
    

    def bind_gdtp(self, gdtp):
        '''Function that binds a global DateRangePicker object to the individual Tab objects in the TabView.'''
        self.gdtp = gdtp
        for t in self.tablist:
            t.bind_gdtp(gdtp)
