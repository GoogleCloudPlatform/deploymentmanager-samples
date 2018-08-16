# Copyright 2018 Google Inc. All rights reserved.
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

""" Creates a cloud function """

import zipfile
import hashlib
import base64
import uuid
from StringIO import StringIO
from copy import deepcopy

GS_SCHEMA_LENGTH = 5
NO_RESOURCES_OR_OUTPUTS = ([], [])

def extract_source_files(imports, local_upload_path):
    """ Returns tuples of imported sources files. """

    imported_files = []
    for imported_file in imports:
        if imported_file.startswith(local_upload_path):
            file_name = imported_file[len(local_upload_path):]
            file_content = imports[imported_file]
            imported_files.append((file_name, file_content))

    return imported_files

def archive_files(files):
    """ Archives input files and returns its as binary array. """

    output_file = StringIO()
    sources_zip = zipfile.ZipFile(output_file,
                                  mode='w',
                                  compression=zipfile.ZIP_DEFLATED)

    for source_file in files:
        sources_zip.writestr(*source_file)

    sources_zip.close()
    return output_file.getvalue()

def upload_source(function, imports, local_path, source_archive_url):
    """ Creates upload sources resource. """

    # Create in-memory archive of cloud function source files
    sources = extract_source_files(imports, local_path)
    archive_base64 = base64.b64encode(archive_files(sources))

    # Cloud function will know it was updated when MD5 changes
    md5 = hashlib.md5()
    md5.update(archive_base64)

    # Split upload path to a bucket and an archive names
    bucket_name = source_archive_url[:source_archive_url.index('/', GS_SCHEMA_LENGTH)] # pylint: disable=line-too-long
    archive_name = source_archive_url[source_archive_url.rfind('/') + 1:]

    # We'll use a Docker volume to pass the archive between the build steps
    volume = '/cloud-function'
    volume_archive_path = volume + '/' + archive_name
    volumes = [
        {
            'name': 'cloud-function',
            'path': volume
        }
    ]

    # Save inline base64-ZIP to a file
    cmd = "echo '{}' | base64 -d > {};".format(archive_base64,
                                               volume_archive_path)

    build_action = {
        'name': 'upload-task',
        'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
        'metadata':
            {
                'runtimePolicy': ['UPDATE_ON_CHANGE']
            },
        'properties':
            {
                'steps':
                    [
                        { # Save a ZIP to a file
                            'name': 'ubuntu',
                            'args': ['bash', '-c', cmd],
                            'volumes': volumes,
                        },
                        { # Create a bucket if not exists
                            'name': 'gcr.io/cloud-builders/gsutil',
                            'args': [
                                '-c',
                                'gsutil mb {} || true'.format(bucket_name)
                            ],
                            'entrypoint': '/bin/bash'
                        },
                        { # Upload a ZIP to a bucket
                            'name': 'gcr.io/cloud-builders/gsutil',
                            'args': [
                                'cp',
                                volume_archive_path, source_archive_url
                            ],
                            'volumes': deepcopy(volumes)
                        }
                    ],
                'timeout': '120s'
            }
    }

    function['properties']['labels'] = {'content-md5': md5.hexdigest()}

    return ([build_action], [])

def generate_bucket_name():
    """ Generates bucket name for cloud function. """

    return 'gs://cloud-functions-{}'.format(uuid.uuid4())

def generate_archive_name():
    """ Generates cloud function zip name. """

    return 'cloud-function-{}.zip'.format(uuid.uuid4())

def generate_upload_path():
    """ Generates cloud function upload full path. """

    return generate_bucket_name() + '/' + generate_archive_name()

def get_source_url_output(function_name):
    """ Generates cloud function output with link to source archive. """

    return {
        'name':  'sourceArchiveUrl',
        'value': '$(ref.{}.sourceArchiveUrl)'.format(function_name)
    }

def append_cloud_storage_sources(function, context):
    """ Add source code from cloud storage. """

    properties = context.properties
    upload_path = properties.get('sourceArchiveUrl', generate_upload_path())
    local_path = properties.get('localUploadPath')

    function['properties']['sourceArchiveUrl'] = upload_path

    outputs = [get_source_url_output(function['name'])]

    if local_path:
        res = upload_source(function, context.imports, local_path, upload_path)
        source_resources, source_outputs = res
        return (source_resources, outputs + source_outputs)
    elif not upload_path:
        msg = "Either localUploadPath or sourceArchiveUrl must be provided"
        raise Exception(msg)
    return ([], outputs)

def append_cloud_repository_sources(function, context):
    """ Add source code from cloud repository. """

    append_optional_property(function,
                             context.properties,
                             'sourceRepositoryUrl')

    output = {
        'name': 'sourceRepositoryUrl',
        'value': '$(ref.{}.sourceRepository.repositoryUrl)'.format(function['name']) # pylint: disable=line-too-long
    }

    return ([], [output])

def append_source_code(function, context):
    """ Add source code reference section. """

    properties = context.properties
    if 'sourceArchiveUrl' in properties or 'localUploadPath' in properties:
        return append_cloud_storage_sources(function, context)
    elif 'sourceRepositoryUrl' in properties:
        return append_cloud_repository_sources(function, context)

    msg = """At least one of the following properties must be provided:
        - sourceRepositoryUrl
        - localUploadPath
        - sourceArchiveUrl"""
    raise ValueError(msg)

def append_trigger_topic(function, properties):
    """ Append Pub/Sub event trigger. """

    topic = properties['triggerTopic']

    function['properties']['eventTrigger'] = {
        'eventType': 'providers/cloud.pubsub/eventTypes/topic.publish',
        'resource': topic
    }

    return NO_RESOURCES_OR_OUTPUTS

def append_trigger_http(function):
    """ Append https trigger and return generated url as output """

    function['properties']['httpsTrigger'] = {}
    output = {
        'name': 'httpsTriggerUrl',
        'value': '$(ref.{}.httpsTrigger.url)'.format(function['name'])
    }

    return ([], [output])

def append_trigger_storage(function, context):
    """ Append Storage trigger. """

    bucket = context.properties['triggerStorage']['bucketName']
    event = context.properties['triggerStorage']['event']

    function['properties']['eventTrigger'] = {
        'eventType': 'google.storage.object.' + event,
        'resource': 'projects/{}/buckets/{}'.format(context.env['project'],
                                                    bucket)
    }

    return NO_RESOURCES_OR_OUTPUTS

def append_trigger(function, context):
    """ Add trigger section and return any associated new resources
    or outputs. """

    if 'triggerTopic' in context.properties:
        return append_trigger_topic(function, context.properties)
    elif 'triggerStorage' in context.properties:
        return append_trigger_storage(function, context)

    return append_trigger_http(function)

def append_optional_property(function, properties, prop_name):
    """ If property is set, it'll be added to function body. """

    val = properties.get(prop_name)
    if val:
        function['properties'][prop_name] = val
    return

def create_function_resource(resource_name, context):
    """ Create a cloud function resource. """

    properties = context.properties
    region = properties['region']
    function_name = properties.get('name', resource_name)

    function = {
        'type': 'cloudfunctions.v1beta2.function',
        'name': function_name,
        'properties':
            {
                'location': region,
                'function': function_name,
            },
    }

    append_optional_property(function, properties, 'entryPoint')
    append_optional_property(function, properties, 'timeout')
    append_optional_property(function, properties, 'runtime')
    append_optional_property(function, properties, 'availableMemoryMb')
    append_optional_property(function, properties, 'description')

    trigger_resources, trigger_outputs = append_trigger(function, context)
    code_resources, code_outputs = append_source_code(function, context)

    if code_resources:
        function['metadata'] = {
            'dependsOn': [dep['name'] for dep in code_resources]
        }

    return (trigger_resources + code_resources + [function],
            trigger_outputs + code_outputs + [
                {
                    'name':  'region',
                    'value': context.properties['region']
                },
                {
                    'name': 'name',
                    'value': '$(ref.{}.name)'.format(function_name)
                }
            ])

def generate_config(context):
    """ Entry point for the deployment resources. """

    resource_name = context.env['name']
    resources, outputs = create_function_resource(resource_name, context)

    return {
        'resources': resources,
        'outputs': outputs
    }
