# ICECAPS Dashboard

This repo contains files to create a dashboard for the ICECAPS-MELT SLEIGH platform.

## Python

To create a virtual Python environment on your local computer, type (assuming pip is installed):

```
conda env create -f environmental.yml
conda deactivate      # Deactivate base conda environment
conda activate sleigh-dashboard
pip install -e .
```

The local editable install of this repository allows the `sleigh_dashboard` package to be imported within python scripts

## Development

To deploy a development version of the dashboard, use the command
```
python dashboard.py -pd || fuser -n tcp 5006 -k
```

The `-pd` flag ensures the dashboard is deployed on port 5006, and the follow-up command kills any processes attahced to that port, to maintain a clean working environment.


## Deployment

To deploy the live version of the dashboard, run the command:
```
python dashboard.py
```

This command is encapsulated within `run_dashboard.sh`, which is itself executed by the service file `dashboard.service`.


## The `sleigh_dashboard` package

Documentation pertaining to the `sleigh-dashboard` package can be found within the `sleigh_dashboard/` folder, and within the script files.