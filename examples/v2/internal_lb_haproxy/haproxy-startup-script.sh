#!/bin/bash
# Copyright 2016 Google Inc. All rights reserved.
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
# Setup script to get all necessary inputs for configuring an internal load
# balancer using HAProxy.
#
# This script will do the following:
#   1) Pull inputs from metadata,
#   2) Get a list of instances to load balance to from instance groups,
#   3) Install and configure HAProxy,
#   4) Restart HAProxy to begin serving.

set -euxo pipefail

# Install, configure, and run haproxy.
apt-get update
apt-get install -y haproxy

# Save original configuration for use in updating.
cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg_bak

# Push out script to regenerate config for haproxy.
RELOAD_CONFIG=/sbin/haproxy-reloadconfig
cat > "${RELOAD_CONFIG}" << 'EOF'
#!/bin/bash

set -euxo pipefail

get_metadata() {
  echo "$(curl http://metadata/computeMetadata/v1/instance/attributes/${1} -H 'Metadata-Flavor: Google')"
}

CONFIG_FILE=/etc/haproxy/haproxy.cfg
BASE_CONFIG_FILE=${CONFIG_FILE}_bak
TEMP_CONFIG_FILE=$(mktemp "haproxy.cfg_XXXXXXXX")

# Gather inputs.
ALGORITHM=$(get_metadata algorithm)
APP_PORT=$(get_metadata app-port)
PORT=$(get_metadata port)

# Build server list.
# instance group information comes in as a list of <group-name>:<zone> tuples.
SERVERS=
for g in $(get_metadata groups); do
  if [[ "${g}" =~ zones/([^/]+)/instanceGroups/(.*)$ ]];
  then
    SERVERS=${SERVERS}$'\n'$(/usr/local/bin/gcloud compute instance-groups list-instances ${BASH_REMATCH[2]} --zone ${BASH_REMATCH[1]} | grep -v NAME | sed "s/^\(.*\) .*\$/  server \1 \1:${APP_PORT} check/")
  else
    echo "Invalid group: ${g}"
  fi
done

# Set up config file.
cp ${BASE_CONFIG_FILE} ${TEMP_CONFIG_FILE}

echo "
# Internal load balancing config.
listen lb *:${PORT}
  mode tcp
  balance ${ALGORITHM}
${SERVERS}" >> ${TEMP_CONFIG_FILE}

# Update config and restart if config has changed.
ret=0
diff ${TEMP_CONFIG_FILE} ${CONFIG_FILE} || ret=$?
if [ ${ret} -ne 0 ]; then
  mv ${TEMP_CONFIG_FILE} ${CONFIG_FILE}
  service haproxy restart
fi
EOF

# Mark executable and run for initial setup.
chmod +x "${RELOAD_CONFIG}"
${RELOAD_CONFIG}

# Set cron job to regenerate every minute.
CRONFILE=$(mktemp "$0.XXXXXXXX")

crontab -l > "${CRONFILE}" || true
echo "* * * * * ${RELOAD_CONFIG}" >> "${CRONFILE}"
crontab "${CRONFILE}"
service cron start
