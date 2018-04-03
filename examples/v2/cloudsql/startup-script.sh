#!/bin/bash -e
  
PROXY_SRC=https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64

##
## Install and Configure CloudProxy
##
curl -LSso /usr/local/bin/cloud_sql_proxy $PROXY_SRC
chmod +x /usr/local/bin/cloud_sql_proxy
adduser -r -s /sbin/nologin -d /var/cloudsql -m cloudsql

cat <<EOF | tee /usr/lib/systemd/system/cloud-sql-proxy.service
[Unit]
Description=Google Cloud Compute Engine SQL Proxy
After=network.target google-instance-setup.service google-network-setup.service
After=networking.service

[Service]
Type=simple
WorkingDirectory=/var/cloudsql
ExecStart=/usr/local/bin/cloud_sql_proxy -dir=/var/cloudsql -verbose -instances_metadata=instance/attributes/cloud-sql-instances
Restart=always
User=cloudsql 

[Install]
WantedBy=multi-user.target
EOF

systemctl enable cloud-sql-proxy
