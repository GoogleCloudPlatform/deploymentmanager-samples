#!/bin/bash

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

CLUSTER_NAME="@CLUSTER_NAME@"
MDS_HOSTNAME="@CLUSTER_NAME@-mds1"
FS_NAME="@FS_NAME@"
NODE_ROLE="@NODE_ROLE@"

LUSTRE_VERSION="@LUSTRE_VERSION@"
LUSTRE_URL="https://downloads.whamcloud.com/public/lustre/${LUSTRE_VERSION}/el7/server/RPMS/x86_64/"
E2FS_VERSION="@E2FS_VERSION@"
E2FS_URL="https://downloads.whamcloud.com/public/e2fsprogs/${E2FS_VERSION}/el7/RPMS/x86_64/"

LUSTRE_RPMS=("kernel-3*.rpm"
"kernel-devel-*.rpm" 
"kernel-debuginfo-common-*.rpm"
"lustre-2*.rpm"
"lustre-ldiskfs-dkms-*.rpm"
"lustre-osd-ldiskfs-mount-*.rpm"
"kmod-lustre-2*.rpm"
"kmod-lustre-osd-ldiskfs-*.rpm")

E2FS_RPMS=("e2fsprogs-1*.rpm"
"e2fsprogs-libs-1*.rpm"
"libss-1*.rpm"
"libcom_err-1*.rpm")

function yum_install() {
	yum update -y
	yum install -y net-snmp-libs expect patch dkms gcc libyaml-devel 
}

function start_motd() {
	motd="*** Lustre is currently being installed in the background. ***
***  Please wait until notified the installation is done.  ***"
	echo "$motd" > /etc/motd
}

function end_motd() {
	echo -e "Lustre MDS: $MDS_HOSTNAME\nLustre FS Name: $FS_NAME\nMount Command: mount -t lustre $MDS_HOSTNAME:/$FS_NAME" > /etc/motd
	wall -n "*** Lustre installation is complete! *** "
	wall -n "`cat /etc/motd`"
}

function wait_for_internet() {
	time=0
	while [ `ping google.com -c1 | grep "time=" -c` -eq 0 ]; do
		sleep 5
		let time+=1
		if [ $time -gt 60 ]; then
			echo "Internet has not connected. Aborting installation."
			exit 1
		fi
	done
}

function cleanup() {
	rm -rf /lustre/*.rpm
}

function main() {
	if [ ! -e /lustre/install.log ]; then
		start_motd
		wait_for_internet
		yum install -y wget
		yum_install &
	
		mkdir /lustre
		cd /lustre

		for i in ${LUSTRE_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${LUSTRE_URL} -P /lustre; done
		for i in ${E2FS_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${E2FS_URL} -P /lustre; done
		find /lustre -name "*.rpm" | xargs -I{} mv {} /lustre
		
		# Wait for yum_install for finish
		wait `jobs -p`
		
		systemctl disable yum-cron.service
		systemctl stop yum-cron
		sed -i -e "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
		systemctl stop firewalld
		systemctl disable firewalld
		
		rpm -ivh --force *.rpm
	
		echo 1 > /lustre/install.log
		reboot
	elif [ "`cat /lustre/install.log`" == "1" ]; then
		if [ "$NODE_ROLE" == "MDS" ]; then
			modprobe lustre
			host_index=`hostname | grep -o -e '[[:digit:]]*' | tail -1`

			if [ ! $host_index ]; then
				host_index=0
			else
				let host_index=host_index-1
			fi
			
			while [ `sudo lctl ping ${CLUSTER_NAME}-oss1 | grep -c "Input/output error"` -gt 0 ]; do
				sleep 10
			done

			mkfs.lustre --mdt --mgs --index=${host_index} --fsname=${FS_NAME} --mgsnode=${MDS_HOSTNAME} /dev/sdb
			echo NONE > /proc/fs/lustre/mdt/lustre-MDT0000/identity_upcall
			
			mkdir /mdt
			mount -t lustre /dev/sdb /mdt
			
			echo 2 > /lustre/install.log
			end_motd
			cleanup
		elif [ "$NODE_ROLE" == "OSS" ]; then
			modprobe lustre
			sleep 60
			host_index=`hostname | grep -o -e '[[:digit:]]*' | tail -1`
			let host_index=host_index-1
		
			while [ `sudo lctl ping ${MDS_HOSTNAME} | grep -c "Input/output error"` -gt 0 ]; do
				sleep 10
			done

			mkfs.lustre --ost --index=${host_index} --fsname=${FS_NAME} --mgsnode=${MDS_HOSTNAME} /dev/sdb
			
			mkdir /ost
			sleep 20
			mount -t lustre /dev/sdb /ost
			
			echo 2 > /lustre/install.log
			end_motd
			cleanup
		fi
	else
		if [ "$NODE_ROLE" == "MDS" ]; then
			mount -t lustre /dev/sdb /mdt
		elif [ "$NODE_ROLE" == "OSS" ]; then
			sleep 20
			mount -t lustre /dev/sdb /ost
		fi
	fi
}

main $@
