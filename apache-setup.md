# Apache setup for Panel dashboard

1. [Follow instructions](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html) to create a reverse proxy for bokeh server. (Bokeh server is used to serve Panel.)
```
<VirtualHost *:80>
    ServerName localhost

    CustomLog "/home/vonw/repos/sleigh-dashboard/logs/access_log" combined
    ErrorLog "/home/vonw/repos/sleigh-dashboard/logs/error_log"

    ProxyPreserveHost On
    ProxyPass /dashboard/ws ws://127.0.0.1:6646/dashboard/ws
    ProxyPassReverse /dashboard/ws ws://127.0.0.1:6646/dashboard/ws

    ProxyPass /myapp http://127.0.0.1:6646/dashboard
    ProxyPassReverse /myapp http://127.0.0.1:6646/dashboard

    <Directory />
        Require all granted
        Options -Indexes
    </Directory>

    Alias /static /home/vonw/miniforge3/envs/sleigh-dashboard/lib/python3.12/site-packages/bokeh/server/static
    <Directory /home/vonw/miniforge3/envs/sleigh-dashboard/lib/python3.12/site-packages/bokeh/server/static>
        # directives to effect the static directory
        Options +Indexes
    </Directory>

</VirtualHost>
```
2. Enable the necessary Apache modules by typing 
   ```
   sudo a2enmod proxy
   sudo a2enmod proxy_http
   sudo a2enmod proxy_wstunnel
   ```
3. Restart the Apache server by typing ```systemctl restart apache2```