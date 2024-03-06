#!/usr/bin/env bash
set -x

# run the dashboard panel/bokeh/websocket python script for displaying sleigh+mvp info
while true
do 

    # env var allows all resources to be packed into websocket so
    # apache http proxy can actually locate them 
    BOKEH_RESOURCES=inline /home/sleigh/sleigh-dashboard/dashboard.py

    sleep 10 # allow time for killing/reloading file etc

done

