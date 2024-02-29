# ICECAPS Dashboard

This repo contains files to create a dashboard for the ICECAPS-MELT SLEIGH platform.

## Python

To create a virtual Python environment on your local computer, type (assuming pip is installed):

```
conda env create -f environmental.yml
conda deactivate      # Deactivate base conda environment
conda activate sleigh-dashboard
```

## Panel

To serve the panel dashboard for SLEIGH, type

```
panel serve data-dashboard.md --show --autoreload
```

Note that this command will choose a random port on the computer in which it is executed. The local web address will be in the output from the command, so one must use that address to navigate to the served website.

Created by Von P. Walden, Washington State University