# Apache setup for Panel dashboard

1. [Follow instructions](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html) to create a reverse proxy for bokeh server. (Bokeh server is used to serve Panel.) Edited <VirtualHost> in /etc/apache2/sites-available/icecapsmelt.org to be:
```
<VirtualHost *:80>
    ServerAdmin eeasm@leeds.ac.uk
    ServerName icecapsmelt.org
    ServerAlias www.icecapsmelt.org
    DocumentRoot /var/www/icecapsmelt.org
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    # ProxyPass / http://127.0.0.1:6646/
    # RewriteEngine on
    # RewriteCond %{HTTP:Upgrade} websocket [NC]
    # RewriteCond %{HTTP:Connection} upgrade [NC]
    # RewriteRule ^/?(.*) "ws://127.0.0.1:6646/$1" [P,L]

    ProxyPreserveHost On
    ProxyPass /dashboard/ws ws://127.0.0.1:6646/dashboard/ws iobuffersize=65536 responsefieldsize=65536 receivebuffersize=65536
    ProxyPassReverse /dashboard/ws ws://127.0.0.1:6646/dashboard/ws 

    ProxyPass /dashboard http://127.0.0.1:6646/dashboard iobuffersize=65536 responsefieldsize=65536 receivebuffersize=65536
    ProxyPassReverse /dashboard http://127.0.0.1:6646/dashboard 

#    <Directory />
#        Require all granted
#        Options -Indexes
#    </Directory>
#
#    Alias /static /var/www/icecapsmelt.org/static
#    <Directory /var/www/icecapsmelt.org/static>
#        # directives to effect the static directory
#        Options +Indexes
#    </Directory>

</VirtualHost>
```
2. Enable the necessary Apache modules by typing 
   ```
   sudo a2enmod proxy
   sudo a2enmod proxy_http
   sudo a2enmod proxy_wstunnel
   ```
3. Restart the Apache server by typing ```systemctl restart apache2```
4. Changed "None" to "All" in /etc/apache2/apache2.conf for /var/www directory

- The Apache2 ERROR log file is located in ```/var/log/apache2/error.log```
- The Apache2 ACCESS log file is located in ```/var/log/apache2/error.log```
   
