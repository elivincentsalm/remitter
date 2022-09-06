sudo apt update
sudo apt install nginx -y
SCP routes/redirectors/playbooks/nginx-mtls-forwarder/configs/nginx.conf nginx.conf
sudo mv nginx.conf /etc/nginx/nginx.conf
sudo chmod 644 /etc/nginx/nginx.conf
sudo mkdir /etc/nginx/client_certs
sudo openssl req -x509 -newkey rsa:4096 -keyout ca.key -out /etc/nginx/client_certs/ca.crt -nodes -days 365 -subj "/CN=mtls_ca/O=Client\ Certificate\ Demo"
sudo openssl req -newkey rsa:4096 -keyout /etc/ssl/server.key -out server.csr -nodes -days 365 -subj "/CN=54.224.143.19"
sudo openssl x509 -req -in server.csr -CA /etc/nginx/client_certs/ca.crt -CAkey ca.key -CAcreateserial -days 365 -out /etc/ssl/server.crt
sudo openssl req -newkey rsa:4096 -keyout client.key -out client.csr -nodes -days 365 -subj "/CN=client"
sudo openssl x509 -req -in client.csr -CA /etc/nginx/client_certs/ca.crt -CAkey ca.key -CAcreateserial -days 365 -out client.crt
sudo systemctl restart nginx
