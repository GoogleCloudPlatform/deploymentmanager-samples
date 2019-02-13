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

# Install utilities and condor and configure it
sleep 2 #Give some time to setup yum info
cd /tmp
yum install -y wget curl net-tools vim gcc
wget https://research.cs.wisc.edu/htcondor/yum/RPM-GPG-KEY-HTCondor
rpm --import RPM-GPG-KEY-HTCondor
cd /etc/yum.repos.d && wget $CONDOR_REPO_URL
yum install -y $CONDOR_INSTALL_OPT

cd /tmp
cat <<EOF > condor_config.local
DISCARD_SESSION_KEYRING_ON_STARTUP=False
CONDOR_ADMIN=EMAIL
CONDOR_HOST=condor-master
DAEMON_LIST = MASTER, SCHEDD
ALLOW_WRITE = \$(ALLOW_WRITE), \$(CONDOR_HOST)
EOF
mkdir -p /etc/condor/config.d
mv condor_config.local /etc/condor/config.d
eval $CONDOR_STARTUP_CMD

# Install Google python API for optional autoscaler installation
cd /tmp
curl https://bootstrap.pypa.io/get-pip.py | python
pip install --upgrade google-api-python-client
pip install --upgrade oauth2client

# Install and configure logging agent
cd /tmp; curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
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

mkdir -p /var/log/condor/jobs
touch /var/log/condor/jobs/stats.log
chmod 666 /var/log/condor/jobs/stats.log

service google-fluentd restart
