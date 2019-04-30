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

# Imported variables from lustre.jinja, do not modify
CLUSTER_NAME="@CLUSTER_NAME@"
MDS_HOSTNAME="@CLUSTER_NAME@-mds1"
FS_NAME="@FS_NAME@"
NODE_ROLE="@NODE_ROLE@"
ost_mount_point="/mnt/ost"
mdt_mount_point="/mnt/mdt"

LUSTRE_VERSION="@LUSTRE_VERSION@"
LUSTRE_URL="https://downloads.whamcloud.com/public/lustre/${LUSTRE_VERSION}/el7/server/RPMS/x86_64/"
E2FS_VERSION="@E2FS_VERSION@"
E2FS_URL="https://downloads.whamcloud.com/public/e2fsprogs/${E2FS_VERSION}/el7/RPMS/x86_64/"

# Array of all required RPMs for Lustre
LUSTRE_RPMS=("kernel-3*.rpm"
"kernel-devel-*.rpm" 
"kernel-debuginfo-common-*.rpm"
"lustre-2*.rpm"
"lustre-ldiskfs-dkms-*.rpm"
"lustre-osd-ldiskfs-mount-*.rpm"
"kmod-lustre-2*.rpm"
"kmod-lustre-osd-ldiskfs-*.rpm")

# Array of all required RPMs for E2FS
E2FS_RPMS=("e2fsprogs-1*.rpm"
"e2fsprogs-libs-1*.rpm"
"libss-1*.rpm"
"libcom_err-1*.rpm")

# Install updates and minimum packages to install Lustre
function yum_install() {
	yum update -y
	yum install -y net-snmp-libs expect patch dkms gcc libyaml-devel mdadm epel-release pdsh 
}

# Set Message of the Day declaring that Lustre is being installed
function start_motd() {
	motd="*** Lustre is currently being installed in the background. ***
***  Please wait until notified the installation is done.  ***"
	echo "$motd" > /etc/motd
}

#Set Message of the Day to show Lustre cluster information and declare the Lustre installation complete
function end_motd() {
	echo -e "Welcome to the Google Cloud Lustre Deployment!\nLustre MDS: $MDS_HOSTNAME\nLustre FS Name: $FS_NAME\nMount Command: mount -t lustre $MDS_HOSTNAME:/$FS_NAME <local dir>" > /etc/motd
	wall -n "*** Lustre installation is complete! *** "
	wall -n "`cat /etc/motd`"
}

# Wait in a loop until the internet is up
function wait_for_internet() {
	time=0
	#Loop over one ping to google.com, and while no response
	while [ `ping google.com -c1 | grep "time=" -c` -eq 0 ]; do
		sleep 5
		let time+=1
		# If we try 60 times (300 seconds) without success, abort
		if [ $time -gt 60 ]; then
			echo "Internet has not connected. Aborting installation."
			exit 1
		fi
	done
}

# Delete RPMs after installation
function cleanup() {
	rm -rf /lustre/*.rpm
}

function main() {
	# Check for an install.log, if it doesn't exist begin install
	if [ ! -e /lustre/install.log ]; then
		start_motd
		wait_for_internet
		# Install wget
		yum install -y wget
		# Update and install packages in background while RPMs are downloaded
		yum_install &
	
		mkdir /lustre
		cd /lustre

		# Loop over RPM arrays and download them locally
		for i in ${LUSTRE_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${LUSTRE_URL} -P /lustre; done
		for i in ${E2FS_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${E2FS_URL} -P /lustre; done
		find /lustre -name "*.rpm" | xargs -I{} mv {} /lustre
		
		# Wait for yum_install for finish
		wait `jobs -p`
		
		# Disable yum-crom, firewalld, and disable SELINUX (Lustre requirements)
		systemctl disable yum-cron.service
		systemctl stop yum-cron
		sed -i -e "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
		systemctl stop firewalld
		systemctl disable firewalld
		
		# Install all downloaded RPMs
		rpm -ivh --force *.rpm
	
		# Mark install.log as reaching stage 1
		echo 1 > /lustre/install.log
		# Reboot to switch to the Lustre kernel
		reboot
	# If the install.log exists, and contains a 1, begin installation stage 2
	elif [ "`cat /lustre/install.log`" == "1" ]; then
		# Load the Lustre kernel modules
		modprobe lustre
		
		# Get the hostname index (trailing digit on the hostname) 
		host_index=`hostname | grep -o -e '[[:digit:]]*' | tail -1`
		# Decrement the index by 1 to convert to Lustre's indexing
		if [ ! $host_index ]; then
			host_index=0
		else
			let host_index=host_index-1
		fi

		# Determine if the OST/MDT disk is PD or Local SSD
        	num_local_ssds=`lsblk | grep -c nvme`
        	if [ ${num_local_ssds} -gt 1 ]; then
	        	lustre_device="/dev/md0"
	        	sudo mdadm --create ${lustre_device} --level=0 --raid-devices=${num_local_ssds} /dev/nvme0n*
        	elif [ $num_local_ssds -eq 1 ]; then
	        	lustre_device="/dev/nvme0n1"
        	else
	        	lustre_device="/dev/sdb"
        	fi
		
		# If the local node running this script is a Lustre MDS, install the MDS/MGS software
		if [ "$NODE_ROLE" == "MDS" ]; then
			# Do LCTL ping to the OSS nodes and sleep until LNET is up and we get a response 
			while [ `sudo lctl ping ${CLUSTER_NAME}-oss1 | grep -c "Input/output error"` -gt 0 ]; do
				sleep 10
			done

			# Make the MDT mount and mount the device
			mkdir $mdt_mount_point
			mkfs.lustre --mdt --mgs --index=${host_index} --fsname=${FS_NAME} --mgsnode=${MDS_HOSTNAME} $lustre_device
			echo "$lustre_device	$mdt_mount_point	lustre" >> /etc/fstab
			mount -a

			# Once the network is up, make the lustre filesystem on the MDT
			#mkfs.lustre --mdt --mgs --index=${host_index} --fsname=${FS_NAME} --mgsnode=${MDS_HOSTNAME} /dev/sdb

			# Make the MDT mount and mount the device
			#mkdir /mdt
			#mount -t lustre /dev/sdb /mdt
			
			# Check for a successful mount, and fail otherwise.
			if [ `mount | grep -c $mdt_mount_point` -eq 0 ]; then
				echo "MDT mount has failed. Please try mounting manually with "mount -t lustre $lustre_device $mdt_mount_point", or reboot this node."
				exit 1
			fi

			# Disable the authentication upcall by default, change if using auth
			echo NONE > /proc/fs/lustre/mdt/lustre-MDT0000/identity_upcall
		# If the local node running this script is a Lustre OSS, install the OSS software
		elif [ "$NODE_ROLE" == "OSS" ]; then
			# Do LCTL ping to the OSS nodes and sleep until LNET is up and we get a response 
			while [ `sudo lctl ping ${MDS_HOSTNAME} | grep -c "Input/output error"` -gt 0 ]; do
				sleep 10
			done

			# Make the Lustre OST
			# Sleep 60 seconds to give MDS/MGS time to come up before the OSS. More robust communication would be good.
			sleep 60

			# Make the directory to mount the OST, and mount the OST
			mkdir $ost_mount_point
			mkfs.lustre --ost --index=${host_index} --fsname=${FS_NAME} --mgsnode=${MDS_HOSTNAME} $lustre_device
			echo "$lustre_device	$ost_mount_point	lustre" >> /etc/fstab
			mount -a
			
			# Check for a successful mount, and fail otherwise.
			if [ `mount | grep -c $ost_mount_point` -eq 0 ]; then
				echo "OST mount has failed. Please try mounting manually with \"mount -t lustre $lustre_device $ost_mount_point\", or reboot this node."
				exit 1
			fi
		fi
		# Mark install.log as reaching stage 2
		echo 2 > /lustre/install.log
		# Change MOTD to mark install as complete
		end_motd
		# Run the cleanup function to remove RPMs
		cleanup
	# If install.log shows stage 2, then Lustre is installed and just needs to be started
	#else
		# If it's an MDS/MGS, mount the MDT
	#	if [ "$NODE_ROLE" == "MDS" ]; then
	#		mount -t lustre /dev/sdb /mdt
		# If it's an OSS, sleep to let the MDT mount, and then mount the OST
	#	elif [ "$NODE_ROLE" == "OSS" ]; then
	#		sleep 20
	#		mount -t lustre /dev/sdb $ost_mount_point
	#	fi
	fi
}

main $@
