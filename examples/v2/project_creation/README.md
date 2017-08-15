# Creating Projects Through Deployment Manager

This example set of templates will:

1.  Create a new project.
2.  Set the billing account on the new project.
3.  Set IAM permissions on the new project.
4.  Turn on a set of apis in the new project.
5.  Create service accounts in the new project.

There is some set up required to allow the service account under which
Deployment Manager runs to be able to perform these actions. You will also need
to customize the templates to set the information appropriately for your
organization (eg the billing account to use).

# Prerequisites

The prerequisites to create a project via DM. You can perform these steps via
the cloud console at https://console.cloud.google.com/

Permission changes can take up to 20 minutes to propagate. Sometimes propagation
is much faster, but if you run commands too early you may receive errors about
the user not having permissions.

1.  Create a project that will create and own the deployments.

    *   This will be called the "DM Creation Project" for the rest of these
        instructions.
    *   See:
        https://cloud.google.com/resource-manager/docs/creating-managing-organization
    *   Because of the special permissions granted in later steps, this DM
        Creation Project should not be used for any purpose other than creating
        other projects.

2.  Activate the following APIs on the DM Creation Project.

    *   Google Cloud Deployment Manager V2 API
    *   Google Cloud Resource Manager API
    *   Google Cloud Billing API
    *   Google Identity and Access Management (IAM) API
    *   Google Service Management API

3.  Find the Cloud Services service account associated with the DM Creation
    Project. It will be in the form
    &lt;project_number&gt;@cloudservices.gserviceaccount.com. This will be
    called the "DM Service Account" for the rest of these instructions.

    *   See https://cloud.google.com/resource-manager/docs/access-control-proj

4.  If you don't already have an Organization node under which you will create
    projects, then create one following [these
    instructions](https://cloud.google.com/resource-manager/docs/creating-managing-organization).

5.  Give the DM Service Account the following permissions on the organization
    node:

    *   'roles/resourcemanager.projectCreator'
        *   Visible in Cloud Console's IAM permissions in Resource Manager ->
            Project Creator.
    *   'roles/billing.user'
        *   Visible in Cloud Console's IAM permissions in Billing -> Billing
            Account User.
    *   See https://cloud.google.com/resource-manager/docs/access-control-proj

6.  Create/find a billing account associated with the organization.

    *   See: https://cloud.google.com/support/billing/

## Using the templates.

Once the prerequisites have been completed, projects can be created with
Deployment Manager via the API or the CLI. **Users SHOULD NOT use the DM
Creation Project to create any other resources. It SHOULD be dedicated to
project creation exclusively.**

1.  Now customize the templates for your organization. You will need to:

    *   Set the name of the new project you want to create. It must be unique
        among all project names.
    *   Set the organization id.
    *   Set the billing account to use.
    *   Set the APIs to turn on.
    *   Set the service accounts to create.
    *   Set the desired IAM policy for the project.
2.  Ensure you include the creating DM Service Account under "roles/owner"
    in your yaml config.
3.  Create the project. If using the CLI:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME
    --config config.yaml

**Note: Project names are globally unique, and cannot be reused. Make sure you
have a good naming scheme before stamping out projects.**
