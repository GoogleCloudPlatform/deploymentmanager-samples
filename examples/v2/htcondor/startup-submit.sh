#!/bin/bash
apt-get update && apt-get install -y wget net-tools vim curl gcc
echo "deb http://research.cs.wisc.edu/htcondor/debian/stable/ jessie contrib" >> /etc/apt/sources.list
wget -qO - http://research.cs.wisc.edu/htcondor/debian/HTCondor-Release.gpg.key | apt-key add -
apt-get update && apt-get install -y condor
if  dpkg -s condor >& /dev/null  ; then echo "yes"; else sleep 10; apt-get install -y condor; fi;
cat <<EOF > /etc/condor/config.d/condor_config.local
DISCARD_SESSION_KEYRING_ON_STARTUP=False
CONDOR_ADMIN=EMAIL
CONDOR_HOST=condor-master
DAEMON_LIST = MASTER, SCHEDD
ALLOW_WRITE = \$(ALLOW_WRITE), \$(CONDOR_HOST)
EOF
/etc/init.d/condor start
cd /tmp; curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
bash install-logging-agent.sh
cat <<EOF > /etc/google-fluentd/config.d/condor.conf
<source>
type tail
format none
path /var/log/condor/*Log
pos_file /var/lib/google-fluentd/pos/condor.pos
read_from_head true
tag condor
</source>
EOF
cat <<EOF > /etc/google-fluentd/config.d/condor-jobs.conf
<source>
type tail
format multiline
format_firstline /^\.\.\./
format1 /^\\.\\.\\.\\n... \\((?<job>[^\.]*)\\.(?<subjob>[^\\.]*)\\.(?<run>[^\\)]*)\\).*Usr 0 (?<usrh>[^:]*):(?<usrm>[^:]*):(?<usrs>[^,]*), Sys 0 (?<sysh>[^:]*):(?<sysm>[^
:]*):(?<syss>[^ ]*)  -  Run Remote Usage.*/
types usrh:integer,usrm:integer,usrs:integer,sysh:integer,sysm:integer,syss:integer
path /var/log/condor/jobs/*.log
pos_file /var/lib/google-fluentd/pos/condor-jobs.pos
read_from_head true
tag condor
</source>
EOF
mkdir -p /var/log/condor/jobs
touch /var/log/condor/jobs/stats.log
chmod 666 /var/log/condor/jobs/stats.log
service google-fluentd restart
