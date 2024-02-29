---
title: "ICECAPS-MELT - RAVEN CAMP 2024"
author: 
    Von P. Walden
    Michael Gallagher
date: 28 February 2024
---

# SLEIGH Dashboard for ICECAPS-MELT

```python
import panel as pn

pn.extension(template='fast')
```

## DOCS

This application provides a minimal example demonstrating how to write an app in a Markdown file.

```.py
widget = pn.widgets.TextInput(value='world')

def hello_world(text):
    return f'Hello {text}!'

pn.Row(widget, pn.bind(hello_world, widget)).servable()
```

## Plot

```python
widget = pn.widgets.TextInput(value='world')

def hello_world(text):
    return f'Hello {text}!'

pn.Row(widget, pn.bind(hello_world, widget)).servable()
```
