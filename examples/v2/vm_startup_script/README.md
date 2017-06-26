# VM with Startup Script

## Overview
This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a single VM running the startup-script specified as a parameter.

## Deploy the template

Use `vm.yaml` to deploy this example template. Before deploying, edit the file
and specify the zone in which to create the VM instance by replacing the
ZONE_TO_RUN.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create vm-startup-script --config vm.yaml

Then, to test the startup script, run the following command:

    gcloud compute instances describe my-vm-vm | grep "natIP"

Then, open a browser and paste the IP address followed by ':8080' into the
address bar.
