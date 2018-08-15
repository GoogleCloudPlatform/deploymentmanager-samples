# Projects

Templated project creation. This templates will:

1. Create a new project.
2. Set the billing account on the new project.
3. Set IAM permissions on the new project.
4. Turn on a set of APIs in the new project.
5. Create service accounts in the new project.
6. Create an usage export Cloud Storage bucket in the new project


## Prerequisites

The prerequisites to create a project via DM. You can perform some of these
steps via the Cloud Console at https://console.cloud.google.com/

The `gcloud` command line tool is used for the deployment of the configs.

Permission changes can take up to 20 minutes to propagate. Sometimes
propagation is much faster, but if you run commands too early you may
receive errors about the user not having permissions.

1. **Install [gcloud](https://cloud.google.com/sdk)**

1.  **Create a project that will create and own the deployments**

    * This will be called the *"DM Creation Project"* for the rest of these
      instructions.
    * See: https://cloud.google.com/resource-manager/docs/creating-managing-organization
    * **IMPORTANT**: Because of the special permissions granted in later steps,
      this *DM Creation Project* should not be used for any purpose other than
      creating other projects.

1.  **Activate the following APIs on the *DM Creation Project***

    * Google Cloud Deployment Manager V2 API
    * Google Cloud Resource Manager API
    * Google Cloud Billing API
    * Google Identity and Access Management (IAM) API
    * Google Service Management API

    You may use `gcloud services enable` command to do this:

    ```
    gcloud services enable deploymentmanager.googleapis.com
    gcloud services enable cloudresourcemanager.googleapis.com
    gcloud services enable cloudbilling.googleapis.com
    gcloud services enable iam.googleapis.com
    gcloud services enable servicemanagement.googleapis.com
    ```

1.  **Find the *Cloud Services* service account associated with the *DM Creation Project***

    It will be in the form `<project_number>@cloudservices.gserviceaccount.com`
    and listed under [IAM & admin](https://console.cloud.google.com/iam-admin/iam)
    in Google Cloud Console. This will be called the *"DM Service Account"* for
    the rest of these instructions.
    * See https://cloud.google.com/resource-manager/docs/access-control-proj

1.  **Create an Organization node**

    If you don't already have an Organization node under which you will create
    projects, then create one following [these
    instructions](https://cloud.google.com/resource-manager/docs/creating-managing-organization).

1.  **Give the *DM Service Account* the following permissions on the organization node:**

    * `roles/resourcemanager.projectCreator`
        * This is visible in Cloud Console's *IAM permissions in Resource Manager
        ->  Project Creator.*
    * See https://cloud.google.com/resource-manager/docs/access-control-proj

1.  **Create/find a *Billing Account* associated with the organization**

    * See: https://cloud.google.com/support/billing/
    * Take note if the Billing Account ID that looks like `00E12A-0AB8B2-078CE8`

1.  **Give the *DM Service Account* the following permissions on the Billing Account:**
    * `roles/billing.user`
        * This is visible in Cloud Console's IAM permissions in
          *Billing -> Billing Account User*.


## Deployment

### Resources

- [cloudresourcemanager.v1.project](https://cloud.google.com/compute/docs/reference/latest/projects)
- [deploymentmanager.v2.virtual.projectBillingInfo](https://cloud.google.com/billing/reference/rest/v1/projects/updateBillingInfo)
- [iam.v1.serviceAccount](https://cloud.google.com/iam/reference/rest/v1/projects.serviceAccounts)
- [deploymentmanager.v2.virtual.enableService](https://cloud.google.com/service-management/reference/rest/v1/services/enable)
- [gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy](https://cloud.google.com/deployment-manager/docs/configuration/supported-gcp-types)
- [gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy](https://cloud.google.com/deployment-manager/docs/configuration/supported-gcp-types)
- [gcp-types/storage-v1:buckets](https://cloud.google.com/deployment-manager/docs/configuration/supported-gcp-types)
- [gcp-types/compute-v1:compute.projects.setUsageExportBucket](https://cloud.google.com/deployment-manager/docs/configuration/supported-gcp-types)
- [compute.beta.xpnResource](https://cloud.google.com/compute/docs/reference/rest/beta/projects/enableXpnResource)
- [compute.beta.xpnHost](https://cloud.google.com/compute/docs/reference/rest/beta/projects/enableXpnHost)
- [gcp-types/compute-beta:compute.firewalls.delete](https://cloud.google.com/compute/docs/reference/rest/beta/firewalls)
- [gcp-types/compute-beta:compute.networks.delete](https://cloud.google.com/compute/docs/reference/rest/beta/networks)
- [gcp-types/iam-v1:iam.projects.serviceAccounts.delete](https://cloud.google.com/iam/reference/rest/v1/projects.serviceAccounts)


### Properties

See `properties` section in the schema files

-  [project](project.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Go to the [community/cloud-foundation](../../../cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/project.yaml](examples/project.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
cd community/cloud-foundation
cp templates/project/examples/project.yaml my_project.yaml
vim my_project.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_project.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_project.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Project](examples/project.yaml)
