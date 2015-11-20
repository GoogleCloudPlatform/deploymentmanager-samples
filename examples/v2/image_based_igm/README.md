Creates an autoscaled managed instance group.

Deploy the jinja file and specify properties on the command line like so:

`$ gcloud deployment-manager deployments create igm-deploy --config image_based_igm.jinja --properties targetSize=3,zone=us-central1-f,maxReplicas=5`
