#!/bin/bash -x
CONDOR_VERSION="CONDORVERSION"
OS_VERSION="OSVERSION"

if [ $CONDOR_VERSION == "CONDORVERSION" ]; then
   CONDOR_INSTALL_OPT=condor-all
else
   CONDOR_INSTALL_OPT="condor-all-$CONDOR_VERSION"
fi
if [ $OS_VERSION == "6" ]; then
   CONDOR_STARTUP_CMD="service condor start"
else
   CONDOR_STARTUP_CMD="systemctl start condor;systemctl enable condor"
fi
CONDOR_REPO_URL=https://research.cs.wisc.edu/htcondor/yum/repo.d/htcondor-stable-rhel${OS_VERSION}.repo

sleep 2 #Give it some time to setup yum
cd /tmp
yum install -y wget curl net-tools vim
wget https://research.cs.wisc.edu/htcondor/yum/RPM-GPG-KEY-HTCondor
rpm --import RPM-GPG-KEY-HTCondor
cd /etc/yum.repos.d && wget $CONDOR_REPO_URL
yum install -y $CONDOR_INSTALL_OPT
cd /tmp
cat <<EOF > condor_config.local
DISCARD_SESSION_KEYRING_ON_STARTUP=False
DAEMON_LIST = MASTER, COLLECTOR, NEGOTIATOR
CONDOR_ADMIN=EMAIL
CONDOR_HOST=condor-master
ALLOW_WRITE = \$(ALLOW_WRITE),10.240.0.0/16
EOF
mkdir -p /etc/condor/config.d
mv condor_config.local /etc/condor/config.d
eval $CONDOR_STARTUP_CMD

cd curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
bash install-logging-agent.sh
cat <<EOF > condor.conf
<source>
type tail
format none
path /var/log/condor/*Log
pos_file /var/lib/google-fluentd/pos/condor.pos
read_from_head true
tag condor
</source>
EOF
mkdir -p /etc/google-fluentd/config.d/
mv condor.conf /etc/google-fluentd/config.d/

service google-fluentd restart
