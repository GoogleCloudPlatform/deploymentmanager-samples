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
HSM_GCS_BUCKET="@HSM_GCS_BUCKET@"
HSM_GCS_BUCKET_IMPORT="@HSM_GCS_BUCKET_IMPORT@"
ost_mount_point="/mnt/ost"
mdt_mount_point="/mnt/mdt"

LUSTRE_VERSION="@LUSTRE_VERSION@"
LUSTRE_CLIENT_VERSION="lustre-2.10.8"
LUSTRE_URL="https://downloads.whamcloud.com/public/lustre/${LUSTRE_VERSION}/el7/server/RPMS/x86_64/"
LUSTRE_CLIENT_URL="https://downloads.whamcloud.com/public/lustre/${LUSTRE_CLIENT_VERSION}/el7/client/RPMS/x86_64/"
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

LUSTRE_CLIENT_RPMS=("kmod-lustre-client-2*.rpm"
"lustre-client-2*.rpm")

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

# Install Lemur Lustre HSM Data Mover
function install_lemur() {
	yum install -y wget go make rpm-build libselinux-devel libyaml-devel zlib-devel
	yum groupinstall -y "Development Tools" --skip-broken

	mkdir /lustre
	cd /lustre

	git clone https://github.com/mhugues/lemur.git
	cd lemur

	git checkout feature/lhsm-plugin-gcs

	sudo make local-rpm

	rpm -ivh /root/rpmbuild/RPMS/x86_64/*.rpm

}

function configure_lemur() {
	#Lemur Agent Configuration
	mkdir -p /var/lib/lhsmd/roots

	cat > /etc/lhsmd/agent << EOF
## The mount target for the Lustre file system that will be used with this agent.
##
client_device=  "${MDS_HOSTNAME}@tcp:/lustre"

##
## Base directory used for the Lustre mount points created by the agent
##
mount_root= "/var/lib/lhsmd/roots"

##
## List of enabled plugins
##
enabled_plugins = ["lhsm-plugin-gcs"]

##
## Directory to look for the plugins
##
plugin_dir = "/usr/libexec/lhsmd"

##
## Number of threads handling incoming HSM requests.
##
handler_count = 8

##
## Enable experimental snapshot feature.
##
snapshots {
     enabled = false
}

EOF

	#Lemur GCS Plugin Conf
	cat > /etc/lhsmd/lhsm-plugin-gcs << EOF
## Credentials file in Json format from the service account (Optional)
#service_account_key="[SA_NAME-key.json]"

## Maximum number of concurrent copies.
##
num_threads=8

##
## One or more archive definition is required.
##
archive "1" {
        id = 1
        bucket = "${HSM_GCS_BUCKET:5}"
}
EOF

	chmod 600 /etc/lhsmd/lhsm-plugin-gcs

	#Start lhsm agent daemon
	systemctl start lhsmd


}

function hsm_import_bucket()
{

	bucket_file_list=`gsutil ls -r ${HSM_GCS_BUCKET_IMPORT}/** | sed "/\/:$/d"`

	for i in $bucket_file_list
	do
		# Convert to destination file full path
		dest_file_name=`echo ${i} | sed "s%${HSM_GCS_BUCKET_IMPORT}%/mnt/%g"`
		dir_name=`dirname ${dest_file_name}`

		if [ ! -d ${dir_name} ]; then
			mkdir -p ${dir_name}
		fi

		src_file_name=`echo $i | sed "s%gs://.[^/]*/%%g"`
		lhsm import --uuid ${src_file_name} --uid 0 --gid 0 ${dest_file_name}

	done
}

function install_lustre_client() {

	yum install -y git

	git clone git://git.whamcloud.com/fs/lustre-release.git && cd lustre-release
	git checkout 2.10.8

	yum install -y kernel-devel kernel-headers kernel-debug libtool libyaml-devel libselinux-devel zlib-devel rpm-build

	sh ./autogen.sh
	./configure --disable-server --with-o2ib=no --enable-client
	make rpms

	mkdir -p /lustre/lustre_client_release
	cp *.rpm /lustre/lustre_client_release/
	rpm -ivh /lustre/lustre_client_release/${LUSTRE_CLIENT_RPMS[@]}

}

function main() {
	# Check for an install.log, if it doesn't exist begin install
	if [ ! -e /lustre/install.log ]; then
		start_motd
		wait_for_internet
		# Install wget
		yum install -y wget

		mkdir /lustre
		cd /lustre

		if [ "$NODE_ROLE" != "HSM" ]; then
			# Update and install packages in background while RPMs are downloaded
			yum_install &

			# Loop over RPM arrays and download them locally
			for i in ${LUSTRE_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${LUSTRE_URL} -P /lustre; done
			for i in ${E2FS_RPMS[@]}; do wget -r -l1 --no-parent -A "$i" ${E2FS_URL} -P /lustre; done
			find /lustre -name "*.rpm" | xargs -I{} mv {} /lustre
		
			# Wait for yum_install for finish
			wait `jobs -p`
		fi
		
		# Disable yum-crom, firewalld, and disable SELINUX (Lustre requirements)
		systemctl disable yum-cron.service
		systemctl stop yum-cron
		sed -i -e "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
		systemctl stop firewalld
		systemctl disable firewalld
		
		# Install all downloaded RPMs
		rpm -ivh --force *.rpm
		if [ "$NODE_ROLE" == "HSM" ]; then
			install_lustre_client
		fi
	
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

			# Enable HSM on the Lustre MGS
			lctl set_param -P mdt.*-MDT0000.hsm_control=enabled

			# Setup the archive id for the specific HSM backend, we are only using 1 so id=1 is just fine
			lctl set_param -P mdt.*-MDT0000.hsm.default_archive_id=1

			# Increase the number of HSM Max requests on the MDT, you may want to
			# experiment with various values if you intend to go to production
			lctl set_param mdt.*-MDT0000.hsm.max_requests=128

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
		# If the local node running this script is a Lustre HSM Data Mover, install the Lemur software
		elif [ "$NODE_ROLE" == "HSM" ]; then
			# Do LCTL ping to the OSS nodes and sleep until LNET is up and we get a response 
			while [ `sudo lctl ping ${MDS_HOSTNAME} | grep -c "Input/output error"` -gt 0 ]; do
				sleep 10
			done

			mount_status=1

			while [ ${mount_status} -ne 0 ]; do
				mount -t lustre ${MDS_HOSTNAME}:/${FS_NAME} /mnt
				mount_status=$?
			done

			install_lemur
			configure_lemur

			if [ ! -z "${HSM_GCS_BUCKET_IMPORT}" ]; then
				hsm_import_bucket
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
