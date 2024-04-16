# dashboard module

The idea behind the dashboard module is to have an object-oriented implementation of the data dashboard that is scalable, easy to adapt and portable. It will consist of several core classes and data structures that must be adhered to in order for the code to work properly.

## Dependancies

The rendering for the dashboard runs off of the `panel` package, and utilizes `holoviews` (and by extension, `bokeh`) for plotting. Data handling is performed via `xarray`.

## Classes

### `DataLoader`

### `Tab`

Tab supplied with 

+ `dld: dict[str, DataLoader]`
+ `data: pn.bind( f -> xr.Dataset )`

### `Plottables`

### `TabView`

### `Dashboard`



## Example workflows

### Standalone `Tab`

A `Tab` object should be able to be displayed as a standalone panel object. 

### Singular `TabView`

### `Dashboard` deployment