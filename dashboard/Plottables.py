'''Author: Andrew Martin
Creation Date: 15/4/24

Script containing the class for the BasePlottable, and the inheriting Plottable objects that describe scatter, line, 2D plots, etc.
'''
import xarray as xr
import holoviews as hv
import hvplot.xarray


class BasePlottable:
    '''Base pllottable class'''

    def __init__(self, datasource, variable, plotargs):
        self.datasource = datasource
        self.variable = variable
        self.plotargs = plotargs
        self.plotargs['responsive'] = True

    def __panel__(self):
        raise NotImplemented('Please use a class inheriting from BasePlottable for rendering in panel')
    
    def __call__(self, dd: dict[str: xr.Dataset]):
        '''NOTE: dd should be a dict containing panel-bound xarray Datasets, to ensure automatic updating.'''
        self.dd = dd



class Plot_2D(BasePlottable):
    '''Plottable class for the 2D plots.'''
    def __init__(self, datasource, variable, plotargs, height=400, cmap='viridis', cnorm='linear', clim=(None, None)):
        
        super().__init__(datasource, variable, plotargs)
        self.plotargs['height'] = height

        self.plotargs['cmap']=cmap
        self.plotargs['cnorm']=cnorm
        self.plotargs['clim']=clim

    def __panel__(self):
        return self.dd[self.datasource]()[self.variable].hvplot(
            **self.plotargs
        )
    

class Plot_scatter(BasePlottable):
    '''Plottable class for the scatter plots.'''
    def __init__(self, datasource, variable, plotargs, height=300, s=5):
        
        super().__init__(datasource, variable, plotargs)
        
        self.plotargs['height'] = height
        self.plotargs['s'] = 5

    def __panel__(self):
        return self.dd[self.datasource].hvplot.scatter(
            **self.plotargs
        )
    