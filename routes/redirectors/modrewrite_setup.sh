sudo apt update
sudo apt install apache -y
sudo a2enmod rewrite proxy proxy_http
SCP routes/redirectors/playbooks/modrewrite-forwarder/configs/apache2.conf apache2.conf
sudo mv apache2.conf /etc/apache2/apache2.conf
SCP routes/redirectors/playbooks/modrewrite-forwarder/configs/.htaccess .htaccess
sudo mv .htaccess /var/www/html/.htaccess
sudo systemctl restart apache2
