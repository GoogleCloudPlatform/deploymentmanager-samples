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

# Script for resizing managed instance group (MIG) cluster size based
# on the number of jobs in the Condor Queue.

from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

import os
import math
import argparse

parser = argparse.ArgumentParser("autoscaler.py")
parser.add_argument("-p", "--project_id", help="Project id", type=str)
parser.add_argument("-r", "--region", help="GCP region where the managed instance group is located", type=str)
parser.add_argument("-z", "--zone", help="Name of GCP zone where the managed instance group is located", type=str)
parser.add_argument("-g", "--group_manager", help="Name of the managed instance group", type=str)
parser.add_argument("-c", "--computeinstancelimit", help="Maximum number of compute instances", type=int)
parser.add_argument("-v", "--verbosity", help="Increase output verbosity. 1-show basic debug info. 2-show detail debug info", type=int, choices=[0, 1, 2])
args = parser.parse_args()

# Project ID
project = args.project_id  # Ex:'slurm-var-demo'

# Region where the managed instance group is located
region = args.region  # Ex: 'us-central1'

# Name of the zone where the managed instance group is located
zone = args.zone  # Ex: 'us-central1-f'

# The name of the managed instance group.
instance_group_manager = args.group_manager  # Ex: 'condor-compute-igm'

# Default number of cores per intance, will be replaced with actual value
cores_per_node = 4

# Default number of running instances that the managed instance group should maintain at any given time. This number will go up and down based on the load (number of jobs in the queue)
size = 0

# Debug level: 1-print debug information, 2 - print detail debug information
debug = 0
if (args.verbosity):
    debug = args.verbosity

# Limit for the maximum number of compute instance. If zero (default setting), no limit will be enforced by the  script 
compute_instance_limit = 0
if (args.computeinstancelimit):
    compute_instance_limit = abs(args.computeinstancelimit)


if debug > 1:
    print 'Launching autoscaler.py with the following arguments:'
    print 'project_id: ' + project
    print 'region: ' + region
    print 'zone: ' + zone
    print 'group_manager: ' + instance_group_manager
    print 'computeinstancelimit: ' + str(compute_instance_limit)
    print 'debuglevel: ' + str(debug)


# Remove specified instance from MIG and decrease MIG size
def deleteFromMig(instance):
    instanceUrl = 'https://www.googleapis.com/compute/v1/projects/' \
        + project + '/zones/' + zone + '/instances/' + instance
    instances_to_delete = {'instances': [instanceUrl]}

    requestDelInstance = \
        service.instanceGroupManagers().deleteInstances(project=project,
            zone=zone, instanceGroupManager=instance_group_manager,
            body=instances_to_delete)
    response = requestDelInstance.execute()
    if debug > 0:
        print 'Request to delete instance ' + instance
        pprint(response)

    return response

def getInstanceTemplateInfo():
    requestTemplateName = \
        service.instanceGroupManagers().get(project=project, zone=zone,
            instanceGroupManager=instance_group_manager,
            fields='instanceTemplate')
    responseTemplateName = requestTemplateName.execute()
    template_name = ''

    if debug > 1:
        print 'Request for the template name'
        pprint(responseTemplateName)

    if len(responseTemplateName) > 0:
        template_url = responseTemplateName.get('instanceTemplate')
        template_url_partitioned = template_url.split('/')
        template_name = \
            template_url_partitioned[len(template_url_partitioned) - 1]

    requestInstanceTemplate = \
        service.instanceTemplates().get(project=project,
            instanceTemplate=template_name, fields='properties')
    responseInstanceTemplateInfo = requestInstanceTemplate.execute()

    if debug > 1:
        print 'Template information'
        pprint(responseInstanceTemplateInfo['properties'])

    machine_type = responseInstanceTemplateInfo['properties']['machineType']
    is_preemtible = responseInstanceTemplateInfo['properties']['scheduling']['preemptible']
    if debug > 0:
        print 'Machine Type: ' + machine_type
        print 'Is preemtible: ' + str(is_preemtible)
    request = service.machineTypes().get(project=project, zone=zone,
            machineType=machine_type)
    response = request.execute()
    guest_cpus = response['guestCpus']
    if debug > 1:
        print 'Machine information'
        pprint(responseInstanceTemplateInfo['properties'])
    if debug > 0:
        print 'Guest CPUs: ' + str(guest_cpus)

    instanceTemlateInfo = {'machine_type': machine_type,
                           'is_preemtible': is_preemtible,
                           'guest_cpus': guest_cpus}
    return instanceTemlateInfo


# Obtain credentials
credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

# Get total number of jobs in the queue that includes number of jos waiting as well as number of jobs already assigned to nodes
queue_length_req = 'condor_q -totals -format "%d " Jobs -format "%d " Idle -format "%d " Held'
queue_length_resp = os.popen(queue_length_req).read().split()

if len(queue_length_resp) > 1:
    queue = int(queue_length_resp[0])
    idle_jobs = int(queue_length_resp[1])
    on_hold_jobs = int(queue_length_resp[2])
else:
    queue = 0
    idle_jobs = 0
    on_hold_jobs = 0

print 'Total queue length: ' + str(queue)
print 'Idle jobs: ' + str(idle_jobs)
print 'Jobs on hold: ' + str(on_hold_jobs)

instanceTemlateInfo = getInstanceTemplateInfo()
if debug > 1:
    print 'Information about the compute instance template'
    pprint(instanceTemlateInfo)

cores_per_node = instanceTemlateInfo['guest_cpus']
print 'Number of CPU per compute node: ' + str(cores_per_node)

# Get state for for all jobs in Condor
name_req = 'condor_status  -af name state'
slot_names = os.popen(name_req).read().splitlines()
if debug > 1:
    print 'Currently running jobs in Condor'
    print slot_names

# Adjust current queue length by the number of jos that are on-hold
queue -=on_hold_jobs
if on_hold_jobs>0:
    print "Adjusted queue length: " + str(queue) 

# Calculate number instances to satisfy current job queue length
if queue > 0:
    size = int(math.ceil(float(queue) / float(cores_per_node)))
    if debug>0:
       print "Calucalting size of MIG: ⌈" + str(queue) + "/" + str(cores_per_node) + "⌉ = " + str(size)
else:
    size = 0

# If compute instance limit is specified, can not start more instances then specified in the limit
if compute_instance_limit > 0 and size > compute_instance_limit:
    size = compute_instance_limit;
    print "MIG target size will be limited by " + str(compute_instance_limit)

print 'New MIG target size: ' + str(size)

# Get current number of instances in the MIG
requestGroupInfo = service.instanceGroupManagers().get(project=project,
        zone=zone, instanceGroupManager=instance_group_manager)
responseGroupInfo = requestGroupInfo.execute()
currentTarget = int(responseGroupInfo['targetSize'])
print 'Current MIG target size: ' + str(currentTarget)

if debug > 1:
    print 'MIG Information:'
    print responseGroupInfo

if size == 0 and currentTarget == 0:
    print 'No jobs in the queue and no compute instances running. Nothing to do'
    exit()

if size == currentTarget:
    print 'Running correct number of compute nodes to handle number of jobs in the queue'
    exit()


if size < currentTarget:
    print 'Scaling down. Looking for nodes that can be shut down' 
    # Find nodes that are not busy (all slots showing status as "Unclaimed")

    node_busy = {}
    for slot_name in slot_names:
        name_status = slot_name.split()
        if len(name_status) > 1:
            name = name_status[0]
            status = name_status[1]
            slot = "NO-SLOT"
            slot_server = name.split('@')
            if len(slot_server) > 1:
                slot = slot_server[0]
                server = slot_server[1].split('.')[0]
            else:
                server = slot_server[0].split('.')[0]

            if debug > 0:
                print slot + ', ' + server + ', ' + status + '\n'

            if server not in node_busy:
                if status == 'Unclaimed':
                    node_busy[server] = False
                else:
                    node_busy[server] = True
            else:
                if status != 'Unclaimed':
                    node_busy[server] = True
                    
    if debug > 1:
        print 'Compuute node busy status:'
        print node_busy

    # Shut down nodes that are not busy
    for node in node_busy:
        if not node_busy[node]:
            print 'Will shut down: ' + node + ' ...'
            respDel = deleteFromMig(node)
            if debug > 1:
                print "Shut down request for compute node " + node
                pprint(respDel)
                
    if debug > 1:
        print "Scaling down complete"

if size > currentTarget:
    print "Scaling up. Need to increase number of instances to " + str(size)
    #Request to resize
    request = service.instanceGroupManagers().resize(project=project,
            zone=zone, 
            instanceGroupManager=instance_group_manager,
            size=size)
    response = request.execute()
    if debug > 1:
        print 'Requesting to increase MIG size'
        pprint(response)
        print "Scaling up complete"
