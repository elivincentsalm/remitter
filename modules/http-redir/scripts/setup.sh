#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y apache2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
sudo a2enmod rewrite proxy proxy_http
sudo sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf
sudo systemctl start apache2
sudo systemctl enable apache2
