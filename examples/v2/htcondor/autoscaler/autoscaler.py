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
import json
import argparse

parser = argparse.ArgumentParser("autoscaler.py")
parser.add_argument("project_id", help="Project id", type=str)
parser.add_argument("region", help="GCP region where the managed instance group is located", type=str)
parser.add_argument("zone", help="Name of GCP zone where the managed instance group is located", type=str)
parser.add_argument("group_manager", help="Name of the managed instance group", type=str)
parser.add_argument("--debug-level", help="Show detailed debug information. 1-basic debug info. 2-detail debug info", type=int)
args = parser.parse_args()

# Project ID
project = args.project_id #Ex:'slurm-var-demo'

# Region where the managed instance group is located
region = args.region #Ex: 'us-central1'

# Name of the zone where the managed instance group is located
zone = args.zone #Ex: 'us-central1-f'

# The name of the managed instance group.
instance_group_manager = args.group_manager #Ex: 'condor-compute-igm'

# Default number of cores per intance, will be replaced with actual value
cores_per_node = 2

# Default number of running instances that the managed instance group should maintain at any given time. This number will go up and down based on the load (number of jobs in the queue)
size = 0

# Debug level: 1-print debug information, 2 - print detail debug information
debug = 0
if (args.debug-level):
    debug = args.debug-level


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
        pprint(respDel)

    return response


def getCpuLimit():
    request = service.regions().get(project=project, region=region,
                                    fields='quotas')
    response = request.execute()
    cpuLimit = 0

    quotas = response['quotas']
    for quota in quotas:
        if quota['metric'] == 'PREEMPTIBLE_CPUS':
            cpuLimit = quota['limit']

    return int(cpuLimit)


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
        print 'Machine information information'
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
queue_length_req = 'condor_q -totals | tail -n 1'
queue_length_resp = os.popen(queue_length_req).read().split()

if len(queue_length_resp) > 1:
    queue = int(queue_length_resp[0])
    idle_jobs = int(queue_length_resp[6])
else:
    queue = 0
    idle_jobs = 0

print 'Current queue length: ' + str(queue)
print 'Idle jobs: ' + str(idle_jobs)

instanceTemlateInfo = getInstanceTemplateInfo()  # test 'guest_cpus': 4, 'is_preemtible': True, 'machine_type': u'n1-standard-4'
pprint(instanceTemlateInfo)

cores_per_node = instanceTemlateInfo['guest_cpus']
print 'Number of CPU per node: ' + str(cores_per_node)


instance_limit = int(math.ceil(float(getCpuLimit())
                     / float(cores_per_node)))
print 'Instance limit: ' + str(instance_limit)


# Get state for for all jobs in Condor
name_req = 'condor_status  -af name state'
slot_names = os.popen(name_req).read().splitlines()
if debug > 1:
    print 'Jobs in Condor'
    print slot_names

# Scaling down (if needed)
# Find nodes that are not busy (all slots showing status as "Unclaimed")

node_busy = {}
for slot_name in slot_names:
    name_status = slot_name.split()
    if len(name_status) > 1:
        name = name_status[0]
        status = name_status[1]
        slot_server = name.split('@')
        slot = slot_server[0]
        server = slot_server[1].split('.')[0]

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
print node_busy

# Shut down nodes that are not busy
for node in node_busy:
    if not node_busy[node]:
        print 'Will shut down: ' + node + ' ...'

        respDel = deleteFromMig(node)
        if debug > 1:
            pprint(respDel)

# Scale up (if needed)

# Get current number of instances in the MIG
requestGroupInfo = service.instanceGroupManagers().get(project=project,
        zone=zone, instanceGroupManager=instance_group_manager)
responseGroupInfo = requestGroupInfo.execute()
currentTarget = int(responseGroupInfo['targetSize'])
print 'Current target:' + str(currentTarget)

if debug > 1:
    print 'MIG Information:'
    print responseGroupInfo

# Calculate number instances to satisfy current job queue length
if queue > 0:
    size = int(math.ceil(float(queue) / float(cores_per_node)))
    if debug>1:
       print "Calucalting size of MIG: " + str(queue) + "/" + str(cores_per_node) + " = " + str(size)
else:
    size = 0

# Limit number of instances based on quota
size = min(instance_limit, size)

print 'New MIG target size: ' + str(size)

if size > 0 and size <= currentTarget:
    print 'Nothing to do. Current target is sufficient for the queue length'
    exit()

if size == 0 and currentTarget == 0:
    print 'No jobs in the queue. Nothing to do'
    exit()
print

# Number of instances request to resize
request = service.instanceGroupManagers().resize(project=project,
        zone=zone, instanceGroupManager=instance_group_manager,
        size=size)
response = request.execute()
if debug > 1:
    print 'requesting new MIG size:'
    pprint(response)