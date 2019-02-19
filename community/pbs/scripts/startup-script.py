#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Configure PBS Pro Open Source Edition cluster on GCP (https://www.pbspro.org/)
# Create deployment: "gcloud deployment-manager deployments --project=<project-name> create <deployment-name>  --config pbs-cluster.yaml"
# Clean-up (delete) deployment: "gcloud deployment-manager deployments delete --project=<project-name>  <deployment-name>"
#

import httplib
import os
import shlex
import subprocess
import time
import urllib
import urllib2
import socket

CLUSTER_NAME      = '@CLUSTER_NAME@'
MACHINE_TYPE      = '@MACHINE_TYPE@' # e.g. n1-standard-1, n1-starndard-2
INSTANCE_TYPE     = '@INSTANCE_TYPE@'   #'controller' #'@INSTANCE_TYPE@' # e.g. controller or compute

PROJECT           = '@PROJECT@'
ZONE              = '@ZONE@'

APPS_DIR          = '/apps'
PBS_VERSION       = '@PBS_VERSION@'
STATIC_NODE_COUNT =  @STATIC_NODE_COUNT@

COMPUTE_PUBLIC_IPS = @COMPUTE_PUBLIC_IPS@

PBS_PREFIX  = APPS_DIR + '/pbs/pbs-' + PBS_VERSION
INSTANCE_NAME_PREFIX = '@INSTANCE_NAME_PREFIX@'

MOTD_HEADER = '''


*********          PBS PRO          ********* 

qsub	submit a pbs job
qdel	delete pbs batch job
qhold	hold pbs batch jobs
qrls	release hold on pbs batch jobs

qstat -q		list all queues
qstat -a		list all jobs
qstat -u userid		list jobs for userid
qstat -r		list running jobs
qstat -f job_id		list full information about job_id
qstat -Qf queue		list full information about queue
qstat -B		list summary status of the job server
pbsnodes -a		list status of all compute nodes
tracejob 		Extracts job info from log files
sudo /etc/init.d/pbs restart Restart PBS

export PATH=$PATH:/opt/pbs/bin/

'''

NodeName=""


def add_pbs_user():

    PBS_UID = str(992)
    subprocess.call(['groupadd', '-g', PBS_UID, 'pbs'])
    subprocess.call(['useradd', '-m', '-c', 'PBS Workload Manager',
        '-d', '/var/lib/pbs', '-u', PBS_UID, '-g', 'pbs',
        '-s', '/bin/bash', 'pbs'])

# END add_pbs_user()


def start_motd():

    msg = MOTD_HEADER + """
*** PBS is currently being installed/configured in the background. ***
A terminal broadcast will announce when installation and configuration is
complete.

You can check startup log messages in /var/log/messages
To run startup script again: sudo google_metadata_script_runner --script-type startup
More info: https://cloud.google.com/compute/docs/startupscript#rerunthescript 

"""

    if INSTANCE_TYPE != "controller":
        msg += """/home on the controller will be mounted over the existing /home.
Any changes in /home will be hidden. Please wait until the installation is
complete before making changes in your home directory.

"""

    f = open('/etc/motd', 'w')
    f.write(msg)
    f.close()

# END start_motd()


def end_motd():

    f = open('/etc/motd', 'w')
    f.write(MOTD_HEADER)
    f.close()

    subprocess.call(['wall', '-n',
        '*** PBS ' + INSTANCE_TYPE + ' daemon installation complete ***'])

    if INSTANCE_TYPE != "controller":
        subprocess.call(['wall', '-n', """
/home on the controller was mounted over the existing /home.
Either log out and log back in or cd into ~.
"""])

#END start_motd()


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=1)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

#END have_internet()


def install_packages():

    packages = [
                'munge',
                'munge-devel',
                'munge-libs',

                'wget',
                'gcc',
                'make',
                'rpm-build',
                'libtool',
                'hwloc-devel',
                'libX11-devel',
                'libXt-devel',
                'libedit-devel',
                'libical-devel',
                'ncurses-devel',
                'perl',
                'postgresql-devel',
                'python-devel',
                'tcl-devel',
                'tk-devel',
                'swig',
                'expat-devel',
                'openssl-devel',
                'libXext',
                'libXft',
                'expat',
                'libedit',
                'postgresql-server',
                'python',
                'sendmail',
                'sudo',
                'tcl',
                'tk',
                'libical',
   		'unzip',
   		'nfs-utils',
   		'nfs-utils-lib'
               ]

    while subprocess.call(['yum', 'install', '-y'] + packages):
        print "yum failed to install packages. Trying again in 5 seconds"
        time.sleep(5)

#END install_packages()



def setup_nfs_exports():

    f = open('/etc/exports', 'w')
    f.write("""
/home  *(rw,sync,no_subtree_check,no_root_squash)
%s  *(rw,sync,no_subtree_check,no_root_squash)
""" % APPS_DIR)
    f.close()

    subprocess.call(shlex.split("exportfs -a"))

#END setup_nfs_exports()


def expand_machine_type():

    # Force re-evaluation of site-packages so that namespace packages (such
    # as google-auth) are importable. This is needed because we install the
    # packages while this script is running and do not have the benefit of
    # restarting the interpreter for it to do it's usual startup sequence to
    # configure import magic.
    import sys
    import site
    for path in [x for x in sys.path if 'site-packages' in x]:
        site.addsitedir(path)

    import googleapiclient.discovery

    # Assume sockets is 1. Currently, no instances with multiple sockets
    # Assume hyper-threading is on and 2 threads per core
    machine = {'sockets': 1, 'cores': 1, 'threads': 1, 'memory': 1}

    try:
        compute = googleapiclient.discovery.build('compute', 'v1',
                                                  cache_discovery=False)
        type_resp = compute.machineTypes().get(project=PROJECT, zone=ZONE,
                machineType=MACHINE_TYPE).execute()
        if type_resp:
            tot_cpus = type_resp['guestCpus']
            if tot_cpus > 1:
                machine['cores']   = tot_cpus / 2
                machine['threads'] = 2

            # Because the actual memory on the host will be different than what
            # is configured (e.g. kernel will take it). From experiments, about
            # 16 MB per GB are used (plus about 400 MB buffer for the first
            # couple of GB's. Using 30 MB to be safe.
            gb = type_resp['memoryMb'] / 1024;
            machine['memory'] = type_resp['memoryMb'] - (400 + (gb * 30))

    except Exception, e:
        print "Failed to get MachineType '%s' from google api (%s)" % (MACHINE_TYPE, str(e))

    return machine
#END expand_machine_type()



def install_pbs():
    #Ex. Source http://wpc.23a7.iotacdn.net/8023A7/origin2/rl/PBS-Open/pbspro_18.1.2.centos7.zip
    #Ex2: https://s3.amazonaws.com/pbspro/pbspro-server-18.1.1-0.x86_64.rpm
    #Ex3: https://github.com/PBSPro/pbspro/releases/download/v18.1.3/pbspro_18.1.3.centos7.zip

    BASE_URL = 'https://github.com/PBSPro/pbspro/releases/download/'
    file = 'v' + PBS_VERSION + '/pbspro_' + PBS_VERSION + '.centos7.zip'

    print "Will download %s to /tmp/ directory" % file

    urllib.urlretrieve(BASE_URL + file, '/tmp/pbs.zip')

    prev_path = os.getcwd()


    os.chdir('/tmp')
    pkgPbs = "/tmp/" + file 
    subprocess.call(['unzip', '-o', 'pbs.zip'])
    os.chdir('/tmp/pbspro_' + PBS_VERSION + '.centos7')
    subprocess.call(['yum', 'install', '-y', 'pbspro-server-' + PBS_VERSION + '-0.x86_64.rpm'])

#END install_pbs()

def install_pbs_tmpfile():

    run_dir = '/var/run/pbs'

    f = open('/etc/tmpfiles.d/pbs.conf', 'w')
    f.write("""
d %s 0755 pbs pbs -
""" % run_dir)
    f.close()

    if not os.path.exists(run_dir):
        os.makedirs(run_dir)

    os.chmod(run_dir, 0o755)
    subprocess.call(['chown', 'pbs:', run_dir])

#END install_pbs_tmpfile()

def install_controller_service_scripts():

    install_pbs_tmpfile()

    # pbsctld.service
    f = open('/usr/lib/systemd/system/pbsctld.service', 'w')
    f.write("""
[Unit]
Description=PBS controller daemon
After=network.target munge.service
ConditionPathExists={prefix}/etc/pbs.conf

[Service]
Type=forking
EnvironmentFile=-/etc/sysconfig/pbsctld
ExecStart={prefix}/sbin/pbsctld $PBSCTLD_OPTIONS
ExecReload=/bin/kill -HUP $MAINPID
PIDFile=/var/run/pbs/pbsctld.pid

[Install]
WantedBy=multi-user.target
""".format(prefix = PBS_PREFIX))
    f.close()

    os.chmod('/usr/lib/systemd/system/pbsctld.service', 0o644)

    # pbsdbd.service
    f = open('/usr/lib/systemd/system/pbsdbd.service', 'w')
    f.write("""
[Unit]
Description=PPS DBD accounting daemon
After=network.target munge.service
ConditionPathExists={prefix}/etc/pbsdbd.conf

[Service]
Type=forking
EnvironmentFile=-/etc/sysconfig/pbsdbd
ExecStart={prefix}/sbin/pbsdbd $PBSDBD_OPTIONS
ExecReload=/bin/kill -HUP $MAINPID
PIDFile=/var/run/pbs/pbsdbd.pid

[Install]
WantedBy=multi-user.target
""".format(prefix = APPS_DIR + "/pbs/current"))
    f.close()

    os.chmod('/usr/lib/systemd/system/pbsdbd.service', 0o644)

#END install_controller_service_scripts()


def install_compute_service_scripts():

    install_pbs_tmpfile()

    #config {test}
    f = open('/etc/pbs.conf', 'w')
    f.write("""
PBS_EXEC=/opt/pbs
PBS_SERVER={instance_prefix}controller
PBS_START_SERVER=0
PBS_START_SCHED=0
PBS_START_COMM=1
PBS_START_MOM=1
PBS_HOME=/var/spool/pbs
PBS_CORE_LIMIT=unlimited
PBS_SCP=/bin/scp
""".format(instance_prefix = INSTANCE_NAME_PREFIX))

 

    f.close()


    # pbsd.service
    f = open('/usr/lib/systemd/system/pbsd.service', 'w')
    f.write("""
[Unit]
Description=pbs node daemon
After=network.target munge.service
ConditionPathExists={prefix}/etc/pbs.conf

[Service]
Type=forking
EnvironmentFile=-/etc/sysconfig/pbsd
ExecStart={prefix}/sbin/pbsd $PBSD_OPTIONS
ExecReload=/bin/kill -HUP $MAINPID
PIDFile=/var/run/pbs/pbsd.pid
KillMode=process
LimitNOFILE=51200
LimitMEMLOCK=infinity
LimitSTACK=infinity

[Install]
WantedBy=multi-user.target
""".format(prefix = APPS_DIR + "/pbs/current"))
    f.close()

    os.chmod('/usr/lib/systemd/system/pbsd.service', 0o644)

#END install_compute_service_scripts()


def setup_bash_profile():

    f = open('/etc/profile.d/pbs.sh', 'w')
    f.write("""
S_PATH=/opt/pbs
PATH=$PATH:$S_PATH/bin
""")
    f.close()

#END setup_bash_profile()


def mount_nfs_vols():

    f = open('/etc/fstab', 'a')
    f.write("""
{1}controller:{0}    {0}     nfs      rw,sync,hard,intr  0     0
{1}controller:/home  /home   nfs      rw,sync,hard,intr  0     0
""".format(APPS_DIR, INSTANCE_NAME_PREFIX))
    f.close()

    while subprocess.call(['mount', '-a']):
        print "Waiting for " + APPS_DIR + " and /home to be mounted"
        time.sleep(5)

#END mount_nfs_vols()

def test_pbs():
    urllib.urlretrieve('https://s3.amazonaws.com/pbspro/test.zip', '/tmp/test.zip')
    os.chdir('/tmp')
    subprocess.call(['unzip', '-o', 'test.zip'])

    #install pip
    urllib.urlretrieve('https://bootstrap.pypa.io/get-pip.py', '/tmp/get-pip.py') 
    subprocess.call(['python', 'get-pip.py'])

    os.chdir('/tmp/test/fw')
    subprocess.call(shlex.split('pip install -r requirements.txt .'))
    subprocess.call(shlex.split('pbs_config --make-ug'))

    os.chdir('/tmp/test/tests')

    subprocess.call(shlex.split('pbs_benchpress -l INFOCLI2 -o ptl.txt'))
#END test_pbs()

def register_compute_nodes():
    host = socket.gethostname();
    for node_id in range(1, STATIC_NODE_COUNT+1):
      cmd_create_node = "/opt/pbs/bin/qmgr -c 'create node " + INSTANCE_NAME_PREFIX + "compute" + str(node_id) + "'"
      print "will execute: " + cmd_create_node 
      subprocess.call(shlex.split(cmd_create_node))    
#END create_node()

def main():
    # Disable SELinux
    subprocess.call(shlex.split('setenforce 0'))
    
    print "ARGUMENT STATIC_NODE_COUNT: @STATIC_NODE_COUNT@"
    

    #if ((INSTANCE_TYPE == "controller") and  not COMPUTE_PUBLIC_IPS):
    if (INSTANCE_TYPE == "controller"):
        # Setup a NAT gateway for the compute instances to get internet from.
        subprocess.call(shlex.split("sysctl -w net.ipv4.ip_forward=1"))
        subprocess.call(shlex.split("firewall-cmd --direct --add-rule ipv4 nat POSTROUTING 0 -o eth0 -j MASQUERADE"))
        subprocess.call(shlex.split("firewall-cmd --reload"))
        subprocess.call(shlex.split("echo net.ipv4.ip_forward=1 >> /etc/sysctl.conf"))

    if INSTANCE_TYPE == "compute":
        while not have_internet():
            print "Waiting for internet connection"

    add_pbs_user()
    start_motd()

    print "Installing packages..."
    install_packages()

    if not os.path.exists(APPS_DIR + '/pbs'):
        os.makedirs(APPS_DIR + '/pbs')

    if INSTANCE_TYPE != "controller":
        mount_nfs_vols()

    if INSTANCE_TYPE == "controller":
        print "Installing PBS on controller node..."
        install_pbs()

        print "Installing PBS service scripts..."
        install_controller_service_scripts()

        print "Starting PBS process..."
        subprocess.call(shlex.split('/etc/init.d/pbs start'))

        print "Registering compute nodes ..."
        register_compute_nodes()

        # Export at the end to signal that everything is up
        subprocess.call(shlex.split('systemctl enable nfs-server'))
        subprocess.call(shlex.split('systemctl start nfs-server'))
        setup_nfs_exports()
        
    elif INSTANCE_TYPE == "compute":
        print "Installing PBS on compute node..."
        install_pbs()

        install_compute_service_scripts()
        subprocess.call(shlex.split('systemctl enable pbsd'))
        subprocess.call(shlex.split('systemctl start pbsd'))
        print "Installed additional components on compute node"

    end_motd()

    print "Setting up bash profile..."
    setup_bash_profile()
  
    print "Restarting PBS to get activate new configuration..."
    subprocess.call(shlex.split("/etc/init.d/pbs restart"))

    subprocess.call(["wall", "Completed PBS installation"])

    #test_pbs()

    print "Completed PBS installation on " + INSTANCE_TYPE
# END main()


if __name__ == '__main__':
    main()


