sudo apt update
sudo apt install socat -y
SCP routes/redirectors/playbooks/dns-socat-forwarder/configs/dns-redir.service dns-redir.service
sudo mv dns-redir.service /etc/systemd/system/dns-redir.service
sudo systemctl restart dns-redir
