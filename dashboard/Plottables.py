'''Author: Andrew Martin
Creation Date: 15/4/24

Script containing the class for the BasePlottable, and the inheriting Plottable objects that describe scatter, line, 2D plots, etc.
'''
import xarray as xr
import holoviews as hv
import hvplot.xarray
import panel as pn


class BasePlottable:
    '''Base plottable class'''

    def __init__(self, datasource, variable, plotargs):
        self.datasource = datasource
        self.variable = variable
        self.plotargs = plotargs
        self.plotargs['responsive'] = True
        self.dd = None
        self.plotfuncs = [self.plot]


    def __panel__(self):
        panelob = pn.bind(self._plot, self.dd)
        #panelob = pn.bind(self.plot, self.dd)
        if type(panelob) is AttributeError:
            panelob = pn.pane.Markdown(f'## Attribute error, {panelob}')
        elif type(panelob) is TypeError:
            panelob = pn.pane.Markdown(f'## Type Error: {panelob}')
        elif type(panelob) is Exception:
            panelob = pn.pane.Markdown(f'## general exception, {panelob}')
        return panelob
    

    def __call__(self, dd: dict[str: xr.Dataset]):
        '''NOTE: dd should be a dict containing panel-bound xarray Datasets, to ensure automatic updating.'''
        self.dd = dd


    def __mul__(self, other_plottable):
        new_plottable = BasePlottable(None, None, {})
        new_plottable.plotfuncs = [*self.plotfuncs, *other_plottable.plotfuncs]
        return new_plottable
        

    def _plot(self,dd):
        '''This is the wrapper function for calling plotting functions that return holoviews objects. This will handle type exceptions'''
        plot_outputs = [f(dd) for f in self.plotfuncs]
        hv_outputs = []
        erroneous_outputs = []
        
        for po in plot_outputs:
            if isinstance(po, Exception):
                erroneous_outputs.append(
                    pn.pane.Markdown(f'## Exception: {po}')
                )
            else:
                hv_outputs.append(po)

        if hv_outputs:
            return pn.Column(
                hv.Overlay(hv_outputs),
                *erroneous_outputs
            )
        else:
            return pn.Column(*erroneous_outputs)

    def plot(self,dd):
        '''Function that needs to be called to return the panel object, is bound in __panel__'''
        raise NotImplementedError('Please use a class ingeriting from BasePlottable for rendering in panel')


class Plot_2D(BasePlottable):
    '''Plottable class for the 2D plots.'''
    def __init__(self, datasource, variable, plotargs, height=400, cmap='viridis', cnorm='linear', clim=(None, None)):
        
        super().__init__(datasource, variable, plotargs)
        self.plotargs['height'] = height

        self.plotargs['cmap']=cmap
        self.plotargs['cnorm']=cnorm
        self.plotargs['clim']=clim
        
    def plot(self, dd):
        try:
            return dd[self.datasource][self.variable].hvplot(
                **self.plotargs
            )
        except Exception as e:
            return e
    

class Plot_scatter(BasePlottable):
    '''Plottable class for the scatter plots.'''
    def __init__(self, datasource, variable, plotargs, height=300, s=5):
        
        super().__init__(datasource, variable, plotargs)
        
        self.plotargs['height'] = height
        self.plotargs['s'] = 5
        self.plotargs['label'] = f'{self.datasource}.{self.variable}'

    def plot(self, dd):
        try:
            return dd[self.datasource][self.variable].hvplot.scatter(
                **self.plotargs
            )
        except Exception as e:
            return e
    