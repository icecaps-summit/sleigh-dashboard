'''Author: Andrew Martin
Creation Date: 15/4/24

Script for the DataLoader class, which will contain the logic to load data and serve data within given datetime ranges.
'''

import datetime as dt
import xarray as xr
import os

class DataLoader:
    '''DataLoader is a class that loads .nc files from a specific directory with a given filename format. The class can be provided with a datetime range, from which the data is loaded (rather than lodading all available files).
    
    ATTRIBUTES:
        name: str
        dir: str
        fname_fmt: str
        sortby_dim: str
        loaded_files: list[str]
        data: xr.Dataset

    METHODS:
        __call__
        update_data
        _get_files_in_dtr
    '''

    def __init__(self,
        name: str,
        dir: str,
        fname_fmt: str,
        init_dtr: tuple[dt.datetime, dt.datetime] | None = None,
        sortby_dim: str = 'time',
        concat_dim: str | None = None,
        file_preproc: callable = (lambda x: x)
    ):
        '''Initilisation function. Requires a dataloader name, directory and filename format.
        
        INPUTS:
            name: str
                name for the dataloader

            dir: str
                string describing the path to the directory containing the data to be loaded

            fname_fmt: str
                filename format for the data to be loaded. Requires datetime accessors at the  -day resolution.

            init_dtr: tuple[dt.datetime, dt.datetime] | None
                Either, a sorted tuple of datetime objects describing a left-inclusive datetime range, or None. If None, no data will be loaded on initialisation.

            sortby_dim: str
                string describing the dimesnion along which the dataset should be sorted when new data is loaded.

            concat_dim: str | None
                string describing the dimension along which multiple datsets should be concatenated. If None, this will be the same as sortby_dim

            file_preproc: callable[xr.Dataset] -> xr.Dataset
                Function that accepts an xarray dataset, returns an xarray dataset, ad is applied to each file before they are combined along combine_dim. The default is to apply no preprocessing.
        '''
        self.name = name
        self.dir = dir
        self.fname_fmt = fname_fmt
        self.data = None
        self.loaded_files = []
        self.sortby_dim = sortby_dim

        if concat_dim is None:
            concat_dim = sortby_dim
        self.concat_dim = concat_dim    
        
        self.file_preproc = file_preproc

        if init_dtr is not None:
            self.update_data(init_dtr)

    def __call__(self, 
        dtr: tuple[dt.datetime, dt.datetime],
        augment=False
    ) -> xr.Dataset:
        '''When called, the DataLoader updates its data based on the given datetime range and returns the appropriately sliced data.
        
        dtr: tuple[dt.datetime, dt.datetime]
            tuple containing the start and end datetime objects of the range of data to be served.

        augment: bool
            If true, change all of the dimension, coordinate and variables names to contain a trailing underscore, so that shared_axes is broken between augmented and non-augmented plots on the Dashboard.
        '''
        self.update_data(dtr)
        if self.data is not None:
            tslice = slice(*dtr, None)
            selarg = {self.sortby_dim: tslice}
            ds = self.data.sel(**selarg)

            if augment: 
                ds = ds.rename_dims({k:k+'_' for k in ds.dims})
                ds = ds.rename_vars({k:k+'_' for k in ds.coords})
            return ds
        return None

    def update_data(self,
        dtr: tuple[dt.datetime, dt.datetime]
    ) -> None:
        '''Function that takes a datetime range, and updates the DataLoaders stored data attribute if the requested data isn't already loaded.'''
        print(f'DataLoader {self.name}.update_data: called')
        # get all the required files for loading the datetime range
        flist_dtr = self._get_files_from_dtr(dtr)
        flist_to_load = [f for f in flist_dtr if f not in self.loaded_files]
        # exit if there are no files to load
        if not flist_to_load: return

        flist_in_dir = os.listdir(self.dir)
        flist_to_load = [f for f in flist_to_load if f in flist_in_dir]
        if not flist_to_load: return

        ds_to_merge = []
        if self.data is not None: ds_to_merge = [self.data]

        for f in sorted(flist_to_load):
            try:
                ds_to_merge.append( 
                    self.file_preproc(
                        xr.load_dataset(os.path.join( self.dir, f ))
                    ) 
                )
                self.loaded_files.append(f)
            except Exception as e:
                print('!!! ' + '='*44 + ' !!!')
                print(f'DATALOADER ERROR: failed to load {f}')
                print(e)
                print('!!! ' + '-'*44 + ' !!!')

        # TODO: assess if coords='minimal' causes issues
        self.data = xr.concat(ds_to_merge, dim=self.concat_dim, coords='minimal').sortby(self.sortby_dim)
        return

    def _get_files_from_dtr(self,
        dtr: tuple[dt.datetime, dt.datetime]
    ) -> list[str]:
        '''Returns a list of filenames using the fname_fmt that are utilised within dtr.'''
        # TODO: implement hourly loading? for gfs... 
        start = dtr[0]
        end = dt.datetime.combine(dtr[1], dt.datetime.min.time())
        dt0 = dt.datetime(year=start.year, month=start.month, day=start.day)
        one_day = dt.timedelta(days=1)

        flist = []
        while dt0 < end:
            flist.append( dt0.strftime(self.fname_fmt) )
            dt0 += one_day
        return flist
