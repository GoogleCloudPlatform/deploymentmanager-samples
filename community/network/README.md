# Creating Networks and Subnetworks Through Deployment Manager

This example set of templates will:

1. Create a new network.
2. Create some subnetworks with the specified CIDR.

## Using the templates.

1.  Customize the templates for your organization. You will need to:
    *   Choose the name of your network,
    *   List the subnetworks (with their associated region and
        CIDR) that you want.
2.  Create the network and subnetworks. If using the CLI:

        gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME \
           --config config.yaml
