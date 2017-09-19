# Access control example

## Overview

This [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template
deploys a PubSub topic and limits the permissions using a DM access control
section.

Note that the access control section gives the service account admin privileges.
This is important so DM can make changes to the resource later.

## Deploy the template

Use `access_control.jinja` to deploy this example template. Fill in `YOUR_EMAIL_HERE`
with your email to retain permissions to the resource (if using DM, you
technically only need the service account). Note there should be no space between
`user:` and your email.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create my-access-control-test --template access_control.jinja

## More information

[Access Control Documentation](https://cloud.google.com/deployment-manager/docs/configuration/set-access-control-resources)
