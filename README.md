# ICECAPS Dashboard

This repo contains files to create a dashboard for the ICECAPS-MELT SLEIGH platform.

## Python

To create a virtual Python environment on your local computer, type (assuming pip is installed):

```
python3 -m venv .venv
python3 -m pip install -r requirements.txt
```

## Quarto

Install quarto on your local computer using [these instructions](https://quarto.org/docs/get-started/).

## git

To update the website that is associated with this github repo, type the following from the directory that contains the repo:

```
quarto render
git add *
git commit -m "Quarto render at 2023-11-09 09:07"
git push
```

This update will be viewable at https://vonw.github.io/icecaps-dashboard/icecaps-dashboard.html within a couple of minutes.

Created by Von P. Walden, Washington State University
Date: 8 Nov 2023
