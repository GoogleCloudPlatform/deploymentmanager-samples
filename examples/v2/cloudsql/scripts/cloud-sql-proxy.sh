#!/bin/bash -e

PROXY_SRC=https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64

##
## Install and Configure CloudProxy for CentOS 7 or Debian 8,9
##
curl -LSso /usr/local/bin/cloud_sql_proxy $PROXY_SRC
chmod +x /usr/local/bin/cloud_sql_proxy

add_cloud_proxy_service(){
touch $1
cat <<EOF | tee $1
Description=Google Cloud Compute Engine SQL Proxy
After=network.target google-instance-setup.service google-network-setup.service
After=networking.service

[Service]
Type=simple
UMask=022
WorkingDirectory=/var/cloudsql
ExecStart=/usr/local/bin/cloud_sql_proxy -dir=/var/cloudsql -verbose -instances_metadata=instance/attributes/cloud-sql-instances
Restart=always
User=cloudsql

[Install]
WantedBy=multi-user.target
EOF

systemctl enable cloud-sql-proxy
systemctl start cloud-sql-proxy
}

if  [ -f /etc/debian_version ];then
        adduser --system --shell /sbin/nologin --home /var/cloudsql cloudsql
        chmod 755 /var/cloudsql
        rel=$(cat /etc/debian_version)
        if [ $(echo "$rel > 8" | bc) -ne 0 ]; then
                service_file=/etc/systemd/system/cloud-sql-proxy.service
                add_cloud_proxy_service $service_file
                apt install myql -y
        fi

elif [ -f /etc/redhat-release ];then
        adduser -r -s /sbin/nologin -d /var/cloudsql -m cloudsql
        chmod 755 /var/cloudsql
        rel=$(rpm -q --qf '%{VERSION}' centos-release)
        if [ "$rel" == "7" ]; then
                service_file=/usr/lib/systemd/system/cloud-sql-proxy.service
                add_cloud_proxy_service $service_file
                yum -y install mysql
        fi

fi
