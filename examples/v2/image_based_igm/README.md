# Creates an autoscaled managed instance group.

## Overview

Deploy the template and specify properties on the command line like below:

```
$ gcloud deployment-manager deployments create igm-deploy
 --template image_based_igm.jinja
 --properties targetSize:3,zone:us-central1-f,maxReplicas:5
```

You may also use the python template in the command like below:

```
$ gcloud deployment-manager deployments create igm-deploy
 --template image_based_igm.py
 --properties targetSize:3,zone:us-central1-f,maxReplicas:5
```
